from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.supabase_client import supabase_request


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    response = await supabase_request(
        "GET",
        "/user",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return response.json()