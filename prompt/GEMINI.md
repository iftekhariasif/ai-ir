Analyze this TNFD report and categorize each section into LEAP framework phases.

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
{"L": ["section content with heading...", "another section..."], "E": ["section content with heading...", "another section..."], "A": ["section content with heading...", "another section..."], "P": ["section content with heading...", "another section..."]}

Important:
- Include the section heading (as ###) at the start of each categorized content
- Keep the original markdown formatting
- If a section doesn't clearly fit any phase, put it in the most relevant one
- Some sections may span multiple phases - choose the PRIMARY focus

Document to analyze:
{full_text}

Return ONLY the JSON object, no other text.
