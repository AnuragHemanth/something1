#!/usr/bin/env python
import sys
import traceback

try:
    sys.path.insert(0, 'backend')
    from app.services.ingestion import ingest_document
    from app.services.financial_extractor_new import extract_financial_data
    
    print("[TEST] Imports success")
    
    doc_path = 'uploads/Dabur Quaterly Financial Statements.pdf'
    print(f"[TEST] Starting ingestion...")
    text = ingest_document(doc_path)
    print(f"[TEST] Extracted {len(text)} chars from PDF")
    
    print("[TEST] Starting extraction...")
    result = extract_financial_data(text)
    headers = result.get("headers", [])
    rows = result.get("rows", [])
    
    print(f"\n[TEST] === FINAL RESULTS ===")
    print(f"Headers: {headers}")
    print(f"Rows extracted: {len(rows)}")
    if rows:
        for i, row in enumerate(rows[:10]):
            print(f"  Row {i+1}: {row[0][:40]}... -> {row[1:][:3]}")
        
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {str(e)}")
    traceback.print_exc()
