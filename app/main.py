from fastapi import FastAPI
from app.routers import ingest, chat, booking

app = FastAPI(title="RAG Backend")

@app.get("/")
def root():
    return {"message": "Backend running"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(booking.router)