from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import sys
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

# Add parent directory to path to import scraper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import scrape_jobs

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="TechFlow Scraper API", version="1.0.0")

# CORS middleware - allow Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with Netlify domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# API Secret for simple protection
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-key-here")

# TinyURL API Key
TINYURL_API_KEY = os.getenv("TINYURL_API_KEY", "nRFavNgCA9lwoqmk0BxuxBe1TXGTb4s97jR2os6Aq8TfxWAGXNoVlr1qLe2D")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flag to track scraping status
SCRAPING_ACTIVE = False
STOP_SCRAPING = False

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()
logger.info("APScheduler started")


# Helper function to create TinyURL
def create_tinyurl(long_url: str) -> str:
    """إنشاء TinyURL باستخدام API الرسمي"""
    try:
        # Skip TinyURL for Indeed links (domain is banned)
        if 'indeed.com' in long_url:
            return long_url
        
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
            except:
                pass
        
        return long_url
    except Exception as e:
        logger.error(f"TinyURL error: {e}")
        return long_url


def scheduled_scraping_job():
    """العملية المجدولة للسكريب"""
    global SCRAPING_ACTIVE
    
    if SCRAPING_ACTIVE:
        logger.info("Scheduled scraping skipped - already running")
        return
    
    try:
        # جلب إعدادات Schedule من database
        result = supabase.table("settings").select("*").eq("key", "schedule").execute()
        
        if not result.data or len(result.data) == 0:
            logger.info("No schedule configured")
            return
        
        schedule_config = result.data[0]["value"]
        if isinstance(schedule_config, str):
            import json
            schedule_config = json.loads(schedule_config)
        
        # التحقق من أن Schedule مفعّل
        if not schedule_config.get("enabled", False):
            logger.info("Schedule is disabled")
            return
        
        logger.info(f"Starting scheduled scraping: {schedule_config}")
        
        # Log configuration details
        supabase.table("scraping_logs").insert({
            "level": "info",
            "message": f"📅 Scheduled run with config: Blogger={schedule_config.get('upload_to_blogger')}, Telegram={schedule_config.get('send_to_telegram')}, WhatsApp={schedule_config.get('send_to_whatsapp')}",
            "metadata": schedule_config
        }).execute()
        
        # إنشاء ScrapeRequest object
        scrape_config = ScrapeRequest(
            max_jobs=schedule_config.get("max_jobs", 6),
            sources=schedule_config.get("sources", ["wuzzuf", "indeed"]),
            upload_to_blogger=schedule_config.get("upload_to_blogger", False),
            send_to_telegram=schedule_config.get("send_to_telegram", False),
            send_to_whatsapp=schedule_config.get("send_to_whatsapp", False),
            use_selenium_skills=False,
            use_tinyurl=True
        )
        
        # تشغيل السكريب
        run_scraper(scrape_config)
        
    except Exception as e:
        logger.error(f"Scheduled scraping error: {e}")
        supabase.table("scraping_logs").insert({
            "level": "error",
            "message": f"❌ Scheduled scraping failed: {str(e)}",
            "metadata": {"error": str(e)}
        }).execute()


def update_schedule_job():
    """تحديث جدولة السكريب حسب الإعدادات"""
    try:
        # حذف الجدولة القديمة
        scheduler.remove_all_jobs()
        
        # جلب إعدادات Schedule
        result = supabase.table("settings").select("*").eq("key", "schedule").execute()
        
        if not result.data or len(result.data) == 0:
            logger.info("No schedule to update")
            return
        
        schedule_config = result.data[0]["value"]
        if isinstance(schedule_config, str):
            import json
            schedule_config = json.loads(schedule_config)
        
        if not schedule_config.get("enabled", False):
            logger.info("Schedule disabled - no jobs added")
            return
        
        # قراءة الوقت
        time_str = schedule_config.get("time", "10:00")
        hour, minute = map(int, time_str.split(":"))
        
        frequency = schedule_config.get("frequency", "daily")
        
        # إضافة job حسب التكرار
        if frequency == "hourly":
            trigger = CronTrigger(minute=minute)
        elif frequency == "daily":
            trigger = CronTrigger(hour=hour, minute=minute)
        elif frequency == "weekly":
            trigger = CronTrigger(day_of_week=0, hour=hour, minute=minute)  # Monday
        else:
            trigger = CronTrigger(hour=hour, minute=minute)
        
        scheduler.add_job(
            scheduled_scraping_job,
            trigger=trigger,
            id="scraping_job",
            name="Scheduled Scraping",
            replace_existing=True
        )
        
        logger.info(f"Schedule updated: {frequency} at {time_str}")
        
    except Exception as e:
        logger.error(f"Error updating schedule: {e}")


