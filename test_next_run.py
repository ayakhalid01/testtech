import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def test_next_run():
    """Test next_run calculation"""
    
    # 1. Save a schedule
    schedule_data = {
        "enabled": True,
        "time": "14:30",
        "frequency": "daily",
        "max_jobs": 6,
        "sources": ["wuzzuf", "indeed"],
        "upload_to_blogger": True,
        "send_to_telegram": True,
        "send_to_whatsapp": False
    }
    
    print("🔄 Saving schedule...")
    response = requests.post(f"{API_URL}/api/schedule", json=schedule_data)
    print(f"Response status: {response.status_code}")
    result = response.json()
    print(f"Response data: {json.dumps(result, indent=2)}")
    
    if result.get("data") and result["data"].get("next_run"):
        next_run = result["data"]["next_run"]
        print(f"\n✅ Next Run: {next_run}")
        
        # Convert to readable format
        dt = datetime.fromisoformat(next_run.replace('Z', '+00:00'))
        print(f"📅 Next Run (readable): {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ No next_run in response!")
    
    # 2. Get schedule again to verify
    print("\n\n🔄 Getting schedule...")
    response = requests.get(f"{API_URL}/api/schedule")
    schedule = response.json()
    print(f"Schedule data: {json.dumps(schedule, indent=2)}")
    
    if schedule.get("next_run"):
        next_run = schedule["next_run"]
        print(f"\n✅ Next Run: {next_run}")
        
        # Convert to readable format
        dt = datetime.fromisoformat(next_run.replace('Z', '+00:00'))
        print(f"📅 Next Run (readable): {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if it's tomorrow at 14:30
        now = datetime.now()
        if dt.hour == 14 and dt.minute == 30:
            if dt.date() == now.date():
                print("✅ Next run is TODAY at 14:30")
            else:
                print("✅ Next run is TOMORROW at 14:30")
    else:
        print("❌ No next_run in schedule!")

if __name__ == "__main__":
    try:
        test_next_run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
