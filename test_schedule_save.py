import requests
import json

# Test saving schedule to the API
API_URL = "http://localhost:8000"

# Test schedule data
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

print("Testing schedule save...")
print(f"Data to save: {json.dumps(schedule_data, indent=2)}")

try:
    # Save schedule
    response = requests.post(f"{API_URL}/api/schedule", json=schedule_data)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Get schedule back
    print("\n" + "="*50)
    print("Getting schedule from database...")
    get_response = requests.get(f"{API_URL}/api/schedule")
    print(f"Response: {json.dumps(get_response.json(), indent=2)}")
    
except requests.exceptions.ConnectionError:
    print("\n❌ Error: Backend server not running!")
    print("Start the backend first: cd d:/TechFlow/backend && python -m uvicorn main:app --reload")
except Exception as e:
    print(f"\n❌ Error: {e}")
