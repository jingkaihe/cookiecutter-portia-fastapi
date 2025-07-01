"""Entry point for the FastAPI application."""

import uvicorn

from app.config import get_settings
from app.main import app

if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=settings.debug,
    )
