from fastapi import APIRouter, HTTPException
from db.supabase import SupabaseDB

router = APIRouter()

@router.get("/{user_id}")
async def get_timeline(user_id: str):
    """
    GET /timeline/{user_id}
    
    TODO IMPLEMENTATION STEPS:
    1. Retrieve the list of timeline events from Supabase via `SupabaseDB.fetch_timeline(user_id)`.
    2. Categorize the list into periods: 'Today', 'Yesterday', 'Last Week', and 'Older'.
    3. Return the grouped structure to the client for horizontal/vertical timeline rendering.
    """
    try:
        # events = SupabaseDB.fetch_timeline(user_id)
        
        # Mock structured output
        mock_timeline = {
            "Today": [
                {"title": "Uploaded Resume.pdf", "category": "PDF", "time": "2 hours ago", "desc": "Ingested professional work experience"},
                {"title": "Visited URL: cognee.dev", "category": "URL", "time": "4 hours ago", "desc": "Saved documentation bookmark"}
            ],
            "Yesterday": [
                {"title": "Meeting Recording", "category": "Audio", "time": "1 day ago", "desc": "Transcribed meeting session audio"}
            ],
            "Last Week": [
                {"title": "Screenshot", "category": "Image", "time": "5 days ago", "desc": "Parsed dashboard image details"}
            ]
        }
        
        return {
            "status": "success",
            "timeline": mock_timeline
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
