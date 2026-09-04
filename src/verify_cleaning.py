import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "leads_raw.csv"
CLEAN_FILE = BASE_DIR / "data" / "processed" / "leads_cleaned.csv"


def main():

    raw = pd.read_csv(RAW_FILE)
    clean = pd.read_csv(CLEAN_FILE)

    print("=" * 60)
    print("LEADFORGE - CLEANING VERIFICATION")
    print("=" * 60)

    print("\nRECORD COUNT")
    print(f"Raw records:     {len(raw)}")
    print(f"Cleaned records: {len(clean)}")

    print("\nEXACT DUPLICATES")
    print(f"Cleaned duplicates: {clean.duplicated().sum()}")

    print("\nMISSING VALUES")
    missing = clean.isna().sum()
    print(missing[missing > 0] if missing.sum() else "No missing values")

    print("\nEMAIL VALIDATION")
    print(f"Valid Email 1:   {clean['Email 1 Valid'].sum()}")
    print(f"Invalid Email 1: {(~clean['Email 1 Valid']).sum()}")

    print("\nPHONE VALIDATION")
    print(f"Valid Phone 1:   {clean['Phone 1 Valid'].sum()}")
    print(f"Invalid Phone 1: {(~clean['Phone 1 Valid']).sum()}")

    print("\nDERIVED FIELDS")
    for column in [
        "Lead ID",
        "Email",
        "Email Domain",
        "Phone",
        "Website Domain"
    ]:
        print(f"{column}: {'OK' if column in clean.columns else 'MISSING'}")

    print("\nSAMPLE CLEANED RECORD")
    print(clean.head(1).to_string(index=False))

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()