"""Alternative: Auto-upload using Blogger's Import API or direct post"""
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
import csv

# Reuse existing scraper code but skip API posting
# Import will be done via XML/CSV

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HISTORY_FILE = "history.json"
OUTPUT_FILE = "today_jobs.txt"
BLOG_OUTPUT_FILE = "blog_posts.html"
WHATSAPP_CHANNEL_LINK = "https://bit.ly/3V7nEN5"
BLOG_DOMAIN = "https://careerjobst01.blogspot.com"
BLOGGER_BLOG_ID = "6949685611084082756"

TARGET_JOBS_COUNT = 6
SEARCH_KEYWORDS = [
    "Flutter", "Backend", "Frontend", "Data Analyst", 
    "Data Engineer", "Data Scientist", "UI/UX", "Tester"
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_history(history_set):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(history_set), f, indent=4)

def create_slug(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug[:100]  # Limit length

def generate_blog_post_html(job):
    try:
        from string import Template
        with open("templates/job_post.html", "r", encoding="utf-8") as f:
            template_str = f.read()
        
        template = Template(template_str)
        reqs_html = "\n".join([f"<li>{r.replace('🔹 ', '')}</li>" for r in job['requirements']])
        
        html_content = template.substitute(
            job_title=job['title'],
            location=job['location'],
            salary=job['salary'],
            requirements_list=reqs_html,
            apply_link=job['link'],
            whatsapp_link=WHATSAPP_CHANNEL_LINK
        )
        return html_content
    except Exception as e:
        print(f"Error generating blog HTML: {e}")
        return ""

def get_job_details(job_url):
    try:
        response = requests.get(job_url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        salary = "Confidential"
        requirements = []
        req_section = soup.find("div", class_="css-1t5f0fr")
        if not req_section:
             h2 = soup.find("h2", string="Job Requirements")
             if h2:
                 req_section = h2.find_next_sibling("div")
        
        if req_section:
            ul = req_section.find("ul")
            if ul:
                for li in ul.find_all("li"):
                    requirements.append(f"🔹 {li.get_text(strip=True)}")
            else:
                requirements.append(f"🔹 {req_section.get_text(strip=True)[:200]}...")

        return {
            "salary": salary,
            "requirements": requirements[:5]
        }
    except Exception as e:
        print(f"Error fetching details for {job_url}: {e}")
        return None

def format_message(job, blog_link):
    reqs_text = "\n".join(job['requirements'])
    return f"""
*{job['title']}*

📍 *Location:* {job['location']}
💰 *Salary:* {job['salary']}

*Requirements:*
{reqs_text}

🔗 *Apply Here:* {blog_link}

⚡ WhatsApp Channel: {WHATSAPP_CHANNEL_LINK}
"""

def get_search_url(keyword):
    encoded_keyword = quote(keyword)
    return f"https://wuzzuf.net/search/jobs/?q={encoded_keyword}&a=hpb&filters%5Bcareer_level%5D%5B0%5D=Entry%20Level&filters%5Bcareer_level%5D%5B1%5D=Student&filters%5Bpost_date%5D%5B0%5D=within_24_hours"

def scrape_jobs():
    history = load_history()
    new_jobs = []
    blog_posts_html = []
    
    keywords = list(SEARCH_KEYWORDS)
    random.shuffle(keywords)
    
    print(f"Searching for jobs in categories: {', '.join(keywords)}")
    print("\n⚠️  Note: Posts will be saved for manual import to Blogger")
    print("   Files generated: blogger_posts.xml and blog_posts.html\n")
    
    for keyword in keywords:
        if len(new_jobs) >= TARGET_JOBS_COUNT:
            break
            
        url = get_search_url(keyword)
        print(f"Fetching jobs for: {keyword}...")
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            job_cards = soup.find_all("div", class_="css-pkv5jc")
            print(f"Found {len(job_cards)} potential jobs for {keyword}...")

            found_for_keyword = False
            for card in job_cards:
                if len(new_jobs) >= TARGET_JOBS_COUNT:
                    break
                if found_for_keyword:
                    break
                    
                try:
                    title_tag = card.find("h2", class_="css-193uk2c")
                    if not title_tag: 
                        title_tag = card.find("h2")
                    
                    if not title_tag: continue
                    
                    link_tag = title_tag.find("a")
                    link = link_tag['href']
                    if not link.startswith("http"):
                        link = "https://wuzzuf.net" + link
                    
                    if link in history:
                        continue
                        
                    title = link_tag.get_text(strip=True)
                    location_span = card.find("span", class_="css-16x61xq")
                    location = location_span.get_text(strip=True) if location_span else "Egypt"
                    
                    print(f"Scraping details for: {title}")
                    details = get_job_details(link)
                    
                    if details:
                        slug = create_slug(title)
                        
                        job_data = {
                            "title": title,
                            "location": location,
                            "link": link,
                            "salary": details.get("salary", "Confidential"),
                            "requirements": details.get("requirements", []),
                            "slug": slug
                        }
                        
                        blog_html = generate_blog_post_html(job_data)
                        blog_posts_html.append(f"<!-- {slug} -->\n{blog_html}\n<hr>\n")
                        
                        job_data['blog_link'] = f"{BLOG_DOMAIN}/{time.strftime('%Y/%m')}/{slug}.html"
                        
                        new_jobs.append(job_data)
                        history.add(link)
                        found_for_keyword = True
                        print(f"✅ Saved: {title}")
                        time.sleep(1) 
                        
                except Exception as e:
                    print(f"Error parsing card: {e}")
                    continue
        except Exception as e:
            print(f"Error fetching {keyword}: {e}")
            continue

    save_history(history)
    
    # Output messages to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for job in new_jobs:
            msg = format_message(job, job['blog_link'])
            f.write(msg + "\n" + "-"*20 + "\n")
            
    # Output blog posts to file
    with open(BLOG_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(blog_posts_html))

    # Output Blogger XML for import
    blogger_xml_file = "blogger_posts.xml"
    with open(blogger_xml_file, "w", encoding="utf-8") as f:
        f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        f.write("<feed xmlns='http://www.w3.org/2005/Atom' xmlns:openSearch='http://a9.com/-/spec/opensearchrss/1.0/' xmlns:georss='http://www.georss.org/georss' xmlns:gd='http://schemas.google.com/g/2005' xmlns:thr='http://purl.org/syndication/thread/1.0'>\n")
        f.write(f"<id>tag:blogger.com,1999:blog-{BLOGGER_BLOG_ID}.archive</id>\n")
        f.write(f"<updated>{time.strftime('%Y-%m-%dT%H:%M:%S.000+00:00')}</updated>\n")
        f.write(f"<title type='text'>Job Listings Import</title>\n")
        f.write(f"<generator version='7.00' uri='http://www.blogger.com'>Blogger</generator>\n")
        
        for i, job in enumerate(new_jobs):
            html_content = generate_blog_post_html(job)
            post_id = int(time.time() * 1000) + i
            
            f.write("<entry>\n")
            f.write(f"<id>tag:blogger.com,1999:blog-{BLOGGER_BLOG_ID}.post-{post_id}</id>\n")
            f.write(f"<published>{time.strftime('%Y-%m-%dT%H:%M:%S.000+00:00')}</published>\n")
            f.write(f"<updated>{time.strftime('%Y-%m-%dT%H:%M:%S.000+00:00')}</updated>\n")
            f.write(f"<category scheme='http://www.blogger.com/atom/ns#' term='Jobs'/>\n")
            f.write(f"<title type='text'>{job['title']}</title>\n")
            # Escape HTML entities properly
            escaped_content = html_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            f.write(f"<content type='html'>{escaped_content}</content>\n")
            f.write(f"<link rel='alternate' type='text/html' href='{job['blog_link']}' title='{job['title']}'/>\n")
            f.write(f"<author><name>Career Team</name></author>\n")
            f.write("<app:control xmlns:app='http://purl.org/atom/app#'>\n")
            f.write("<app:draft>no</app:draft>\n")
            f.write("</app:control>\n")
            f.write("</entry>\n")
            
        f.write("</feed>\n")

    print(f"\n{'='*60}")
    print(f"✅ Saved {len(new_jobs)} new jobs")
    print(f"{'='*60}")
    print(f"\n📁 Files created:")
    print(f"   • {OUTPUT_FILE} - WhatsApp messages")
    print(f"   • {BLOG_OUTPUT_FILE} - HTML for manual posting")
    print(f"   • {blogger_xml_file} - Blogger XML import file")
    print(f"\n📤 To import to Blogger:")
    print(f"   1. Go to Blogger → Settings → Other")
    print(f"   2. Click 'Import content'")
    print(f"   3. Upload: {blogger_xml_file}")
    print(f"   4. Posts will be published automatically!")

if __name__ == "__main__":
    scrape_jobs()
