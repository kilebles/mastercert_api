from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "API is running"}


@router.post("/ask")
async def ask(data: dict):
    message = data.get("message", "Nothing")
    return {"message": f"you said: {message}"}