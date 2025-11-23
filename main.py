from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption
import os
import requests
import json
from dotenv import load_dotenv
import re
from pathlib import Path
import base64

def detect_language(text):
    """Detect if text is primarily Japanese or English"""
    # Count Japanese characters (Hiragana, Katakana, Kanji)
    japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text))
    # Count English/Latin characters
    english_chars = len(re.findall(r'[a-zA-Z]', text))

    # Compare ratio
    total_chars = japanese_chars + english_chars
    if total_chars == 0:
        return 'en'  # Default to English

    japanese_ratio = japanese_chars / total_chars

    # If more than 30% Japanese characters, consider it Japanese
    return 'ja' if japanese_ratio > 0.3 else 'en'

def get_leap_keywords(language='en'):
    """Get LEAP keywords for the specified language"""
    keywords = {
        'en': {
            'locate': ['locate', 'location', 'priority location', 'geographic', 'site', 'biome', 'facility', 'ecosystem', 'area'],
            'evaluate': ['evaluate', 'evaluation', 'dependency', 'dependencies', 'impact', 'materiality', 'ecosystem service', 'encore'],
            'assess': ['assess', 'assessment', 'risk', 'opportunity', 'scenario', 'financial impact', 'nature-related risk'],
            'prepare': ['prepare', 'strategy', 'target', 'indicator', 'governance', 'metric', 'commitment', 'action plan']
        },
        'ja': {
            'locate': ['ロケート', '場所', '位置', '地理', 'サイト', '生物群系', 'バイオーム', '優先地域', '場所の特定', '地域特定', '立地'],
            'evaluate': ['評価', '依存性', '依存関係', '影響', 'マテリアリティ', '重要性評価', '生態系サービス', 'エンコア'],
            'assess': ['アセスメント', 'リスク', '機会', 'シナリオ', '財務影響', '自然関連リスク', 'リスク評価', '機会評価'],
            'prepare': ['準備', '戦略', '目標', 'ターゲット', '指標', 'ガバナンス', 'メトリクス', 'コミットメント', '行動計画', 'アクションプラン']
        }
    }
    return keywords.get(language, keywords['en'])

def generate_markdown_output(leap_content, leap_framework, full_text, output_file, images_folder, pdf_name, language='en'):
    """Generate Markdown output with embedded images"""

    markdown_content = []

    # Header
    markdown_content.append(f"# TNFD LEAP Analysis\n")
    markdown_content.append(f"**Report:** {pdf_name}\n")
    markdown_content.append(f"\n---\n\n")

    # LEAP phases
    phases = [
        ('locate', 'L', '🟢'),
        ('evaluate', 'E', '🔵'),
        ('assess', 'A', '🟠'),
        ('prepare', 'P', '🟣')
    ]

    no_content_msg = "*[このフェーズのコンテンツは識別されませんでした]*" if language == 'ja' else "*[No content identified for this phase]*"

    for phase_key, phase_letter, emoji in phases:
        phase_name = leap_framework[phase_letter]

        # Phase header
        markdown_content.append(f"## {emoji} {phase_letter} - {phase_name}\n\n")

        if leap_content[phase_key]:
            for section in leap_content[phase_key]:
                markdown_content.append(f"{section}\n\n")
        else:
            markdown_content.append(f"{no_content_msg}\n\n")

        markdown_content.append(f"---\n\n")

    # Full text section
    full_text_header = "完全抽出テキスト" if language == 'ja' else "FULL EXTRACTED TEXT"
    markdown_content.append(f"## 📄 {full_text_header}\n\n")
    markdown_content.append(f"```\n{full_text}\n```\n")

    # Save markdown file
    md_file = output_file.replace('.txt', '.md')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(''.join(markdown_content))

    return md_file

