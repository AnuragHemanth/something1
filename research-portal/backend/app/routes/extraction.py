from fastapi import APIRouter, UploadFile, HTTPException
import shutil
import os
from datetime import datetime

from backend.app.services.ingestion import ingest_document
from backend.app.services.financial_extractor import extract_financial_data
from backend.app.output.excel_writer import write_to_excel


router = APIRouter(tags=["Financial Extraction"])

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"


@router.post("/extract-financials")
async def extract(file: UploadFile):

    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"File saved at: {file_path}")

        text = ingest_document(file_path)

        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="No text extracted from document"
            )

        # Extract returns a dictionary with structured data
        extraction_result = extract_financial_data(text)
        
        headers = extraction_result.get("headers", [])
        rows = extraction_result.get("rows", [])
        currency = extraction_result.get("currency")
        unit = extraction_result.get("unit")
        notes = extraction_result.get("notes")

        if not rows:
            error_detail = "No financial data detected"
            if notes:
                error_detail += f". Notes: {', '.join(notes)}"
            
            print(f"[ERROR] Extraction failed: {error_detail}")
            raise HTTPException(
                status_code=400,
                detail=error_detail
            )

        excel_path = write_to_excel(headers, rows)

        print(f"Excel generated at: {excel_path}")

        # IMPORTANT: convert to URL path
        excel_url = excel_path.replace("\\", "/")

        return {
            "message": "Extraction successful",
            "excel_file": excel_url,
            "rows_extracted": len(rows),
            "headers": headers,
            "rows": rows,
            "currency": currency,
            "unit": unit,
            "notes": notes
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Extraction Error:", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outputs-list")
async def list_outputs():
    """List all available output files for download"""
    try:
        if not os.path.exists(OUTPUT_DIR):
            return {"files": []}
        
        files = []
        for filename in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                file_date = datetime.fromtimestamp(file_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                files.append({
                    "filename": filename,
                    "url": f"/outputs/{filename}",
                    "size": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "date": file_date
                })
        
        # Sort by date (newest first)
        files.sort(key=lambda x: x["date"], reverse=True)
        
        return {"files": files}
    
    except Exception as e:
        print("Error listing outputs:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
