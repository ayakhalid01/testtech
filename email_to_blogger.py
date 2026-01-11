"""
AUTO-UPLOAD TO BLOGGER VIA EMAIL

Blogger has a secret email address that you can send posts to.
This bypasses the API permission issues completely!

Setup:
1. Go to Blogger → Settings → Email
2. Find your secret posting email address
3. It looks like: username.secret@blogger.com
4. Add it to the EMAIL_TO_BLOGGER variable below
5. Configure your Gmail SMTP credentials

Then this script will automatically email posts to Blogger!
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

# ============= CONFIGURATION =============
# Your Gmail credentials for sending
GMAIL_USER = "your_email@gmail.com"  # Your Gmail address
GMAIL_APP_PASSWORD = "your_app_password"  # Gmail App Password (not regular password)

# Your Blogger email posting address
# Find it at: Blogger → Settings → Email → "Posting options"
EMAIL_TO_BLOGGER = "username.secret@blogger.com"  # UPDATE THIS!

# =========================================

def send_post_to_blogger(title, html_content):
    """Send a post to Blogger via email"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = title
        msg['From'] = GMAIL_USER
        msg['To'] = EMAIL_TO_BLOGGER
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Send via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Emailed to Blogger: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Email failed for {title}: {e}")
        return False

def test_email_posting():
    """Test if email posting works"""
    test_html = """
    <h2>Test Post</h2>
    <p>This is a test post sent via email.</p>
    <p>If you see this in Blogger, email posting works! 🎉</p>
    """
    
    print("Testing email posting to Blogger...")
    print(f"Sending from: {GMAIL_USER}")
    print(f"Sending to: {EMAIL_TO_BLOGGER}")
    
    if EMAIL_TO_BLOGGER == "username.secret@blogger.com":
        print("\n⚠️  ERROR: You need to set EMAIL_TO_BLOGGER!")
        print("   1. Go to Blogger → Settings → Email")
        print("   2. Copy your secret posting email")
        print("   3. Update EMAIL_TO_BLOGGER in this script")
        return False
    
    if GMAIL_APP_PASSWORD == "your_app_password":
        print("\n⚠️  ERROR: You need to set GMAIL_APP_PASSWORD!")
        print("   1. Go to https://myaccount.google.com/apppasswords")
        print("   2. Generate an App Password")
        print("   3. Update GMAIL_APP_PASSWORD in this script")
        return False
    
    return send_post_to_blogger("🧪 Test Post - Delete Me", test_html)

if __name__ == "__main__":
    print("=" * 60)
    print("BLOGGER EMAIL POSTING TEST")
    print("=" * 60)
    print()
    
    if test_email_posting():
        print("\n✅ SUCCESS! Check your Blogger dashboard for the test post.")
        print("   Now update scraper.py to use email posting for automation!")
    else:
        print("\n❌ Email posting failed. Check configuration above.")
