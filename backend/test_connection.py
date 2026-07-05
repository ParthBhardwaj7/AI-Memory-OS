import asyncio
import os
import sys
from dotenv import load_dotenv

# Load variables
load_dotenv()

async def test_supabase():
    print("Testing Supabase Connection...")
    try:
        from db.supabase import supabase
        # Run a simple select query to check connection
        response = supabase.table("documents").select("count", count="exact").limit(1).execute()
        print("✅ Supabase Connected Successfully!")
        print(f"   Current document count in DB: {response.count}\n")
        return True
    except Exception as e:
        print(f"❌ Supabase Connection Failed: {e}\n")
        return False

async def test_cognee():
    print("Testing Cognee AWS Tenant Connection...")
    try:
        import cognee
        
        api_url = os.environ.get("COGNEE_API_URL")
        api_key = os.environ.get("COGNEE_API_KEY")
        
        if not api_url or not api_key:
            print("❌ Cognee config missing in .env! (Set COGNEE_API_URL and COGNEE_API_KEY)\n")
            return False
            
        print(f"   Connecting to: {api_url}")
        
        # Connect to custom tenant
        await cognee.serve(url=api_url, api_key=api_key)
        
        # Retrieve schema inventory to verify the server responded to our authentication
        schema = await cognee.get_schema_inventory()
        print("✅ Cognee Tenant Connected Successfully!")
        print(f"   Active schemas/brains: {list(schema.keys()) if schema else 'None'}\n")
        return True
    except Exception as e:
        print(f"❌ Cognee Tenant Connection Failed: {e}\n")
        return False

async def main():
    print("=== AI Memory OS Connection Diagnostics ===\n")
    sb_ok = await test_supabase()
    cg_ok = await test_cognee()
    
    if sb_ok and cg_ok:
        print("🎉 All systems green! Your backend configuration is correct.")
    else:
        print("⚠️ Some connections failed. Please check your credentials in backend/.env")

if __name__ == "__main__":
    asyncio.run(main())
