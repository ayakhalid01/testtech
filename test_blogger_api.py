#!/usr/bin/env python3
"""Test and authenticate with Blogger API"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Blogger API Configuration
BLOGGER_BLOG_ID = "6949685611084082756"
BLOGGER_SCOPES = ['https://www.googleapis.com/auth/blogger']
BLOGGER_CLIENT_SECRETS = "client_secrets.json"
BLOGGER_TOKEN_FILE = "blogger_token.pickle"

def authenticate_blogger():
    """Authenticate with Blogger API"""
    creds = None
    
    # Load existing token
    if os.path.exists(BLOGGER_TOKEN_FILE):
        print("Loading existing token...")
        with open(BLOGGER_TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
        print(f"Token valid: {creds.valid}")
        print(f"Token expired: {creds.expired}")
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("\nRefreshing expired token...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully!")
            except Exception as e:
                print(f"❌ Refresh failed: {e}")
                print("Getting new credentials...")
                creds = None
        
        if not creds:
            print("\nStarting OAuth2 flow...")
            print("A browser window will open for authentication.")
            print("Please select the account that owns the blog.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                BLOGGER_CLIENT_SECRETS, BLOGGER_SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ Authentication successful!")
        
        # Save the credentials
        with open(BLOGGER_TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print(f"✅ Token saved to {BLOGGER_TOKEN_FILE}")
    
    return build('blogger', 'v3', credentials=creds)

def test_blogger_connection(service):
    """Test connection by getting blog info"""
    try:
        print("\n" + "="*60)
        print("Testing Blogger API Connection...")
        print("="*60)
        
        blog = service.blogs().get(blogId=BLOGGER_BLOG_ID).execute()
        
        print(f"\n✅ Connected to blog: {blog['name']}")
        print(f"   URL: {blog['url']}")
        print(f"   Posts: {blog['posts']['totalItems']}")
        print(f"   Updated: {blog['updated']}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error connecting to blog: {e}")
        return False

def main():
    try:
        # Authenticate
        service = authenticate_blogger()
        
        # Test connection
        test_blogger_connection(service)
        
        print("\n" + "="*60)
        print("✅ Blogger API is ready to use!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
