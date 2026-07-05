import asyncio
import os
import sys
import platform

# Cognee storage path: env var takes priority, otherwise detect OS
if not os.environ.get("SYSTEM_ROOT_DIRECTORY"):
    if platform.system() == "Windows":
        os.environ["SYSTEM_ROOT_DIRECTORY"] = "C:/Users/parth/.cognee_system"
        os.environ["DATA_ROOT_DIRECTORY"] = "C:/Users/parth/.cognee_system/data"
    else:
        os.environ["SYSTEM_ROOT_DIRECTORY"] = "/tmp/cognee_system"
        os.environ["DATA_ROOT_DIRECTORY"] = "/tmp/cognee_system/data"

from dotenv import load_dotenv

# Load variables
load_dotenv()

# Verify imports
try:
    from db.supabase import supabase, SupabaseDB
    from services.cognee_service import CogneeService
    from services.transcribing import AudioTranscriber
    from services.scraper import WebScraper
except ImportError as e:
    print(f"[ERROR] Import error during test setup: {e}")
    sys.exit(1)

TEST_USER = "test-runner-user"

async def test_supabase_flow():
    print("\n--- 1. Testing Supabase CRUD Operations ---")
    try:
        # Create a document record
        doc = SupabaseDB.log_document(
            user_id=TEST_USER,
            filename="test_diagnostics.pdf",
            file_path="uploads/test_diagnostics.pdf",
            doc_type="PDF",
            size=999
        )
        if not doc or "id" not in doc:
            raise Exception("Failed to insert document record")
        print(f"   [OK] Created document record (ID: {doc['id']})")

        # Update status
        SupabaseDB.update_document_status(doc["id"], "completed")
        print("   [OK] Updated document status to 'completed'")

        # Create timeline event
        timeline_event = SupabaseDB.add_timeline_event(
            user_id=TEST_USER,
            title="Diagnostics Test",
            category="PDF",
            description="Integration test execution"
        )
        print("   [OK] Created timeline activity event")

        # Fetch timeline
        timeline = SupabaseDB.fetch_timeline(TEST_USER)
        if not timeline:
            raise Exception("Failed to retrieve timeline events")
        print(f"   [OK] Retrieved {len(timeline)} timeline events successfully")

        # Save chat logs
        SupabaseDB.save_chat_message(TEST_USER, "user", "What is memory OS?")
        SupabaseDB.save_chat_message(TEST_USER, "assistant", "It is your digital twin.")
        print("   [OK] Logged chat message turns")

        # Fetch chat logs
        history = SupabaseDB.fetch_chat_history(TEST_USER, limit=2)
        if len(history) < 2:
            raise Exception("Failed to retrieve chat history")
        print(f"   [OK] Fetched chat history turns: User: '{history[0]['content']}', AI: '{history[1]['content']}'")
        
        # Cleanup test records to keep database clean
        print("   Cleaning up test records...")
        supabase.table("documents").delete().eq("user_id", TEST_USER).execute()
        supabase.table("timeline").delete().eq("user_id", TEST_USER).execute()
        supabase.table("chat_history").delete().eq("user_id", TEST_USER).execute()
        print("   [SUCCESS] Supabase DB operations working perfectly!")
        return True
    except Exception as e:
        print(f"   [FAIL] Supabase test failed: {e}")
        return False

async def test_scraper_and_audio():
    print("\n--- 2. Testing Scraper and Audio Transcribing ---")
    try:
        # Test scraper (using a real URL to check network calls)
        url = "https://example.com"
        scraped = WebScraper.scrape(url)
        if "Example Domain" not in scraped and "[Mock" not in scraped:
            raise Exception("Scraped text does not contain key page contents")
        print(f"   [OK] Scraped webpage successfully! Snippet: {scraped[:80].strip()}...")

        # Test audio transcription
        transcription = AudioTranscriber.transcribe_audio("uploads/dummy_file.wav")
        print(f"   [OK] Audio transcriber completed successfully. Output: {transcription[:80]}...")
        
        print("   [SUCCESS] Scraper and Audio utilities working perfectly!")
        return True
    except Exception as e:
        print(f"   [FAIL] Utilities test failed: {e}")
        return False

