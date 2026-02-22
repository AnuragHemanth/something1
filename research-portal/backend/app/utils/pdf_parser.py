import fitz
import pytesseract
from pdf2image import convert_from_path


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_pdf(file_path: str) -> str:

    text = ""
    
    print(f"[PDF] Opening file: {file_path}")

    try:
        doc = fitz.open(file_path)
        
        print(f"[PDF] PDF has {doc.page_count} pages")

        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            text += page_text
            if page_num == 0:
                print(f"[PDF] Page 0 text length: {len(page_text)}")

        doc.close()
        print(f"[PDF] Total extracted text: {len(text)} chars")
    except Exception as e:
        print(f"[PDF] Error during fitz extraction: {e}")
        return text

    # Only use OCR as fallback if extraction really failed
    if len(text.strip()) < 100:
        print("[PDF] Fallback: Using OCR extraction (text too short)...")
        
        try:
            images = convert_from_path(
                file_path,
                poppler_path=r"C:\poppler\poppler-25.12.0\Library\bin"
                # Removed first_page and last_page limits to get full document
            )
            
            print(f"[PDF] Converted {len(images)} pages to images")

            for page_num, img in enumerate(images):
                print(f"[PDF] OCRing page {page_num + 1}...")
                page_text = pytesseract.image_to_string(img)
                text += page_text
                print(f"[PDF] Page {page_num + 1} OCR result length: {len(page_text)}")
                
        except Exception as e:
            print(f"[PDF] Error during OCR extraction: {e}")

    return text
