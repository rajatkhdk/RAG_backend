from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.services.vector_store import get_embedding, qdrant_client, COLLECTION_NAME
from app.utils.llm import generate_answer, extract_json, extract_intent
from app.services.redis_memory import get_history, save_history
from app.db.session import get_db
from app.db.booking_model import Booking
import json

router = APIRouter(prefix="/conversational", tags=["Conversational"])

class ChatBookingResponse(BaseModel):
    question: Optional[str]
    answer: Optional[str]
    retrieved_chunks: Optional[list] = None
    name: Optional[str] = None
    email: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    confirmation: Optional[str] = None

@router.post("/query", response_model=ChatBookingResponse)
def chat_query(
    session_id: str,
    message: str,
    top_k: int = Query(5, ge=1, le=20, description="Number of top chunks to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Unified endpoint that handles both RAG queries and booking requests.
    """
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Load conversation history
    history = get_history(session_id)

    # --- Step 1: Check if the message is a booking request ---
    intent_prompt = f"""
You are an intent classification system.
Decide whether this message is a booking request or a general query.
Respond ONLY with 'BOOKING' or 'GENERAL'.

Message: "{message}"
"""
    intent = extract_intent(message)  # Use LLM to classify intent
    print("Intent:",intent)
    ## Normalize to string safely
    if isinstance(intent, dict):
        intent_str = intent.get("intent", "")  # default to empty string if missing
    else:
        intent_str = str(intent)

    is_booking = "BOOKING" in intent_str.upper()
    if is_booking:
        # --- Step 2: Extract booking details using your existing LLM extraction ---
        extract_prompt = f"""
You are an information extraction system.

Extract interview booking info from this message. Return only JSON with keys: name, email, date, time.
If info is missing, leave it null.

{{
  "name": string | null,
  "email": string | null,
  "date": string | null,
  "time": string | null
}}

Message: {message}
"""
        try:
            data = extract_json(extract_prompt)
            if isinstance(data, str):
                data = json.loads(data)  # ensure dict
        except Exception:
            data = {"name": None, "email": None, "date": None, "time": None}

        # --- Step 3: Store booking in SQL ---
        booking_row = Booking(
            session_id=session_id,
            name=data.get("name"),
            email=data.get("email"),
            date=data.get("date"),
            time=data.get("time")
        )
        db.add(booking_row)
        db.commit()

        confirmation = f"Booking received for {data.get('name', 'Unknown')}"

        return ChatBookingResponse(
            question=message,
            answer=confirmation,
            retrieved_chunks=[],
            name=data.get("name"),
            email=data.get("email"),
            date=data.get("date"),
            time=data.get("time"),
            confirmation=confirmation
        )
    
    else:
        # --- Step 4: Regular RAG query ---
        query_vector = get_embedding(message)

        try:
            results = qdrant_client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=top_k,
                with_payload=True
            ).points
        except Exception as e:
            return {"error": str(e)}

        top_chunks = []
        for res in results:
            payload = getattr(res, "payload", {})
            top_chunks.append({
                "chunk_id": getattr(res, "id", None),
                "score": getattr(res, "score", None),
                "text": payload.get("text", ""),
                "filename": payload.get("filename", ""),
                "chunk_index": payload.get("chunk_index", None)
            })

        # Combine context
        context = "\n\n".join([chunk["text"] for chunk in top_chunks])

        # Generate answer
        answer = generate_answer(message, context, history)

        # Update history
        history.append({"role": "user", "content": message})
        history.append({"role": "ai", "content": answer})
        save_history(session_id, history)

        return ChatBookingResponse(
            question=message,
            answer=answer,
            retrieved_chunks=top_chunks
        )