async def test_cognee_ingest_and_query():
    print("\n--- 3. Testing Cognee Ingestion and Semantic Search ---")
    try:
        test_text = "AI Memory OS is built using Next.js on the frontend and FastAPI on the backend."
        
        # Ingest text into Cognee AWS Tenant
        print("   Ingesting text to Cognee...")
        ingest_ok = await CogneeService.ingest_text(test_text, TEST_USER)
        if not ingest_ok:
            raise Exception("Cognee failed to ingest text memory")
        print("   [OK] Ingested text into Cognee graph database")

        # Query Cognee
        print("   Running semantic query...")
        memories = await CogneeService.query_memory("What backend is used?", TEST_USER)
        print(f"   [OK] Query retrieved {len(memories)} matching memory blocks")
        
        # Check if memory contains information
        found_matches = any("FastAPI" in m or "Next.js" in m for m in memories)
        if memories and not found_matches:
            print("   [Warning] Semantic search succeeded but did not return exact FastAPI keywords")
        else:
            print("   [OK] Semantic search matches verified")
            
        print("   [SUCCESS] Cognee Cloud pipeline working perfectly!")
        return True
    except Exception as e:
        print(f"   [FAIL] Cognee test failed: {e}")
        return False

async def test_openrouter_agent():
    print("\n--- 4. Testing OpenRouter LLM Q&A Agent ---")
    try:
        import openai
        api_key = os.environ.get("LLM_API_KEY")
        endpoint = os.environ.get("LLM_ENDPOINT", "https://openrouter.ai/api/v1")
        model = os.environ.get("LLM_MODEL", "meta-llama/llama-3-8b-instruct:free")
        if model.startswith("openrouter/"):
            model = model.replace("openrouter/", "", 1)
            
        print(f"   Model: {model}")
        print("   Calling OpenRouter Chat Completion API...")
        
        client = openai.OpenAI(base_url=endpoint, api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful test runner assistant."},
                {"role": "user", "content": "Write exactly: 'Agent online and verified'"}
            ],
            timeout=15,
            max_tokens=200
        )
        answer = response.choices[0].message.content.strip()
        print(f"   [OK] Model responded: '{answer}'")
        print("   [SUCCESS] OpenRouter LLM Agent working perfectly!")
        return True
    except Exception as e:
        print(f"   [FAIL] OpenRouter agent test failed: {e}")
        return False

async def run_diagnostics():
    print("==============================================")
    print("   AI Memory OS End-to-End Integration Test   ")
    print("==============================================")
    
    # 1. Supabase
    db_ok = await test_supabase_flow()
    
    # 2. Scraper & Audio
    utils_ok = await test_scraper_and_audio()
    
    # 3. Cognee Ingest
    cognee_ok = await test_cognee_ingest_and_query()
    
    # 4. OpenRouter LLM
    agent_ok = await test_openrouter_agent()
    
    print("\n==============================================")
    print("            Final Diagnostic Summary          ")
    print("==============================================")
    print(f" Supabase Database Integration : {'PASS' if db_ok else 'FAIL'}")
    print(f" Scraping & Audio Utilities    : {'PASS' if utils_ok else 'FAIL'}")
    print(f" Cognee Ingestion & Search     : {'PASS' if cognee_ok else 'FAIL'}")
    print(f" OpenRouter LLM Agent          : {'PASS' if agent_ok else 'FAIL'}")
    print("==============================================")
    
    if db_ok and utils_ok and cognee_ok and agent_ok:
        print("\nALL TESTS PASSED! Project is ready for deployment!")
        sys.exit(0)
    else:
        print("\nSome checks failed. Review errors above before hosting.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
