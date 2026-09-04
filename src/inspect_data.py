import pandas as pd
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "leads_raw.csv"


def inspect_dataset():
    print("=" * 60)
    print("LEADFORGE - RAW DATA INSPECTION")
    print("=" * 60)

    # Load dataset
    df = pd.read_csv(RAW_FILE)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\n" + "-" * 60)
    print("COLUMN NAMES")
    print("-" * 60)

    for column in df.columns:
        print(f"- {column}")

    print("\n" + "-" * 60)
    print("DATA TYPES")
    print("-" * 60)

    print(df.dtypes)

    print("\n" + "-" * 60)
    print("MISSING VALUES")
    print("-" * 60)

    missing = df.isnull().sum()
    print(missing)

    print("\n" + "-" * 60)
    print("DUPLICATE ROWS")
    print("-" * 60)

    print(f"Exact duplicate rows: {df.duplicated().sum()}")

    print("\n" + "-" * 60)
    print("UNIQUE VALUES")
    print("-" * 60)

    for column in df.columns:
        print(f"{column}: {df[column].nunique()} unique values")

    print("\n" + "-" * 60)
    print("CATEGORY VALUES")
    print("-" * 60)

    for column in ["Source", "Deal Stage"]:
        if column in df.columns:
            print(f"\n{column}:")
            print(df[column].value_counts(dropna=False))

    print("\n" + "-" * 60)
    print("DUPLICATE COMPANIES")
    print("-" * 60)

    company_counts = df["Company"].value_counts()
    duplicate_companies = company_counts[company_counts > 1]

    if duplicate_companies.empty:
        print("No duplicate companies found.")
    else:
        print(duplicate_companies)

    print("\n" + "-" * 60)
    print("SAMPLE RECORDS")
    print("-" * 60)

    print(df.head(5).to_string(index=False))

    print("\n" + "=" * 60)
    print("INSPECTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    inspect_dataset()