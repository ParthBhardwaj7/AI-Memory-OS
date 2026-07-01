from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, chat, timeline, graph, summary

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
