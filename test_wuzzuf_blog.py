#!/usr/bin/env python3
"""Test blog post generation for Wuzzuf job with requirements"""

import os
import sys

# Add script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from scraper import generate_blog_post_html

# Sample Wuzzuf job with requirements from description
wuzzuf_job = {
    "title": "Software Tester",
    "company": "Tech Company",
    "location": "Maadi, Cairo, Egypt",
    "link": "https://wuzzuf.net/jobs/p/test123",
    "keyword": "Tester",
    "source": "wuzzuf",
    "description": "We are looking for a skilled Software Tester...",
    "requirements": [
        "🔹 Analyze user stories and system specifications to create detailed test plans",
        "🔹 Perform Functional, Regression, Integration, API, and UI/UX testing",
        "🔹 Develop automated test scripts using Playwright, Selenium, or Cypress",
        "🔹 Identify, document, and track software defects using Jira",
        "🔹 Provide developers with clear bug reports and reproduction steps"
    ],
    "skills": ["Testing", "Selenium", "Jira", "API Testing"]
}

# Generate HTML
print("=" * 60)
print("TESTING BLOG POST GENERATION")
print("=" * 60)
print(f"\nJob: {wuzzuf_job['title']}")
print(f"Keyword: {wuzzuf_job['keyword']}")
print(f"Requirements: {len(wuzzuf_job['requirements'])}")

html = generate_blog_post_html(wuzzuf_job)

# Save to test file
output_file = "test_wuzzuf_post.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n✅ Generated HTML saved to: {output_file}")
print(f"   File size: {len(html)} bytes")

# Check for key elements
checks = [
    ("Image section", '<div class="job-header-image">' in html),
    ("Title", wuzzuf_job['title'] in html),
    ("Technical Requirements section", '<h3>Technical Requirements</h3>' in html),
    ("Qualifications section", '<h3>Qualifications</h3>' in html),
    ("Job Details section", '<h3>Job Details</h3>' in html),
    ("Contact section", 'contact-section' in html),
    ("Apply button", 'Apply Now' in html),
    ("Has bullets", '<li>' in html),
]

print("\n" + "=" * 60)
print("STRUCTURE CHECKS")
print("=" * 60)

for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")

# Count sections
sections = html.count('<h3>')
bullet_items = html.count('<li>')

print(f"\n📊 Stats:")
print(f"   Sections (h3): {sections}")
print(f"   Bullet items: {bullet_items}")
print(f"   Total HTML size: {len(html):,} bytes")
