import pandas as pd
import re
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

INPUT_PATH = Path("data/raw/leads_raw.csv")
OUTPUT_PATH = Path("data/processed/leads_cleaned.csv")


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def clean_text(value):
    """Remove leading/trailing spaces and collapse repeated spaces."""
    if pd.isna(value):
        return ""
    
    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)
    return value


def clean_name(value):
    """Standardize personal names without affecting company names."""
    value = clean_text(value)
    
    if not value:
        return ""
    
    return value.title()


def clean_company(value):
    """
    Clean company text while preserving the original capitalization.
    We intentionally do NOT use .title() because it can damage
    acronyms and brand names such as IBM, AT&T, eBay, etc.
    """
    return clean_text(value)


def clean_category(value):
    """Clean categorical text while keeping it readable."""
    value = clean_text(value)
    
    if not value:
        return ""
    
    return value.title()


def normalize_email(value):
    """Normalize email address to lowercase."""
    value = clean_text(value).lower()
    
    if not value:
        return ""
    
    return value


def validate_email(email):
    """Basic email syntax validation."""
    if not email:
        return False
    
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))


def extract_email_domain(email):
    """
    Extract only the domain portion from an email.
    Example:
    john@example.com -> example.com
    """
    email = normalize_email(email)
    
    if not validate_email(email):
        return ""
    
    return email.split("@", 1)[1]


def normalize_phone(value):
    """
    Normalize phone numbers to digits only while preserving extensions.

    Examples:
    999-826-8118 -> 9998268118
    +1-942-704-6437x07516 -> 19427046437 ext 07516
    """
    value = clean_text(value)
    
    if not value:
        return ""
    
    # Detect extension
    extension_match = re.search(
        r"(?:ext\.?|extension|x)\s*(\d+)$",
        value,
        flags=re.IGNORECASE
    )
    
    extension = ""
    
    if extension_match:
        extension = extension_match.group(1)
        value = value[:extension_match.start()]
    
    # Keep digits only
    digits = re.sub(r"\D", "", value)
    
    if not digits:
        return ""
    
    if extension:
        return f"{digits} ext {extension}"
    
    return digits


def validate_phone(phone):
    """Phone is valid if it contains 7-15 digits."""
    if not phone:
        return False
    
    digits = re.sub(r"\D", "", phone)
    return 7 <= len(digits) <= 15


def normalize_website(value):
    """
    Normalize website URL by removing protocol, www and trailing slash.
    """
    value = clean_text(value).lower()
    
    if not value:
        return ""
    
    value = re.sub(r"^https?://", "", value)
    value = re.sub(r"^www\.", "", value)
    value = value.rstrip("/")
    
    return value


def extract_website_domain(website):
    """Extract the domain from a normalized website."""
    website = normalize_website(website)
    
    if not website:
        return ""
    
    # Remove anything after the domain
    domain = website.split("/")[0]
    
    return domain


# ---------------------------------------------------------
# Load raw dataset
# ---------------------------------------------------------

print("=" * 60)
print("DATA CLEANING")
print("=" * 60)

df = pd.read_csv(INPUT_PATH)

raw_count = len(df)

print(f"\nRaw records: {raw_count}")
print(f"Raw columns: {len(df.columns)}")


# ---------------------------------------------------------
# Clean text fields
# ---------------------------------------------------------

text_columns = [
    "Lead Owner",
    "Notes",
    "Source",
    "Deal Stage"
]

for column in text_columns:
    if column in df.columns:
        df[column] = df[column].apply(clean_text)


# ---------------------------------------------------------
# Clean names
# ---------------------------------------------------------

for column in ["First Name", "Last Name"]:
    if column in df.columns:
        df[column] = df[column].apply(clean_name)


# ---------------------------------------------------------
# Clean company names
# ---------------------------------------------------------

if "Company" in df.columns:
    df["Company"] = df["Company"].apply(clean_company)


# ---------------------------------------------------------
# Standardize categorical fields
# ---------------------------------------------------------

for column in ["Source", "Deal Stage"]:
    if column in df.columns:
        df[column] = df[column].apply(clean_category)


# ---------------------------------------------------------
# Email cleaning
# ---------------------------------------------------------

for column in ["Email 1", "Email 2"]:
    if column in df.columns:
        df[column] = df[column].apply(normalize_email)
        df[f"{column} Valid"] = df[column].apply(validate_email)


# ---------------------------------------------------------
# Select primary email
# ---------------------------------------------------------

df["Email"] = df["Email 1"]

df.loc[
    (df["Email"] == "") & (df["Email 2"] != ""),
    "Email"
] = df["Email 2"]


# ---------------------------------------------------------
# Email domain
# ---------------------------------------------------------

df["Email Domain"] = df["Email"].apply(extract_email_domain)


# ---------------------------------------------------------
# Phone cleaning
# ---------------------------------------------------------

for column in ["Phone 1", "Phone 2"]:
    if column in df.columns:
        df[column] = df[column].apply(normalize_phone)
        df[f"{column} Valid"] = df[column].apply(validate_phone)


# ---------------------------------------------------------
# Select primary phone
# ---------------------------------------------------------

df["Phone"] = df["Phone 1"]

df.loc[
    (df["Phone"] == "") & (df["Phone 2"] != ""),
    "Phone"
] = df["Phone 2"]


# ---------------------------------------------------------
# Website cleaning
# ---------------------------------------------------------

df["Website"] = df["Website"].apply(normalize_website)

df["Website Domain"] = df["Website"].apply(extract_website_domain)


# ---------------------------------------------------------
# Remove exact duplicate records
# ---------------------------------------------------------

before_duplicates = len(df)

df = df.drop_duplicates().reset_index(drop=True)

duplicates_removed = before_duplicates - len(df)


# ---------------------------------------------------------
# Add Lead ID
# ---------------------------------------------------------

df.insert(
    0,
    "Lead ID",
    range(1, len(df) + 1)
)


# ---------------------------------------------------------
# Save cleaned dataset
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
# Cleaning report
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("CLEANING RESULTS")
print("=" * 60)

print(f"\nOriginal records: {raw_count}")
print(f"Final records: {len(df)}")
print(f"Duplicates removed: {duplicates_removed}")

print(
    f"Records retained: "
    f"{(len(df) / raw_count) * 100:.2f}%"
)

print("\nDerived fields added:")

derived_fields = [
    "Email 1 Valid",
    "Email 2 Valid",
    "Email",
    "Email Domain",
    "Phone 1 Valid",
    "Phone 2 Valid",
    "Phone",
    "Website Domain",
    "Lead ID"
]

for field in derived_fields:
    if field in df.columns:
        print(f"  ✓ {field}")

print(f"\nOutput: {OUTPUT_PATH}")

print("\nCLEANING COMPLETE")