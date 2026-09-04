# LeadForge: Data Cleaning & AI Powered Data Enrichment

## 1. Project Overview

LeadForge is a data cleaning and enrichment pipeline developed for processing a generic business leads dataset.

The project takes a raw CSV dataset, identifies and fixes common data quality issues, validates important fields, generates useful derived information, and uses Google Gemini AI to add additional business-level enrichment.

The final cleaned dataset contains 1,000 lead records and is also stored in Google Sheets.

---

## 2. Dataset

### Source

The dataset used for this project is a generic business leads CSV dataset from the Datablist sample CSV repository.

### Original Dataset

- Records: 1,000
- Columns: 14
- Format: CSV

### Main Fields

- Index
- Account Id
- Lead Owner
- First Name
- Last Name
- Company
- Phone 1
- Phone 2
- Email 1
- Email 2
- Website
- Source
- Deal Stage
- Notes

---

## 3. Data Inspection

The raw dataset was inspected before cleaning.

The inspection checked for:

- Missing values
- Duplicate records
- Duplicate companies
- Data types
- Unique values
- Category distributions
- Email formatting
- Phone number formatting
- Website formatting
- Unnecessary or inconsistent data

The raw dataset contained 1,000 records and no exact duplicate rows.

The inspection also identified inconsistent phone number formats and differences in website URL formatting.

---

## 4. Data Cleaning

The following cleaning operations were implemented using Python and Pandas.

### Text Cleaning

- Removed leading and trailing whitespace
- Collapsed repeated spaces
- Standardized personal names
- Cleaned lead owners, notes, sources, and deal stages
- Preserved company capitalization to avoid damaging brand names and acronyms

### Email Cleaning

- Converted email addresses to lowercase
- Validated email syntax
- Selected a primary email from the available email fields
- Extracted the email domain

Example:

`person@example.com`

becomes:

`example.com`

as the email domain.

### Phone Cleaning

Phone numbers were normalized by removing unnecessary formatting characters while preserving extensions.

Examples of handled formats include:

- `999-826-8118`
- `583.518.0548`
- `(904)696-6905`
- `+1-942-704-6437x07516`

Phone validity was also checked using a basic digit-length validation rule.

### Website Cleaning

Website URLs were normalized by:

- Removing HTTP/HTTPS
- Removing `www`
- Removing trailing slashes
- Converting URLs to lowercase
- Extracting the website domain

### Duplicate Handling

Exact duplicate records were removed.

Company names were not used as a duplicate key because multiple leads can legitimately belong to the same company.

Result:

- Original records: 1,000
- Final records: 1,000
- Exact duplicates removed: 0

---

## 5. Derived Data Enrichment

Additional fields were generated from the cleaned data.

### Company Lead Count

Counts how many leads are associated with each company.

### Data Completeness Score

Calculates the percentage of important lead fields that contain usable information.

The score considers:

- First Name
- Last Name
- Company
- Phone
- Email
- Website
- Notes

### Lead Quality

Leads are categorized as:

- High
- Medium
- Low

The classification is based on data completeness and the availability of valid contact information.

---

## 6. AI-Powered Enrichment

Google Gemini was integrated using the official Google GenAI Python SDK.

The model used for AI enrichment was:

`gemini-3.1-flash-lite`

The AI enrichment generates:

- AI Industry
- AI Company Type
- AI Summary

The AI was instructed to use only the information available in the lead record and return `Unknown` when there is insufficient evidence.

This prevents unsupported assumptions about company revenue, employee count, location, products, or other business information.

### AI Enrichment Status

The AI enrichment pipeline was successfully implemented and tested.

Due to the Gemini free tier daily request quota, 483 records were successfully AI enriched during the processing run before the quota was reached.

The complete 1,000 record cleaned and derived-enriched dataset remains available as the main final dataset.

---

## 7. Project Workflow

```text
Raw Leads Dataset
       ↓
Data Inspection
       ↓
Data Cleaning & Validation
       ↓
Derived Enrichment
       ↓
AI Enrichment
       ↓
Final Dataset
       ↓
Google Sheets
