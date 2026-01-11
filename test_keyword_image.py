#!/usr/bin/env python3
"""Test keyword image matching with case-insensitive search"""

import os
import sys

# Add script directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_DIR = os.path.join(SCRIPT_DIR, "Photos By Keywords")

def test_keyword_matching(keyword):
    """Test if keyword matches any image file"""
    keyword_lower = keyword.lower().strip()
    extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    
    print(f"\n🔍 Testing keyword: '{keyword}'")
    print(f"   Normalized: '{keyword_lower}'")
    
    # Search all files in directory (case-insensitive)
    matching_file = None
    partial_match = None
    
    for filename in os.listdir(PHOTOS_DIR):
        name_without_ext, ext = os.path.splitext(filename)
        
        # Skip if not an image file
        if ext.lower() not in extensions:
            continue
        
        # Compare case-insensitive, allowing both spaces and underscores
        name_lower = name_without_ext.lower().replace("_", " ")
        keyword_compare = keyword_lower.replace("_", " ")
        
        # Exact match
        if name_lower == keyword_compare:
            matching_file = filename
            print(f"   ✅ EXACT MATCH: {filename}")
            break
        
        # Partial match (e.g., "Data Analyst" matches "analyst.png")
        if not partial_match:
            if keyword_compare in name_lower or name_lower in keyword_compare:
                if len(name_lower) >= 3:
                    partial_match = filename
            # Special case: check if words are similar (e.g., "tester" and "testing")
            elif keyword_compare.rstrip('er').rstrip('ing') == name_lower.rstrip('er').rstrip('ing'):
                if len(name_lower) >= 3:
                    partial_match = filename
    
    # Use exact match if found, otherwise use partial match
    if matching_file:
        return matching_file
    elif partial_match:
        print(f"   🔍 PARTIAL MATCH: {partial_match}")
        return partial_match
    else:
        print(f"   ❌ NO MATCH")
        return None

# Test all keywords from scraper
test_keywords = [
    "IT",
    "Cyber Security", 
    "Flutter",
    "Backend",
    "Frontend",
    "Data Analyst",
    "Data Engineer",
    "Data Scientist",
    "Tester",
    "DevOps",
    "Full Stack",
    "Software Engineer",
    "Python",
    "Java",
    "React",
    ".NET",
    "PHP",
    "Laravel",
    "Cloud Engineer",
    "developer",
    "engineer",
    "analyst",
    "Testing"
]

print("=" * 60)
print("KEYWORD IMAGE MATCHING TEST")
print("=" * 60)

matches = 0
no_matches = 0

for keyword in test_keywords:
    result = test_keyword_matching(keyword)
    if result:
        matches += 1
    else:
        no_matches += 1

print("\n" + "=" * 60)
print(f"SUMMARY: {matches} matches, {no_matches} no matches")
print("=" * 60)

# List available images
print("\n📁 Available images in Photos By Keywords:")
for filename in sorted(os.listdir(PHOTOS_DIR)):
    if os.path.splitext(filename)[1].lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        print(f"   - {filename}")