def get_leap_prompt(language='en'):
    """Get LEAP analysis prompt for the specified language"""
    prompts = {
        'en': {
            'instruction': """Analyze this TNFD report and identify which sections belong to each LEAP phase.

IMPORTANT: DO NOT SUMMARIZE. Return the exact section titles/headings that belong to each phase.

LEAP Framework:
- L (Locate): Geographic locations, priority location identification, site assessment, biomes
- E (Evaluate): Dependencies and impacts analysis, materiality assessment, ENCORE usage
- A (Assess): Risk and opportunity assessment, scenario analysis, financial impact
- P (Prepare): Strategy, targets, action plans, governance, metrics, commitments

Return ONLY valid JSON with section headings (not content):
{
  "locate": ["Section Title 1", "Section Title 2"],
  "evaluate": ["Section Title 3"],
  "assess": ["Section Title 4", "Section Title 5"],
  "prepare": ["Section Title 6"]
}""",
            'framework': {
                'L': 'Locate',
                'E': 'Evaluate',
                'A': 'Assess',
                'P': 'Prepare'
            }
        },
        'ja': {
            'instruction': """このTNFDレポートを分析し、各セクションがLEAPフレームワークのどのフェーズに属するかを特定してください。

重要: 要約しないでください。各フェーズに属する正確なセクションタイトル/見出しを返してください。

LEAPフレームワーク:
- L (ロケート/場所の特定): 地理的位置、優先地域の特定、サイト評価、生物群系
- E (評価): 依存関係と影響の分析、マテリアリティ評価、ENCOREの使用
- A (アセスメント): リスクと機会の評価、シナリオ分析、財務影響
- P (準備): 戦略、目標、行動計画、ガバナンス、指標、コミットメント

有効なJSONのみを返してください（セクション見出しのみ、内容は含めない）:
{
  "locate": ["セクションタイトル1", "セクションタイトル2"],
  "evaluate": ["セクションタイトル3"],
  "assess": ["セクションタイトル4", "セクションタイトル5"],
  "prepare": ["セクションタイトル6"]
}""",
            'framework': {
                'L': 'ロケート（場所の特定）',
                'E': '評価',
                'A': 'アセスメント',
                'P': '準備'
            }
        }
    }
    return prompts.get(language, prompts['en'])

