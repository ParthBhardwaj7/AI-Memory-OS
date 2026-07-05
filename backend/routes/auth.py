from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from db.supabase import SupabaseDB
from services.cognee_service import CogneeService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class UserAuthSchema(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(payload: UserAuthSchema):
    """
    POST /auth/register
    Registers a new user with hashed credentials.
    """
    try:
        username = payload.username.strip()
        password = payload.password
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")
            
        if len(username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")
            
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
            
        user = SupabaseDB.register_user(username, password)
        if not user:
            raise HTTPException(status_code=500, detail="User creation failed")
            
        return {
            "status": "success",
            "message": "User registered successfully",
            "user": {
                "id": user.get("id"),
                "username": user.get("username")
            }
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        # Hint for user in case table is missing
        if "relation" in str(e) and "users" in str(e):
            raise HTTPException(
                status_code=400, 
                detail="Supabase 'users' table not found. Please create it in your Supabase SQL editor using: "
                       "CREATE TABLE users (id UUID DEFAULT gen_random_uuid() PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TIMESTAMP WITH TIME ZONE DEFAULT now());"
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(payload: UserAuthSchema):
    """
    POST /auth/login
    Authenticates a user and starts a session.
    """
    try:
        username = payload.username.strip()
        password = payload.password
        
        user = SupabaseDB.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
            
        return {
            "status": "success",
            "message": "Login successful",
            "user": user
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def run_guest_cleanup(guest_id: str):
    """
    Background worker to wipe Supabase records and Cognee indices for transient guest.
    """
    try:
        logger.info(f"Starting transient cleanup for guest: {guest_id}")
        # 1. Clear database records
        SupabaseDB.clear_user_data(guest_id)
        # 2. Clear Cognee index (runs as async inside a background task via event loop)
        import asyncio
        asyncio.run(CogneeService.delete_dataset(guest_id))
        logger.info(f"Successfully cleaned up guest: {guest_id}")
    except Exception as e:
        logger.error(f"Failed to cleanup guest: {guest_id}: {e}")

@router.post("/clear-guest/{guest_id}")
async def clear_guest(guest_id: str, background_tasks: BackgroundTasks):
    """
    POST /auth/clear-guest/{guest_id}
    Triggers asynchronous data erasure for guest users on session end.
    """
    if not guest_id.startswith("guest_"):
        raise HTTPException(status_code=400, detail="Wiping is only permitted for transient guest sessions.")
        
    background_tasks.add_task(run_guest_cleanup, guest_id)
    return {
        "status": "success",
        "message": f"Transient cleanup task scheduled for {guest_id}."
    }
