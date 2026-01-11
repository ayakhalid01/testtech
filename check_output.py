import json

# Read today_jobs.txt to see if requirements are there
with open('today_jobs.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    
print("Content from today_jobs.txt:")
print(content)
print("\n" + "="*80 + "\n")

# Check if there's a blog_posts.html
try:
    with open('blog_posts.html', 'r', encoding='utf-8') as f:
        blog_content = f.read()
    print(f"blog_posts.html length: {len(blog_content)} chars")
    print("First 500 chars:")
    print(blog_content[:500])
except Exception as e:
    print(f"Error reading blog_posts.html: {e}")
