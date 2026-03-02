from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from sentence_transformers import SentenceTransformer
from typing import List
import uuid
from app.config import settings
from langchain_huggingface import HuggingFaceEmbeddings

# Load embedding model (once)
model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Initialize Qdrant client
qdrant_client = QdrantClient(
    host=settings.QDRANT_HOST, 
    port=settings.QDRANT_PORT
)

# Ensure collection exists
COLLECTION_NAME = "documents"

def init_collection():
    """
    Create collection only if not exists
    """
    if COLLECTION_NAME not in [c.name for c in qdrant_client.get_collections().collections]:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,   # MiniLM dimension
                distance=Distance.COSINE
            )
        )


# Embedding
def get_embedding(text: str) -> List[float]:
    """
    Generate embedding locally
    """
    return model.embed_query(text)

# Store chunks
def store_chunks_in_qdrant(chunks: List[str], filename: str, strategy: str):
    points = []

    for idx, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "filename": filename,
                    "chunk_index": idx,
                    "strategy": strategy,
                    "text": chunk
                }
            )
        )

    # print("Points",points[2])

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True
    )

    return len(points)