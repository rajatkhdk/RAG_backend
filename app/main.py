from fastapi import FastAPI
from app.routers import ingest, chat, booking
from app.db.session import engine
from app.db.models import Base
from app.services.vector_store import init_collection

app = FastAPI(title="RAG Backend")

@app.on_event("startup")
def startup():
    init_collection()

@app.get("/")
def root():
    return {"message": "Backend running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# create tabkes automatically
Base.metadata.create_all(bind=engine)

app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(booking.router)
