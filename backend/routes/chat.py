from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.cognee_service import CogneeService
from db.supabase import SupabaseDB
import openai

router = APIRouter()

class ChatQuery(BaseModel):
    user_id: str = "default-user"
    question: str

@router.post("")
async def query_memory(query: ChatQuery):
    """
    POST /chat
    
    TODO IMPLEMENTATION STEPS:
    1. Retrieve relevant memories from Cognee using `CogneeService.query_memory(query.question, query.user_id)`.
    2. Format the retrieved context into a prompt.
    3. Generate the response using OpenAI / Gemini ChatCompletion.
       System Prompt instructions:
       "You are an AI Memory Assistant. Use only the retrieved memories. If answer is unavailable, say you don't know."
    4. Save the user question and the assistant response in Supabase `SupabaseDB.save_chat_message`.
    5. Return the assistant response and list of source/relevant document references.
    """
    try:
        # 1. Cognee Search Query
        # retrieved_memories = CogneeService.query_memory(query.question, query.user_id)
        retrieved_memories = ["Sample retrieved memory context block."]
        
        # 2. OpenAI Prompt Generation
        # client = openai.OpenAI()
        # response = client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #         {"role": "system", "content": "You are an AI Memory Assistant. Use only the retrieved memories. If answer is unavailable, say you don't know."},
        #         {"role": "user", "content": f"Context: {retrieved_memories}\nQuestion: {query.question}"}
        #     ]
        # )
        # answer = response.choices[0].message.content
        
        answer = "I searched your memories and found that you uploaded a document about project setup. However, the LLM query is in mock mode right now."
        
        # 3. Save logs in Supabase
        # SupabaseDB.save_chat_message(query.user_id, "user", query.question)
        # SupabaseDB.save_chat_message(query.user_id, "assistant", answer)
        
        return {
            "answer": answer,
            "sources": ["mock_resume.pdf"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
