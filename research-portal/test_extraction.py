#!/usr/bin/env python
import sys
sys.path.insert(0, 'backend')
from app.services.ingestion import ingest_document
from app.services.financial_extractor import extract_financial_data

# Read the PDF
doc_path = 'uploads/Dabur Quaterly Financial Statements.pdf'
text = ingest_document(doc_path)
print(f'[TEST] Extracted text: {len(text)} chars, {len(text.split(chr(10)))} lines')

# Try extraction
result = extract_financial_data(text)
headers = result["headers"]
rows = result["rows"]
print(f"[TEST] Headers: {headers[:3] if headers else []}")  
print(f"[TEST] Rows extracted: {len(rows)}")
if rows:
    print(f"[TEST] First row: {rows[0]}")
    if len(rows) > 1:
        print(f"[TEST] Second row: {rows[1]}")
    currency = result.get("currency", "N/A")
    unit = result.get("unit", "N/A")
    print(f"[TEST] Currency: {currency}, Unit: {unit}")
