import os
import platform

# Cognee storage path: use env var if set (Render sets /tmp/cognee_system),
# else fall back to a short local path that works on Windows and Linux
if not os.environ.get("SYSTEM_ROOT_DIRECTORY"):
    if platform.system() == "Windows":
        os.environ["SYSTEM_ROOT_DIRECTORY"] = "C:/Users/parth/.cognee_system"
        os.environ["DATA_ROOT_DIRECTORY"] = "C:/Users/parth/.cognee_system/data"
    else:
        os.environ["SYSTEM_ROOT_DIRECTORY"] = "/tmp/cognee_system"
        os.environ["DATA_ROOT_DIRECTORY"] = "/tmp/cognee_system/data"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, chat, timeline, graph, summary, auth

app = FastAPI(
    title="AI Memory OS API",
    description="Backend API for AI Memory OS Hackathon MVP",
    version="1.0.0"
)

# CORS configuration to allow local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production/staging, specify frontend domain (e.g. http://localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Include routers for different features
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(timeline.router, prefix="/timeline", tags=["Timeline"])
app.include_router(graph.router, prefix="/graph", tags=["Graph"])
app.include_router(summary.router, prefix="/summary", tags=["Summary"])

@app.get("/")
def home():
    """
    Health check endpoint.
    Verifies that the FastAPI backend is running properly.
    """
    return {"status": "running", "message": "AI Memory OS API is active"}

# Run using: uvicorn app:app --reload
