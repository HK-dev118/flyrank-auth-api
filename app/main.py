from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse

from app.routers.auth import router as auth_router


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
    # Stage 2: only check that a Bearer token was provided.
    # Actual token verification will be added in Stage 3.

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

    return {
        "message": "Token received. Verification will be added in Stage 3."
    }