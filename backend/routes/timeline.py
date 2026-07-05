from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException
from db.supabase import SupabaseDB

router = APIRouter()

@router.get("/{user_id}")
async def get_timeline(user_id: str):
    """
    GET /timeline/{user_id}
    Retrieves and groups timeline events from Supabase dynamically.
    """
    try:
        events = SupabaseDB.fetch_timeline(user_id)
        
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        last_week_start = today_start - timedelta(days=7)
        
        categorized = {
            "Today": [],
            "Yesterday": [],
            "Last Week": [],
            "Older": []
        }
        
        for event in events:
            created_at_str = event.get("created_at")
            if not created_at_str:
                event["time"] = "Just now"
                categorized["Today"].append(event)
                continue
                
            try:
                # Handle standard ISO formats (Supabase typically outputs UTC strings with timezone info)
                # Parse replacing Z with +00:00 for robust python datetime loading
                dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                
                if dt >= today_start:
                    time_str = dt.astimezone().strftime("%I:%M %p")
                    event["time"] = time_str
                    categorized["Today"].append(event)
                elif dt >= yesterday_start:
                    time_str = "Yesterday, " + dt.astimezone().strftime("%I:%M %p")
                    event["time"] = time_str
                    categorized["Yesterday"].append(event)
                elif dt >= last_week_start:
                    days_ago = (today_start - dt.replace(hour=0, minute=0, second=0, microsecond=0)).days
                    time_str = f"{days_ago} days ago"
                    event["time"] = time_str
                    categorized["Last Week"].append(event)
                else:
                    time_str = dt.astimezone().strftime("%b %d, %Y")
                    event["time"] = time_str
                    categorized["Older"].append(event)
            except Exception as parse_err:
                print(f"Error parsing timestamp {created_at_str}: {parse_err}")
                event["time"] = "Recently"
                categorized["Today"].append(event)
        
        # Remove keys that don't have any items to keep the timeline interface neat
        filtered_categorized = {k: v for k, v in categorized.items() if len(v) > 0}
        
        return {
            "status": "success",
            "timeline": filtered_categorized
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
