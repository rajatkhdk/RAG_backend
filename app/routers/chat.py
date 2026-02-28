from fastapi import APIRouter, HTTPException, Query
from app.services.vector_store import get_embedding, qdrant_client, COLLECTION_NAME
from app.utils.llm import generate_answer
from app.services.redis_memory import get_history, save_history

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/query")
def query_text(
    session_id: str,
    question: str,
    top_k: int = Query(5, ge=1, le=20, description="Number of top chunks to retrieve")
):
    """
    Query the ingested documents. Returns top_k most similar chunks.
    """
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    history = get_history(session_id)

    # Step 1: Compute embedding
    query_vector = get_embedding(question)
    # print("length",len(query_vector))
    # print("Count:",qdrant_client.count(COLLECTION_NAME))

    # print(qdrant_client.get_collections())

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

    # print("Result \n:",results)

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

    # Combine context
    context = "\n\n".join([chunk["text"] for chunk in top_chunks])

    #Generate answer using Grok LLaMa
    answer = generate_answer(question, context, history)
    
    # Save updated conversation
    history.append({"role": "user", "content": question})
    history.append({"role": "ai", "content": answer})
    save_history(session_id, history)
    
    return {
        "question": question,
        "answer": answer,
        "retrieved_chunks": top_chunks
    }