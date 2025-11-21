# TNFD PDF LEAP Analysis Project - Context File

## Project Overview
Automated system to extract and categorize TNFD (Task Force on Nature-related Financial Disclosures) reports by LEAP framework phases using Docling for PDF extraction and Perplexity API for categorization.

## Objective
- Input: TNFD PDF reports
- Output: Text file with content divided into L, E, A, P phases
- Requirement: Full text extraction (no summarization), organized by LEAP phases

## LEAP Framework Definition
- **L (Locate)**: Geographic locations, priority location identification, site assessment, biomes, ecosystem types
- **E (Evaluate)**: Dependencies and impacts analysis, materiality assessment, ENCORE usage, ecosystem services
- **A (Assess)**: Risk and opportunity assessment, scenario analysis, financial impact, nature-related risks
- **P (Prepare)**: Strategy, targets, action plans, governance, metrics, commitments, indicators

## Technology Stack
- **Docling**: PDF to text extraction (open-source, free)
- **Perplexity API**: AI-powered text analysis and categorization
- **Python 3.12**: Runtime environment
- **python-dotenv**: Environment variable management

## Current Implementation Status
✅ Working: Single PDF processing with keyword-based LEAP categorization
✅ Working: Full text extraction (not summarized)
✅ Working: Perplexity API integration with "sonar" model
⏳ Pending: Batch processing for multiple PDFs (5+)
⏳ Pending: Improved LEAP categorization accuracy

## Folder Structure
```
pdf-extract/
├── .env                    # API keys (DO NOT COMMIT)
├── main.py                 # Main processing script
├── input/                  # Place TNFD PDFs here
│   └── 01.pdf             # Example PDF
└── output/                 # Results saved here
    └── 01_leap.txt        # Categorized output
```

## Environment Variables (.env file)
```
PERPLEXITY_API_KEY=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
```

## Dependencies
```bash
pip install docling --break-system-packages
pip install python-dotenv requests --break-system-packages
```

## Current main.py Code
```python
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
                
                # Categorize based on keywords
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
            if line.strip():
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
```

## How to Run
```bash
# 1. Install dependencies
pip install docling python-dotenv requests --break-system-packages

# 2. Create .env file with API key
echo "PERPLEXITY_API_KEY=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" > .env

# 3. Place PDF in input/ folder

# 4. Run
python main.py
```

## Output Format
```
============================================================
L - LOCATE
============================================================

[Full text content from Locate-related sections]


============================================================
E - EVALUATE
============================================================

[Full text content from Evaluate-related sections]


============================================================
A - ASSESS
============================================================

[Full text content from Assess-related sections]


============================================================
P - PREPARE
============================================================

[Full text content from Prepare-related sections]


============================================================
FULL EXTRACTED TEXT
============================================================

[Complete original text from PDF]
```

## Known Issues
1. **Keyword matching is basic** - May miscategorize some sections
2. **Only processes first PDF** in input folder (single file at a time)
3. **No n8n integration yet** - Currently standalone Python script
4. **Limited to 15,000 characters** sent to Perplexity for analysis

## Next Steps / Improvements Needed
1. Improve LEAP categorization accuracy
2. Add batch processing for multiple PDFs
3. Integrate with n8n workflow
4. Add page number references
5. Handle edge cases (PDFs with images, tables, etc.)
6. Add logging and error handling
7. Create summary statistics (how many sections per phase)

## API Costs
- **Perplexity API**: ~$0.001-0.005 per request (Sonar model)
- **Docling**: Free (open-source)
- **Estimated cost for 100 PDFs**: ~$0.50-1.00

## Important Notes
- Perplexity model used: `sonar` (as of Nov 2025)
- Docling extracts text locally (no API needed)
- Current implementation uses keyword matching as fallback
- Full text is preserved (not summarized)

## Example TNFD Report Used for Testing
- Company: BIPROGY Group
- Report Date: April 2025
- File: 01.pdf
- Result: Successfully categorized into L, E, A, P phases

## Keyword Mapping for LEAP Categorization

### Locate (L) Keywords
- locate, location, priority location
- geographic, site, biome
- facility, ecosystem, area

### Evaluate (E) Keywords
- evaluate, evaluation
- dependency, dependencies
- impact, materiality
- ecosystem service, ENCORE

### Assess (A) Keywords
- assess, assessment
- risk, opportunity
- scenario, financial impact
- nature-related risk

### Prepare (P) Keywords
- prepare, strategy
- target, indicator
- governance, metric
- commitment, action plan

## Contact/Support
- Perplexity API Docs: https://docs.perplexity.ai/
- Docling GitHub: https://github.com/docling-project/docling
- Perplexity Model Names: sonar, sonar-pro, sonar-reasoning, sonar-reasoning-pro
- TNFD Framework: https://tnfd.global/

## Usage in New Conversation
To continue this project in a new chat:
1. Upload this `context.md` file
2. Say: "Continue working on the TNFD LEAP analysis project based on the context file"
3. The AI will have all necessary information to help you

## Version History
- v1.0 (Nov 2025): Initial implementation with Docling + Perplexity
- Working features: Single PDF processing, keyword-based categorization, full text extraction
