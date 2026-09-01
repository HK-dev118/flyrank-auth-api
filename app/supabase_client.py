import httpx

from app.config import settings


SUPABASE_AUTH_URL = f"{settings.supabase_url}/auth/v1"


def get_supabase_headers():
    return {
        "apikey": settings.supabase_key,
        "Content-Type": "application/json",
    }


async def supabase_request(method: str, endpoint: str, **kwargs):
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            f"{SUPABASE_AUTH_URL}{endpoint}",
            headers=get_supabase_headers(),
            **kwargs,
        )

    return response