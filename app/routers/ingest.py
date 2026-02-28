from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session

from app.services.chunking import chunk_text
from app.db.session import get_db
from app.db.models import DocumentChunk
from app.services.vector_store import store_chunks_in_qdrant

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

ALLOWED_EXTENSIONS = ["txt","pdf"]

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), strategy: str = "fixed", db: Session = Depends(get_db)):
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
            page_text = page.extract_text() or ""
            text += page_text + "\n"

    # Chunk text
    chunks = chunk_text(text, strategy)

    # Clean up
    os.remove(save_path)

    # Store metadata in SQL
    for idx, chunk in enumerate(chunks):
        db_chunk = DocumentChunk(
            filename = file.filename,
            chunk_index = idx,
            chunk_text = chunk,
            strategy = strategy
        )
        db.add(db_chunk)
    db.commit()

    # Store vectors in Qdrant
    num_vectors = store_chunks_in_qdrant(chunks, file.filename, strategy)

    return JSONResponse({
        "filename": file.filename,
        "strategy": strategy,
        "num_chunks" : len(chunks),
        "num_vectors": num_vectors,
        "chunks_preview": chunks[:3] # first 3 chunks
    })