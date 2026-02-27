from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.get("/")
def test():
    return {"msg": "ingest ready"}