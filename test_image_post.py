"""
Test script to verify image integration in blog posts
"""
import os
import sys

# Add scraper to path
sys.path.insert(0, os.path.dirname(__file__))

from scraper import get_keyword_image, generate_blog_post_html

def test_keyword_image():
    """Test getting keyword image"""
    print("Testing keyword image function...\n")
    
    # Test with a keyword (replace with your actual keyword)
    test_keyword = "data"
    
    print(f"Looking for image for keyword: '{test_keyword}'")
    image_html = get_keyword_image(test_keyword)
    
    if image_html:
        print(f"✅ Image found and converted!")
        print(f"HTML length: {len(image_html)} characters")
        print("\nFirst 200 characters:")
        print(image_html[:200])
    else:
        print(f"❌ No image found for '{test_keyword}'")
        print(f"\nTip: Add an image file named '{test_keyword}.png' or '{test_keyword}.jpg'")
        print(f"     to: D:\\TechFlow\\Photos By Keywords\\")

def test_blog_post():
    """Test complete blog post generation with image"""
    print("\n" + "="*60)
    print("Testing complete blog post generation...\n")
    
    # Sample job data
    sample_job = {
        'title': 'Senior Data Analyst',
        'company': 'TechCorp',
        'location': 'Cairo, Egypt',
        'description': 'We are looking for an experienced Data Analyst to join our team.',
        'link': 'https://example.com/job/123',
        'keyword': 'data',  # This should match your image filename
        'requirements': [
            'Bachelor degree in Computer Science',
            '3+ years of experience in data analysis',
            'Strong SQL skills',
            'Python proficiency',
            'Experience with visualization tools'
        ]
    }
    
    html = generate_blog_post_html(sample_job)
    
    if html:
        print("✅ Blog post HTML generated successfully!")
        print(f"Total HTML length: {len(html)} characters")
        
        # Save to test file
        test_file = "test_blog_post_output.html"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n📄 Full HTML saved to: {test_file}")
        print("   Open this file in a browser to preview!")
        
        # Check if image is included
        if '<img' in html and 'data:image' in html:
            print("\n✅ Image is embedded in the HTML!")
        else:
            print("\n⚠️  No embedded image found in HTML")
            print("   Make sure you have an image file for the keyword")
    else:
        print("❌ Failed to generate blog post HTML")

if __name__ == "__main__":
    print("="*60)
    print("Blog Post Image Integration Test")
    print("="*60 + "\n")
    
    test_keyword_image()
    test_blog_post()
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)
