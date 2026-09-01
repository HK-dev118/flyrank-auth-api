from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.supabase_client import supabase_request


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class AuthRequest(BaseModel):
    email: str
    password: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: AuthRequest):

    if not user.email or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    response = await supabase_request(
        "POST",
        "/signup",
        json={
            "email": user.email,
            "password": user.password
        }
    )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json()


@router.post("/login")
async def login(user: AuthRequest):

    if not user.email or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    response = await supabase_request(
        "POST",
        "/token?grant_type=password",
        json={
            "email": user.email,
            "password": user.password
        }
    )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )

    return response.json()