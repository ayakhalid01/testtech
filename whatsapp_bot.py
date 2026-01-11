"""
WhatsApp Channel Bot - Send job messages to WhatsApp Channel
Uses WhatsApp Business Cloud API
"""
import requests
import json
import sys

# WhatsApp Configuration
WHATSAPP_API_TOKEN = "EAAMdZBpqDLncBQOD9s6ubnARroNKaUzTeKvZA53PIAvVwzSDBC17CJh4RyJUa2iFCLxxDr74NfozwiiEFciwTkIJUmWYYHMrZBNnXTnAcI1wwojxhwPTaAucLQ1fJlE6tFSlGVaNxYXJoREicJVGaOF8QzTm8Bj1ACzmLxxF193VISOBrbZAR3WUEONhDrcZCwQZDZD"
WHATSAPP_PHONE_NUMBER_ID = "915769064949083"
WHATSAPP_CHANNEL_ID = "1469839234118740"  # Your Channel ID here

def send_to_whatsapp(message):
    """Send message to WhatsApp Channel"""
    if not WHATSAPP_API_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("❌ WhatsApp API not configured!")
        print("Please set WHATSAPP_API_TOKEN and WHATSAPP_PHONE_NUMBER_ID")
        return False
    
    if not WHATSAPP_CHANNEL_ID:
        print("❌ WhatsApp Channel ID not set!")
        print("Please set WHATSAPP_CHANNEL_ID in the script")
        return False
    
    try:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": 201013414748,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Message sent successfully!")
            print(f"   Message ID: {result.get('messages', [{}])[0].get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to send message")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def send_from_file(filename):
    """Send job messages from today_jobs.txt"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by separator
        jobs = content.split('--------------------')
        
        print(f"📋 Found {len(jobs)} jobs in {filename}")
        
        for i, job in enumerate(jobs, 1):
            job = job.strip()
            if not job:
                continue
            
            print(f"\n📤 Sending job {i}...")
            success = send_to_whatsapp(job)
            
            if success:
                print(f"   ✅ Job {i} sent")
            else:
                print(f"   ❌ Job {i} failed")
            
            # Wait between messages to avoid rate limiting
            if i < len(jobs):
                import time
                time.sleep(2)
        
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def interactive_mode():
    """Interactive mode - paste message and send"""
    print("="*60)
    print("WhatsApp Channel Bot - Interactive Mode")
    print("="*60)
    print("Paste your job message below (press Enter twice to send):")
    print()
    
    lines = []
    empty_count = 0
    
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
            lines.append(line)
    
    message = "\n".join(lines).strip()
    
    if message:
        print("\n📤 Sending message...")
        send_to_whatsapp(message)
    else:
        print("❌ Empty message!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # File mode - send from file
        filename = sys.argv[1]
        send_from_file(filename)
    else:
        # Interactive mode
        interactive_mode()
