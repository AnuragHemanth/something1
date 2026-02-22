#!/usr/bin/env python
import sys
import traceback

try:
    sys.path.insert(0, 'backend')
    from app.services.ingestion import ingest_document
    from app.services.financial_extractor_v6 import extract_financial_data
    
    print("[TEST] Imports success")
    
    # Read the PDF
    doc_path = 'uploads/Dabur Quaterly Financial Statements.pdf'
    print(f"[TEST] Starting ingestion of {doc_path}")
    text = ingest_document(doc_path)
    print(f"[TEST] Extracted text: {len(text)} chars, {len(text.split(chr(10)))} lines")
    
    # Try extraction
    print("[TEST] Starting extraction...")
    result = extract_financial_data(text)
    headers = result.get("headers", [])
    rows = result.get("rows", [])
    print(f"\n[TEST] === RESULTS ===")
    print(f"[TEST] Headers count: {len(headers)}")  
    if headers:
        print(f"[TEST] Headers: {headers[:5]}")
    print(f"[TEST] Rows extracted: {len(rows)}")
    if rows:
        print(f"[TEST] First row: {rows[0]}")
        if len(rows) > 1:
            print(f"[TEST] Second row: {rows[1]}")
        if len(rows) > 2:
            print(f"[TEST] Third row: {rows[2]}")
        currency = result.get("currency", "N/A")
        unit = result.get("unit", "N/A")
        notes = result.get("notes", "N/A")
        print(f"[TEST] Currency: {currency}, Unit: {unit}, Notes: {notes}")
        
except Exception as e:
    print(f"[ERROR] Exception occurred: {type(e).__name__}: {str(e)}")
    traceback.print_exc()