# Helper function to create TinyURL
def create_tinyurl(long_url: str) -> str:
    """Create a TinyURL using official API"""
    try:
        # Skip TinyURL for Indeed links (domain is banned)
        if 'indeed.com' in long_url:
            logger.info(f"Using direct Indeed link (TinyURL blocks Indeed domain)")
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
            except:
                pass
        
        return long_url
    except Exception as e:
        logger.error(f"TinyURL error: {e}")
        return long_url


# Pydantic Models
class ScrapeRequest(BaseModel):
    max_jobs: int = 6
    sources: List[str] = ["wuzzuf", "indeed"]  # "wuzzuf", "indeed", or both
    upload_to_blogger: bool = False
    send_to_telegram: bool = False
    send_to_whatsapp: bool = False
    use_tinyurl: bool = True
    use_selenium_skills: bool = False


class ScrapeResponse(BaseModel):
    status: str
    message: str
    jobs_scraped: Optional[int] = None


class SettingsUpdate(BaseModel):
    key: str
    value: dict


class ScheduleConfig(BaseModel):
    enabled: bool = False
    time: str = "10:00"
    frequency: str = "daily"
    max_jobs: int = 6
    sources: List[str] = ["wuzzuf", "indeed"]
    upload_to_blogger: bool = False
    send_to_telegram: bool = False
    send_to_whatsapp: bool = False


