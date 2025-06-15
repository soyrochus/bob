# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | Copyright (c) 2025 | License: MIT

import uvicorn

from .settings import settings
from .web import app

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
