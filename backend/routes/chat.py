import os
import openai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.cognee_service import CogneeService
from db.supabase import SupabaseDB

router = APIRouter()

class ChatQuery(BaseModel):
    user_id: str = "default-user"
    question: str

@router.post("")
async def query_memory(query: ChatQuery):
    """
    POST /chat
    Searches Cognee memories semantically, retrieves chat history context,
    queries the OpenRouter LLM, and logs history in Supabase.
    """
    try:
        # 1. Retrieve matching memory chunks from Cognee AWS Tenant
        retrieved_memories = await CogneeService.query_memory(query.question, query.user_id)
        
        # 2. Fetch recent chat history from Supabase for conversation thread memory (e.g. last 6 messages)
        history = SupabaseDB.fetch_chat_history(query.user_id, limit=6)
        
        # 3. Format OpenAI compatible message chain
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI Memory Assistant, a digital twin of the user's mind. "
                    "You answer the user's questions based ONLY on the retrieved memories provided below. "
                    "If the answer cannot be found in the retrieved context, politely explain that you do "
                    "not recall this information. Do not invent details."
                )
            }
        ]
        
        # Add history stubs
        for msg in history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
            
        # Add current context and question
        context_str = "\n---\n".join(retrieved_memories) if retrieved_memories else "No relevant memories found."
        messages.append({
            "role": "user",
            "content": f"Retrieved Memories:\n{context_str}\n\nUser Question: {query.question}"
        })

        # 4. Request completion from OpenRouter API
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
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content.strip()

        # 5. Log current Q&A back to Supabase
        SupabaseDB.save_chat_message(query.user_id, "user", query.question)
        SupabaseDB.save_chat_message(query.user_id, "assistant", answer)

        # Build clean source listings
        sources = []
        if retrieved_memories:
            # Check for document names mentioned or display a summary pill
            # We return short snippets of matching memories as sources
            sources = [snippet[:60] + "..." if len(snippet) > 60 else snippet for snippet in retrieved_memories]
        else:
            sources = ["System Knowledge Base"]

        return {
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