def calculate_next_run(schedule_config: dict) -> str:
    """حساب موعد التشغيل القادم"""
    from datetime import datetime, timedelta
    
    if not schedule_config.get("enabled") or not schedule_config.get("time"):
        return None
    
    try:
        now = datetime.now()
        time_str = schedule_config.get("time", "10:00")
        hour, minute = map(int, time_str.split(":"))
        
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # إذا الوقت فات، حدد الموعد القادم حسب التكرار
        if next_run <= now:
            frequency = schedule_config.get("frequency", "daily")
            if frequency == "hourly":
                next_run = now.replace(minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(hours=1)
            elif frequency == "daily":
                next_run += timedelta(days=1)
            elif frequency == "weekly":
                next_run += timedelta(weeks=1)
        
        return next_run.isoformat()
    except Exception as e:
        logger.error(f"Error calculating next run: {e}")
        return None


def calculate_next_run(schedule_config: dict) -> str:
    """حساب موعد التشغيل القادم"""
    from datetime import datetime, timedelta
    
    if not schedule_config.get("enabled") or not schedule_config.get("time"):
        return None
    
    try:
        now = datetime.now()
        time_str = schedule_config.get("time", "10:00")
        hour, minute = map(int, time_str.split(":"))
        
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # إذا الوقت فات، حدد الموعد القادم حسب التكرار
        if next_run <= now:
            frequency = schedule_config.get("frequency", "daily")
            if frequency == "hourly":
                next_run = now.replace(minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(hours=1)
            elif frequency == "daily":
                next_run += timedelta(days=1)
            elif frequency == "weekly":
                next_run += timedelta(weeks=1)
        
        return next_run.isoformat()
    except Exception as e:
        logger.error(f"Error calculating next run: {e}")
        return None


# Simple API Key authentication
def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True


# Health check
@app.get("/")
def root():
    return {
        "status": "online",
        "service": "TechFlow Scraper API",
        "version": "1.0.0"
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test Supabase connection
        result = supabase.table("settings").select("*").limit(1).execute()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": result.data
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.post("/api/update-tinyurls")
async def update_tinyurls(x_api_key: str = Header(None)):
    """Update TinyURLs for jobs that don't have them"""
    verify_api_key(x_api_key)
    
    try:
        # Get jobs without tiny_url
        result = supabase.table("jobs").select("id, link, blogger_url").is_("tiny_url", "null").execute()
        jobs_to_update = result.data
        
        updated_count = 0
        for job in jobs_to_update:
            # Use blogger_url if available, otherwise use link
            url_to_shorten = job.get("blogger_url") if job.get("blogger_url") else job.get("link")
            
            if url_to_shorten:
                tiny_url = create_tinyurl(url_to_shorten)
                
                # Update job with tiny_url
                supabase.table("jobs").update({"tiny_url": tiny_url}).eq("id", job["id"]).execute()
                updated_count += 1
                logger.info(f"Updated TinyURL for job {job['id']}")
        
        return {"status": "success", "updated": updated_count}
    except Exception as e:
        logger.error(f"Error updating TinyURLs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scrape", response_model=ScrapeResponse)
async def start_scraping(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    """
    Start scraping jobs from Wuzzuf and/or Indeed
    This will run in background and save results to Supabase
    """
    # Verify API key
    verify_api_key(x_api_key)
    
    try:
        # Add scraping task to background
        background_tasks.add_task(run_scraper, request)
        
        # Log to Supabase
        log_data = {
            "level": "info",
            "message": f"Scraping started with config: {request.dict()}",
            "metadata": request.dict()
        }
        supabase.table("scraping_logs").insert(log_data).execute()
        
        return ScrapeResponse(
            status="started",
            message="Scraping job started in background"
        )
    except Exception as e:
        logger.error(f"Error starting scraper: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs")
async def get_jobs(
    limit: int = 50,
    offset: int = 0,
    source: Optional[str] = None
):
    """Get scraped jobs from database"""
    try:
        query = supabase.table("jobs").select("*").order("created_at", desc=True)
        
        if source:
            query = query.eq("source", source)
        
        result = query.range(offset, offset + limit - 1).execute()
        
        return {
            "jobs": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get scraping statistics"""
    try:
        # Total jobs
        total_jobs = supabase.table("jobs").select("*", count="exact").execute()
        
        # Jobs by source
        wuzzuf_jobs = supabase.table("jobs").select("*", count="exact").eq("source", "wuzzuf").execute()
        indeed_jobs = supabase.table("jobs").select("*", count="exact").eq("source", "indeed").execute()
        
        # Posted to blogger
        posted_jobs = supabase.table("jobs").select("*", count="exact").eq("posted_to_blogger", True).execute()
        
        return {
            "total_jobs": total_jobs.count,
            "wuzzuf_jobs": wuzzuf_jobs.count,
            "indeed_jobs": indeed_jobs.count,
            "posted_to_blogger": posted_jobs.count,
            "sent_to_telegram": 0,  # TODO: implement counter
            "sent_to_whatsapp": 0   # TODO: implement counter
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/settings")
async def get_settings():
    """Get all settings from database"""
    try:
        result = supabase.table("settings").select("*").execute()
        
        # Convert to key-value dict
        settings_dict = {item["key"]: item["value"] for item in result.data}
        
        return settings_dict
    except Exception as e:
        logger.error(f"Error fetching settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/settings")
async def update_settings(
    settings: SettingsUpdate,
    x_api_key: str = Header(None)
):
    """Update settings in database"""
    verify_api_key(x_api_key)
    
    try:
        # Upsert settings
        data = {
            "key": settings.key,
            "value": settings.value
        }
        
        result = supabase.table("settings").upsert(data).execute()
        
        return {
            "status": "success",
            "message": f"Settings updated for key: {settings.key}"
        }
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs")
async def get_logs(limit: int = 100, level: Optional[str] = None):
    """Get scraping logs"""
    try:
        query = supabase.table("scraping_logs").select("*").order("timestamp", desc=True)
        
        if level:
            query = query.eq("level", level)
        
        result = query.limit(limit).execute()
        
        return {
            "logs": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Background task function
def run_scraper(config: ScrapeRequest):
    """
    Run the scraper with given configuration
    This will be implemented to call scraper.py
    """
    logger.info(f"Starting scraper with config: {config}")
    
    try:
        # Log start
        supabase.table("scraping_logs").insert({
            "level": "info",
            "message": "🚀 Scraping started",
            "metadata": config.dict()
        }).execute()
        
        # Log configuration
        sources_text = " and ".join(config.sources)
        supabase.table("scraping_logs").insert({
            "level": "info",
            "message": f"📋 Configuration: Scraping {config.max_jobs} jobs from {sources_text}",
            "metadata": {
                "max_jobs": config.max_jobs,
                "sources": config.sources,
                "upload_to_blogger": config.upload_to_blogger,
                "send_to_telegram": config.send_to_telegram,
                "send_to_whatsapp": config.send_to_whatsapp
            }
        }).execute()
        
        # Log step 1
        supabase.table("scraping_logs").insert({
            "level": "info",
            "message": "🔍 Step 1: Initializing web scraper...",
            "metadata": {}
        }).execute()
        
        # Log step 2
        supabase.table("scraping_logs").insert({
            "level": "info",
            "message": "🌐 Step 2: Connecting to job sources...",
            "metadata": {"sources": config.sources}
        }).execute()
        
        # ============ CALL ACTUAL SCRAPER ============
        # Determine source parameters based on config
        wuzzuf_only = "wuzzuf" in config.sources and "indeed" not in config.sources
        indeed_only = "indeed" in config.sources and "wuzzuf" not in config.sources
        include_indeed = "indeed" in config.sources
        
        # Log step 3
        supabase.table("scraping_logs").insert({
            "level": "info",
            "message": "📊 Step 3: Extracting job listings...",
            "metadata": {}
        }).execute()
        
        # Run the actual scraper
        logger.info(f"Calling scrape_jobs with: max_jobs={config.max_jobs}, wuzzuf_only={wuzzuf_only}, indeed_only={indeed_only}")
        
        try:
            scraper_result = scrape_jobs(
                upload=config.upload_to_blogger,
                save_posts=False,  # We'll save to Supabase instead
                use_selenium_skills=config.use_selenium_skills,
                send_whatsapp=config.send_to_whatsapp,
                send_telegram=config.send_to_telegram,
                max_jobs=config.max_jobs,
                include_indeed=include_indeed,
                wuzzuf_only=wuzzuf_only,
                indeed_only=indeed_only,
                use_tinyurl=config.use_tinyurl
            )
            
            # Extract jobs and stats from result
            if isinstance(scraper_result, dict):
                jobs_data = scraper_result.get("jobs", [])
                scraper_stats = scraper_result.get("stats", {})
            else:
                # Backward compatibility: if scraper returns list directly
                jobs_data = scraper_result
                scraper_stats = {}
                
        except Exception as scraper_error:
            logger.error(f"Scraper function error: {scraper_error}")
            supabase.table("scraping_logs").insert({
                "level": "error",
                "message": f"❌ Scraper error: {str(scraper_error)}",
                "metadata": {"error": str(scraper_error), "type": type(scraper_error).__name__}
            }).execute()
            raise
        
        # Log step 4
        total_jobs = len(jobs_data) if jobs_data else 0
        supabase.table("scraping_logs").insert({
            "level": "info",
            "message": f"✅ Step 4: Processing {total_jobs} job details...",
            "metadata": {"total_jobs": total_jobs}
        }).execute()
        
        # ============ SAVE JOBS TO SUPABASE ============
        jobs_saved = 0
        if jobs_data and isinstance(jobs_data, list) and len(jobs_data) > 0:
            global STOP_SCRAPING
            total_jobs = len(jobs_data)
            logger.info(f"Found {total_jobs} jobs, saving to database...")
            
            for idx, job in enumerate(jobs_data, 1):
                try:
                    # Check if job already exists (duplicate check)
                    job_link = job.get("link", "")
                    existing_job = supabase.table("jobs").select("id").eq("link", job_link).execute()
                    
                    if existing_job.data and len(existing_job.data) > 0:
                        # Job already exists, skip it
                        logger.info(f"⏭️ Skipping duplicate job: {job.get('title', 'Unknown')}")
                        supabase.table("scraping_logs").insert({
                            "level": "info",
                            "message": f"⏭️ Skipped duplicate: {job.get('title', 'Unknown')}",
                            "metadata": {"link": job_link, "reason": "duplicate"}
                        }).execute()
                        continue  # Skip to next job
                    
                    # Log progress
                    progress_percent = int((idx / total_jobs) * 100)
                    supabase.table("scraping_logs").insert({
                        "level": "info",
                        "message": f"💾 Saving job {idx}/{total_jobs} ({progress_percent}%): {job.get('title', 'Unknown')}",
                        "metadata": {
                            "progress": progress_percent,
                            "current": idx,
                            "total": total_jobs
                        }
                    }).execute()
                    # Get source and validate
                    source = str(job.get("source", "")).lower().strip()
                    
                    # Validate source - if invalid, try to detect from link
                    if source not in ["wuzzuf", "indeed"]:
                        if "indeed" in job_link.lower():
                            source = "indeed"
                        elif "wuzzuf" in job_link.lower():
                            source = "wuzzuf"
                        else:
                            source = "wuzzuf"  # Final fallback
                    
                    # Create TinyURL for the link (if not blogger)
                    blogger_url = job.get("blog_link", "")  # scraper.py already sets this if uploaded
                    
                    # Use blogger URL with TinyURL if available, otherwise create TinyURL for job link
                    if blogger_url:
                        tiny_url = create_tinyurl(blogger_url)
                    else:
                        tiny_url = create_tinyurl(job_link)
                    
                    # Prepare job data for Supabase
                    job_record = {
                        "title": job.get("title", ""),
                        "company": job.get("company", ""),
                        "location": job.get("location", ""),
                        "salary": job.get("salary", "Confidential"),
                        "link": job_link,
                        "tiny_url": tiny_url,
                        "source": source,
                        "description": job.get("description", ""),
                        "requirements": job.get("requirements", []),
                        "skills": job.get("skills", []),
                        "slug": job.get("slug", ""),
                        "blogger_url": blogger_url,
                        "html_content": job.get("html_content", ""),
                        "posted_to_blogger": bool(blogger_url),  # True if blogger_url exists
                        "sent_to_telegram": job.get("sent_to_telegram", False),  # From scraper
                        "sent_to_whatsapp": job.get("sent_to_whatsapp", False),   # From scraper
                        "keyword": job.get("keyword", "")  # Add keyword
                    }
                    
                    # Insert into Supabase
                    result = supabase.table("jobs").insert(job_record).execute()
                    jobs_saved += 1
                    logger.info(f"Saved job: {job.get('title')} from {source}")
                    
                    # Check if stop signal received
                    if STOP_SCRAPING:
                        logger.info("Stop signal detected, breaking loop")
                        supabase.table("scraping_logs").insert({
                            "level": "warning",
                            "message": f"⛔ Scraping stopped by user after {jobs_saved} jobs",
                            "metadata": {"jobs_saved": jobs_saved}
                        }).execute()
                        break
                    
                except Exception as e:
                    logger.error(f"Error saving job to database: {e}")
                    supabase.table("scraping_logs").insert({
                        "level": "warning",
                        "message": f"⚠️ Could not save job: {job.get('title', 'Unknown')}",
                        "metadata": {"error": str(e)}
                    }).execute()
        else:
            logger.warning(f"No jobs returned from scraper. jobs_data type: {type(jobs_data)}, value: {jobs_data}")
            supabase.table("scraping_logs").insert({
                "level": "warning",
                "message": "⚠️ Scraper returned no jobs",
                "metadata": {"jobs_data_type": str(type(jobs_data)), "is_none": jobs_data is None}
            }).execute()
        
        # Log completion
        total_scraped = len(jobs_data) if jobs_data else 0
        duplicates_skipped = total_scraped - jobs_saved
        
        completion_message = f"🎉 Scraping completed! Saved {jobs_saved} new jobs"
        if duplicates_skipped > 0:
            completion_message += f" (skipped {duplicates_skipped} duplicates)"
        
        supabase.table("scraping_logs").insert({
            "level": "info",
            "message": completion_message,
            "metadata": {
                "status": "completed", 
                "jobs_saved": jobs_saved,
                "duplicates_skipped": duplicates_skipped,
                "total_scraped": total_scraped,
                "sources": config.sources,
                "skip_reasons": scraper_stats.get("skip_reasons", {}),
                "wuzzuf_stats": scraper_stats.get("wuzzuf", {}),
                "indeed_stats": scraper_stats.get("indeed", {})
            }
        }).execute()
        
        logger.info(f"Scraping completed - {jobs_saved} new jobs saved, {duplicates_skipped} duplicates skipped")
        
    except Exception as e:
        logger.error(f"Scraper error: {e}")
        supabase.table("scraping_logs").insert({
            "level": "error",
            "message": f"❌ Scraping failed: {str(e)}",
            "metadata": {"error": str(e), "type": type(e).__name__}
        }).execute()
    
    finally:
        SCRAPING_ACTIVE = False
        STOP_SCRAPING = False


@app.post("/api/stop-scraping")
async def stop_scraping():
    """إيقاف عملية السكريب الحالية"""
    global STOP_SCRAPING
    try:
        if not SCRAPING_ACTIVE:
            return {"status": "info", "message": "No scraping process is currently running"}
        
        STOP_SCRAPING = True
        logger.info("Stop signal sent to scraper")
        
        # Log to database
        supabase.table("scraping_logs").insert({
            "level": "warning",
            "message": "⛔ Scraping stopped by user",
            "metadata": {}
        }).execute()
        
        return {
            "status": "success",
            "message": "Scraping will stop after current job"
        }
    except Exception as e:
        logger.error(f"Error stopping scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scraping-status")
async def get_scraping_status():
    """التحقق من حالة السكريب"""
    global SCRAPING_ACTIVE
    return {
        "is_running": SCRAPING_ACTIVE,
        "can_stop": SCRAPING_ACTIVE
    }


@app.get("/api/schedule")
async def get_schedule():
    """جلب إعدادات Schedule من database"""
    try:
        result = supabase.table("settings").select("*").eq("key", "schedule").execute()
        
        if result.data and len(result.data) > 0:
            schedule_data = result.data[0]["value"]
            # إذا كان string، حوله إلى dict
            if isinstance(schedule_data, str):
                import json
                schedule_data = json.loads(schedule_data)
            
            # حساب next_run
            next_run = calculate_next_run(schedule_data)
            schedule_data["next_run"] = next_run
            
            return schedule_data
        else:
            # إرجاع الإعدادات الافتراضية
            default_schedule = {
                "enabled": False,
                "time": "10:00",
                "frequency": "daily",
                "max_jobs": 6,
                "sources": ["wuzzuf", "indeed"],
                "upload_to_blogger": False,
                "send_to_telegram": False,
                "send_to_whatsapp": False,
                "next_run": None
            }
            return default_schedule
    except Exception as e:
        logger.error(f"Error fetching schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/schedule")
async def save_schedule(schedule: ScheduleConfig):
    """حفظ إعدادات Schedule في database"""
    try:
        # تحويل إلى dict
        schedule_dict = schedule.dict()
        
        # حساب next_run
        next_run = calculate_next_run(schedule_dict)
        schedule_dict["next_run"] = next_run
        
        logger.info(f"💾 Saving schedule to database: {schedule_dict}")
        
        # Upsert في settings table
        result = supabase.table("settings").upsert({
            "key": "schedule",
            "value": schedule_dict
        }).execute()
        
        logger.info(f"✅ Schedule saved successfully: enabled={schedule.enabled}, time={schedule.time}, frequency={schedule.frequency}")
        logger.info(f"📊 Next run: {next_run}")
        logger.info(f"📊 Database result: {result.data}")
        
        # تحديث scheduler فوراً
        update_schedule_job()
        
        return {
            "status": "success",
            "message": "Schedule saved and updated successfully",
            "data": schedule_dict,
            "db_result": result.data
        }
    except Exception as e:
        logger.error(f"❌ Error saving schedule: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/history")
async def get_scraping_history(limit: int = 20):
    """Get detailed history of scraping runs"""
    try:
        # Get completion logs with metadata
        response = supabase.table("scraping_logs").select("*").eq("status", "completed").order("timestamp", desc=True).limit(limit).execute()
        
        # Also get logs with completion message
        completion_logs = supabase.table("scraping_logs").select("*").ilike("message", "%Scraping completed%").order("timestamp", desc=True).limit(limit).execute()
        
        history = []
        for log in completion_logs.data:
            metadata = log.get("metadata", {})
            
            history.append({
                "id": log.get("id"),
                "timestamp": log.get("timestamp"),
                "total_scraped": metadata.get("total_scraped", 0),
                "jobs_saved": metadata.get("jobs_saved", 0),
                "duplicates": metadata.get("duplicates_skipped", 0),
                "total_skipped": metadata.get("total_scraped", 0) - metadata.get("jobs_saved", 0),
                "skip_reasons": metadata.get("skip_reasons", {}),
                "keywords_found": metadata.get("keywords_found", {}),
                "sources": metadata.get("sources", {}),
                "duration": metadata.get("duration", 0)
            })
        
        logger.info(f"Found {len(history)} scraping history entries")
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting scraping history: {e}")
        return {"history": []}


@app.get("/api/analytics/summary")
async def get_analytics_summary(range: str = "today"):
    """Get scraping analytics summary"""
    try:
        from datetime import datetime, timedelta
        
        # Calculate date range
        now = datetime.now()
        if range == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif range == "week":
            start_date = now - timedelta(days=7)
        elif range == "month":
            start_date = now - timedelta(days=30)
        else:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info(f"Analytics query: range={range}, start_date={start_date.isoformat()}")
        
        # Get ALL jobs first (without date filter) to debug
        all_jobs_result = supabase.table("jobs").select("*").execute()
        all_jobs = all_jobs_result.data if all_jobs_result.data else []
        logger.info(f"Total jobs in database: {len(all_jobs)}")
        
        # Filter jobs by date if they have created_at field
        jobs = []
        for job in all_jobs:
            created_at = job.get("created_at")
            if created_at:
                try:
                    job_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if job_date >= start_date:
                        jobs.append(job)
                except:
                    # If date parsing fails, include the job anyway for today
                    if range == "today":
                        jobs.append(job)
            else:
                # No created_at, include for today only
                if range == "today":
                    jobs.append(job)
        
        logger.info(f"Jobs in selected range: {len(jobs)}")
        
        # Get logs to extract skip reasons and duplicates
        logs_result = supabase.table("scraping_logs").select("*").gte("timestamp", start_date.isoformat()).order("timestamp", desc=True).execute()
        logs = logs_result.data if logs_result.data else []
        logger.info(f"Logs found: {len(logs)}")
        
        # Calculate metrics
        total_saved = len(jobs)
        
        # Extract duplicates and skip reasons from logs
        duplicates_count = 0
        skip_reasons = {}
        total_scraped = total_saved
        last_run = None
        
        # Find the most recent completion log
        for log in logs:
            message = log.get("message", "")
            metadata = log.get("metadata", {})
            
            # Check for completion message
            if "Scraping completed" in message and not last_run:
                total_scraped = metadata.get("total_scraped", total_saved)
                duplicates_count = metadata.get("duplicates_skipped", 0)
                skip_reasons = metadata.get("skip_reasons", {})
                last_run = log.get("timestamp")
                logger.info(f"Found completion log: scraped={total_scraped}, duplicates={duplicates_count}")
                break
        
        # Keywords analysis
        keywords_found = {}
        
        for job in jobs:
            keyword = job.get("keyword", "")
            if keyword:
                keywords_found[keyword] = keywords_found.get(keyword, 0) + 1
        
        # Get all possible keywords and find which ones didn't return results
        # For now, we'll leave this empty unless we track searched keywords
        keywords_empty = []
        
        # Sources breakdown
        sources = {}
        for job in jobs:
            source = job.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_scraped": total_scraped,
            "jobs_saved": total_saved,
            "duplicates_skipped": duplicates_count,
            "keywords_found": keywords_found,
            "keywords_empty": keywords_empty,
            "skip_reasons": skip_reasons,
            "sources": sources,
            "last_run": last_run
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.on_event("startup")
async def startup_event():
    """تحميل schedule عند بدء الخادم"""
    logger.info("Loading schedule on startup...")
    update_schedule_job()
    logger.info("Schedule loaded")
