from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/")
def test():
    return {"msg": "chat ready"}