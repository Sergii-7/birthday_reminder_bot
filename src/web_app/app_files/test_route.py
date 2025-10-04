from fastapi import Depends
from fastapi_limiter.depends import RateLimiter

from src.web_app.create_app import app


@app.get(
    path="/health",
    include_in_schema=False,
    status_code=200,
    dependencies=[Depends(RateLimiter(times=60, seconds=60))],
)
async def health():
    return {"status": "ok"}