def process_tnfd():
    """Extract PDF and categorize full text by LEAP phases"""
    
    # Load API key
    load_dotenv()
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    
    if not PERPLEXITY_API_KEY:
        print("❌ PERPLEXITY_API_KEY not found in .env file")
        return
    
    # Setup folders
    input_folder = "input"
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    # Find PDF
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDF found in input folder")
        return

    pdf_path = os.path.join(input_folder, pdf_files[0])
    pdf_name = pdf_files[0].replace('.pdf', '')
    print(f"📄 Processing: {pdf_files[0]}")

    # Create images folder
    images_folder = os.path.join(output_folder, f"{pdf_name}_images")
    os.makedirs(images_folder, exist_ok=True)

    # Step 1: Extract with Docling (with image export enabled)
    print("⚙️  Extracting text and images with Docling...")

    # Configure pipeline to export images
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

    # Export markdown
    full_text = result.document.export_to_markdown()
    print(f"✅ Extracted {len(full_text)} characters")

    # Extract and save images
    image_counter = 0
    image_mapping = {}  # Map image placeholders to saved file paths

    if hasattr(result.document, 'pictures') and result.document.pictures:
        print(f"🖼️  Extracting {len(result.document.pictures)} images...")
        for idx, picture in enumerate(result.document.pictures):
            try:
                image_counter += 1
                image_filename = f"image_{image_counter:03d}.png"
                image_path = os.path.join(images_folder, image_filename)

                # Save image (pass document to get_image)
                if hasattr(picture, 'get_image'):
                    img = picture.get_image(result.document)
                    if img:
                        img.save(image_path)
                        image_mapping[f"<!-- image -->"] = f"{pdf_name}_images/{image_filename}"
                elif hasattr(picture, 'image'):
                    picture.image.save(image_path)
                    image_mapping[f"<!-- image -->"] = f"{pdf_name}_images/{image_filename}"
            except Exception as e:
                print(f"⚠️  Warning: Could not extract image {image_counter}: {e}")
                image_counter -= 1  # Don't count failed images

        print(f"✅ Saved {image_counter} images to {images_folder}")
    else:
        print("ℹ️  No images found in PDF")

    # Step 1.5: Detect language
    detected_language = detect_language(full_text[:5000])  # Check first 5000 chars for speed
    language_name = "Japanese" if detected_language == 'ja' else "English"
    print(f"🌐 Detected language: {language_name} ({detected_language})")

    # Get language-specific keywords and prompts
    leap_keywords = get_leap_keywords(detected_language)
    leap_prompt_config = get_leap_prompt(detected_language)

    # Step 2: Identify LEAP sections with Perplexity
    print("🤖 Identifying LEAP sections with Perplexity...")

    prompt = f"""{leap_prompt_config['instruction']}

Document:
{full_text[:15000]}
"""

    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [{"role": "user", "content": prompt}],
                "return_citations": False
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        leap_sections = result['choices'][0]['message']['content']
        
        print("✅ LEAP sections identified")
        
        # Clean JSON
        leap_sections = leap_sections.replace("```json", "").replace("```", "").strip()
        section_mapping = json.loads(leap_sections)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("Using keyword-based fallback...")
        section_mapping = {
            "locate": [],
            "evaluate": [],
            "assess": [],
            "prepare": []
        }
    
    # Step 3: Extract full text for each section
    print("📝 Extracting full text by LEAP phase...")
    
    leap_content = {
        "locate": [],
        "evaluate": [],
        "assess": [],
        "prepare": []
    }
    
    # Split by sections
    lines = full_text.split('\n')
    current_section = None
    current_content = []
    global_image_counter = 0

    for line in lines:
        # Check if this is a heading
        if line.startswith('##') or line.startswith('#'):
            # Save previous section
            if current_section and current_content:
                content_text = '\n'.join(current_content)

                # Replace image placeholders with markdown image syntax
                while '<!-- image -->' in content_text and global_image_counter < image_counter:
                    global_image_counter += 1
                    image_filename = f"image_{global_image_counter:03d}.png"
                    # Use just the image filename (no folder prefix) for n8n Google Drive compatibility
                    image_path = image_filename
                    img_tag = f'\n\n![Image {global_image_counter}]({image_path})\n\n'
                    content_text = content_text.replace('<!-- image -->', img_tag, 1)

                # Categorize based on language-specific keywords
                section_lower = current_section.lower()

                # Check which LEAP phase this belongs to using language-specific keywords
                if any(keyword.lower() in section_lower for keyword in leap_keywords['locate']):
                    leap_content['locate'].append(f"### {current_section}\n\n{content_text}")
                elif any(keyword.lower() in section_lower for keyword in leap_keywords['evaluate']):
                    leap_content['evaluate'].append(f"### {current_section}\n\n{content_text}")
                elif any(keyword.lower() in section_lower for keyword in leap_keywords['assess']):
                    leap_content['assess'].append(f"### {current_section}\n\n{content_text}")
                elif any(keyword.lower() in section_lower for keyword in leap_keywords['prepare']):
                    leap_content['prepare'].append(f"### {current_section}\n\n{content_text}")

            # Start new section
            current_section = line.replace('#', '').strip()
            current_content = []
        else:
            if line.strip():  # Skip empty lines
                current_content.append(line)
    
    # Step 4: Save output with full text
    output_file = os.path.join(output_folder, pdf_files[0].replace('.pdf', '_leap.txt'))

    # Language-specific "no content" message
    no_content_msg = "[このフェーズのコンテンツは識別されませんでした]" if detected_language == 'ja' else "[No content identified for this phase]"
    full_text_header = "完全抽出テキスト" if detected_language == 'ja' else "FULL EXTRACTED TEXT"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write(f"L - {leap_prompt_config['framework']['L']}\n")
        f.write("="*60 + "\n\n")
        if leap_content['locate']:
            f.write('\n\n'.join(leap_content['locate']) + "\n\n\n")
        else:
            f.write(f"{no_content_msg}\n\n\n")

        f.write("="*60 + "\n")
        f.write(f"E - {leap_prompt_config['framework']['E']}\n")
        f.write("="*60 + "\n\n")
        if leap_content['evaluate']:
            f.write('\n\n'.join(leap_content['evaluate']) + "\n\n\n")
        else:
            f.write(f"{no_content_msg}\n\n\n")

        f.write("="*60 + "\n")
        f.write(f"A - {leap_prompt_config['framework']['A']}\n")
        f.write("="*60 + "\n\n")
        if leap_content['assess']:
            f.write('\n\n'.join(leap_content['assess']) + "\n\n\n")
        else:
            f.write(f"{no_content_msg}\n\n\n")

        f.write("="*60 + "\n")
        f.write(f"P - {leap_prompt_config['framework']['P']}\n")
        f.write("="*60 + "\n\n")
        if leap_content['prepare']:
            f.write('\n\n'.join(leap_content['prepare']) + "\n\n\n")
        else:
            f.write(f"{no_content_msg}\n\n\n")

        f.write("="*60 + "\n")
        f.write(f"{full_text_header}\n")
        f.write("="*60 + "\n\n")
        f.write(full_text)
    
    print(f"💾 Saved text output: {output_file}")

    # Step 5: Generate Markdown output
    print("📝 Generating Markdown output...")
    md_file = generate_markdown_output(
        leap_content=leap_content,
        leap_framework=leap_prompt_config['framework'],
        full_text=full_text,
        output_file=output_file,
        images_folder=images_folder,
        pdf_name=pdf_name,
        language=detected_language
    )
    print(f"💾 Saved Markdown output: {md_file}")
    print(f"📁 Images saved to: {images_folder}")
    print("\n✅ Done! Open the .md file to view the results.")

if __name__ == "__main__":
    process_tnfd()