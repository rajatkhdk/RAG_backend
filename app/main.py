from fastapi import FastAPI
from app.routers import ingest, chat, booking, conversational
from app.db.session import engine
from app.db.models import Base
from app.services.vector_store import init_collection
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    init_collection()
    # Create tables automatically inside lifespan
    Base.metadata.create_all(bind=engine)
    yield

    # shutdown (optional cleanup here)

app = FastAPI(title="RAG Backend", lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Backend running"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(ingest.router)
# app.include_router(chat.router)
# app.include_router(booking.router)
app.include_router(conversational.router)
