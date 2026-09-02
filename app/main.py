from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse

from app.routers.auth import router as auth_router
from app.supabase_client import supabase_request


app = FastAPI(
    title="FlyRank Auth API",
    description="Authentication API using FastAPI and Supabase",
    version="1.0.0",
)

app.include_router(auth_router)


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
    authorization: str | None = Header(default=None)
):
    # Extract Bearer token
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={
                "error": "Access token required"
            }
        )

    token = authorization[7:]

    if not token:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Access token required"
            }
        )

    # Stage 3: verify token with Supabase
    response = await supabase_request(
        "GET",
        "/user",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    if response.status_code != 200:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid or expired token"
            }
        )

    user = response.json()

    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "created_at": user.get("created_at")
    }