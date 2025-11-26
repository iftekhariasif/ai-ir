"""
Complete API for TNFD LEAP Analysis with Google Drive Integration
This API:
1. Downloads PDFs from Google Drive input folder
2. Processes them with LEAP categorization
3. Uploads markdown + images to Google Drive output folder
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
import tempfile
import base64
from pathlib import Path
from typing import Optional

# Add parent directory to path to import main module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Google Drive imports
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import pickle

# Load environment
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="TNFD LEAP Analysis API with Google Drive")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Drive API Scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

# Default folder IDs from your n8n workflow
DEFAULT_INPUT_FOLDER = "12jkoNxUr8fJr_hDKquaj73s0AX0AYTQS"
DEFAULT_OUTPUT_FOLDER = "1l9zQhCkO-NLUDQRlZbliysvc4uHXBJ-X"

class ProcessRequest(BaseModel):
    inputFolderId: Optional[str] = DEFAULT_INPUT_FOLDER
    outputFolderId: Optional[str] = DEFAULT_OUTPUT_FOLDER

def get_google_drive_service():
    """Get Google Drive API service"""
    creds = None
    token_file = 'token.pickle'

    # Load saved credentials
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise HTTPException(
                    status_code=500,
                    detail="credentials.json not found. Please add your Google OAuth credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def download_file_from_drive(service, file_id, destination_path):
    """Download a file from Google Drive"""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    with open(destination_path, 'wb') as f:
        f.write(fh.read())

def upload_file_to_drive(service, file_path, folder_id, file_name=None):
    """Upload a file to Google Drive"""
    if file_name is None:
        file_name = os.path.basename(file_path)

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    # Determine mime type
    if file_path.endswith('.md'):
        mime_type = 'text/markdown'
    elif file_path.endswith('.txt'):
        mime_type = 'text/plain'
    elif file_path.endswith('.png'):
        mime_type = 'image/png'
    else:
        mime_type = 'application/octet-stream'

    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()

    return file

def upload_folder_to_drive(service, local_folder, parent_folder_id, folder_name):
    """Upload an entire folder to Google Drive"""
    # Create folder in Google Drive
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    folder = service.files().create(body=folder_metadata, fields='id, name').execute()
    folder_id = folder['id']

    # Upload all files in the folder
    uploaded_files = []
    for file_name in os.listdir(local_folder):
        file_path = os.path.join(local_folder, file_name)
        if os.path.isfile(file_path):
            uploaded = upload_file_to_drive(service, file_path, folder_id, file_name)
            uploaded_files.append(uploaded)

    return folder, uploaded_files

def process_pdf(pdf_path, pdf_name):
    """Process a PDF file - uses core function from main.py"""

    # Create temporary output folder
    temp_output = tempfile.mkdtemp()

    # Use the core processing function from main.py
    from main import process_pdf_to_markdown

    result = process_pdf_to_markdown(pdf_path, temp_output, pdf_name)

    return {
        'markdown_file': result['markdown_file'],
        'images_folder': result['images_folder'],
        'image_count': result['image_count'],
        'language': 'en'  # Default for now
    }

@app.get("/")
def read_root():
    return {
        "message": "TNFD LEAP Analysis API with Google Drive",
        "version": "2.0",
        "endpoints": {
            "/convert": "POST - Convert uploaded PDF to Markdown (for n8n)",
            "/process": "POST - Process PDFs from Google Drive (automated)"
        }
    }

@app.post("/process")
async def process_from_google_drive(request: ProcessRequest):
    """
    Process PDFs from Google Drive input folder and upload results to output folder
    """
    try:
        # Get Google Drive service
        print("🔑 Authenticating with Google Drive...")
        service = get_google_drive_service()

        # List PDF files in input folder
        print(f"📂 Listing PDFs in folder: {request.inputFolderId}")
        query = f"'{request.inputFolderId}' in parents and mimeType='application/pdf' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if not files:
            return {
                "success": False,
                "message": "No PDF files found in input folder",
                "processed": 0
            }

        print(f"📄 Found {len(files)} PDF file(s)")

        processed_files = []

        # Process each PDF
        for file in files:
            file_id = file['id']
            file_name = file['name']
            pdf_name = file_name.replace('.pdf', '')

            print(f"\n🔄 Processing: {file_name}")

            with tempfile.TemporaryDirectory() as temp_dir:
                # Download PDF
                pdf_path = os.path.join(temp_dir, file_name)
                print(f"⬇️  Downloading from Google Drive...")
                download_file_from_drive(service, file_id, pdf_path)

                # Process PDF
                print(f"⚙️  Converting to Markdown...")
                result = process_pdf(pdf_path, pdf_name)

                # Upload markdown file
                print(f"⬆️  Uploading markdown...")
                md_uploaded = upload_file_to_drive(
                    service,
                    result['markdown_file'],
                    request.outputFolderId,
                    f"{pdf_name}_leap.md"
                )

                # Upload text file
                txt_uploaded = upload_file_to_drive(
                    service,
                    result['text_file'],
                    request.outputFolderId,
                    f"{pdf_name}_leap.txt"
                )

                # Upload images folder
                images_uploaded = None
                if result['image_count'] > 0:
                    print(f"⬆️  Uploading {result['image_count']} images...")
                    folder, images = upload_folder_to_drive(
                        service,
                        result['images_folder'],
                        request.outputFolderId,
                        f"{pdf_name}_images"
                    )
                    images_uploaded = folder

                processed_files.append({
                    "fileName": file_name,
                    "language": result['language'],
                    "imageCount": result['image_count'],
                    "markdownUrl": md_uploaded.get('webViewLink'),
                    "imagesUrl": images_uploaded.get('webViewLink') if images_uploaded else None
                })

                print(f"✅ Completed: {file_name}")

        return {
            "success": True,
            "message": f"Successfully processed {len(processed_files)} PDF(s)",
            "processed": len(processed_files),
            "files": processed_files
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    """
    Convert PDF to Markdown with LEAP categorization

    Accepts: PDF file upload
    Returns: markdown (base64) + images (base64)
    """
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded PDF
            pdf_path = os.path.join(temp_dir, file.filename)
            with open(pdf_path, 'wb') as f:
                content = await file.read()
                f.write(content)

            pdf_name = file.filename.replace('.pdf', '')

            print(f"📄 Processing: {file.filename}")

            # Process PDF using the existing function
            result = process_pdf(pdf_path, pdf_name)

            print(f"💾 Generated markdown: {result['markdown_file']}")

            # Read markdown file and encode to base64
            with open(result['markdown_file'], 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            markdown_base64 = base64.b64encode(markdown_content.encode('utf-8')).decode('utf-8')

            # Read all images and encode to base64
            images_data = []
            if os.path.exists(result['images_folder']):
                for img_file in sorted(os.listdir(result['images_folder'])):
                    if img_file.endswith('.png'):
                        img_path = os.path.join(result['images_folder'], img_file)
                        with open(img_path, 'rb') as f:
                            img_base64 = base64.b64encode(f.read()).decode('utf-8')
                        images_data.append({
                            "fileName": img_file,
                            "data": img_base64
                        })

            print("✅ Conversion complete!")

            # Return response in n8n-compatible format
            return JSONResponse({
                "success": True,
                "markdownFileName": f"{pdf_name}_leap.md",
                "markdownData": markdown_base64,
                "images": images_data,
                "language": result['language'],
                "imageCount": result['image_count']
            })

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting TNFD LEAP Analysis API with Google Drive Integration")
    print("📝 Make sure you have credentials.json in the project folder")
    uvicorn.run(app, host="0.0.0.0", port=8000)
