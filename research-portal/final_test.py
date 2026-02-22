import sys
sys.path.insert(0, 'backend')
from app.services.ingestion import ingest_document
from app.services.financial_extractor import extract_financial_data

print("[FINAL TEST]")
text = ingest_document('uploads/Dabur Quaterly Financial Statements.pdf')
result = extract_financial_data(text)
print(f'\nExtractionResult:')
print(f'  Headers: {result["headers"][:3] if result["headers"] else "None"}')
print(f'  Total rows: {len(result["rows"])}')
if result['rows']:
    print(f'\nFirst 5 rows:')
    for i, r in enumerate(result['rows'][:5]):
        print(f'    {i+1}. {r[0][:40]}... = {r[1:3]}')
    print(f'\nCurrency: {result.get("currency")}, Unit: {result.get("unit")}')
else:
    print("  No rows extracted!")
    print(f'  Error notes: {result.get("notes")}')
