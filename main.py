from docling.document_converter import DocumentConverter
import os
import requests
import json
from dotenv import load_dotenv

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
    print(f"📄 Processing: {pdf_files[0]}")
    
    # Step 1: Extract with Docling
    print("⚙️  Extracting text with Docling...")
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    full_text = result.document.export_to_markdown()
    print(f"✅ Extracted {len(full_text)} characters")
    
    # Step 2: Identify LEAP sections with Perplexity
    print("🤖 Identifying LEAP sections with Perplexity...")
    
    prompt = f"""Analyze this TNFD report and identify which sections belong to each LEAP phase.

IMPORTANT: DO NOT SUMMARIZE. Return the exact section titles/headings that belong to each phase.

LEAP Framework:
- L (Locate): Geographic locations, priority location identification, site assessment, biomes
- E (Evaluate): Dependencies and impacts analysis, materiality assessment, ENCORE usage
- A (Assess): Risk and opportunity assessment, scenario analysis, financial impact
- P (Prepare): Strategy, targets, action plans, governance, metrics, commitments

Return ONLY valid JSON with section headings (not content):
{{
  "locate": ["Section Title 1", "Section Title 2"],
  "evaluate": ["Section Title 3"],
  "assess": ["Section Title 4", "Section Title 5"],
  "prepare": ["Section Title 6"]
}}

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
    
    for line in lines:
        # Check if this is a heading
        if line.startswith('##') or line.startswith('#'):
            # Save previous section
            if current_section and current_content:
                content_text = '\n'.join(current_content)
                
                # Categorize based on keywords or AI mapping
                section_lower = current_section.lower()
                
                # Check which LEAP phase this belongs to
                if any(keyword in section_lower for keyword in ['locate', 'location', 'priority location', 'geographic', 'site', 'biome']):
                    leap_content['locate'].append(f"### {current_section}\n{content_text}")
                elif any(keyword in section_lower for keyword in ['evaluate', 'evaluation', 'dependency', 'dependencies', 'impact', 'materiality']):
                    leap_content['evaluate'].append(f"### {current_section}\n{content_text}")
                elif any(keyword in section_lower for keyword in ['assess', 'assessment', 'risk', 'opportunity', 'scenario']):
                    leap_content['assess'].append(f"### {current_section}\n{content_text}")
                elif any(keyword in section_lower for keyword in ['prepare', 'strategy', 'target', 'indicator', 'governance', 'metric']):
                    leap_content['prepare'].append(f"### {current_section}\n{content_text}")
            
            # Start new section
            current_section = line.replace('#', '').strip()
            current_content = []
        else:
            if line.strip():  # Skip empty lines
                current_content.append(line)
    
    # Step 4: Save output with full text
    output_file = os.path.join(output_folder, pdf_files[0].replace('.pdf', '_leap.txt'))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("L - LOCATE\n")
        f.write("="*60 + "\n\n")
        if leap_content['locate']:
            f.write('\n\n'.join(leap_content['locate']) + "\n\n\n")
        else:
            f.write("[No content identified for Locate phase]\n\n\n")
        
        f.write("="*60 + "\n")
        f.write("E - EVALUATE\n")
        f.write("="*60 + "\n\n")
        if leap_content['evaluate']:
            f.write('\n\n'.join(leap_content['evaluate']) + "\n\n\n")
        else:
            f.write("[No content identified for Evaluate phase]\n\n\n")
        
        f.write("="*60 + "\n")
        f.write("A - ASSESS\n")
        f.write("="*60 + "\n\n")
        if leap_content['assess']:
            f.write('\n\n'.join(leap_content['assess']) + "\n\n\n")
        else:
            f.write("[No content identified for Assess phase]\n\n\n")
        
        f.write("="*60 + "\n")
        f.write("P - PREPARE\n")
        f.write("="*60 + "\n\n")
        if leap_content['prepare']:
            f.write('\n\n'.join(leap_content['prepare']) + "\n\n\n")
        else:
            f.write("[No content identified for Prepare phase]\n\n\n")
        
        f.write("="*60 + "\n")
        f.write("FULL EXTRACTED TEXT\n")
        f.write("="*60 + "\n\n")
        f.write(full_text)
    
    print(f"💾 Saved to: {output_file}")
    print("\n✅ Done!")

if __name__ == "__main__":
    process_tnfd()