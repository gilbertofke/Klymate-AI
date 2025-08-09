from fastapi import APIRouter
from .endpoints import users, auth

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include user routes (protected by authentication middleware)
api_router.include_router(users.router, prefix="/users", tags=["users"])
