import os
from supabase import create_client, Client

# SUPABASE CLIENT SETUP
# TODO: Set up these environment variables in a .env file
# SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://your-project.supabase.co")
# SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "your-anon-key")
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseDB:
    """
    Helper class to manage queries to Supabase tables.
    Tables required:
    - users (id, email, name, created_at)
    - memories (id, user_id, content, cognee_id, memory_type, created_at)
    - documents (id, user_id, filename, file_path, doc_type, size, created_at)
    - chat_history (id, user_id, role, content, created_at)
    - timeline (id, user_id, title, category, description, created_at)
    """

    @staticmethod
    def log_document(user_id: str, filename: str, file_path: str, doc_type: str, size: int):
        """
        TODO: Insert a record into the 'documents' table.
        This logs when a user uploads a new PDF, image, audio, or URL.
        """
        # data = {
        #     "user_id": user_id,
        #     "filename": filename,
        #     "file_path": file_path,
        #     "doc_type": doc_type,
        #     "size": size
        # }
        # return supabase.table("documents").insert(data).execute()
        pass

    @staticmethod
    def log_memory(user_id: str, content: str, cognee_id: str, memory_type: str):
        """
        TODO: Insert a record into the 'memories' table.
        Saves a reference to the ingested Cognee memory block.
        """
        pass

    @staticmethod
    def fetch_timeline(user_id: str):
        """
        TODO: Query the 'timeline' table to list user memory events.
        Order by created_at descending.
        """
        # return supabase.table("timeline").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return []

    @staticmethod
    def add_timeline_event(user_id: str, title: str, category: str, description: str):
        """
        TODO: Insert a record into the 'timeline' table.
        Example: Title="Uploaded Resume.pdf", Category="PDF", Description="Saved resume memory"
        """
        pass

    @staticmethod
    def save_chat_message(user_id: str, role: str, content: str):
        """
        TODO: Save user question or assistant response to 'chat_history' table.
        """
        pass

    @staticmethod
    def fetch_chat_history(user_id: str, limit: int = 20):
        """
        TODO: Fetch recent chat messages for conversational memory context.
        """
        return []
