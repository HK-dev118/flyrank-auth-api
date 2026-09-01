@'
from fastapi import FastAPI

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
'@ | Set-Content app\main.py