from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer

from app.auth_dependency import get_current_user
from app.routers.auth import router as auth_router


app = FastAPI(
    title="FlyRank Auth API",
    description="Authentication API using FastAPI and Supabase",
    version="1.0.0",
)

app.include_router(auth_router)

security = HTTPBearer()


@app.get("/")
async def root():
    return {
        "message": "Server running and ready for Supabase authentication"
    }


@app.get("/public/info")
async def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


@app.get("/protected/profile")
async def protected_profile(
    current_user=Depends(get_current_user)
):
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "created_at": current_user.get("created_at")
    }


@app.get("/protected/dashboard")
async def protected_dashboard(
    current_user=Depends(get_current_user)
):
    return {
        "message": "Welcome to your protected dashboard!",
        "user_id": current_user.get("id"),
        "email": current_user.get("email")
    }