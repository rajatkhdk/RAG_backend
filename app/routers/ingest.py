from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
from PyPDF2 import PdfReader
from app.services.chunking import chunk_text

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
        reader = PdfReader(save_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "/n"

    # Chunk text
    chunks = chunk_text(text, strategy)

    # Clean up
    os.remove(save_path)

    return JSONResponse({
        "filename": file.filename,
        "strategy": strategy,
        "num_chunks" : len(chunks),
        "chunks_preview": chunks[:3] # first 3 chunks
    })