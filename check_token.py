"""Check token permissions"""
import pickle
import json

with open('blogger_token.pickle', 'rb') as f:
    creds = pickle.load(f)
    
print("Current Token Info:")
print("=" * 60)
print(f"Valid: {creds.valid}")
print(f"Expired: {creds.expired}")
print(f"Scopes: {creds.scopes}")
print(f"Token: {creds.token[:50]}..." if creds.token else "No token")
print(f"Has refresh token: {bool(creds.refresh_token)}")

# Check if the token has the right scope
if creds.scopes:
    if 'https://www.googleapis.com/auth/blogger' in creds.scopes:
        print("\n✅ Token has correct Blogger scope")
    else:
        print("\n❌ Token missing Blogger scope!")
        print(f"   Current scopes: {creds.scopes}")
else:
    print("\n⚠️  No scopes in token")
