import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from backend/.env
load_dotenv()

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase environment variables are missing! Set them in backend/.env")

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseDB:
    """
    Helper class to manage queries to Supabase tables.
    """

    @staticmethod
    def log_document(user_id: str, filename: str, file_path: str, doc_type: str, size: int):
        """
        Insert a record into the 'documents' table with status 'processing'.
        """
        data = {
            "user_id": user_id,
            "filename": filename,
            "file_path": file_path,
            "doc_type": doc_type,
            "size": size,
            "status": "processing"
        }
        res = supabase.table("documents").insert(data).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None

    @staticmethod
    def update_document_status(doc_id: str, status: str):
        """
        Update the status of a document (e.g. 'completed' or 'failed').
        """
        res = supabase.table("documents").update({"status": status}).eq("id", doc_id).execute()
        return res.data

    @staticmethod
    def log_memory(user_id: str, content: str, cognee_id: str, memory_type: str):
        """
        Insert a record into the 'memories' table.
        """
        data = {
            "user_id": user_id,
            "content": content,
            "cognee_id": cognee_id,
            "memory_type": memory_type
        }
        res = supabase.table("memories").insert(data).execute()
        return res.data

    @staticmethod
    def fetch_timeline(user_id: str):
        """
        Query the 'timeline' table to list user memory events.
        """
        res = supabase.table("timeline").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return res.data or []

    @staticmethod
    def add_timeline_event(user_id: str, title: str, category: str, description: str):
        """
        Insert a record into the 'timeline' table.
        """
        data = {
            "user_id": user_id,
            "title": title,
            "category": category,
            "description": description
        }
        res = supabase.table("timeline").insert(data).execute()
        return res.data

    @staticmethod
    def save_chat_message(user_id: str, role: str, content: str):
        """
        Save user question or assistant response to 'chat_history' table.
        """
        data = {
            "user_id": user_id,
            "role": role,
            "content": content
        }
        res = supabase.table("chat_history").insert(data).execute()
        return res.data

    @staticmethod
    def fetch_chat_history(user_id: str, limit: int = 20):
        """
        Fetch recent chat messages for conversational memory context.
        Returns messages in chronological order.
        """
        res = supabase.table("chat_history").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        messages = res.data or []
        # Reverse to get chronological order
        messages.reverse()
        return messages

    @staticmethod
    def fetch_document_stats(user_id: str):
        """
        Fetch counts of documents grouped by document type (PDF, Image, Audio, URL).
        """
        res = supabase.table("documents").select("doc_type").eq("user_id", user_id).execute()
        docs = res.data or []
        
        stats = {
            "total": len(docs),
            "pdfs": sum(1 for d in docs if d.get("doc_type") == "PDF"),
            "images": sum(1 for d in docs if d.get("doc_type") == "Image"),
            "audio": sum(1 for d in docs if d.get("doc_type") == "Audio"),
            "urls": sum(1 for d in docs if d.get("doc_type") == "URL"),
        }
        return stats

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash password using PBKDF2 HMAC-SHA256 (safe, standard, no external C deps like bcrypt needed).
        """
        import hashlib
        import os
        salt = os.urandom(16)
        pwdhash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return salt.hex() + ":" + pwdhash.hex()

    @staticmethod
    def _verify_password(stored_password: str, provided_password: str) -> bool:
        """
        Verify password hash.
        """
        import hashlib
        try:
            salt_hex, hash_hex = stored_password.split(":")
            salt = bytes.fromhex(salt_hex)
            expected_hash = bytes.fromhex(hash_hex)
            provided_hash = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt, 100000)
            return provided_hash == expected_hash
        except Exception:
            return False

    @staticmethod
    def register_user(username: str, password_raw: str):
        """
        Registers a new user inside the Supabase 'users' table.
        """
        username_clean = username.strip().lower()
        password_hash = SupabaseDB._hash_password(password_raw)
        
        # Check if user already exists
        exists = supabase.table("users").select("id").eq("username", username_clean).execute()
        if exists.data and len(exists.data) > 0:
            raise ValueError("Username already taken")
            
        data = {
            "username": username_clean,
            "password_hash": password_hash
        }
        res = supabase.table("users").insert(data).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None

    @staticmethod
    def authenticate_user(username: str, password_raw: str):
        """
        Authenticates a user against the 'users' table.
        """
        username_clean = username.strip().lower()
        res = supabase.table("users").select("*").eq("username", username_clean).execute()
        if not res.data or len(res.data) == 0:
            return None
            
        user = res.data[0]
        if SupabaseDB._verify_password(user["password_hash"], password_raw):
            return {"id": user["id"], "username": user["username"]}
        return None

    @staticmethod
    def clear_user_data(user_id: str):
        """
        Deletes all document records, timeline events, and chat logs for a user.
        Used for guest session erasure and sandbox cleanup.
        """
        supabase.table("documents").delete().eq("user_id", user_id).execute()
        supabase.table("timeline").delete().eq("user_id", user_id).execute()
        supabase.table("chat_history").delete().eq("user_id", user_id).execute()
        return True

