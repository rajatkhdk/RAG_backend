from fastapi import APIRouter

router = APIRouter(prefix="/booking", tags=["Booking"])

@router.get("/")
def test():
    return {"msg": "booking ready"}