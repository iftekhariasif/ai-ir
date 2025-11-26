"""
TNFD LEAP Analysis - Core Processing Module
Supports both local (dev) and API (prod) modes
"""

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption
import os
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai
import json
import requests

# Load environment variables
load_dotenv()

def process_pdf_to_markdown(pdf_path, output_folder, pdf_name, enable_leap=True):
    """
    Core function to process PDF and generate markdown with images

    Args:
        pdf_path: Path to the PDF file
        output_folder: Directory to save output
        pdf_name: Name of the PDF (without extension)
        enable_leap: Whether to generate LEAP categorized files (default: True)

    Returns:
        dict with paths to generated files
    """
    # Create output folder structure
    os.makedirs(output_folder, exist_ok=True)
    images_folder = os.path.join(output_folder, f"{pdf_name}_images")
    os.makedirs(images_folder, exist_ok=True)

    print(f"📄 Processing: {pdf_name}.pdf")

    # Step 1: Extract with Docling
    print("⚙️  Extracting text and images with Docling...")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.images_scale = 2.0
    pipeline_options.generate_page_images = False
    pipeline_options.generate_picture_images = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    result = converter.convert(pdf_path)
    full_text = result.document.export_to_markdown()
    print(f"✅ Extracted {len(full_text)} characters")

    # Step 2: Extract and save images
    image_counter = 0
    if hasattr(result.document, 'pictures') and result.document.pictures:
        print(f"🖼️  Extracting {len(result.document.pictures)} images...")
        for idx, picture in enumerate(result.document.pictures):
            try:
                image_counter += 1
                image_filename = f"image_{image_counter:03d}.png"
                image_path = os.path.join(images_folder, image_filename)

                if hasattr(picture, 'get_image'):
                    img = picture.get_image(result.document)
                    if img:
                        img.save(image_path)
                elif hasattr(picture, 'image'):
                    picture.image.save(image_path)
            except Exception as e:
                print(f"⚠️  Warning: Could not extract image {image_counter}: {e}")
                image_counter -= 1

        print(f"✅ Saved {image_counter} images to {images_folder}")
    else:
        print("ℹ️  No images found in PDF")

    # Step 3: Process full text and replace image placeholders
    print("📝 Processing full text with images...")

    full_text_with_images = full_text
    global_image_counter = 0

    # Replace image placeholders with markdown image syntax
    while '<!-- image -->' in full_text_with_images and global_image_counter < image_counter:
        global_image_counter += 1
        image_filename = f"image_{global_image_counter:03d}.png"
        # Reference images in the images folder
        image_path = f"{pdf_name}_images/{image_filename}"
        img_tag = f'\n\n![Image {global_image_counter}]({image_path})\n\n'
        full_text_with_images = full_text_with_images.replace('<!-- image -->', img_tag, 1)

    # Step 4: Save full text markdown
    output_file = os.path.join(output_folder, f"{pdf_name}_full_text.md")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {pdf_name}\n\n")
        f.write("---\n\n")
        f.write(full_text_with_images)

    print(f"💾 Saved full text markdown: {output_file}")
    print(f"📁 Images saved to: {images_folder}")
    print(f"🖼️  Total images: {image_counter}")

    # Step 5: Generate LEAP categorized files (optional)
    leap_files = {}
    if enable_leap:
        print("📊 Categorizing content into LEAP framework...")
        leap_files = categorize_leap_content(full_text_with_images, output_folder, pdf_name, image_counter)

    print("\n✅ Done!")

    return {
        'markdown_file': output_file,
        'images_folder': images_folder,
        'image_count': image_counter,
        'leap_files': leap_files,
        'full_text': full_text_with_images
    }


