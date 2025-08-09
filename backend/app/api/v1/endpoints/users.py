from fastapi import APIRouter

router = APIRouter()

@router.get("/users/me")
async def read_user_me():
    return {"user_id": "current_user"}

@router.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id}
