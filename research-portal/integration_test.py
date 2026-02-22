import sys
sys.path.insert(0, 'backend')
from app.services.ingestion import ingest_document
from app.services.financial_extractor import extract_financial_data
from app.output.excel_writer import write_to_excel

print("[INTEGRATION TEST]")
text = ingest_document('uploads/Dabur Quaterly Financial Statements.pdf')
result = extract_financial_data(text)

if result['rows']:
    print(f"Extraction successful: {len(result['rows'])} rows")
    print(f"Headers: {result['headers']}")
    
    # Try to write to Excel
    output_path = write_to_excel(result['headers'], result['rows'])
    print(f"Excel file created: {output_path}")
    
    # Check if file exists
    import os
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"File size: {size} bytes")
        print("SUCCESS: Excel file created successfully!")
    else:
        print(f"ERROR: File not found at {output_path}")
else:
    print(f"Extraction failed: {result.get('notes')}")
