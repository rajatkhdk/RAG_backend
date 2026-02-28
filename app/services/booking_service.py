# from sqlalchemy.orm import Session
# from app.models.booking import Booking
# from datetime import datetime


# def save_booking(db: Session, booking_data: dict):
#     date_obj = datetime.strptime(booking_data["date"], "%Y-%m-%d").date()
#     time_obj = datetime.strptime(booking_data["time"], "%H:%M").time()

#     booking = Booking(
#         name=booking_data["name"],
#         email=booking_data["email"],
#         date=date_obj,
#         time=time_obj
#     )

#     db.add(booking)
#     db.commit()
#     db.refresh(booking)

#     return booking