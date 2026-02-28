from sqlalchemy import Column, Integer, String, DateTime
from app.db.models import Base
import datetime

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    name = Column(String)
    email = Column(String)
    date = Column(String)
    time = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)