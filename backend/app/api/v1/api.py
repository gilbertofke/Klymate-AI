from fastapi import APIRouter
from .endpoints import users, auth, habits, ai_coach

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include user routes (protected by authentication middleware)
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Include habit tracking routes
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])

# Include AI coach routes
api_router.include_router(ai_coach.router, tags=["ai-coach"])
