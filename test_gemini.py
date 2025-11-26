"""
Test script to verify Gemini API works
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Test with a simple prompt
# Using gemini-2.5-flash (fast and efficient)
model = genai.GenerativeModel('gemini-2.5-flash')

test_text = """
# TNFD Report Sample

## Location Analysis
Our facilities are located in Southeast Asia, specifically in Indonesia and Malaysia.
The operations span across 5 biodiversity hotspots including rainforest areas.

## Environmental Impact
We have identified dependencies on local water sources and ecosystem services.
The materiality assessment shows high impact on forest ecosystems.

## Risk Assessment
Climate-related risks include flooding and extreme weather events.
We assess financial impacts could reach $10M annually if mitigation measures are not implemented.

## Strategic Planning
Our governance framework includes quarterly biodiversity monitoring.
Target: Achieve 50% reduction in ecosystem impact by 2030.
"""

prompt = f"""
Analyze this TNFD report excerpt and categorize each section into LEAP framework phases:
- L (Locate): Geographic information, site locations, areas, facilities
- E (Evaluate): Dependencies, impacts, materiality, ecosystem services
- A (Assess): Risks, opportunities, scenarios, financial impacts
- P (Prepare): Strategy, targets, indicators, governance, action plans

Text:
{test_text}

Return a JSON with sections categorized under 'L', 'E', 'A', 'P' keys.
"""

print("🔬 Testing Gemini API...")
print("=" * 60)

try:
    response = model.generate_content(prompt)
    print("✅ Gemini API works!")
    print("\nResponse:")
    print(response.text)
    print("=" * 60)

except Exception as e:
    print(f"❌ Error: {e}")
    print("=" * 60)
