import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Load enriched dataset
input_path = "data/processed/leads_enriched.csv"
df = pd.read_csv(input_path)

# Use only ONE lead for testing
lead = df.iloc[0]

# Gemini client
client = genai.Client(api_key=api_key)

# Structured output schema
schema = {
    "type": "object",
    "properties": {
        "ai_industry": {
            "type": "string",
            "description": "Likely industry of the company. Use Unknown if there is not enough evidence."
        },
        "ai_company_type": {
            "type": "string",
            "description": "Likely type of company, such as Software, Consulting, Manufacturing, Retail, Healthcare, Finance, Education, Nonprofit, or Unknown."
        },
        "ai_summary": {
            "type": "string",
            "description": "A short 1-2 sentence summary of what can reasonably be inferred about this lead/company."
        }
    },
    "required": [
        "ai_industry",
        "ai_company_type",
        "ai_summary"
    ]
}

# Prepare lead information
prompt = f"""
You are performing data enrichment for a generic business leads dataset.

Analyze the following lead using ONLY the information provided.

Lead information:
First Name: {lead.get('First Name', '')}
Last Name: {lead.get('Last Name', '')}
Company: {lead.get('Company', '')}
Website: {lead.get('Website', '')}
Email Domain: {lead.get('Email Domain', '')}
Source: {lead.get('Source', '')}
Deal Stage: {lead.get('Deal Stage', '')}
Notes: {lead.get('Notes', '')}

Return:
1. The most likely industry.
2. The most likely company type.
3. A short summary.

IMPORTANT:
- Do not invent facts.
- Do not assume revenue, employee count, location, or other information that is not provided.
- If the available information is insufficient, use "Unknown".
- Return only the requested structured JSON.
"""

# Generate structured response
response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema
    )
)

# Parse JSON
result = json.loads(response.text)

print("\n" + "=" * 60)
print("AI ENRICHMENT TEST")
print("=" * 60)

print("\nOriginal Lead:")
print(f"Company: {lead.get('Company', '')}")
print(f"Website: {lead.get('Website', '')}")
print(f"Email Domain: {lead.get('Email Domain', '')}")

print("\nAI Enrichment:")
print(f"AI Industry: {result['ai_industry']}")
print(f"AI Company Type: {result['ai_company_type']}")
print(f"AI Summary: {result['ai_summary']}")

print("\n" + "=" * 60)
print("AI ENRICHMENT TEST COMPLETE")
print("=" * 60)