def categorize_leap_content(full_text, output_folder, pdf_name, image_count, ai_model='gemini'):
    """
    Categorize content into LEAP framework phases using AI
    Creates separate markdown files for L, E, A, P

    Args:
        ai_model: 'gemini', 'perplexity', or 'keyword'
    """
    # Initialize LEAP content storage
    leap_content = {
        'L': [],
        'E': [],
        'A': [],
        'P': []
    }

    # Try AI-powered categorization based on selected model
    if ai_model == 'gemini':
        print("  🤖 Using Gemini AI for categorization...")
        try:
            leap_content = categorize_with_gemini(full_text)
        except Exception as e:
            print(f"  ⚠️  Gemini API failed: {e}")
            print("  🔄 Falling back to keyword-based categorization...")
            leap_content = categorize_with_keywords(full_text)
    elif ai_model == 'perplexity':
        print("  🤖 Using Perplexity AI for categorization...")
        try:
            leap_content = categorize_with_perplexity(full_text)
        except Exception as e:
            print(f"  ⚠️  Perplexity API failed: {e}")
            print("  🔄 Falling back to keyword-based categorization...")
            leap_content = categorize_with_keywords(full_text)
    else:
        print("  📝 Using keyword-based categorization...")
        leap_content = categorize_with_keywords(full_text)

    # Generate separate markdown files for each LEAP phase
    leap_files = {}
    phase_names = {
        'L': 'Locate',
        'E': 'Evaluate',
        'A': 'Assess',
        'P': 'Prepare'
    }

    for phase, phase_name in phase_names.items():
        phase_file = os.path.join(output_folder, f"{pdf_name}_{phase}.md")

        with open(phase_file, 'w', encoding='utf-8') as f:
            f.write(f"# {pdf_name} - LEAP Phase: {phase_name}\n\n")
            f.write("---\n\n")

            if leap_content[phase]:
                f.write('\n\n'.join(leap_content[phase]))
            else:
                f.write(f"*No content identified for {phase_name} phase*\n")

        leap_files[phase] = phase_file
        print(f"  📝 Created {phase}.md with {len(leap_content[phase])} sections")

    return leap_files


def categorize_with_gemini(full_text):
    """
    Use Gemini AI to categorize content into LEAP phases
    Reads prompt from prompt/GEMINI.md for easy customization
    """
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise Exception("GEMINI_API_KEY not found in environment")

    genai.configure(api_key=api_key)

    # Get model name from .env (default: gemini-2.5-flash)
    model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    model = genai.GenerativeModel(model_name)

    # Read prompt template from markdown file
    prompt_file = Path(__file__).parent / 'prompt' / 'GEMINI.md'
    prompt_template = None

    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()

    if not prompt_template:
        # Fallback to default prompt if not found in .env
        prompt_template = """Analyze this TNFD report and categorize each section into LEAP framework phases.

LEAP Framework:
- L (Locate): Geographic information, site locations, areas, facilities, biomes, regions, spatial data
- E (Evaluate): Dependencies, impacts, materiality, ecosystem services, environmental effects
- A (Assess): Risks, opportunities, scenarios, financial impacts, climate risks, threats
- P (Prepare): Strategy, targets, indicators, governance, action plans, metrics, goals

Instructions:
1. Read through the entire document
2. Identify distinct sections (by headings)
3. Categorize each section into L, E, A, or P based on its primary focus
4. Return a JSON object with this structure:
{{"L": ["section content with heading...", "another section..."], "E": ["section content with heading...", "another section..."], "A": ["section content with heading...", "another section..."], "P": ["section content with heading...", "another section..."]}}

Important:
- Include the section heading (as ###) at the start of each categorized content
- Keep the original markdown formatting
- If a section doesn't clearly fit any phase, put it in the most relevant one
- Some sections may span multiple phases - choose the PRIMARY focus

Document to analyze:
{full_text}

Return ONLY the JSON object, no other text."""

    # Replace {full_text} placeholder with actual content
    prompt = prompt_template.replace('{full_text}', full_text)

    # Call Gemini API
    response = model.generate_content(prompt)
    response_text = response.text.strip()

    # Extract JSON from response (handle markdown code blocks)
    if response_text.startswith('```json'):
        response_text = response_text.split('```json')[1].split('```')[0].strip()
    elif response_text.startswith('```'):
        response_text = response_text.split('```')[1].split('```')[0].strip()

    # Parse JSON response
    leap_data = json.loads(response_text)

    # Ensure all phases exist
    leap_content = {
        'L': leap_data.get('L', []),
        'E': leap_data.get('E', []),
        'A': leap_data.get('A', []),
        'P': leap_data.get('P', [])
    }

    return leap_content


