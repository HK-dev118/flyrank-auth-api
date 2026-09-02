from fastapi import Header, HTTPException

from app.supabase_client import supabase_request


async def get_current_user(
    authorization: str | None = Header(default=None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    token = authorization[7:]

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