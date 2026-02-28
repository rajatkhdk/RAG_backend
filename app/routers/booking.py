from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.utils.llm import generate_answer
from app.services.redis_memory import get_history
import json

router = APIRouter(prefix="/booking", tags=["Booking"])

class BookingRequest(BaseModel):
    session_id: str
    message: str # natural language message contatining booking info

class BookingResponse(BaseModel):
    name: Optional[str]
    email: Optional[str]
    date: Optional[str]
    time: Optional[str]
    confirmation: str

# For demonstration, store bookings in-memory
BOOKINGS: List[BookingResponse] = []

@router.post("/", response_model=BookingResponse)
def book_interview(request: BookingRequest):
    # Use LLM to extract structured info
    history = get_history(request.session_id)
    prompt = f"""
Extract interview booking info from this message. Return only JSON with keys: name, email, date, time.
If info is missing, leave it null.

Message: {request.message}
"""
    answer = generate_answer(request.message, context_chunks=prompt, chat_history=history)

    try:
        data = json.loads(answer)
    except Exception:
        data = {"name": None, "email": None, "date": None, "time": None}

    confirmation = f"Booking received for {data.get('name', 'Unknown')}"
    booking = BookingResponse(**data, confirmation=confirmation)
    BOOKINGS.append(booking)

    return booking