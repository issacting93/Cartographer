"""
Context Engine Backend Server

Run with: uvicorn main:app --reload --port 8000
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from context_engine.api import router as context_router
from routers.chat import router as chat_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Context Engine API",
    description="Task-First Interaction Model for CUI 2026",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the context engine router
app.include_router(context_router, prefix="/api/context", tags=["Context Engine"])

# Mount the chat router for LLM-backed prototype
app.include_router(chat_router, prefix="/api", tags=["Chat"])


@app.get("/")
async def root():
    return {
        "name": "Context Engine API",
        "version": "1.0.0",
        "description": "Task-First Interaction Model for CUI 2026",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
