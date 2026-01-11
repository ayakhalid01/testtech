"""
Supabase integration helper for TechFlow scraper
Handles database operations for jobs, settings, and logs
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
from supabase import create_client, Client
from cryptography.fernet import Fernet
import json


class SupabaseDB:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(self.url, self.key)
        
        # Encryption for API keys
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            self.cipher = None
    
    def save_job(self, job_data: Dict) -> Optional[str]:
        """Save a job to database"""
        try:
            # Check if job already exists
            existing = self.client.table("jobs").select("id").eq("link", job_data["link"]).execute()
            
            if existing.data:
                print(f"   ⏭️  Job already in database: {job_data['title']}")
                return None
            
            # Prepare data
            data = {
                "title": job_data.get("title"),
                "company": job_data.get("company"),
                "location": job_data.get("location"),
                "salary": job_data.get("salary"),
                "requirements": json.dumps(job_data.get("requirements", [])),
                "skills": json.dumps(job_data.get("skills", [])),
                "description": job_data.get("description"),
                "link": job_data.get("link"),
                "source": job_data.get("source", "wuzzuf"),
                "slug": job_data.get("slug"),
                "posted_to_blogger": job_data.get("posted_to_blogger", False),
                "sent_to_telegram": job_data.get("sent_to_telegram", False),
                "sent_to_whatsapp": job_data.get("sent_to_whatsapp", False),
                "blogger_url": job_data.get("blog_link"),
                "html_content": job_data.get("html_content")
            }
            
            result = self.client.table("jobs").insert(data).execute()
            return result.data[0]["id"] if result.data else None
            
        except Exception as e:
            print(f"   ❌ Error saving job to database: {e}")
            return None
    
    def get_settings(self, key: str) -> Optional[Dict]:
        """Get settings from database"""
        try:
            result = self.client.table("settings").select("value").eq("key", key).execute()
            return result.data[0]["value"] if result.data else None
        except Exception as e:
            print(f"   ❌ Error fetching settings: {e}")
            return None
    
    def update_settings(self, key: str, value: Dict):
        """Update settings in database"""
        try:
            data = {"key": key, "value": value}
            self.client.table("settings").upsert(data).execute()
            return True
        except Exception as e:
            print(f"   ❌ Error updating settings: {e}")
            return False
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get decrypted API key for a service"""
        try:
            result = self.client.table("api_keys").select("key_encrypted").eq("service", service).eq("active", True).execute()
            
            if not result.data:
                return None
            
            encrypted_key = result.data[0]["key_encrypted"]
            
            if self.cipher:
                return self.cipher.decrypt(encrypted_key.encode()).decode()
            else:
                return encrypted_key
                
        except Exception as e:
            print(f"   ❌ Error fetching API key for {service}: {e}")
            return None
    
    def save_api_key(self, service: str, api_key: str):
        """Save encrypted API key"""
        try:
            if self.cipher:
                encrypted = self.cipher.encrypt(api_key.encode()).decode()
            else:
                encrypted = api_key
            
            data = {
                "service": service,
                "key_encrypted": encrypted,
                "active": True
            }
            
            self.client.table("api_keys").upsert(data).execute()
            return True
            
        except Exception as e:
            print(f"   ❌ Error saving API key: {e}")
            return False
    
    def log(self, level: str, message: str, metadata: Optional[Dict] = None):
        """Save log to database"""
        try:
            data = {
                "level": level,
                "message": message,
                "metadata": metadata or {}
            }
            self.client.table("scraping_logs").insert(data).execute()
        except Exception as e:
            print(f"   ❌ Error saving log: {e}")
    
    def is_job_scraped(self, job_link: str) -> bool:
        """Check if job already exists in database"""
        try:
            result = self.client.table("jobs").select("id").eq("link", job_link).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"   ❌ Error checking job: {e}")
            return False
    
    def get_blacklisted_companies(self) -> List[str]:
        """Get list of blacklisted company names"""
        try:
            result = self.client.table("blacklisted_companies").select("company_name").execute()
            return [item["company_name"].lower() for item in result.data]
        except Exception as e:
            print(f"   ❌ Error fetching blacklist: {e}")
            return []
    
    def update_job_status(self, job_id: str, **kwargs):
        """Update job posting status (blogger, telegram, whatsapp)"""
        try:
            self.client.table("jobs").update(kwargs).eq("id", job_id).execute()
            return True
        except Exception as e:
            print(f"   ❌ Error updating job status: {e}")
            return False
