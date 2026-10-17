import asyncio
from app.services.project_service import verify_ownership

async def main():
    res = await verify_ownership("proj-123", "user-123")
    print(f"Ownership Result: {res}")

asyncio.run(main())
