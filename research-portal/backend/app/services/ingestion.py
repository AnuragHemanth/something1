from backend.app.utils.pdf_parser import extract_text_from_pdf


def ingest_document(file_path):

    print("INGEST FUNCTION CALLED")   # ✅ debug

    text = extract_text_from_pdf(file_path)

    print("TEXT LENGTH:", len(text))  # ✅ debug
    print("TEXT SAMPLE:", text[:500])

    return text
