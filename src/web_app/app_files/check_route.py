from fastapi import Depends, status
from fastapi_limiter.depends import RateLimiter

from src.web_app.create_app import app


@app.get(
    path="/health",
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
    responses={200: {"status": "ok"}},
    dependencies=[Depends(RateLimiter(times=60, seconds=60))],
)
async def health():
    """
    ### Check the health of the application.

    - Returns `{"status": ok"}` if the application is running properly.
    """
    return {"status": "ok"}
