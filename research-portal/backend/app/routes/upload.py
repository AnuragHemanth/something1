from fastapi import APIRouter, UploadFile
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.post("/upload")
async def upload_file(file: UploadFile):

    # create uploads folder automatically
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully",
        "file_path": file_path
    }
