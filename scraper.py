import requests
from bs4 import BeautifulSoup
import json
import os
import time
import sys
import io
import random
from urllib.parse import quote

import re
import argparse
from supabase import create_client, Client
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Try to import Selenium (optional, for JavaScript-rendered content like Skills)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    # Try to import undetected_chromedriver to bypass Cloudflare
    try:
        import undetected_chromedriver as uc
        UNDETECTED_AVAILABLE = True
        print("✓ Undetected ChromeDriver available")
    except ImportError:
        UNDETECTED_AVAILABLE = False
        print("⚠️  Undetected ChromeDriver not available. Install with: pip install undetected-chromedriver")
    
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    UNDETECTED_AVAILABLE = False
    print("⚠️  Selenium not installed. Skills extraction will be limited.")
    print("   Install with: pip install selenium")

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Get the directory where this script is located (for absolute paths)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def verify_blogger_post(blog_url, max_retries=3):
    """
    Verify that the blog post is accessible and returns 200 OK.
    Retries up to max_retries times with 2-second delays.
    """
    if not blog_url:
        return False
    
    for attempt in range(max_retries):
        try:
            response = requests.get(blog_url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                print(f"   ✅ Blog post verified: {blog_url}")
                return True
            else:
                print(f"   ⚠️  Blog verification attempt {attempt + 1}/{max_retries}: Status {response.status_code}")
            time.sleep(2)
        except Exception as e:
            print(f"   ⚠️  Blog verification attempt {attempt + 1}/{max_retries} failed: {e}")
            time.sleep(2)
    
    print(f"   ❌ Blog post verification failed after {max_retries} attempts")
    return False

# Configuration - use absolute paths to ensure files are found even when run from backend/
HISTORY_FILE = os.path.join(SCRIPT_DIR, "history.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "today_jobs.txt")
BLOG_OUTPUT_FILE = os.path.join(SCRIPT_DIR, "blog_posts.html")
PHOTOS_DIR = os.path.join(SCRIPT_DIR, "Photos By Keywords")  # Directory for keyword images
WHATSAPP_CHANNEL_LINK = "https://tinyurl.com/3nyujz59"
TELEGRAM_CHANNEL_LINK = "https://tinyurl.com/4p4wjvww"
BLOG_DOMAIN = "https://careerjobst01.blogspot.com"
# BLOGGER API
BLOGGER_BLOG_ID = "6949685611084082756"
# Use the full access scope that includes write permissions
BLOGGER_SCOPES = ['https://www.googleapis.com/auth/blogger']
BLOGGER_CLIENT_SECRETS = os.path.join(SCRIPT_DIR, "client_secrets.json")
BLOGGER_TOKEN_FILE = os.path.join(SCRIPT_DIR, "blogger_token.pickle")
POSTS_DIR = os.path.join(SCRIPT_DIR, "posts")

# TinyURL API Configuration
TINYURL_API_KEY = "nRFavNgCA9lwoqmk0BxuxBe1TXGTb4s97jR2os6Aq8TfxWAGXNoVlr1qLe2D"

# WhatsApp Cloud API Configuration
# Get these from: https://developers.facebook.com/apps/
WHATSAPP_API_TOKEN = "EAAMdZBpqDLncBQOD9s6ubnARroNKaUzTeKvZA53PIAvVwzSDBC17CJh4RyJUa2iFCLxxDr74NfozwiiEFciwTkIJUmWYYHMrZBNnXTnAcI1wwojxhwPTaAucLQ1fJlE6tFSlGVaNxYXJoREicJVGaOF8QzTm8Bj1ACzmLxxF193VISOBrbZAR3WUEONhDrcZCwQZDZD"  # Your WhatsApp Cloud API token
WHATSAPP_PHONE_NUMBER_ID = "915769064949083"  # Your WhatsApp Business Phone Number ID
WHATSAPP_CHANNEL_ID = "1469839234118740"  # Your WhatsApp Channel ID (if using channels)

# Telegram Bot Configuration
# Get these from @BotFather on Telegram
TELEGRAM_BOT_TOKEN = "7972154095:AAEGGqNAI005XLZ98VkjnubP-rj64AOJxwM"  # Your Telegram Bot Token (from @BotFather)
TELEGRAM_CHANNEL_ID = "@techflow_channel"  # Your Telegram Channel ID (e.g., @your_channel or -100123456789)

# Supabase Configuration
SUPABASE_URL = "https://zxoostjcukaritjzxmwh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4b29zdGpjdWthcml0anp4bXdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODk4ODgsImV4cCI6MjA4MzU2NTg4OH0.0HCqxeHnvDjQGXQ7MFxdj2409uS76s7VpI5w4gTrBO4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_job_exists_in_db(job_link):
    """Check if job already exists in Supabase database"""
    try:
        response = supabase.table("jobs").select("id").eq("link", job_link).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"   ⚠️  Error checking job in database: {e}")
        return False

def send_to_telegram_channel(message):
    """Send message to Telegram Channel using Bot API"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("   ⚠️  Telegram Bot not configured. Skipping...")
        return False
    
    try:
        print(f"   📤 Sending to Telegram Channel: {TELEGRAM_CHANNEL_ID}")
        
        # Telegram Bot API endpoint
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown",  # Support for bold, italic formatting
            "disable_web_page_preview": False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Sent to Telegram Channel successfully")
            return True
        else:
            print(f"   ❌ Telegram API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Telegram send error: {e}")
        import traceback
        traceback.print_exc()
        return False

def send_to_whatsapp_channel(message):
    """Send message to WhatsApp Channel using Cloud API"""
    if not WHATSAPP_API_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("   ⚠️  WhatsApp API not configured. Skipping...")
        return False
    
    try:
        # WhatsApp Cloud API endpoint
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # For Channel posting, use different format
        # For now, using standard message format
        payload = {
            "messaging_product": "whatsapp",
            "to": 201013414748,  # Channel ID
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Sent to WhatsApp Channel")
            return True
        else:
            print(f"   ❌ WhatsApp API error: {response.status_code} - {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"   ❌ WhatsApp send error: {e}")
        return False

def create_tinyurl(long_url):
    """Create a TinyURL using official API with authentication"""
    try:
        # Skip TinyURL for Indeed links (domain is banned)
        if 'indeed.com' in long_url:
            print(f"   ℹ️  Using direct Indeed link (TinyURL blocks Indeed domain)")
            return long_url
        
        # Use TinyURL API v2 with authentication
        api_url = "https://api.tinyurl.com/create"
        headers = {
            "Authorization": f"Bearer {TINYURL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": long_url,
            "domain": "tinyurl.com"
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                short_url = data.get('data', {}).get('tiny_url')
                if short_url and short_url.startswith('http'):
                    return short_url
            except Exception as json_err:
                print(f"   ⚠️  TinyURL JSON parse error: {json_err}")
                print(f"   Response text: {response.text[:200]}")
        else:
            print(f"   ⚠️  TinyURL API error: {response.status_code} - {response.text[:100]}")
        
        # If API fails, return original URL
        return long_url
    except Exception as e:
        print(f"   ⚠️  URL shortener error: {e}, using original URL")
        return long_url

TARGET_JOBS_COUNT = 6
SEARCH_KEYWORDS = [
    "Flutter", "Backend", "Frontend", "Data Analyst", 
    "Data Engineer", "Data Scientist", "UI/UX", "Tester", "QA", 
    "Solution Architect", "Cyber Security", "DevOps", "Full Stack",
    "Mobile Developer", "Cloud Engineer", "IT", "Software Engineer",
    "Python", "Java", "JavaScript", ".NET", "PHP", "React", "Angular",
    "Node.js", "Machine Learning", "AI", "Product Manager", "Scrum Master",
    "Business Analyst", "System Administrator", "Network Engineer",
    "Database Administrator", "Automation", "Digital Marketing"
]

# Keywords variations for better matching
KEYWORD_VARIATIONS = {
    "tester": ["tester", "test", "qa", "quality assurance", "testing", "quality control", "sqa", "test engineer"],
    "data analyst": ["data analyst", "data analysis", "analyst", "business analyst", "financial analyst", "system analyst"],
    "data engineer": ["data engineer", "data engineering", "etl developer", "big data engineer"],
    "data scientist": ["data scientist", "data science", "ml engineer", "ai scientist"],
    "ui/ux": ["ui/ux", "ux/ui", "ui", "ux", "user experience", "user interface", "ui designer", "ux designer", "product designer"],
    "backend": ["backend", "back-end", "back end", "server", "php", "senior backend", "junior backend", "backend engineer", "server side"],
    "frontend": ["frontend", "front-end", "front end", "frontend engineer", "frontend developer", "ui developer"],
    "flutter": ["flutter", "flutter developer", "dart developer", "mobile flutter"],
    "solution architect": ["solution architect", "software architect", "system architect", "enterprise architect", "technical architect"],
    "cyber security": ["cyber security", "cybersecurity", "information security", "security engineer", "infosec", "security analyst"],
    "devops": ["devops", "dev ops", "devops engineer", "sre", "site reliability", "deployment engineer"],
    "full stack": ["full stack", "full-stack", "fullstack", "full stack developer", "full stack engineer"],
    "mobile developer": ["mobile developer", "mobile development", "ios developer", "android developer", "mobile engineer", "app developer"],
    "cloud engineer": ["cloud engineer", "cloud engineering", "cloud developer", "aws engineer", "azure engineer", "gcp engineer"],
    "it": ["it", "information technology", "it specialist", "it support", "technical support"],
    "software engineer": ["software engineer", "software developer", "programmer", "developer", "software engineering"],
    "python": ["python", "python developer", "python engineer", "django", "flask", "fastapi"],
    "java": ["java", "java developer", "java engineer", "spring", "spring boot"],
    "javascript": ["javascript", "js", "javascript developer", "node", "typescript"],
    ".net": [".net", "dotnet", "c#", "csharp", "asp.net", ".net developer"],
    "php": ["php", "php developer", "laravel", "symfony", "wordpress"],
    "react": ["react", "reactjs", "react.js", "react developer", "react native"],
    "angular": ["angular", "angularjs", "angular developer"],
    "node.js": ["node.js", "nodejs", "node", "node developer", "express"],
    "machine learning": ["machine learning", "ml", "deep learning", "neural networks", "ml engineer"],
    "ai": ["ai", "artificial intelligence", "ai engineer", "ai developer"],
    "product manager": ["product manager", "pm", "product owner", "product management"],
    "scrum master": ["scrum master", "agile coach", "scrum", "agile"],
    "business analyst": ["business analyst", "ba", "business analysis", "requirements analyst"],
    "system administrator": ["system administrator", "sysadmin", "sys admin", "system admin", "it admin"],
    "network engineer": ["network engineer", "network administrator", "network specialist", "ccna", "ccnp"],
    "database administrator": ["database administrator", "dba", "database admin", "sql admin"],
    "automation": ["automation", "automation engineer", "test automation", "qa automation", "selenium"],
    "digital marketing": ["digital marketing", "marketing specialist", "social media marketing", "content marketing"]
}

def job_title_matches_keywords(title):
    """
    Check if job title contains any of the search keywords or their variations.
    Returns True if title contains at least one keyword.
    """
    title_lower = title.lower()
    
    # Check each keyword and its variations
    for keyword in SEARCH_KEYWORDS:
        keyword_lower = keyword.lower()
        
        # Get variations for this keyword
        variations = KEYWORD_VARIATIONS.get(keyword_lower, [keyword_lower])
        
        # Check if any variation is in the title
        for variation in variations:
            if variation in title_lower:
                return True
    
    return False

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return set()
                return set(json.loads(content))
        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Could not parse {HISTORY_FILE}: {e}")
            print(f"   Creating new history file...")
            return set()
        except Exception as e:
            print(f"⚠️  Warning: Error loading history: {e}")
            return set()
    return set()

def save_history(history_set):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(history_set), f, indent=4)

def create_slug(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug

def get_keyword_image(keyword):
    """
    Find image for keyword from Photos By Keywords folder.
    Returns HTML image block or empty string if no image found.
    
    Looks for images with pattern: keyword.png, keyword.jpg, keyword.jpeg, etc.
    """
    if not keyword:
        return ""
    
    # Create photos directory if it doesn't exist
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)
        print(f"📁 Created photos directory: {PHOTOS_DIR}")
        return ""
    
    # Normalize keyword for searching (lowercase, flexible matching)
    keyword_lower = keyword.lower().strip()
    # Also create version without special chars for better matching
    keyword_clean = keyword_lower.replace("/", "").replace("_", "").replace(" ", "")
    
    # Common image extensions
    extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    
    # Try multiple filename variations:
    # 1. Exact keyword (e.g., "Cyber Security" → "Cyber Security.png")
    # 2. Lowercase (e.g., "IT" → "it.png")  
    # 3. With underscores (e.g., "Cyber Security" → "cyber_security.png")
    # 4. Without special chars (e.g., "UI/UX" → "uiux.png")
    
    # Search all files in directory (case-insensitive)
    matching_file = None
    partial_match = None
    best_match_score = 0
    
    for filename in os.listdir(PHOTOS_DIR):
        name_without_ext, ext = os.path.splitext(filename)
        
        # Skip if not an image file
        if ext.lower() not in extensions:
            continue
        
        # Normalize filename for flexible comparison
        name_lower = name_without_ext.lower()
        name_clean = name_lower.replace("/", "").replace("_", "").replace(" ", "")
        
        # Try multiple comparison strategies
        # 1. Exact match (case-insensitive)
        if name_lower == keyword_lower:
            matching_file = filename
            print(f"   ✅ Exact match: '{filename}' for keyword '{keyword}'")
            break
        
        # 2. Match without special characters (e.g., "ui/ux" matches "uiux.png")
        if name_clean == keyword_clean and len(keyword_clean) >= 2:
            matching_file = filename
            print(f"   ✅ Clean match: '{filename}' for keyword '{keyword}'")
            break
        
        # Compare allowing spaces and underscores to be interchangeable
        name_spaced = name_lower.replace("_", " ")
        keyword_spaced = keyword_lower.replace("_", " ")
        
        # 3. Exact match with space normalization
        if name_spaced == keyword_spaced:
            matching_file = filename
            print(f"   ✅ Space-normalized match: '{filename}' for keyword '{keyword}'")
            break
        
        # Calculate match score for partial matching
        match_score = 0
        
        # Special handling for short keywords (2-3 chars like "IT", "QA", "UI")
        if len(keyword_spaced) <= 3:
            if name_lower == keyword_spaced:
                match_score = 100  # Perfect short match
            elif keyword_spaced in name_lower.split():
                match_score = 90  # Word match
            elif keyword_spaced in name_lower:
                match_score = 50  # Contains match
        else:
            # Check if keyword contains filename or filename contains keyword
            if keyword_spaced in name_lower:
                match_score = len(name_lower) * 2  # Prefer longer matches
            elif name_lower in keyword_spaced:
                match_score = len(name_lower) * 3  # Strong match
            
            # Check individual words (e.g., "Data Scientist" matches "data.png" or "scientist.png")
            keyword_words = keyword_spaced.split()
            name_words = name_lower.split()
            
            for kw in keyword_words:
                for nw in name_words:
                    if kw == nw and len(kw) >= 2:  # Reduced from 3 to 2
                        match_score += len(kw) * 4  # Word match is strong
                    elif kw.startswith(nw) or nw.startswith(kw):
                        if len(kw) >= 2 and len(nw) >= 2:  # Reduced from 3 to 2
                            match_score += min(len(kw), len(nw)) * 2
            
            # Check stem matching (e.g., "tester"/"testing", "developer"/"development")
            keyword_stem = keyword_spaced.rstrip('er').rstrip('ing').rstrip('ment').rstrip('s')
            name_stem = name_lower.rstrip('er').rstrip('ing').rstrip('ment').rstrip('s')
            if len(keyword_stem) >= 2 and keyword_stem == name_stem:  # Reduced from 3 to 2
                match_score += len(keyword_stem) * 3
        
        # Update best match if this score is higher
        if match_score > best_match_score:
            best_match_score = match_score
            partial_match = filename
    
    # Use exact match if found, otherwise use best partial match
    if matching_file:
        image_path = os.path.join(PHOTOS_DIR, matching_file)
    elif partial_match and best_match_score >= 2:  # Reduced from 3 to 2 for short keywords
        matching_file = partial_match
        image_path = os.path.join(PHOTOS_DIR, matching_file)
        print(f"   🔍 Using match '{matching_file}' (score: {best_match_score}) for keyword '{keyword}'")
    else:
        return ""
    
    if os.path.exists(image_path):
            # Read image and convert to base64 for Blogger
            try:
                # Try to resize image if PIL is available (optional optimization)
                try:
                    from PIL import Image
                    import io
                    
                    # Open and resize image to max width 800px (for faster loading)
                    img = Image.open(image_path)
                    
                    # Calculate new dimensions (max width 800px, maintain aspect ratio)
                    max_width = 800
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Convert to RGB if necessary (for JPEG compatibility)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    # Save to bytes
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='JPEG', quality=85, optimize=True)
                    img_data = img_bytes.getvalue()
                    mime_type = "image/jpeg"
                    
                except ImportError:
                    # PIL not available, use original image
                    with open(image_path, 'rb') as img_file:
                        img_data = img_file.read()
                        mime_type = f"image/{ext[1:]}" if ext[1:] != 'jpg' else "image/jpeg"
                
                # Convert to base64
                import base64
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                
                # Create data URL
                data_url = f"data:{mime_type};base64,{img_base64}"
                
                # Return HTML with image matching the new template structure
                image_html = f'''<div class="job-header-image">
    <img src="{data_url}" alt="{keyword} jobs" loading="lazy" />
  </div>'''
                
                print(f"   🖼️  Found image for keyword '{keyword}': {matching_file}")
                return image_html
                    
            except Exception as e:
                print(f"   ⚠️  Error reading image {matching_file}: {e}")
                return ""
    
    # No image found for this keyword
    print(f"   📷 No image found for keyword '{keyword}' in {PHOTOS_DIR}")
    return ""

def generate_blog_post_html(job):
    try:
        from string import Template
        from datetime import datetime
        
        template_path = os.path.join(SCRIPT_DIR, "templates", "job_post.html")
        with open(template_path, "r", encoding="utf-8") as f:
            template_str = f.read()
        
        template = Template(template_str)
        
        # Get keyword-based image
        keyword = job.get('keyword', '').lower().strip()
        print(f"   🖼️  Looking for image with keyword: '{keyword}'")
        header_image = get_keyword_image(keyword)
        if header_image:
            print(f"   ✅ Image found for keyword '{keyword}'")
            job['has_image'] = True
        else:
            print(f"   ⚠️  No image found for keyword '{keyword}'")
            job['has_image'] = False
        
        # Job description
        description = job.get('description', 'Check job link for details')
        if len(description) > 500:
            description = description[:500] + '...'
        job_description = f"<strong>{job.get('company', 'Company')}</strong> is hiring for this position. {description}"
        
        # Technical Requirements section
        requirements = job.get('requirements', [])
        technical_requirements = ""
        if requirements:
            # Split requirements into first half for technical requirements
            mid = len(requirements) // 2
            tech_reqs = requirements[:mid] if mid > 0 else requirements
            # Clean all bullets from text (CSS will add them)
            cleaned_reqs = []
            for r in tech_reqs:
                r_clean = r.strip()
                if r_clean.startswith('🔹 '):
                    r_clean = r_clean[2:]
                elif r_clean.startswith('🔹'):
                    r_clean = r_clean[1:]
                elif r_clean.startswith('- '):
                    r_clean = r_clean[2:]
                elif r_clean.startswith('• '):
                    r_clean = r_clean[2:]
                cleaned_reqs.append(r_clean.strip())
            tech_items = "\n    ".join([f"<li>{r}</li>" for r in cleaned_reqs])
            technical_requirements = f'''<h3>Technical Requirements</h3>
  <ul>
    {tech_items}
  </ul>'''
        
        # Qualifications section
        qualifications = ""
        if requirements:
            # Use second half or all requirements for qualifications
            mid = len(requirements) // 2
            qual_reqs = requirements[mid:] if mid > 0 and len(requirements) > 3 else requirements
            # Clean all bullets from text (CSS will add them)
            cleaned_quals = []
            for r in qual_reqs:
                r_clean = r.strip()
                if r_clean.startswith('🔹 '):
                    r_clean = r_clean[2:]
                elif r_clean.startswith('🔹'):
                    r_clean = r_clean[1:]
                elif r_clean.startswith('- '):
                    r_clean = r_clean[2:]
                elif r_clean.startswith('• '):
                    r_clean = r_clean[2:]
                cleaned_quals.append(r_clean.strip())
            qual_items = "\n    ".join([f"<li>{r}</li>" for r in cleaned_quals])
            qualifications = f'''<h3>Qualifications</h3>
  <ul>
    {qual_items}
  </ul>'''
        
        # Job Details section
        job_details = f'''<h3>Job Details</h3>
  <ul>
    <li>Position: {job['title']}</li>
    <li>Location: {job['location']}</li>
    <li>Company: {job.get('company', 'Not specified')}</li>
  </ul>'''
        
        # Contact information
        contact_instructions = "Interested candidates are invited to apply through the link below:"
        contact_email = "See job link for contact details"
        contact_whatsapp_text = "Or contact via:"
        contact_whatsapp = "See job link"
        application_note = "Please check the job link for full details and application instructions."
        apply_button_text = "Apply Now"

        html_content = template.substitute(
            header_image=header_image,
            job_title=job['title'],
            job_description=job_description,
            technical_requirements=technical_requirements,
            qualifications=qualifications,
            job_details=job_details,
            contact_instructions=contact_instructions,
            contact_email=contact_email,
            contact_whatsapp_text=contact_whatsapp_text,
            contact_whatsapp=contact_whatsapp,
            application_note=application_note,
            apply_link=job['link'],
            apply_button_text=apply_button_text
        )
        return html_content
    except Exception as e:
        print(f"Error generating blog HTML: {e}")
        import traceback
        traceback.print_exc()
        return ""

def authenticate_blogger():
    """Authenticate with Blogger API"""
    creds = None
    if os.path.exists(BLOGGER_TOKEN_FILE):
        with open(BLOGGER_TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                BLOGGER_CLIENT_SECRETS, BLOGGER_SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(BLOGGER_TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('blogger', 'v3', credentials=creds)

def post_to_blogger(service, title, content):
    """Post to Blogger and return URL"""
    try:
        if not content:
            print(f"⚠️  No content for: {title}")
            return None
        
        print(f"   📝 Posting to Blogger: {title}")
            
        # Use full HTML content (Blogger will handle it properly)
        clean_content = content.strip()
        
        if not clean_content or clean_content.strip() == "":
            print(f"⚠️  Empty content for: {title}")
            return None
        
        post = {
            'kind': 'blogger#post',
            'blog': {'id': BLOGGER_BLOG_ID},
            'title': title,
            'content': clean_content,
            'labels': ['Jobs']
        }
        
        # Insert as PUBLISHED (not draft)
        result = service.posts().insert(blogId=BLOGGER_BLOG_ID, body=post, isDraft=False).execute()
        post_url = result.get('url')
        print(f"✅ Posted to Blogger: {post_url}")
        return post_url
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error posting to Blogger: {e}")
        if "403" in error_str or "permission" in error_str.lower():
            print("   → Account needs Admin/Owner role in Blogger Settings → Permissions")
        import traceback
        traceback.print_exc()
        return None

def get_skills_with_selenium(job_url):
    """
    Extract skills using Selenium (for JavaScript-rendered content).
    This is more reliable for Skills extraction as Wuzzuf loads them with JS.
    """
    if not SELENIUM_AVAILABLE:
        return []
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(job_url)
        
        # Wait for skills section to load (max 10 seconds)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Skills And Tools')]"))
            )
        except:
            pass  # Timeout is okay, continue anyway
        
        # Give extra time for JS to populate skills
        time.sleep(2)
        
        # Get page source after JavaScript execution
        html = driver.page_source
        driver.quit()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        skills = []
        
        # Find Skills And Tools section
        for heading in soup.find_all(['h4', 'h2', 'h3']):
            if 'Skills And Tools' in heading.get_text() or 'مهارات' in heading.get_text():
                # Get the container after the heading
                container = heading.find_next_sibling()
                if container:
                    # Find all skill elements (anchors and spans)
                    for elem in container.find_all(['a', 'span']):
                        text = elem.get_text(strip=True)
                        # Filter valid skills
                        if (text and 
                            2 <= len(text) <= 40 and 
                            len(text.split()) <= 6 and
                            text.lower() not in ['view', 'see more', 'see less', 'skills and tools'] and
                            text not in skills):
                            skills.append(text)
                            
                            if len(skills) >= 10:
                                break
                    
                    if skills:
                        break
        
        return skills[:10]
        
    except Exception as e:
        print(f"   ⚠️  Selenium error: {e}")
        return []

def get_job_details(job_url, use_selenium_for_skills=False):
    """
    Extract job details from Wuzzuf job page.
    
    RELIABILITY APPROACH:
    This function is designed to be resilient to HTML structure changes.
    Instead of relying on CSS class names (which Wuzzuf frequently changes),
    we use:
    1. Text-based searches (headings like "Job Description", "Requirements", "Skills")
    2. HTML structure patterns (h2 → ul → li hierarchy)
    3. Multiple fallback methods for each field
    4. Content validation (length checks, filtering unwanted text)
    
    This ensures the scraper continues working even if Wuzzuf updates their CSS.
    """
    try:
        response = requests.get(job_url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # ============ SALARY EXTRACTION (Reliable) ============
        salary = "Confidential"
        # Method 1: Find any span/div with salary indicators and currency symbols
        salary_indicators = ["EGP", "SAR", "AED", "USD", "KWD", "QAR", "OMR", "BHD", "JOD"]
        currency_symbols = ["E£", "£", "$", "﷼"]
        
        for elem in soup.find_all(['span', 'div', 'p']):
            text = elem.get_text(strip=True)
            # Check for currency symbols or indicators
            has_currency = any(indicator in text for indicator in salary_indicators) or \
                          any(symbol in text for symbol in currency_symbols)
            
            if has_currency:
                # Verify it's actually a salary (contains numbers and reasonable length)
                if any(char.isdigit() for char in text) and 5 <= len(text) <= 100:
                    # Exclude if it contains date-related words
                    if not any(word in text.lower() for word in ['ago', 'day', 'week', 'month', 'year', 'posted']):
                        salary = text
                        break
        
        # Method 2: If still Confidential, look for "Confidential" or "سري" text explicitly
        if salary == "Confidential":
            for elem in soup.find_all(['span', 'div', 'p']):
                text = elem.get_text(strip=True).lower()
                if text in ["confidential", "سري", "غير محدد"]:
                    salary = "Confidential"
                    break
        
        # ============ JOB DESCRIPTION EXTRACTION (Class-Independent) ============
        description = ""
        desc_items = []
        
        # Method 1: Find by heading text "Job Description" anywhere
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
            heading_text = heading.get_text(strip=True)
            if "Job Description" in heading_text or "وصف الوظيفة" in heading_text:
                # Found heading, now find the nearest ul with li items
                container = heading.find_parent()
                
                # Try to find ul in parent or siblings
                ul = None
                # Check siblings first
                next_sibling = heading.find_next_sibling()
                search_depth = 0
                while next_sibling and not ul and search_depth < 5:
                    if next_sibling.name == "ul":
                        ul = next_sibling
                        break
                    if next_sibling.name in ["div", "section"]:
                        ul = next_sibling.find("ul")
                        if ul:
                            break
                    next_sibling = next_sibling.find_next_sibling()
                    search_depth += 1
                
                # If not found in siblings, check parent container
                if not ul and container:
                    ul = container.find("ul")
                
                if ul:
                    for li in ul.find_all("li", recursive=False):  # Only direct children
                        text = li.get_text(strip=True)
                        # Verify it's meaningful content (not links to other jobs)
                        if (text and 
                            len(text) > 10 and 
                            not text.startswith('•') and  # Already has bullet
                            "/jobs/" not in str(li) and  # Not a job link
                            "ago" not in text.lower()):  # Not a date
                            desc_items.append(text)
                    if desc_items:
                        break
        
        # Method 2: If still empty, search more broadly but with stricter filtering
        if not desc_items:
            all_headings = soup.find_all(string=lambda x: x and ("Job Description" in str(x) or "وصف الوظيفة" in str(x)))
            for heading_text in all_headings:
                parent = heading_text.find_parent()
                if parent:
                    # Search for ul within reasonable distance
                    for element in parent.find_all_next(limit=15):
                        if element.name == "ul":
                            for li in element.find_all("li", recursive=False):
                                text = li.get_text(strip=True)
                                # Strict filtering to avoid garbage
                                if (text and 
                                    len(text) > 15 and 
                                    "/jobs/" not in str(li) and
                                    not any(word in text.lower() for word in ['ago', 'month', 'day', 'year']) and
                                    not text.startswith('•')):
                                    desc_items.append(text)
                            if desc_items:
                                break
                    if desc_items:
                        break
        
        if desc_items:
            description = "\n".join(desc_items)
        
        # ============ REQUIREMENTS EXTRACTION (Class-Independent) ============
        requirements = []
        req_items = []
        
        # Method 1: Find by heading text "Job Requirements" or "Requirements"
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
            heading_text = heading.get_text(strip=True)
            if "Job Requirements" in heading_text or "Requirements" in heading_text or "متطلبات" in heading_text:
                # Find the nearest ul
                ul = None
                next_sibling = heading.find_next_sibling()
                while next_sibling and not ul:
                    if next_sibling.name == "ul":
                        ul = next_sibling
                        break
                    if next_sibling.name in ["div", "section"]:
                        ul = next_sibling.find("ul")
                        if ul:
                            break
                    next_sibling = next_sibling.find_next_sibling()
                
                if ul:
                    for li in ul.find_all("li", recursive=True):
                        text = li.get_text(strip=True)
                        if text and len(text) > 5:
                            req_items.append(text)
                    if req_items:
                        break
        
        # Method 2: Broader search if nothing found
        if not req_items:
            all_headings = soup.find_all(string=lambda x: x and ("Requirements" in str(x) or "متطلبات" in str(x)))
            for heading_text in all_headings:
                parent = heading_text.find_parent()
                if parent:
                    for element in parent.find_all_next(limit=20):
                        if element.name == "ul":
                            for li in element.find_all("li"):
                                text = li.get_text(strip=True)
                                if text and len(text) > 5:
                                    req_items.append(text)
                            if req_items:
                                break
                    if req_items:
                        break
        
        # If no requirements found, use description items as requirements
        if not req_items and desc_items:
            print(f"   ℹ️  No Requirements section - using Job Description as requirements")
            req_items = desc_items[:5]
        
        # Format requirements - remove any existing bullets (CSS will add them)
        requirements = []
        for req in req_items[:5]:
            req_text = req.strip()
            # Remove existing bullets if any
            if req_text.startswith('🔹 '):
                req_text = req_text[2:].strip()
            elif req_text.startswith('🔹'):
                req_text = req_text[1:].strip()
            elif req_text.startswith('- '):
                req_text = req_text[2:].strip()
            elif req_text.startswith('• '):
                req_text = req_text[2:].strip()
            requirements.append(req_text)

        # ============ COMPANY LOGO EXTRACTION (Reliable) ============
        company_logo = ""
        # Method 1: Find img with "logo" in alt text
        for img in soup.find_all("img"):
            alt_text = img.get("alt", "").lower()
            src = img.get("src", "")
            if "logo" in alt_text and src:
                company_logo = src
                break
        
        # Method 2: Find img near company name heading
        if not company_logo:
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                if "company" in heading.get_text().lower() or "شركة" in heading.get_text():
                    parent = heading.find_parent()
                    if parent:
                        img = parent.find("img")
                        if img and img.get("src"):
                            company_logo = img.get("src")
                            break
        
        # Method 3: Find any img in header/top section
        if not company_logo:
            for section in soup.find_all(['header', 'section', 'div'], limit=10):
                img = section.find("img")
                if img and img.get("src"):
                    src = img.get("src", "")
                    # Skip icons and small images
                    if "icon" not in src.lower() and "avatar" not in src.lower():
                        company_logo = src
                        break
        
        # Normalize logo URL
        if company_logo:
            if company_logo.startswith("//"):
                company_logo = "https:" + company_logo
            elif company_logo.startswith("/"):
                company_logo = "https://wuzzuf.net" + company_logo

        # ============ SKILLS EXTRACTION (Class-Independent) ============
        skills = []
        
        # If Selenium is requested and available, use it for more reliable skills extraction
        if use_selenium_for_skills and SELENIUM_AVAILABLE:
            print(f"   🔧 Using Selenium for skills extraction...")
            skills = get_skills_with_selenium(job_url)
            if skills:
                print(f"   ✅ Found {len(skills)} skills with Selenium")
        
        # Fallback to regular HTML parsing if Selenium not used or failed
        if not skills:
            # Method 1: Find by heading text containing "Skills"
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
                heading_text = heading.get_text(strip=True)
                if "skill" in heading_text.lower() or "مهارات" in heading_text:
                    # Found skills heading, search for skill elements
                    container = heading.find_parent()
                    
                    # Look for links or spans that could be skill badges
                    skill_elements = []
                    
                    # Check siblings first
                    next_sibling = heading.find_next_sibling()
                    search_count = 0
                    while next_sibling and search_count < 5:
                        if next_sibling.name in ["div", "section", "ul"]:
                            # Find all potential skill elements
                            skill_elements = next_sibling.find_all(['a', 'span', 'li'])
                            if skill_elements:
                                break
                        next_sibling = next_sibling.find_next_sibling()
                        search_count += 1
                    
                    # Extract text from skill elements
                    for elem in skill_elements:
                        text = elem.get_text(strip=True)
                        # Filter: reasonable length, not too long, not navigation text
                        if (text and 
                            2 <= len(text) <= 40 and 
                            len(text.split()) <= 6 and
                            text.lower() not in ['view', 'view all', 'more', 'less', 'see more'] and
                            text not in skills):
                            skills.append(text)
                        
                        # Limit to 10 skills
                        if len(skills) >= 10:
                            break
                    
                    if skills:
                        break
            
            # Method 2: Search for links with /skill/ in href
            if not skills:
                skill_links = soup.find_all('a', href=lambda x: x and '/skill' in str(x))
                for link in skill_links:
                    text = link.get_text(strip=True)
                    if text and 2 <= len(text) <= 40 and text not in skills:
                        skills.append(text)
                    if len(skills) >= 10:
                        break
        
        # Method 3: Broader search by heading text
        if not skills:
            all_headings = soup.find_all(string=lambda x: x and ("skill" in str(x).lower() or "مهارات" in str(x)))
            for heading_text in all_headings:
                parent = heading_text.find_parent()
                if parent:
                    # Find all potential skill badges within parent
                    for elem in parent.find_all(['a', 'span'], limit=30):
                        text = elem.get_text(strip=True)
                        if (text and 
                            2 <= len(text) <= 40 and 
                            len(text.split()) <= 6 and
                            text.lower() not in ['view', 'view all', 'skills', 'skills and tools'] and
                            text not in skills):
                            skills.append(text)
                            if len(skills) >= 10:
                                break
                    if skills:
                        break

        return {
            "salary": salary,
            "requirements": requirements[:5],
            "skills": skills[:10],
            "company_logo": company_logo,
            "description": description
        }
    except Exception as e:
        print(f"Error fetching details for {job_url}: {e}")
        return None

def format_message(job, apply_link, use_tinyurl=True):
    parts = []
    parts.append(f"*{job['title']}*")
    parts.append("")
    parts.append(f"📍 *Location:* {job['location']}")
    # parts.append(f"💰 *Salary:* {job['salary']}")
    parts.append("")
    # if job.get('description'):
    #     parts.append("*Job Description:*")
    #     # Split description by newlines and add each as a separate line
    #     desc_lines = job['description'].split('\n')
    #     for line in desc_lines:
    #         if line.strip():
    #             parts.append(f"• {line.strip()}")
    #     parts.append("")
    if job.get('requirements'):
        # Use the actual section type (Requirements, Skills, or Responsibilities)
        section_label = job.get('section_type', 'Requirements')
        parts.append(f"*{section_label}:*")
        
        # Define bullet style options with different weights
        # More variety: emoji bullets, dashes, checkmarks, arrows
        bullet_styles = [
            '🔹',  # Diamond
            '-',   # Dash
            '✓',   # Checkmark
            '•',   # Bullet
            '▪',   # Square
        ]
        
        # Randomly choose bullet style for this job
        bullet = random.choice(bullet_styles)
        
        # Apply the chosen bullet to all requirements
        for req in job.get('requirements', []):
            req_text = req.strip()
            # Remove existing bullets if any
            if req_text.startswith('🔹'):
                req_text = req_text[1:].strip()
            elif req_text.startswith('-'):
                req_text = req_text[1:].strip()
            # Add consistent bullet
            parts.append(f"{bullet} {req_text}")
        
        parts.append("")
    # if job.get('skills'):
    #     skills_text = ", ".join(job.get('skills', []))
    #     parts.append(f"*Skills:* {skills_text}")
    #     parts.append("")

    # Apply TinyURL only if use_tinyurl is True
    if use_tinyurl:
        final_link = create_tinyurl(apply_link)
    else:
        final_link = apply_link
    
    parts.append(f"🔗 *Apply Here:* {final_link}")
    parts.append("")
    parts.append(f"⚡ WhatsApp Channel: {WHATSAPP_CHANNEL_LINK}")
    parts.append(f"💬 Telegram Channel: {TELEGRAM_CHANNEL_LINK}")

    return "\n".join(parts)

def get_search_url(keyword):
    encoded_keyword = quote(keyword)
    # Removed career_level filter to get ALL jobs (Entry, Mid, Senior)
    return f"https://wuzzuf.net/search/jobs/?q={encoded_keyword}&a=hpb&filters%5Bpost_date%5D%5B0%5D=within_24_hours"

def get_indeed_job_details(job_url, driver=None):
    """
    Extract requirements and description from Indeed job detail page.
    
    Extraction strategy:
    1. Extract the full job description div
    2. Look for common requirement section patterns
    3. Parse requirements from lists or structured text
    
    Args:
        job_url: URL of the Indeed job detail page
        driver: Selenium WebDriver instance (optional, will create new if not provided)
    
    Returns:
        Dictionary with 'requirements' (list), 'description' (string)
    """
    driver_created = False
    requirements = []
    description = ""
    found_requirements = False
    found_description = False
    section_type_used = "Requirements"  # Default value, will be updated based on actual section found
    
    try:
        # Use provided driver or create new one
        if driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(options=chrome_options)
            driver_created = True
        
        # Load the job details page
        driver.get(job_url)
        time.sleep(5)  # Increased wait time for JS to load
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Save HTML for debugging
        with open('debug_indeed_latest.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"   DEBUG: Saved HTML to debug_indeed_latest.html")
        
        # ============ FIND MAIN JOB DESCRIPTION CONTAINER ============
        # Try multiple ways to find the job description
        job_desc_div = None
        
        # Method 1: id='jobDescriptionText'
        job_desc_div = soup.find('div', id='jobDescriptionText')
        if job_desc_div:
            print(f"   DEBUG: Found job desc via id='jobDescriptionText'")
        
        # Method 2: class contains 'jobDescriptionText'
        if not job_desc_div:
            job_desc_div = soup.find('div', class_=lambda x: x and 'jobDescriptionText' in x if x else False)
            if job_desc_div:
                print(f"   DEBUG: Found job desc via class containing 'jobDescriptionText'")
        
        # Method 3: Look for any div with <b>Requirements</b>
        if not job_desc_div:
            all_divs = soup.find_all('div')
            for div in all_divs:
                if div.find('b', text=lambda t: t and 'requirement' in t.lower() if t else False):
                    job_desc_div = div
                    print(f"   DEBUG: Found job desc via div containing <b>Requirements</b>")
                    break
        
        if job_desc_div:
            # Extract all text for description
            full_text = job_desc_div.get_text(separator='\n', strip=True)
            description = full_text[:500] if full_text else ""  # First 500 chars
            
            # ============ STRATEGY 1: Find <b> tags with "Requirements" text ============
            all_b_tags = job_desc_div.find_all('b')
            print(f"   DEBUG: Found {len(all_b_tags)} <b> tags in job description")
            
            for b_tag in all_b_tags:
                b_text = b_tag.get_text(strip=True).lower()
                print(f"   DEBUG: <b> tag text: '{b_text}'")
                
                # Check if this <b> tag contains requirement-related keywords
                # Priority order: Requirements/Qualifications > Skills > Responsibilities
                section_priority = 0
                section_name = b_tag.get_text(strip=True)
                
                # Highest priority: Requirements, Qualifications
                if any(keyword in b_text for keyword in ['requirement', 'qualification', 'متطلبات', 'مؤهلات']):
                    if 'responsibilit' not in b_text and 'مسؤوليات' not in b_text:
                        section_priority = 3
                        print(f"   ✓ Found HIGH PRIORITY section: '{section_name}'")
                
                # Medium priority: Skills, Experience
                elif any(keyword in b_text for keyword in ['skill', 'experience', 'مهارات', 'خبرة']):
                    section_priority = 2
                    print(f"   ✓ Found MEDIUM PRIORITY section: '{section_name}'")
                
                # Low priority: Responsibilities, Duties
                elif any(keyword in b_text for keyword in ['responsibilit', 'duties', 'مسؤوليات', 'واجبات']):
                    section_priority = 1
                    print(f"   ✓ Found LOW PRIORITY section: '{section_name}'")
                
                if section_priority > 0:
                    temp_requirements = []
                    
                    # Get the next sibling element after this <b> tag
                    # The <b> might be inside a <p>, so we need to check parent's next sibling too
                    current = b_tag
                    
                    # First, try to find <ul> in the same level or parent's next sibling
                    search_elements = [b_tag]
                    if b_tag.parent and b_tag.parent.name == 'p':
                        search_elements.append(b_tag.parent)
                    
                    for elem in search_elements:
                        next_elem = elem.find_next_sibling()
                        attempts = 0
                        while next_elem and attempts < 5:
                            print(f"   DEBUG: Checking next sibling: <{next_elem.name}>")
                            if next_elem.name == 'ul':
                                print(f"   ✓ Found <ul> with {len(next_elem.find_all('li'))} items")
                                for li in next_elem.find_all('li', recursive=False):
                                    li_text = li.get_text(strip=True)
                                    if li_text and len(li_text) > 3:
                                        temp_requirements.append(li_text)
                                        print(f"   ✓ Added item: {li_text[:60]}...")
                                break
                            elif next_elem.name in ['p', 'div'] and next_elem.find('b'):
                                # Stop if we hit another section header
                                print(f"   DEBUG: Hit another section, stopping")
                                break
                            next_elem = next_elem.find_next_sibling()
                            attempts += 1
                        
                        # If found items, stop searching
                        if temp_requirements:
                            break
                    
                    # If found items with higher priority than current, replace
                    # Or if same/lower priority but we have nothing yet, use it
                    if temp_requirements:
                        if section_priority == 3:  # Requirements/Qualifications - always use these
                            requirements = temp_requirements
                            section_type_used = "Requirements"
                            print(f"   ✅ Using HIGH PRIORITY section with {len(requirements)} items")
                            break  # Stop searching, we found the best section
                        elif section_priority == 2 and (not requirements or len(requirements) == 0):
                            requirements = temp_requirements
                            section_type_used = "Skills"
                            print(f"   ✅ Using MEDIUM PRIORITY section with {len(requirements)} items")
                        elif section_priority == 1 and (not requirements or len(requirements) == 0):
                            requirements = temp_requirements
                            section_type_used = "Responsibilities"
                            print(f"   ✅ Using LOW PRIORITY section (fallback) with {len(requirements)} items")
            
            # ============ STRATEGY 2: Skip if no <b> tags found ============
            # If no <b> tags at all, don't try to extract from random <ul> lists
            if not requirements and len(all_b_tags) == 0:
                print(f"   ⚠️  No <b> tags found - skipping this job")
                return {
                    "requirements": [],
                    "description": description,
                    "section_type": section_type_used
                }
            elif not requirements and len(all_b_tags) > 0:
                print(f"   DEBUG: Strategy 1 failed, trying to find all <ul> lists")
                all_lists = job_desc_div.find_all('ul')
                print(f"   DEBUG: Found {len(all_lists)} <ul> lists total")
                for ul in all_lists:
                    for li in ul.find_all('li', recursive=False):
                        li_text = li.get_text(strip=True)
                        if li_text and len(li_text) > 5:  # Skip very short items
                            # Always add 🔹 prefix
                            requirements.append(f"🔹 {li_text}")
                    # Limit to first 10 items total
                    if len(requirements) >= 10:
                        break
                # If we found requirements using this fallback, mark as generic
                if requirements:
                    section_type_used = "Requirements"  # Generic fallback
        
        # If still no requirements found, use old method
        if not requirements:
            print(f"   DEBUG: Both strategies failed, trying fallback method")
            # ============ SCAN ALL SECTIONS WITH <b> HEADERS (FALLBACK) ============
            # Find all <b> tags that might be section headers
            all_b_tags = soup.find_all('b')
        
        for b_tag in all_b_tags:
            b_text = b_tag.get_text(strip=True).lower()
            b_text_full = b_tag.get_text(strip=True)
            
            # ============ CHECK FOR DESCRIPTION SECTION ============
            if not found_description and any(keyword in b_text for keyword in ["description", "وصف"]):
                desc_lines = []
                
                # Get all siblings after this <b> tag until next <b> or <p>
                current = b_tag.next_sibling
                while current:
                    # Stop if we hit another <b> tag or <p> tag
                    if hasattr(current, 'name'):
                        if current.name in ['b', 'p']:
                            break
                        
                        # Extract text from <ul> and <li> elements
                        if current.name == 'ul':
                            for li in current.find_all('li', recursive=False):
                                li_text = li.get_text(strip=True)
                                if li_text:
                                    desc_lines.append(li_text)
                        elif current.name == 'li':
                            li_text = current.get_text(strip=True)
                            if li_text:
                                desc_lines.append(li_text)
                        elif current.name not in ['script', 'style']:
                            text = current.get_text(strip=True)
                            if text and len(text) > 5:  # Avoid very short fragments
                                desc_lines.append(text)
                    
                    current = current.next_sibling
                
                if desc_lines:
                    description = "\n".join(desc_lines)
                    found_description = True
            
            # ============ CHECK FOR REQUIREMENT-TYPE SECTIONS ============
            # Matches: Requirements, Qualifications, Language Requirement, Skills, etc.
            requirement_keywords = [
                "requirement", "متطلبات", "qualification", "مؤهلات", 
                "language", "skill", "مهارات", "experience", "خبرة"
            ]
            
            if not found_requirements and any(keyword in b_text for keyword in requirement_keywords):
                req_items = []
                
                # Get all siblings after this <b> tag until next <b> or <p>
                current = b_tag.next_sibling
                while current:
                    # Stop if we hit another <b> tag or <p> tag
                    if hasattr(current, 'name'):
                        if current.name in ['b', 'p']:
                            break
                        
                        # Extract list items
                        if current.name == 'ul':
                            for li in current.find_all('li', recursive=False):
                                li_text = li.get_text(strip=True)
                                if li_text and li_text not in req_items:
                                    req_items.append(f"🔹 {li_text}")
                        elif current.name == 'li':
                            li_text = current.get_text(strip=True)
                            if li_text and li_text not in req_items:
                                req_items.append(f"🔹 {li_text}")
                    
                    current = current.next_sibling
                
                if req_items:
                    requirements.extend(req_items)
                    found_requirements = True
        
        # ============ FALLBACK: Search <p> tags for sections ============
        # If requirements still not found, search in <p> tags
        if not found_requirements:
            for p_tag in soup.find_all('p'):
                p_text = p_tag.get_text(strip=True).lower()
                
                # Check if <p> contains requirement keywords
                requirement_keywords = [
                    "requirement", "متطلبات", "qualification", "مؤهلات", 
                    "language", "skill", "مهارات"
                ]
                
                has_requirements = any(keyword in p_text for keyword in requirement_keywords)
                
                if has_requirements:
                    # Get all <ul> and <li> elements under this section
                    current = p_tag.next_sibling
                    req_items = []
                    
                    while current:
                        # Stop if we hit another <p> tag
                        if isinstance(current, type(p_tag)) and current.name == 'p':
                            break
                        
                        # Extract list items
                        if hasattr(current, 'name'):
                            if current.name == 'ul':
                                for li in current.find_all('li', recursive=False):
                                    li_text = li.get_text(strip=True)
                                    if li_text and li_text not in req_items:
                                        req_items.append(f"🔹 {li_text}")
                            elif current.name == 'li':
                                li_text = current.get_text(strip=True)
                                if li_text and li_text not in req_items:
                                    req_items.append(f"🔹 {li_text}")
                        
                        current = current.next_sibling
                    
                    if req_items:
                        requirements.extend(req_items)
                        found_requirements = True
                        break
        
        # Randomly take 5 or 6 requirements (keep original order, just limit count)
        if len(requirements) > 6:
            num_to_select = random.choice([5, 6])
            requirements = requirements[:num_to_select]
        elif len(requirements) == 6:
            # If exactly 6, randomly decide to keep all or take 5
            if random.choice([True, False]):
                requirements = requirements[:5]
        # If less than 6, keep all
        
        return {
            "requirements": requirements,
            "description": description,
            "section_type": section_type_used
        }
        
    except Exception as e:
        print(f"   ⚠️  Error extracting Indeed job details: {e}")
        return {"requirements": [], "description": "", "section_type": "Requirements"}
    
    finally:
        if driver_created and driver:
            try:
                driver.quit()
            except:
                pass  # Ignore any cleanup errors


def scrape_indeed_jobs(max_jobs=6, use_selenium_skills=False):
    """
    Scrape jobs from Indeed Egypt using Selenium (bypasses Cloudflare)
    Returns list of job dictionaries compatible with Wuzzuf format
    """
    if not SELENIUM_AVAILABLE:
        print("⚠️  Selenium not available, skipping Indeed scraper")
        return []
    
    print("\n🔍 Fetching jobs from Indeed Egypt...")
    
    driver = None
    jobs = []
    seen_job_ids = set()  # Track job IDs to avoid duplicates within this scraping session
    
    try:
        # Initialize Selenium with undetected_chromedriver if available
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        if UNDETECTED_AVAILABLE:
            print("   Using undetected ChromeDriver to bypass Cloudflare...")
            driver = uc.Chrome(options=chrome_options, use_subprocess=True)
        else:
            print("   Using standard ChromeDriver...")
            driver = webdriver.Chrome(options=chrome_options)
        
        # Search queries - use same keywords as Wuzzuf for consistency
        search_queries = list(SEARCH_KEYWORDS)
        random.shuffle(search_queries)  # Randomize order
        
        for query in search_queries:
            # Don't break here - let it fetch all potential jobs
            # The filtering will happen in the main scrape_jobs() function
            
            print(f"Searching Indeed for: {query}...")
            
            # Indeed Egypt search URL (fromage=1 means last 24 hours)
            url = f"https://eg.indeed.com/jobs?q={query}&l=Egypt&fromage=1"
            
            driver.get(url)
            time.sleep(3)
            
            # Get page source
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('div', class_=lambda x: x and 'job_seen_beacon' in x)
            if not job_cards:
                job_cards = soup.find_all('div', attrs={'data-jk': True})
            
            print(f"Found {len(job_cards)} potential jobs from Indeed...")
            
            for card in job_cards:
                # Don't break here - collect all potential jobs
                # The main function will filter to target count
                
                try:
                    # Extract title
                    title_elem = card.find('h2', class_='jobTitle')
                    if not title_elem:
                        title_elem = card.find('a', attrs={'data-jk': True})
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Filter by keyword
                    if not job_title_matches_keywords(title):
                        print(f"   ⏭️  Skipped (no keyword match): {title}")
                        continue
                    
                    # Extract company
                    company_elem = card.find('span', attrs={'data-testid': 'company-name'})
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                    
                    # Extract location
                    location_elem = card.find('div', attrs={'data-testid': 'text-location'})
                    location = location_elem.get_text(strip=True) if location_elem else "Egypt"
                    
                    # Filter Egypt only - Check for "Egypt" or Egyptian cities
                    egyptian_cities = ["Cairo", "Alexandria", "Giza", "Shubra El-Kheima", "Port Said", 
                                      "Suez", "Luxor", "Mansoura", "El-Mahalla El-Kubra", "Tanta", 
                                      "Asyut", "Ismailia", "Faiyum", "Zagazig", "Aswan", "Damietta",
                                      "Damanhur", "Minya", "Beni Suef", "Qena", "Sohag", "Hurghada",
                                      "6th of October", "Nasr City", "Heliopolis", "Maadi", "Sharm El Sheikh",
                                      "10th of Ramadan", "Obour", "New Cairo", "Sheikh Zayed", "مصر"]
                    
                    is_egypt = "Egypt" in location or any(city in location for city in egyptian_cities)
                    
                    if not is_egypt:
                        print(f"   ⏭️  Skipped (not Egypt): {title} - {location}")
                        continue
                    
                    # Normalize location - add "Egypt" if only city name
                    if "Egypt" not in location and any(city in location for city in egyptian_cities):
                        location = f"{location}, Egypt"
                    
                    # Extract link
                    link_elem = card.find('a', attrs={'data-jk': True})
                    if link_elem and link_elem.get('data-jk'):
                        job_id = link_elem.get('data-jk')
                        job_link = f"https://eg.indeed.com/viewjob?jk={job_id}"
                    else:
                        continue
                    
                    # Skip if already seen in this scraping session (check by job_id)
                    if job_id in seen_job_ids:
                        print(f"   ⏭️  Skipped (duplicate in search results): {title}")
                        continue
                    seen_job_ids.add(job_id)
                    
                    # Extract salary
                    salary_elem = card.find('div', class_=lambda x: x and 'salary' in x.lower() if x else False)
                    salary = salary_elem.get_text(strip=True) if salary_elem else "Not specified"
                    
                    # Extract description snippet
                    snippet_elem = card.find('div', class_='job-snippet')
                    if not snippet_elem:
                        snippet_elem = card.find('div', attrs={'data-testid': 'job-snippet'})
                    description = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    print(f"   ✅ Indeed job: {title} ({company})")
                    
                    # Extract full details from job detail page
                    print(f"   🔍 Fetching job details...")
                    details = get_indeed_job_details(job_link, driver=driver)
                    print(f"   📋 Found {len(details.get('requirements', []))} requirements")
                    if details.get('requirements'):
                        print(f"   Sample requirement: {details['requirements'][0][:50]}...")
                    
                    # Format like Wuzzuf jobs
                    job_data = {
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary": salary,
                        "description": details.get("description", description) or "Check job link for details",
                        "requirements": details.get("requirements", []),
                        "section_type": details.get("section_type", "Requirements"),  # Track which section was used
                        "skills": [],
                        "link": job_link,
                        "slug": create_slug(title),
                        "source": "Indeed Egypt",
                        "keyword": query  # Add keyword that found this job
                    }
                    
                    jobs.append(job_data)
                    
                except Exception as e:
                    print(f"   ⚠️  Error parsing Indeed job: {str(e)}")
                    continue
        
        print(f"✅ Scraped {len(jobs)} jobs from Indeed")
        return jobs
        
    except Exception as e:
        print(f"❌ Error scraping Indeed: {str(e)}")
        return []
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass  # Ignore any cleanup errors

def scrape_jobs(upload=False, save_posts=True, use_selenium_skills=False, send_whatsapp=False, send_telegram=False, max_jobs=None, include_indeed=False, wuzzuf_only=False, indeed_only=False, use_tinyurl=True):
    # Track start time for duration calculation
    import time as time_module
    start_time = time_module.time()
    
    # Use provided max_jobs or default TARGET_JOBS_COUNT
    target_jobs = max_jobs if max_jobs is not None else TARGET_JOBS_COUNT
    
    history = load_history()
    new_jobs = []
    blog_posts_html = []
    
    # Statistics tracking
    stats = {
        "wuzzuf": {"found": 0, "scraped": 0},
        "indeed": {"found": 0, "scraped": 0},
        "total_skipped": 0,
        "skip_reasons": {
            "no_keyword": 0, 
            "not_egypt": 0, 
            "not_recent": 0, 
            "duplicate": 0,
            "no_link": 0,
            "no_title": 0,
            "parse_error": 0
        },
        "images": {
            "total_jobs": 0,
            "with_image": 0,
            "without_image": 0,
            "image_matches": {}  # keyword -> image_filename
        }
    }

    blogger_service = None
    if upload:
        print("🔐 Authenticating with Blogger...")
        print(f"   BLOGGER_TOKEN_FILE: {BLOGGER_TOKEN_FILE}")
        print(f"   Token exists: {os.path.exists(BLOGGER_TOKEN_FILE)}")
        try:
            blogger_service = authenticate_blogger()
            print(f"✅ Authentication successful! Service: {blogger_service}")
        except Exception as e:
            print(f"❌ Auth failed: {e}")
            import traceback
            traceback.print_exc()
            blogger_service = None
    
    # ============ SCRAPE INDEED (if enabled) ============
    if (include_indeed or indeed_only) and not wuzzuf_only:
        # Fetch 3x target jobs to account for duplicates and jobs without requirements
        indeed_max = target_jobs if indeed_only else target_jobs // 2
        fetch_count = indeed_max * 3  # Fetch more to ensure we have enough valid jobs
        indeed_jobs = scrape_indeed_jobs(max_jobs=fetch_count, use_selenium_skills=use_selenium_skills)
        stats["indeed"]["found"] = len(indeed_jobs)
        
        for job in indeed_jobs:
            if len(new_jobs) >= target_jobs:
                break
            # Check if already scraped
            # Check both history.json and database
            if job['link'] not in history:
                if check_job_exists_in_db(job['link']):
                    print(f"   ⏭️  Skipped (duplicate from database): {job['title']}")
                    stats["skip_reasons"]["duplicate"] += 1
                    stats["total_skipped"] += 1
                    history.add(job['link'])  # Add to history to avoid future checks
                    continue
                
                # Check if job has requirements
                has_requirements = job.get('requirements') and len(job.get('requirements', [])) > 0
                
                if not has_requirements:
                    # No requirements - skip this job
                    print(f"   ⏭️  Skipped (no requirements found): {job['title']}")
                    stats["skip_reasons"]["no_requirements"] = stats["skip_reasons"].get("no_requirements", 0) + 1
                    stats["total_skipped"] += 1
                    continue
                
                # Generate Blog HTML for Indeed jobs
                blog_html = generate_blog_post_html(job)
                blog_posts_html.append(f"<!-- {job['slug']} -->\n{blog_html}\n<hr>\n")
                
                # Save individual post HTML if requested
                if save_posts:
                    try:
                        os.makedirs(POSTS_DIR, exist_ok=True)
                        post_file = os.path.join(POSTS_DIR, f"{job['slug']}.html")
                        with open(post_file, "w", encoding="utf-8") as pf:
                            pf.write(blog_html)
                        job['html_file'] = post_file
                    except Exception as e:
                        print(f"⚠️  Could not save post file for {job['title']}: {e}")
                
                # Post to Blogger only if upload=True and service available
                posted_to_blogger = False
                blog_link = None
                
                if upload and blogger_service:
                    print(f"   📤 Attempting to post to Blogger: {job['title']}")
                    real_url = post_to_blogger(blogger_service, job['title'], blog_html)
                    
                    # Verify the blog post is accessible
                    if real_url and verify_blogger_post(real_url):
                        blog_link = real_url
                        posted_to_blogger = True
                        job['blog_link'] = blog_link
                        print(f"   ✅ Blog post verified and accessible")
                    else:
                        print(f"   ⚠️  Blog post failed verification, using original link")
                        posted_to_blogger = False
                elif upload and not blogger_service:
                    print(f"   ⚠️  Skipping Blogger post - service is None (auth failed)")
                
                # Send to WhatsApp Channel if enabled
                telegram_sent = False
                whatsapp_sent = False
                
                # Use blog_link only if verified and uploaded, otherwise use original link
                # Apply TinyURL to the appropriate link
                if posted_to_blogger and blog_link:
                    message_link = create_tinyurl(blog_link) if use_tinyurl else blog_link
                else:
                    message_link = create_tinyurl(job['link']) if use_tinyurl else job['link']
                
                if send_whatsapp:
                    message = format_message(job, message_link, use_tinyurl)
                    whatsapp_sent = send_to_whatsapp_channel(message)
                    job['sent_to_whatsapp'] = whatsapp_sent
                
                # Send to Telegram Channel if enabled
                if send_telegram:
                    message = format_message(job, message_link, use_tinyurl)
                    telegram_sent = send_to_telegram_channel(message)
                    job['sent_to_telegram'] = telegram_sent
                
                # Set posted_to_blogger flag for database
                job['posted_to_blogger'] = posted_to_blogger
                
                new_jobs.append(job)
                history.add(job['link'])  # Use add() for set, not append()
                stats["indeed"]["scraped"] += 1
            else:
                print(f"   ⏭️  Skipped (duplicate from history.json): {job['title']}")
                stats["skip_reasons"]["duplicate"] += 1
                stats["total_skipped"] += 1
    
    # ============ SCRAPE WUZZUF ============
    if not indeed_only:  # Skip Wuzzuf if indeed_only is True
        # Shuffle keywords to get a random mix each time
        keywords = list(SEARCH_KEYWORDS)
        random.shuffle(keywords)
        
        print(f"\n🔍 Searching Wuzzuf for jobs in categories: {', '.join(keywords)}")
        print(f"Target: {target_jobs} jobs (currently have {len(new_jobs)} from Indeed)")
        
        wuzzuf_cards_found = 0
        
        for keyword in keywords:
            if len(new_jobs) >= target_jobs:
                break
                
            url = get_search_url(keyword)
            print(f"Fetching jobs for: {keyword}...")
            
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")
                
                # ============ FIND JOB CARDS (Class-Independent) ============
                job_cards = []
                
                # Method 1: Try known class name (fast path)
                job_cards = soup.find_all("div", class_="css-pkv5jc")
                
                # Method 2: If class changed, find divs containing links to /jobs/p/
                if not job_cards:
                    all_divs = soup.find_all("div")
                    for div in all_divs:
                        # Check if div contains a job link (/jobs/p/ not /jobs/careers/)
                        link = div.find("a", href=lambda x: x and "/jobs/p/" in str(x))
                        if link:
                            # Verify it has a title (h2 or h3)
                            title = div.find(['h2', 'h3'])
                            if title:
                                job_cards.append(div)
                
                # Method 3: Find all h2/h3 with /jobs/p/ links and get their parent containers
                if not job_cards:
                    for heading in soup.find_all(['h2', 'h3']):
                        link = heading.find("a", href=lambda x: x and "/jobs/p/" in str(x))
                        if link:
                            # Get the card container (usually 2-3 levels up)
                            card = heading.find_parent("div")
                            if card and card not in job_cards:
                                job_cards.append(card)

                print(f"Found {len(job_cards)} potential jobs for {keyword}...")
                wuzzuf_cards_found += len(job_cards)
                stats["wuzzuf"]["found"] += len(job_cards)

                found_for_keyword = False
                cards_processed = 0  # Track how many cards we actually checked
                
                for card in job_cards:
                    cards_processed += 1
                    
                    if len(new_jobs) >= target_jobs:
                        # Count remaining cards as "stopped" (reached target)
                        remaining = len(job_cards) - cards_processed + 1
                        if "target_reached" not in stats["skip_reasons"]:
                            stats["skip_reasons"]["target_reached"] = 0
                        stats["skip_reasons"]["target_reached"] += remaining
                        stats["total_skipped"] += remaining
                        break
                    if found_for_keyword:
                        # Count remaining cards as "variety" (one per keyword)
                        remaining = len(job_cards) - cards_processed + 1
                        if "variety_skip" not in stats["skip_reasons"]:
                            stats["skip_reasons"]["variety_skip"] = 0
                        stats["skip_reasons"]["variety_skip"] += remaining
                        stats["total_skipped"] += remaining
                        break # Move to next keyword to ensure variety
                        
                    try:
                        # ============ EXTRACT TITLE AND LINK (Reliable) ============
                        title_tag = None
                        link_tag = None
                        
                        # Find h2 or h3 containing a link to /jobs/p/ (actual job pages)
                        for heading in card.find_all(['h2', 'h3']):
                            link = heading.find("a", href=lambda x: x and "/jobs/p/" in str(x))
                            if link:
                                title_tag = heading
                                link_tag = link
                                break
                        
                        # Fallback: find any link with /jobs/p/ in the card (not /jobs/careers/)
                        if not link_tag:
                            link_tag = card.find("a", href=lambda x: x and "/jobs/p/" in str(x))
                        
                        if not link_tag:
                            stats["skip_reasons"]["no_link"] += 1
                            stats["total_skipped"] += 1
                            continue
                        
                        link = link_tag.get('href', '')
                        if not link:
                            stats["skip_reasons"]["no_link"] += 1
                            stats["total_skipped"] += 1
                            continue
                        
                        if not link.startswith("http"):
                            link = "https://wuzzuf.net" + link
                        
                        # Get title text
                        title = link_tag.get_text(strip=True)
                        if not title and title_tag:
                            title = title_tag.get_text(strip=True)
                        if not title:
                            stats["skip_reasons"]["no_title"] += 1
                            stats["total_skipped"] += 1
                            continue
                        
                        # Check both history.json and database
                        if link in history:
                            print(f"   ⏭️  Skipped (duplicate from history.json): {title}")
                            stats["skip_reasons"]["duplicate"] += 1
                            stats["total_skipped"] += 1
                            continue
                        
                        if check_job_exists_in_db(link):
                            print(f"   ⏭️  Skipped (duplicate from database): {title}")
                            stats["skip_reasons"]["duplicate"] += 1
                            stats["total_skipped"] += 1
                            history.add(link)  # Add to history to avoid future checks
                            continue
                        
                        # ============ FILTER: Check if title contains keywords ============
                        if not job_title_matches_keywords(title):
                            print(f"   ⏭️  Skipped (no keyword match): {title}")
                            stats["skip_reasons"]["no_keyword"] += 1
                            stats["total_skipped"] += 1
                            continue
                        
                        # ============ FILTER: Check if job is within 24 hours ============
                        # Look for time indicator in the card AND surrounding elements
                        is_recent = False
                        time_text = ""
                        
                        # Search in: card itself, parent, previous sibling, next sibling
                        search_areas = [card]
                        if card.parent:
                            search_areas.append(card.parent)
                        if card.find_previous_sibling():
                            search_areas.append(card.find_previous_sibling())
                        if card.find_next_sibling():
                            search_areas.append(card.find_next_sibling())
                        
                        for area in search_areas:
                            if is_recent:
                                break
                                
                            for elem in area.find_all(['span', 'div', 'p', 'time']):
                                text = elem.get_text(strip=True).lower()
                                
                                # Skip empty, very long text, or filter buttons
                                if not text or len(text) > 100:
                                    continue
                                if 'past 24 hours' in text or 'clear all filters' in text or 'jobs found' in text:
                                    continue
                                
                                # Check for very recent (hours, minutes, today)
                                if any(indicator in text for indicator in ['hour', 'hours ago', 'today', 'just now', 'minutes ago', 'minute ago', 'ساعة', 'ساعات', 'اليوم', 'دقيقة', 'دقائق']):
                                    is_recent = True
                                    time_text = text
                                    print(f"   ✅ Recent job ({time_text}): {title}")
                                    break
                                
                                # Check for "1 day ago" or "day ago" (within 24h)
                                if any(indicator in text for indicator in ['1 day ago', 'a day ago', 'يوم واحد', '١ يوم']):
                                    is_recent = True
                                    time_text = text
                                    print(f"   ✅ Recent job ({time_text}): {title}")
                                    break
                                
                                # Exclude older posts (2+ days, weeks, months)
                                if any(old in text for old in ['days ago', '2 day', '3 day', '4 day', '5 day', 'week', 'month', 'أيام', 'أسبوع', 'شهر']):
                                    is_recent = False
                                    time_text = text
                                    break
                        
                        # If no time found, skip (don't trust search filter alone)
                        if not is_recent:
                            if time_text:
                                print(f"   ⏭️  Skipped (posted {time_text}): {title}")
                            else:
                                print(f"   ⏭️  Skipped (no time indicator): {title}")
                            stats["skip_reasons"]["not_recent"] += 1
                            stats["total_skipped"] += 1
                            continue
                        
                        # ============ EXTRACT LOCATION (Reliable) ============
                        location = "Egypt"
                        
                        # Method 1: Find span with location icon or location-related text
                        for span in card.find_all("span"):
                            text = span.get_text(strip=True)
                            # Check if it looks like a location (has comma or common city names)
                            if "," in text or any(city in text for city in ["Cairo", "Alexandria", "Giza", "Riyadh", "Dubai", "Jeddah"]):
                                location = text
                                break
                        
                        # Method 2: Find any text with location indicators
                        if location == "Egypt":
                            card_text = card.get_text()
                            # Look for location patterns
                            import re
                            location_pattern = r'([A-Za-z\s]+,\s*[A-Za-z\s]+)'
                            matches = re.findall(location_pattern, card_text)
                            if matches:
                                # Get the first reasonable match
                                for match in matches:
                                    if len(match) < 50:  # Reasonable length
                                        location = match.strip()
                                        break
                        
                        # ============ FILTER: Egypt Only ============
                        if "Egypt" not in location:
                            print(f"   ⏭️  Skipped (not Egypt): {title} - {location}")
                            stats["skip_reasons"]["not_egypt"] += 1
                            stats["total_skipped"] += 1
                            continue
                        
                        print(f"Scraping details for: {title}")
                        details = get_job_details(link, use_selenium_for_skills=use_selenium_skills)
                        
                        if details:
                            slug = create_slug(title)
                            
                            job_data = {
                                "title": title,
                                "location": location,
                                "link": link,
                                "requirements": details.get("requirements", []),
                                "description": details.get("description", ""),
                                "skills": details.get("skills", []),
                                "company_logo": details.get("company_logo", ""),
                                "keyword": keyword,  # Add keyword that found this job
                                "source": "wuzzuf"
                            }
                            
                            # Generate Blog HTML
                            blog_html = generate_blog_post_html(job_data)
                            blog_posts_html.append(f"<!-- {slug} -->\n{blog_html}\n<hr>\n")

                            # Save individual post HTML if requested
                            if save_posts:
                                try:
                                    os.makedirs(POSTS_DIR, exist_ok=True)
                                    post_file = os.path.join(POSTS_DIR, f"{slug}.html")
                                    with open(post_file, "w", encoding="utf-8") as pf:
                                        pf.write(blog_html)
                                    job_data['html_file'] = post_file
                                except Exception as e:
                                    print(f"⚠️  Could not save post file for {title}: {e}")

                            # Post to Blogger only if upload=True and service available
                            posted_to_blogger = False
                            blog_link = None
                            
                            if upload and blogger_service:
                                print(f"   📤 Attempting to post to Blogger: {title}")
                                real_url = post_to_blogger(blogger_service, title, blog_html)
                                
                                # Verify the blog post is accessible
                                if real_url and verify_blogger_post(real_url):
                                    blog_link = real_url
                                    posted_to_blogger = True
                                    job_data['blog_link'] = blog_link
                                    print(f"   ✅ Blog post verified and accessible")
                                else:
                                    print(f"   ⚠️  Blog post failed verification, using original link")
                                    posted_to_blogger = False
                            elif upload and not blogger_service:
                                print(f"   ⚠️  Skipping Blogger post - service is None (auth failed)")
                            
                            # Send to WhatsApp Channel if enabled
                            telegram_sent = False
                            whatsapp_sent = False
                            
                            # Use blog_link only if verified and uploaded, otherwise use original link
                            # Apply TinyURL to the appropriate link
                            if posted_to_blogger and blog_link:
                                message_link = create_tinyurl(blog_link) if use_tinyurl else blog_link
                            else:
                                message_link = create_tinyurl(link) if use_tinyurl else link
                            
                            if send_whatsapp:
                                message = format_message(job_data, message_link, use_tinyurl)
                                whatsapp_sent = send_to_whatsapp_channel(message)
                                job_data['sent_to_whatsapp'] = whatsapp_sent
                            
                            # Send to Telegram Channel if enabled
                            if send_telegram:
                                message = format_message(job_data, message_link, use_tinyurl)
                                telegram_sent = send_to_telegram_channel(message)
                                job_data['sent_to_telegram'] = telegram_sent
                            
                            # Set posted_to_blogger flag for database
                            job_data['posted_to_blogger'] = posted_to_blogger
                            
                            new_jobs.append(job_data)
                            history.add(link)
                            stats["wuzzuf"]["scraped"] += 1
                            found_for_keyword = True
                            time.sleep(1) 
                        
                    except Exception as e:
                        print(f"Error parsing card: {e}")
                        stats["skip_reasons"]["parse_error"] += 1
                        stats["total_skipped"] += 1
                        continue
            except Exception as e:
                print(f"Error fetching {keyword}: {e}")
                continue

    # Save updated history
    save_history(history)
    
    # Output messages to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for job in new_jobs:
            # Use blog_link only if it was uploaded, otherwise use original link
            display_link = job.get('blog_link') if (upload and blogger_service) else job.get('link')
            msg = format_message(job, display_link, use_tinyurl)
            f.write(msg + "\n" + "-"*20 + "\n")
            print(msg)
            print("-" * 20)
            
    # Output blog posts to file
    with open(BLOG_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(blog_posts_html))

    # Output CSV for Bulk Import Plugin
    import csv
    csv_file = os.path.join(SCRIPT_DIR, "posts.csv")
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Header compatible with "Really Simple CSV Importer"
        writer.writerow(["post_title", "post_content", "post_status", "post_name"])
        
        for job in new_jobs:
            # Generate HTML content again or reuse if stored
            # We need the full HTML content here
            html_content = generate_blog_post_html(job)
            slug = create_slug(job['title'])
            writer.writerow([job['title'], html_content, "publish", slug])

    # Output XML for Blogger Import (Atom Format)
    blogger_xml_file = os.path.join(SCRIPT_DIR, "blogger_posts.xml")
    with open(blogger_xml_file, "w", encoding="utf-8") as f:
        f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        f.write("<feed xmlns='http://www.w3.org/2005/Atom' xmlns:openSearch='http://a9.com/-/spec/opensearchrss/1.0/' xmlns:georss='http://www.georss.org/georss' xmlns:gd='http://schemas.google.com/g/2005' xmlns:thr='http://purl.org/syndication/thread/1.0'>\n")
        f.write(f"<id>tag:blogger.com,1999:blog-123456789.archive</id>\n")
        f.write(f"<updated>{time.strftime('%Y-%m-%dT%H:%M:%S.000+00:00')}</updated>\n")
        f.write(f"<title type='text'>Job Listings</title>\n")
        f.write(f"<generator version='7.00' uri='http://www.blogger.com'>Blogger</generator>\n")
        
        for i, job in enumerate(new_jobs):
            slug = create_slug(job['title'])
            html_content = generate_blog_post_html(job)
            # Escape XML special characters in content if needed, but CDATA handles most
            
            f.write("<entry>\n")
            f.write(f"<id>tag:blogger.com,1999:blog-123456789.post-{int(time.time()) + i}</id>\n")
            f.write(f"<published>{time.strftime('%Y-%m-%dT%H:%M:%S.000+00:00')}</published>\n")
            f.write(f"<updated>{time.strftime('%Y-%m-%dT%H:%M:%S.000+00:00')}</updated>\n")
            f.write(f"<title type='text'>{job['title']}</title>\n")
            f.write(f"<content type='html'><![CDATA[{html_content}]]></content>\n")
            f.write(f"<link rel='alternate' type='text/html' href='{BLOG_DOMAIN}/{time.strftime('%Y/%m')}/{slug}.html' title='{job['title']}'/>\n")
            f.write(f"<author><name>Admin</name></author>\n")
            f.write("</entry>\n")
            
        f.write("</feed>\n")

    print(f"Saved {len(new_jobs)} new jobs to {OUTPUT_FILE}")
    print(f"Saved blog HTML to {BLOG_OUTPUT_FILE}")
    print(f"Saved Blogger XML to {blogger_xml_file}")

    if save_posts:
        print(f"Saved individual post files to ./{POSTS_DIR}/")
    
    # ============ PRINT SUMMARY TABLE ============
    print("\n" + "="*60)
    print("📊 SCRAPING SUMMARY")
    print("="*60)
    print(f"{'Source':<15} {'Found':<10} {'Scraped':<10} {'Success Rate'}")
    print("-"*60)
    
    wuzzuf_found = stats['wuzzuf']['found']
    wuzzuf_scraped = stats['wuzzuf']['scraped']
    wuzzuf_rate = f"{(wuzzuf_scraped/wuzzuf_found*100):.1f}%" if wuzzuf_found > 0 else "N/A"
    print(f"{'Wuzzuf':<15} {wuzzuf_found:<10} {wuzzuf_scraped:<10} {wuzzuf_rate}")
    
    indeed_found = stats['indeed']['found']
    indeed_scraped = stats['indeed']['scraped']
    indeed_rate = f"{(indeed_scraped/indeed_found*100):.1f}%" if indeed_found > 0 else "N/A"
    print(f"{'Indeed':<15} {indeed_found:<10} {indeed_scraped:<10} {indeed_rate}")
    
    print("-"*60)
    total_found = wuzzuf_found + indeed_found
    total_scraped = wuzzuf_scraped + indeed_scraped
    total_rate = f"{(total_scraped/total_found*100):.1f}%" if total_found > 0 else "N/A"
    print(f"{'TOTAL':<15} {total_found:<10} {total_scraped:<10} {total_rate}")
    print("="*60)
    
    print("\n📋 Skip Reasons:")
    print("-"*60)
    skip_reason_labels = {
        "no_keyword": "❌ No keyword match",
        "not_egypt": "🌍 Not in Egypt",
        "not_recent": "⏰ Not recent (>24h)",
        "duplicate": "🔄 Duplicate",
        "no_link": "🔗 No valid link",
        "no_title": "📝 No title",
        "parse_error": "⚠️  Parse error",
        "target_reached": "🎯 Target reached",
        "variety_skip": "🔀 Skipped for variety"
    }
    
    for reason, count in stats['skip_reasons'].items():
        if count > 0:
            reason_label = skip_reason_labels.get(reason, reason)
            print(f"  {reason_label:<30} {count}")
    print("-"*60)
    print(f"  {'Total Skipped':<30} {stats['total_skipped']}")
    print("="*60 + "\n")
    
    # Calculate duration
    duration = time_module.time() - start_time
    
    # Log completion to Supabase
    try:
        # Calculate keywords found
        keywords_found = {}
        for job in new_jobs:
            keyword = job.get('keyword', 'Unknown')
            keywords_found[keyword] = keywords_found.get(keyword, 0) + 1
        
        # Calculate sources
        sources = {
            'indeed': stats['indeed']['scraped'],
            'wuzzuf': stats['wuzzuf']['scraped']
        }
        
        total_scraped = stats['wuzzuf']['found'] + stats['indeed']['found']
        jobs_saved = len(new_jobs)
        duplicates_skipped = stats['skip_reasons'].get('duplicate', 0)
        
        # Calculate image statistics
        images_stats = {
            'total_jobs': len(new_jobs),
            'with_image': sum(1 for job in new_jobs if job.get('has_image', False)),
            'without_image': sum(1 for job in new_jobs if not job.get('has_image', False)),
            'image_by_keyword': {}
        }
        
        # Track which keywords have images
        for job in new_jobs:
            keyword = job.get('keyword', 'Unknown')
            has_image = job.get('has_image', False)
            if keyword not in images_stats['image_by_keyword']:
                images_stats['image_by_keyword'][keyword] = {'with_image': 0, 'without_image': 0}
            if has_image:
                images_stats['image_by_keyword'][keyword]['with_image'] += 1
            else:
                images_stats['image_by_keyword'][keyword]['without_image'] += 1
        
        metadata = {
            'total_scraped': total_scraped,
            'jobs_saved': jobs_saved,
            'duplicates_skipped': duplicates_skipped,
            'skip_reasons': stats['skip_reasons'],
            'keywords_found': keywords_found,
            'sources': sources,
            'duration': round(duration, 2),
            'images': images_stats
        }
        
        log_data = {
            'status': 'completed',
            'message': f'Scraping completed: {jobs_saved} jobs saved from {total_scraped} total scraped',
            'metadata': metadata
        }
        
        supabase.table('scraping_logs').insert(log_data).execute()
        print(f"✅ Logged scraping completion to database (Duration: {duration:.2f}s)")
    except Exception as e:
        print(f"⚠️  Failed to log to database: {e}")
    
    # Return the scraped jobs AND stats
    return {
        "jobs": new_jobs,
        "stats": stats
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape jobs and optionally upload to Blogger")
    parser.add_argument('--upload', action='store_true', help='Post new jobs to Blogger via API')
    parser.add_argument('--save-posts', dest='save_posts', action='store_true', default=True, help='Save individual post HTML files in the posts/ folder')
    parser.add_argument('--no-save-posts', dest='save_posts', action='store_false', help="Don't save individual post HTML files")
    parser.add_argument('--selenium-skills', dest='selenium_skills', action='store_true', help='Use Selenium to extract skills (more reliable, but slower). Requires: pip install selenium')
    parser.add_argument('--send-whatsapp', dest='send_whatsapp', action='store_true', help='Send jobs to WhatsApp Channel automatically')
    parser.add_argument('--send-telegram', dest='send_telegram', action='store_true', help='Send jobs to Telegram Channel automatically')
    parser.add_argument('--max-jobs', type=int, default=None, help=f'Maximum number of jobs to scrape (default: {TARGET_JOBS_COUNT})')
    parser.add_argument('--include-indeed', dest='include_indeed', action='store_true', help='Also scrape jobs from Indeed Egypt (requires Selenium)')
    parser.add_argument('--wuzzuf-only', dest='wuzzuf_only', action='store_true', help='Scrape only from Wuzzuf (ignore Indeed)')
    parser.add_argument('--indeed-only', dest='indeed_only', action='store_true', help='Scrape only from Indeed (ignore Wuzzuf, requires Selenium)')
    parser.add_argument('--use-tinyurl', dest='use_tinyurl', action='store_true', default=True, help='Use TinyURL for job links (default: True)')
    parser.add_argument('--no-tinyurl', dest='use_tinyurl', action='store_false', help="Don't use TinyURL, show full links")
    args = parser.parse_args()
    
    # Validate conflicting arguments
    if args.wuzzuf_only and args.indeed_only:
        print("❌ Error: Cannot use --wuzzuf-only and --indeed-only together")
        exit(1)
    if args.indeed_only and not SELENIUM_AVAILABLE:
        print("❌ Error: --indeed-only requires Selenium. Install with: pip install selenium")
        exit(1)

    scrape_jobs(upload=args.upload, save_posts=args.save_posts, use_selenium_skills=args.selenium_skills, send_whatsapp=args.send_whatsapp, send_telegram=args.send_telegram, max_jobs=args.max_jobs, include_indeed=args.include_indeed, wuzzuf_only=args.wuzzuf_only, indeed_only=args.indeed_only, use_tinyurl=args.use_tinyurl)
