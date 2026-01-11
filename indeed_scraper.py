"""
Indeed Job Scraper
Scrapes jobs from Indeed Egypt with Selenium (to bypass Cloudflare)
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# Search keywords (same as Wuzzuf)
SEARCH_KEYWORDS = [
    "Flutter", "Backend", "Frontend", "Data Analyst", "Data Analysis",
    "QA", "Quality Assurance", "Quality Control", "Analyst"
]

def init_selenium():
    """Initialize Selenium with Chrome"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def job_title_matches_keywords(title):
    """Check if job title matches any search keyword"""
    title_lower = title.lower()
    
    # Keyword variations
    keyword_variations = {
        "qa": ["quality assurance", "quality control", "qa engineer", "qa specialist"],
        "analyst": ["data analyst", "business analyst", "financial analyst", "system analyst"],
        "backend": ["backend developer", "backend engineer", "server side"],
        "frontend": ["frontend developer", "frontend engineer", "ui developer"],
        "flutter": ["flutter developer", "flutter engineer", "mobile developer"],
    }
    
    for keyword in SEARCH_KEYWORDS:
        keyword_lower = keyword.lower()
        
        # Direct match
        if keyword_lower in title_lower:
            return True
        
        # Check variations
        if keyword_lower in keyword_variations:
            for variation in keyword_variations[keyword_lower]:
                if variation in title_lower:
                    return True
    
    return False

def is_recent_job(date_text):
    """Check if job was posted within last 24 hours"""
    if not date_text:
        return False
    
    date_lower = date_text.lower()
    
    # Indeed date formats
    recent_indicators = [
        "just posted", "today", "1 day ago", 
        "hours ago", "hour ago", "minutes ago"
    ]
    
    for indicator in recent_indicators:
        if indicator in date_lower:
            return True
    
    return False

def scrape_indeed_jobs(max_jobs=6):
    """
    Scrape jobs from Indeed Egypt
    Returns list of job dictionaries
    """
    print("\n🔍 Fetching jobs from Indeed Egypt...")
    
    driver = None
    jobs = []
    
    try:
        driver = init_selenium()
        
        # Search queries (same as Wuzzuf)
        search_queries = ["IT", "Software", "Developer"]
        
        for query in search_queries:
            if len(jobs) >= max_jobs:
                break
            
            print(f"\nSearching Indeed for: {query}...")
            
            # Indeed Egypt search URL (fromage=1 means last 24 hours)
            url = f"https://eg.indeed.com/jobs?q={query}&l=Egypt&fromage=1"
            
            driver.get(url)
            time.sleep(3)  # Wait for page load
            
            # Get page source
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find job cards
            # Indeed uses various card structures, let's try multiple selectors
            job_cards = soup.find_all('div', class_=lambda x: x and 'job_seen_beacon' in x)
            
            if not job_cards:
                # Try alternative selector
                job_cards = soup.find_all('div', attrs={'data-jk': True})
            
            print(f"Found {len(job_cards)} potential jobs...")
            
            for card in job_cards:
                if len(jobs) >= max_jobs:
                    break
                
                try:
                    # Extract job title
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
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                    
                    # Extract location
                    location_elem = card.find('div', attrs={'data-testid': 'text-location'})
                    location = location_elem.get_text(strip=True) if location_elem else "Egypt"
                    
                    # Filter Egypt only
                    if "Egypt" not in location:
                        print(f"   ⏭️  Skipped (not Egypt): {title} - {location}")
                        continue
                    
                    # Extract date
                    date_elem = card.find('span', attrs={'data-testid': 'myJobsStateDate'})
                    if not date_elem:
                        date_elem = card.find('span', class_=lambda x: x and 'date' in x.lower() if x else False)
                    
                    date_text = date_elem.get_text(strip=True) if date_elem else ""
                    
                    # Filter by time (24 hours)
                    if not is_recent_job(date_text):
                        print(f"   ⏭️  Skipped (not recent): {title} - {date_text}")
                        continue
                    
                    # Extract job link
                    link_elem = card.find('a', attrs={'data-jk': True})
                    if link_elem and link_elem.get('href'):
                        job_id = link_elem.get('data-jk')
                        job_link = f"https://eg.indeed.com/viewjob?jk={job_id}"
                    else:
                        job_link = "https://eg.indeed.com"
                    
                    # Extract salary (if available)
                    salary_elem = card.find('div', class_=lambda x: x and 'salary' in x.lower() if x else False)
                    salary = salary_elem.get_text(strip=True) if salary_elem else "Not specified"
                    
                    # Extract snippet/description
                    snippet_elem = card.find('div', class_='job-snippet')
                    if not snippet_elem:
                        snippet_elem = card.find('div', attrs={'data-testid': 'job-snippet'})
                    
                    description = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    print(f"   ✅ Recent job: {title} ({company})")
                    
                    job_data = {
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary": salary,
                        "description": description,
                        "link": job_link,
                        "date": date_text,
                        "source": "Indeed Egypt"
                    }
                    
                    jobs.append(job_data)
                    
                except Exception as e:
                    print(f"   ⚠️  Error parsing job card: {str(e)}")
                    continue
        
        print(f"\n✅ Scraped {len(jobs)} jobs from Indeed")
        return jobs
        
    except Exception as e:
        print(f"❌ Error scraping Indeed: {str(e)}")
        return []
    
    finally:
        if driver:
            driver.quit()

def format_indeed_job_message(job):
    """Format Indeed job for messaging"""
    message = f"""
🎯 *{job['title']}*

🏢 *Company:* {job['company']}
📍 *Location:* {job['location']}
💰 *Salary:* {job['salary']}
📅 *Posted:* {job['date']}

📝 *Description:*
{job['description'][:300]}...

🔗 *Apply:* {job['link']}

🌐 *Source:* Indeed Egypt
    """.strip()
    
    return message

# Test the scraper
if __name__ == "__main__":
    jobs = scrape_indeed_jobs(max_jobs=3)
    
    print("\n" + "="*50)
    print("INDEED JOBS")
    print("="*50)
    
    for job in jobs:
        print(format_indeed_job_message(job))
        print("\n" + "-"*50 + "\n")
