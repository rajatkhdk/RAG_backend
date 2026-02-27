from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

ALLOWED_EXTENSIONS = ["txt","pdf"]

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), strategy: str = "fixed"):
    # Validate strategy
    if strategy not in ["fixed", "sentence"]:
        raise HTTPException(status_code=400, detail="Invalid chunking strategy")
    
    # Validate file extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not supported")
    
    # Save temporarily
    save_path = f"temp_{file.filename}"
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # Extract text (we'll implement real PDF reading next)
    if ext == "txt":
        with open(save_path, "r", encoding="utf-8") as f:
            text = f.read()

    elif ext == "pdf":
        text = "PDF parsing not implemented yet"

    # Clean up
    os.remove(save_path)

    return JSONResponse({
        "filename": file.filename,
        "strategy": strategy,
        "text_preview": text[:200] # first 200 chars
    })