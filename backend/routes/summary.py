from fastapi import APIRouter, HTTPException
from db.supabase import SupabaseDB
from services.cognee_service import CogneeService
import openai

router = APIRouter()

@router.get("/digest/{user_id}")
async def get_daily_digest(user_id: str):
    """
    GET /summary/digest/{user_id}
    
    TODO IMPLEMENTATION STEPS:
    1. Query all timeline events / memories for the current user created within the last 24 hours.
    2. Format details (e.g. "Uploaded Resume.pdf", "Visited URL: cognee.dev", "Transcribed Audio").
    3. Pass this context to GPT / Gemini:
       Prompt: "Synthesize these memory events into a neat bulleted daily digest. Bullet highlights, action items, meeting recap."
    4. Return the text result.
    """
    try:
        # 1. Fetch activities
        # activities = SupabaseDB.fetch_timeline(user_id)
        
        # 2. Mock summary compilation
        mock_digest = """
### Today's AI Memory Digest

**Highlights & Document Ingests**
- 📄 Ingested **Resume.pdf** describing full-stack development achievements.
- 🔗 Bookmarked documentation from **cognee.dev**.
- 🔊 Processed and transcribed **Meeting Recording** discussing Backend architecture.

**Key Topics Recognized**
- Python, FastAPI, vector database embeddings, React Flow styling.

**Suggested Actions**
- Follow up on the FastAPI refactoring session discussed in your afternoon audio meeting.
        """
        
        return {
            "status": "success",
            "digest": mock_digest
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all/{user_id}")
async def get_overall_summary(user_id: str):
    """
    GET /summary/all/{user_id}
    
    TODO IMPLEMENTATION STEPS:
    1. Retrieve all stored user document titles/summaries.
    2. Compile into an executive briefing using GPT/Gemini:
       Prompt: "Summarize everything this user has uploaded. Create a personal profile dashboard summary."
    3. Return the text response.
    """
    try:
        mock_overall = """
### Personal Knowledge base Summary

You have active memories spanning **3 document uploads**, **1 audio transcript**, and **1 scraped website**.

Your primary domain knowledge covers:
1. **Resume & Career**: Software engineering experience.
2. **Frameworks**: Next.js (App Router), FastAPI, Cognee.
3. **Architecture**: Knowledge graphs, memory databases, and LLM integrations.
        """
        return {
            "status": "success",
            "summary": mock_overall
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
