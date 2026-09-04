import os
import json
import time
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

INPUT_PATH = Path("data/processed/leads_enriched.csv")
OUTPUT_PATH = Path("data/processed/leads_final.csv")

MODEL_NAME = "gemini-3.1-flash-lite"

SAVE_EVERY = 25
MAX_RETRIES = 3
RETRY_DELAY = 5


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")


# ---------------------------------------------------------
# Gemini client
# ---------------------------------------------------------

client = genai.Client(api_key=api_key)


# ---------------------------------------------------------
# Structured response schema
# ---------------------------------------------------------

schema = {
    "type": "object",
    "properties": {
        "ai_industry": {
            "type": "string",
            "description": (
                "Likely industry of the company. "
                "Use Unknown if there is insufficient evidence."
            )
        },
        "ai_company_type": {
            "type": "string",
            "description": (
                "Likely company type such as Software, Consulting, "
                "Manufacturing, Retail, Healthcare, Finance, Education, "
                "Nonprofit, or Unknown."
            )
        },
        "ai_summary": {
            "type": "string",
            "description": (
                "A concise 1-2 sentence summary based only on "
                "the information provided."
            )
        }
    },
    "required": [
        "ai_industry",
        "ai_company_type",
        "ai_summary"
    ]
}


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

print("=" * 60)
print("AI DATA ENRICHMENT")
print("=" * 60)

df = pd.read_csv(INPUT_PATH)

total_records = len(df)

print(f"\nRecords to process: {total_records}")
print(f"Model: {MODEL_NAME}")


# ---------------------------------------------------------
# Prepare output columns
# ---------------------------------------------------------

if "AI Industry" not in df.columns:
    df["AI Industry"] = ""

if "AI Company Type" not in df.columns:
    df["AI Company Type"] = ""

if "AI Summary" not in df.columns:
    df["AI Summary"] = ""


# ---------------------------------------------------------
# Process each lead
# ---------------------------------------------------------

successful = 0
failed = 0

for index in range(total_records):

    # Skip already processed records
    if (
        str(df.at[index, "AI Industry"]).strip()
        and str(df.at[index, "AI Company Type"]).strip()
        and str(df.at[index, "AI Summary"]).strip()
    ):
        successful += 1
        continue

    company = str(df.at[index, "Company"])
    website = str(df.at[index, "Website"])
    email_domain = str(df.at[index, "Email Domain"])
    source = str(df.at[index, "Source"])
    deal_stage = str(df.at[index, "Deal Stage"])
    notes = str(df.at[index, "Notes"])

    prompt = f"""
You are performing AI-powered data enrichment for a generic
business leads dataset.

Analyze ONLY the information provided below.

Company: {company}
Website: {website}
Email Domain: {email_domain}
Source: {source}
Deal Stage: {deal_stage}
Notes: {notes}

Return:

1. The most likely industry.
2. The most likely company type.
3. A short summary.

Rules:
- Do NOT invent facts.
- Do NOT assume revenue.
- Do NOT assume employee count.
- Do NOT assume location.
- Do NOT assume products or services without evidence.
- Do NOT use the person's name to infer anything.
- If the evidence is insufficient, return "Unknown".
- Keep the summary concise.
- Return only the requested structured JSON.
"""

    result = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema
                )
            )

            result = json.loads(response.text)

            break

        except Exception as error:

            print(
                f"\nLead {index + 1}: "
                f"attempt {attempt}/{MAX_RETRIES} failed"
            )

            print(f"Error: {error}")

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)


    # -----------------------------------------------------
    # Save result
    # -----------------------------------------------------

    if result:

        df.at[index, "AI Industry"] = result.get(
            "ai_industry",
            "Unknown"
        )

        df.at[index, "AI Company Type"] = result.get(
            "ai_company_type",
            "Unknown"
        )

        df.at[index, "AI Summary"] = result.get(
            "ai_summary",
            "Unknown"
        )

        successful += 1

    else:

        df.at[index, "AI Industry"] = "Unknown"
        df.at[index, "AI Company Type"] = "Unknown"
        df.at[index, "AI Summary"] = "AI enrichment failed"

        failed += 1


    # -----------------------------------------------------
    # Progress
    # -----------------------------------------------------

    print(
        f"Processed {index + 1}/{total_records} "
        f"| Successful: {successful} "
        f"| Failed: {failed}"
    )


    # -----------------------------------------------------
    # Periodic checkpoint
    # -----------------------------------------------------

    if (index + 1) % SAVE_EVERY == 0:

        df.to_csv(
            OUTPUT_PATH,
            index=False
        )

        print(
            f"Checkpoint saved at "
            f"{index + 1} records."
        )


    # Small delay between requests
    time.sleep(1)


# ---------------------------------------------------------
# Final save
# ---------------------------------------------------------

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ---------------------------------------------------------
# Final report
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("AI ENRICHMENT RESULTS")
print("=" * 60)

print(f"\nTotal records: {total_records}")
print(f"Successfully enriched: {successful}")
print(f"Failed: {failed}")

print(f"\nOutput file:")
print(OUTPUT_PATH)

print("\nAI fields added:")

print("  ✓ AI Industry")
print("  ✓ AI Company Type")
print("  ✓ AI Summary")

print("\nAI ENRICHMENT COMPLETE")
print("=" * 60)