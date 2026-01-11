#!/usr/bin/env python3
"""Refresh Blogger API token"""

import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

try:
    print("Loading blogger token...")
    with open('blogger_token.pickle', 'rb') as token:
        creds = pickle.load(token)
    
    print(f"Token valid: {creds.valid}")
    print(f"Token expired: {creds.expired}")
    
    if creds.expired and creds.refresh_token:
        print("Refreshing token...")
        creds.refresh(Request())
        
        # Save the refreshed token
        with open('blogger_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        print("✅ Token refreshed successfully!")
        print(f"New token valid: {creds.valid}")
    else:
        print("Token is already valid or cannot be refreshed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
