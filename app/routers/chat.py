from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services.vector_store import get_embedding, qdrant_client, COLLECTION_NAME

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/query")
def query_text(
    question: str,
    top_k: int = Query(5, ge=1, le=20, description="Number of top chunks to retrieve")
):
    """
    Query the ingested documents. Returns top_k most similar chunks.
    """
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Step 1: Compute embedding
    query_vector = get_embedding(question)
    print("length",len(query_vector))
    print("Count:",qdrant_client.count(COLLECTION_NAME))

    print(qdrant_client.get_collections())

    # Step 2: Search Qdrant for top_k similar chunks
    try:
        results = qdrant_client.query_points(
            collection_name = COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            with_payload=True
        ).points
        
    except Exception as e:
        print("Quadrant query failed:",e)
        return {"error": str(e)}

    print("Result \n:",results)

    # Step 3: Prepare readable response
    top_chunks = []
    for res in results: # each result is a Scoredpoint
        # Defensive programming: make sure payload exists
        payload = getattr(res, "payload", {})
        top_chunks.append({
            "chunk_id": getattr(res, "id", None),
            "score": getattr(res, "score", None),
            "text": payload.get("text", ""),
            "filename": payload.get("filename", ""),
            "chunk_index": payload.get("chunk_index", None)
        })

    # # Step 3: Prepare readable response
    # top_chunks = []
    # for res in results:
    #     # Each res is a dict with keys: id, score, payload
    #     payload = res.get("payload", {})
    #     top_chunks.append({
    #         "chunk_id": res.get("id"),
    #         "score": res.get("score"),
    #         "text": payload.get("text", ""),
    #         "filename": payload.get("filename", ""),
    #         "chunk_index": payload.get("chunk_index")
    #     })

    return {
        "question": question,
        "top_k": top_k,
        "retrieved_chunks": top_chunks
    }