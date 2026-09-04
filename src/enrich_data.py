import pandas as pd
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "leads_cleaned.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "leads_enriched.csv"


def calculate_completeness(row):
    """
    Calculate completeness of important lead information.
    Score is based on 7 useful fields.
    """

    fields = [
        "First Name",
        "Last Name",
        "Company",
        "Phone",
        "Email",
        "Website",
        "Notes"
    ]

    completed = 0

    for field in fields:
        value = row.get(field)

        if pd.notna(value) and str(value).strip():
            completed += 1

    return round((completed / len(fields)) * 100, 2)


def assign_lead_quality(row):
    """
    Classify lead quality using contactability and completeness.
    """

    score = row["Data Completeness Score"]

    email_valid = row["Email 1 Valid"]
    phone_valid = row["Phone 1 Valid"]

    if score >= 85 and email_valid and phone_valid:
        return "High"

    if score >= 60 and (email_valid or phone_valid):
        return "Medium"

    return "Low"


def main():

    print("=" * 60)
    print("LEADFORGE - DATA ENRICHMENT")
    print("=" * 60)

    # Load cleaned dataset
    df = pd.read_csv(INPUT_FILE)

    print(f"\nInput records: {len(df)}")

    # ---------------------------------------------------------
    # 1. Company lead count
    # ---------------------------------------------------------

    company_counts = df["Company"].value_counts()

    df["Company Lead Count"] = (
        df["Company"]
        .map(company_counts)
    )

    # ---------------------------------------------------------
    # 2. Data completeness score
    # ---------------------------------------------------------

    df["Data Completeness Score"] = (
        df.apply(calculate_completeness, axis=1)
    )

    # ---------------------------------------------------------
    # 3. Lead quality
    # ---------------------------------------------------------

    df["Lead Quality"] = (
        df.apply(assign_lead_quality, axis=1)
    )

    # ---------------------------------------------------------
    # Save enriched dataset
    # ---------------------------------------------------------

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nEnrichment fields added:")
    print("- Company Lead Count")
    print("- Data Completeness Score")
    print("- Lead Quality")

    print("\nLead Quality distribution:")
    print(df["Lead Quality"].value_counts())

    print("\nAverage completeness:")
    print(f"{df['Data Completeness Score'].mean():.2f}%")

    print(f"\nEnriched dataset saved to:")
    print(OUTPUT_FILE)

    print("\n" + "=" * 60)
    print("DERIVED ENRICHMENT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()