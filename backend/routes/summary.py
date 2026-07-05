import os
import openai
from fastapi import APIRouter, HTTPException
from db.supabase import SupabaseDB

router = APIRouter()

@router.get("/digest/{user_id}")
async def get_daily_digest(user_id: str):
    """
    GET /summary/digest/{user_id}
    Retrieves recent timeline activities and generates an AI Daily Digest.
    """
    try:
        # 1. Fetch recent user timeline events
        events = SupabaseDB.fetch_timeline(user_id)
        if not events:
            return {
                "status": "success",
                "digest": (
                    "### Today's AI Memory Digest\n\n"
                    "No memory activities recorded today. "
                    "Start uploading files or saving website URLs to compile your daily cognitive briefs!"
                )
            }
            
        # 2. Format activities list for LLM context
        activity_lines = []
        for ev in events[:10]: # Max last 10 events for digest scope
            title = ev.get("title", "Ingest Event")
            cat = ev.get("category", "General")
            desc = ev.get("description", "")
            activity_lines.append(f"- [{cat}] {title}: {desc}")
            
        activity_context = "\n".join(activity_lines)

        # 3. Call OpenRouter API
        api_key = os.environ.get("LLM_API_KEY")
        endpoint = os.environ.get("LLM_ENDPOINT", "https://openrouter.ai/api/v1")
        model = os.environ.get("LLM_MODEL", "meta-llama/llama-3-8b-instruct:free")
        
        if model.startswith("openrouter/"):
            model = model.replace("openrouter/", "", 1)
            
        if not api_key:
            raise ValueError("LLM_API_KEY is not set in backend/.env")
            
        client = openai.OpenAI(base_url=endpoint, api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI Memory Assistant. Synthesize the provided list of recent memory "
                        "ingestion events into a neat, professional markdown daily digest. Use sections "
                        "such as: 'Highlights & Document Ingests', 'Key Topics Covered', and 'Suggested Action Items'. "
                        "Be concise and clear."
                    )
                },
                {
                    "role": "user",
                    "content": f"Recent Memory Events:\n{activity_context}"
                }
            ],
            temperature=0.4,
            max_tokens=1000
        )
        
        digest_text = response.choices[0].message.content.strip()
        
        return {
            "status": "success",
            "digest": digest_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all/{user_id}")
async def get_overall_summary(user_id: str):
    """
    GET /summary/all/{user_id}
    Compiles a profile summary based on all ingested documents in the user's space.
    """
    try:
        # 1. Fetch document list
        from db.supabase import supabase
        res = supabase.table("documents").select("filename, doc_type").eq("user_id", user_id).eq("status", "completed").execute()
        docs = res.data or []
        
        if not docs:
            return {
                "status": "success",
                "summary": (
                    "No memories ingested yet. "
                    "Head over to the Upload tab to add files or web links to train your cognitive brain!"
                )
            }
            
        doc_lines = [f"- {d.get('doc_type')}: {d.get('filename')}" for d in docs]
        doc_context = "\n".join(doc_lines)

        # 2. Query OpenRouter
        api_key = os.environ.get("LLM_API_KEY")
        endpoint = os.environ.get("LLM_ENDPOINT", "https://openrouter.ai/api/v1")
        model = os.environ.get("LLM_MODEL", "meta-llama/llama-3-8b-instruct:free")
        
        if model.startswith("openrouter/"):
            model = model.replace("openrouter/", "", 1)
            
        if not api_key:
            raise ValueError("LLM_API_KEY is not set in backend/.env")
            
        client = openai.OpenAI(base_url=endpoint, api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI Memory Assistant. Write a professional executive briefing summarizing "
                        "the user's knowledge profile based on the list of files and URLs they have ingested into their "
                        "brain. Categorize their primary areas of knowledge and keep the summary engaging."
                    )
                },
                {
                    "role": "user",
                    "content": f"Ingested Documents:\n{doc_context}"
                }
            ],
            temperature=0.4,
            max_tokens=1000
        )
        
        summary_text = response.choices[0].message.content.strip()
        
        return {
            "status": "success",
            "summary": summary_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{user_id}")
async def get_stats(user_id: str):
    """
    GET /summary/stats/{user_id}
    Retrieves counts of files grouped by document type for the dashboard metrics.
    """
    try:
        stats = SupabaseDB.fetch_document_stats(user_id)
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