def categorize_with_perplexity(full_text):
    """
    Use Perplexity AI to categorize content into LEAP phases
    Reads prompt from prompt/PERPLEXITY.md for easy customization
    """
    # Get API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        raise Exception("PERPLEXITY_API_KEY not found in environment")

    # Read prompt template from markdown file
    prompt_file = Path(__file__).parent / 'prompt' / 'PERPLEXITY.md'
    prompt_template = None

    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()

    if not prompt_template:
        # Fallback to default prompt if not found in .env
        prompt_template = """Analyze this TNFD report and categorize each section into LEAP framework phases.

LEAP Framework:
- L (Locate): Geographic information, site locations, areas, facilities, biomes, regions, spatial data
- E (Evaluate): Dependencies, impacts, materiality, ecosystem services, environmental effects
- A (Assess): Risks, opportunities, scenarios, financial impacts, climate risks, threats
- P (Prepare): Strategy, targets, indicators, governance, action plans, metrics, goals

Instructions:
1. Read through the entire document
2. Identify distinct sections (by headings)
3. Categorize each section into L, E, A, or P based on its primary focus
4. Return a JSON object with this structure:
{{"L": ["section content with heading...", "another section..."], "E": ["section content with heading...", "another section..."], "A": ["section content with heading...", "another section..."], "P": ["section content with heading...", "another section..."]}}

Important:
- Include the section heading (as ###) at the start of each categorized content
- Keep the original markdown formatting
- If a section doesn't clearly fit any phase, put it in the most relevant one
- Some sections may span multiple phases - choose the PRIMARY focus

Document to analyze:
{full_text}

Return ONLY the JSON object, no other text."""

    # Replace {full_text} placeholder with actual content
    prompt = prompt_template.replace('{full_text}', full_text)

    # Call Perplexity API
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'llama-3.1-sonar-large-128k-online',
        'messages': [
            {
                'role': 'system',
                'content': 'You are an expert in TNFD (Taskforce on Nature-related Financial Disclosures) framework analysis.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'temperature': 0.2,
        'max_tokens': 4000
    }

    response = requests.post(
        'https://api.perplexity.ai/chat/completions',
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")

    result = response.json()
    response_text = result['choices'][0]['message']['content'].strip()

    # Extract JSON from response (handle markdown code blocks)
    if response_text.startswith('```json'):
        response_text = response_text.split('```json')[1].split('```')[0].strip()
    elif response_text.startswith('```'):
        response_text = response_text.split('```')[1].split('```')[0].strip()

    # Parse JSON response
    leap_data = json.loads(response_text)

    # Ensure all phases exist
    leap_content = {
        'L': leap_data.get('L', []),
        'E': leap_data.get('E', []),
        'A': leap_data.get('A', []),
        'P': leap_data.get('P', [])
    }

    return leap_content


def categorize_with_keywords(full_text):
    """
    Fallback: Use keyword-based categorization (legacy method)
    """
    leap_keywords = {
        'L': ['locate', 'location', 'geographic', 'site', 'area', 'region', 'facility', 'biome'],
        'E': ['evaluate', 'evaluation', 'dependency', 'dependencies', 'impact', 'materiality', 'ecosystem'],
        'A': ['assess', 'assessment', 'risk', 'opportunity', 'scenario', 'financial impact'],
        'P': ['prepare', 'strategy', 'target', 'indicator', 'governance', 'metric', 'action plan']
    }

    leap_content = {
        'L': [],
        'E': [],
        'A': [],
        'P': []
    }

    # Split by sections
    lines = full_text.split('\n')
    current_section = None
    current_content = []

    for line in lines:
        # Check if this is a heading
        if line.startswith('##') or line.startswith('#'):
            # Save previous section
            if current_section and current_content:
                content_text = '\n'.join(current_content)
                section_lower = current_section.lower()

                # Categorize based on keywords
                categorized = False
                for phase, keywords in leap_keywords.items():
                    if any(keyword in section_lower for keyword in keywords):
                        leap_content[phase].append(f"### {current_section}\n\n{content_text}")
                        categorized = True
                        break

            # Start new section
            current_section = line.replace('#', '').strip()
            current_content = []
        else:
            if line.strip():
                current_content.append(line)

    # Save last section
    if current_section and current_content:
        content_text = '\n'.join(current_content)
        section_lower = current_section.lower()
        for phase, keywords in leap_keywords.items():
            if any(keyword in section_lower for keyword in keywords):
                leap_content[phase].append(f"### {current_section}\n\n{content_text}")
                break

    return leap_content


def start_web_server():
    """Start the web server with Flask"""
    from flask import Flask, send_file, request, jsonify
    from flask_cors import CORS
    import traceback

    app = Flask(__name__)
    CORS(app)

    PROJECT_ROOT = Path(__file__).parent

    @app.route('/')
    def index():
        """Serve the main frontend"""
        return send_file('client/index.html')

    @app.route('/file')
    def serve_file():
        """Serve any file from the project directory"""
        file_path = request.args.get('path', '')

        print(f"📥 Request: {file_path}")

        if not file_path:
            return jsonify({'error': 'No path specified'}), 400

        full_path = PROJECT_ROOT / file_path

        try:
            full_path = full_path.resolve()
            if not str(full_path).startswith(str(PROJECT_ROOT.resolve())):
                return jsonify({'error': 'Access denied'}), 403
        except Exception as e:
            return jsonify({'error': 'Invalid path'}), 400

        if not full_path.exists():
            return jsonify({'error': f'File not found: {file_path}'}), 404

        try:
            return send_file(full_path)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/list')
    def list_files():
        """List files in a directory"""
        dir_path = request.args.get('path', '')
        full_path = PROJECT_ROOT / dir_path

        if not full_path.exists() or not full_path.is_dir():
            return jsonify({'error': 'Directory not found'}), 404

        files = []
        for item in full_path.iterdir():
            if item.is_file():
                files.append({
                    'name': item.name,
                    'path': str(item.relative_to(PROJECT_ROOT)),
                    'size': item.stat().st_size
                })

        return jsonify({'files': files})

    @app.route('/api/analyze', methods=['POST'])
    def api_analyze():
        """Analyze PDF - Convert to text/markdown only"""
        try:
            data = request.json
            pdf_path = data.get('pdf_path', '')

            if not pdf_path:
                return jsonify({'error': 'No PDF path provided'}), 400

            full_pdf_path = PROJECT_ROOT / pdf_path
            if not full_pdf_path.exists():
                return jsonify({'error': f'PDF not found: {pdf_path}'}), 404

            pdf_name = full_pdf_path.stem
            output_folder = PROJECT_ROOT / 'output'

            print(f"🔬 Analyzing: {pdf_name}.pdf")

            # Process without LEAP categorization
            result = process_pdf_to_markdown(
                str(full_pdf_path),
                str(output_folder),
                pdf_name,
                enable_leap=False
            )

            markdown_rel = Path(result['markdown_file']).relative_to(PROJECT_ROOT)
            images_rel = Path(result['images_folder']).relative_to(PROJECT_ROOT)

            return jsonify({
                'success': True,
                'pdf_name': pdf_name,
                'markdown_path': str(markdown_rel),
                'markdown_name': Path(result['markdown_file']).name,
                'image_count': result['image_count'],
                'images_folder': str(images_rel)
            })

        except Exception as e:
            print(f"❌ Analysis error: {str(e)}")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/leap', methods=['POST'])
    def api_leap():
        """LEAP Categorization - Divide content into L, E, A, P phases"""
        try:
            data = request.json
            markdown_path = data.get('markdown_path', '')
            pdf_name = data.get('pdf_name', '')
            ai_model = data.get('ai_model', 'gemini')  # Default to gemini

            if not markdown_path or not pdf_name:
                return jsonify({'error': 'Missing markdown_path or pdf_name'}), 400

            full_markdown_path = PROJECT_ROOT / markdown_path
            if not full_markdown_path.exists():
                return jsonify({'error': f'Markdown file not found: {markdown_path}'}), 404

            print(f"📊 LEAP categorization: {pdf_name} using {ai_model.upper()}")

            # Read markdown content
            with open(full_markdown_path, 'r', encoding='utf-8') as f:
                full_text = f.read()

            image_count = full_text.count('![Image')
            output_folder = PROJECT_ROOT / 'output'

            # Generate LEAP categorized files
            leap_files = categorize_leap_content(
                full_text,
                str(output_folder),
                pdf_name,
                image_count,
                ai_model=ai_model
            )

            # Return relative paths
            leap_files_rel = {}
            for phase, file_path in leap_files.items():
                leap_files_rel[phase] = str(Path(file_path).relative_to(PROJECT_ROOT))

            return jsonify({
                'success': True,
                'pdf_name': pdf_name,
                'leap_files': leap_files_rel,
                'phases': list(leap_files.keys())
            })

        except Exception as e:
            print(f"❌ LEAP error: {str(e)}")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    print("=" * 60)
    print("🚀 PDF Extract Server")
    print("=" * 60)
    print(f"📁 Project root: {PROJECT_ROOT}")
    print(f"🌐 Open browser: http://localhost:5555")
    print(f"📡 API endpoints:")
    print(f"   • POST /api/analyze - PDF to text conversion")
    print(f"   • POST /api/leap    - LEAP categorization")
    print(f"🛑 Stop server: Press Ctrl+C")
    print("=" * 60)

    app.run(host='127.0.0.1', port=5555, debug=True)


if __name__ == "__main__":
    start_web_server()
