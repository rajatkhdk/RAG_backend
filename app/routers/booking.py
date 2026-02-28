from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.utils.llm import extract_json
from app.services.redis_memory import get_history
import json
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.booking_model import Booking

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

@router.post("/", response_model=BookingResponse)
def book_interview(request: BookingRequest, db: Session = Depends(get_db)):
    # Use LLM to extract structured info
    history = get_history(request.session_id)
    prompt = f"""
You are an information extraction system.

Extract interview booking info from this message. Return only JSON with keys: name, email, date, time.
If info is missing, leave it null.

{{
  "name": string | null,
  "email": string | null,
  "date": string | null,
  "time": string | null
}}

Message: {request.message}
"""
    # print("message:",request.message)
    # print("prompt:",prompt)
    answer = extract_json(prompt)
    # print("answer",answer)

    try:
        data = answer
    except Exception:
        data = {"name": None, "email": None, "date": None, "time": None}

    booking_row = Booking(
        session_id=request.session_id,
        name=data.get("name"),
        email=data.get("email"),
        date=data.get("date"),
        time=data.get("time")
    )

    db.add(booking_row)
    db.commit()

    confirmation = f"Booking received for {data.get('name', 'Unknown')}"
    booking = BookingResponse(**data, confirmation=confirmation)

    return booking