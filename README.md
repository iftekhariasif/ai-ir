# TNFD LEAP Analysis - PDF to Markdown Converter

Automated system for extracting and categorizing TNFD (Taskforce on Nature-related Financial Disclosures) reports using the LEAP framework.

## What It Does

**Input:** PDF files (TNFD reports)

**Process:**
1. Extracts text and images using Docling
2. Detects language (English/Japanese)
3. Categorizes content into LEAP framework using Perplexity API:
   - **L (Locate)**: Geographic locations, priority sites, biomes
   - **E (Evaluate)**: Dependencies, impacts, materiality assessment
   - **A (Assess)**: Risks, opportunities, scenario analysis
   - **P (Prepare)**: Strategy, targets, governance, action plans
4. Generates markdown output with embedded images

**Output:** Organized markdown file + extracted images

---

## Project Structure

```
pdf-extract/
├── api/
│   └── pdf_to_markdown.py      # Complete API with Google Drive integration
├── main.py                      # Core processing script (standalone)
├── api.py                       # Basic API (file upload)
├── n8n/
│   └── workflow.json            # n8n workflow configuration
├── n8n_processor.py             # Python processor for n8n Code node
├── n8n_code_node.js             # JavaScript for n8n Code node
├── input/                       # Place PDFs here (for standalone)
├── output/                      # Generated files (for standalone)
└── requirements.txt             # Python dependencies
```

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file:

```bash
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

---

## Usage Options

### Option 1: Standalone Script (Local Processing)

**Use case:** Process PDFs locally without any API or workflow

```bash
# Place PDF in input/ folder
python main.py
```

**Output:** Files saved to `output/` folder

---

### Option 2: Basic API (File Upload)

**Use case:** Accept PDF uploads via HTTP API

#### Start the API:

```bash
python api.py
```

API runs at: `http://localhost:8000`

#### API Endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/convert` | POST | Convert PDF to Markdown |
| `/health` | GET | Health check |

#### Example Request:

```bash
curl -X POST http://localhost:8000/convert \
  -F "file=@document.pdf"
```

#### Response:

```json
{
  "success": true,
  "markdownFileName": "document_leap.md",
  "markdownData": "<base64 encoded markdown>",
  "images": [
    {
      "fileName": "image_001.png",
      "data": "<base64 encoded image>"
    }
  ],
  "language": "ja",
  "imageCount": 5,
  "textLength": 15000
}
```

---

### Option 3: Complete API (Google Drive Integration)

**Use case:** Fully automated workflow with Google Drive

#### Features:
- Automatically downloads PDFs from Google Drive input folder
- Processes all PDFs with LEAP categorization
- Uploads markdown + images to Google Drive output folder
- No manual file handling needed

#### Setup Google OAuth:

1. **Prepare credentials:**

```bash
# Copy your OAuth credentials
cp keys/final.json credentials.json
```

2. **Start the API:**

```bash
python api/pdf_to_markdown.py
```

3. **First-time authorization:**
   - Browser opens automatically
   - Sign in with Google account
   - Click "Allow"
   - A `token.pickle` file is created (saves authorization)

4. **Subsequent runs:**
   - API starts automatically without authorization prompt

#### API Configuration:

**Default Google Drive Folders:**
- Input: `12jkoNxUr8fJr_hDKquaj73s0AX0AYTQS`
- Output: `1l9zQhCkO-NLUDQRlZbliysvc4uHXBJ-X`

**Endpoint:** `POST /process`

**Request:**

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "inputFolderId": "12jkoNxUr8fJr_hDKquaj73s0AX0AYTQS",
    "outputFolderId": "1l9zQhCkO-NLUDQRlZbliysvc4uHXBJ-X"
  }'
```

**Response:**

```json
{
  "success": true,
  "message": "Successfully processed 2 PDF(s)",
  "processed": 2,
  "files": [
    {
      "fileName": "document1.pdf",
      "language": "ja",
      "imageCount": 5,
      "markdownUrl": "https://drive.google.com/...",
      "imagesUrl": "https://drive.google.com/..."
    }
  ]
}
```

---

## n8n Workflow Integration

### Workflow Architecture:

```
1. Button Trigger
   ↓
2. Workflow Configuration (Set folder IDs)
   ↓
3. HTTP Request → POST /process
   ↓
4. Done! ✅
```

### n8n HTTP Request Node Configuration:

**Method:** `POST`

**URL:** `http://localhost:8000/process`

**Authentication:** None

**Headers:**
- `Content-Type`: `application/json`

**Body (JSON):**

```json
{
  "inputFolderId": "12jkoNxUr8fJr_hDKquaj73s0AX0AYTQS",
  "outputFolderId": "1l9zQhCkO-NLUDQRlZbliysvc4uHXBJ-X"
}
```

**What happens:**
1. API downloads all PDFs from Google Drive input folder
2. Processes each PDF with LEAP categorization
3. Uploads markdown + images to Google Drive output folder
4. Returns success message with links

---

## Deployment Options

### Local (Free)

```bash
python api/pdf_to_markdown.py
```

Use `http://localhost:8000` in n8n

### Expose with ngrok (Testing)

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000
```

Use the ngrok URL: `https://xxxx.ngrok.io`

### Google Cloud Run (Production)

**Create Dockerfile:**

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.pdf_to_markdown:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Deploy:**

```bash
gcloud run deploy tnfd-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PERPLEXITY_API_KEY=your_key_here
```

**Use in n8n:**

Update URL to: `https://tnfd-api-xxxxx.run.app/process`

---

## Troubleshooting

### Error: "PERPLEXITY_API_KEY not configured"
- Ensure `.env` file exists with your API key
- Or set environment variable: `export PERPLEXITY_API_KEY=your_key`

### Error: "credentials.json not found"
- Copy your OAuth credentials: `cp keys/final.json credentials.json`

### Error: "Docling not installed"
- Run: `pip install -r requirements.txt`

### Browser doesn't open for Google OAuth
- Check terminal for authorization link
- Copy and paste link into browser

### Files not appearing in Google Drive
- Verify folder IDs are correct
- Ensure you authorized with the correct Google account
- Check folder permissions

### n8n can't reach localhost
- Use ngrok to expose local API
- Or deploy to cloud service
- Or run n8n and API on same machine

---

## Cost Estimation

**Local (Free):**
- No hosting costs
- Only Perplexity API: ~$0.001-0.005 per PDF

**Google Cloud Run (Free Tier):**
- 2 million requests/month free
- After free tier: ~$0.40 per million requests
- Cold starts may add 2-3 seconds latency

---

## Features

✅ Bilingual support (English/Japanese auto-detection)
✅ Image extraction with proper embedding in markdown
✅ Keyword-based LEAP categorization
✅ Perplexity AI-powered section identification
✅ Multiple deployment options (local/API/cloud)
✅ n8n workflow compatible
✅ Google Drive integration
✅ OAuth authentication
✅ Batch processing support

---

## LEAP Framework Reference

| Phase | Full Name | Focus |
|-------|-----------|-------|
| **L** | Locate | Geographic locations, priority location identification, site assessment, biomes |
| **E** | Evaluate | Dependencies and impacts analysis, materiality assessment, ENCORE usage |
| **A** | Assess | Risk and opportunity assessment, scenario analysis, financial impact |
| **P** | Prepare | Strategy, targets, action plans, governance, metrics, commitments |

---

## License

MIT

---

## Support

For issues or questions, check the troubleshooting section above or review the API logs for detailed error messages.
