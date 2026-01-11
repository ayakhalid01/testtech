"""
Generate sample placeholder images for testing
"""
import os
from PIL import Image, ImageDraw, ImageFont

PHOTOS_DIR = "Photos By Keywords"

# Common keywords (update with your actual SEARCH_KEYWORDS)
KEYWORDS = [
    "data",
    "software engineer",
    "python",
    "react",
    "java",
    "flutter",
    "developer",
    "analyst",
    "engineer"
]

def create_sample_image(keyword, width=1024, height=768):
    """Create a simple placeholder image for a keyword"""
    
    # Create image with gradient background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background (green theme)
    for y in range(height):
        r = int(45 + (y / height) * 20)
        g = int(151 - (y / height) * 30)
        b = int(99 - (y / height) * 20)
        draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
    
    # Add white overlay for text area
    overlay_height = 300
    overlay_y = (height - overlay_height) // 2
    draw.rectangle(
        [(50, overlay_y), (width-50, overlay_y + overlay_height)],
        fill=(255, 255, 255, 200),
        outline=(45, 151, 99),
        width=5
    )
    
    # Add text
    try:
        # Try to use a nice font
        font_large = ImageFont.truetype("arial.ttf", 80)
        font_small = ImageFont.truetype("arial.ttf", 40)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw keyword
    keyword_text = keyword.upper()
    text_bbox = draw.textbbox((0, 0), keyword_text, font=font_large)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    text_y = overlay_y + 60
    
    draw.text((text_x, text_y), keyword_text, fill=(45, 151, 99), font=font_large)
    
    # Draw subtitle
    subtitle = "Jobs & Opportunities"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = text_y + 100
    
    draw.text((subtitle_x, subtitle_y), subtitle, fill=(100, 100, 100), font=font_small)
    
    # Add decorative elements
    # Top left corner decoration
    draw.arc([(20, 20), (120, 120)], 0, 90, fill=(45, 151, 99), width=5)
    
    # Bottom right corner decoration  
    draw.arc([(width-120, height-120), (width-20, height-20)], 180, 270, fill=(45, 151, 99), width=5)
    
    return img

def main():
    print("="*60)
    print("Sample Image Generator")
    print("="*60 + "\n")
    
    # Create directory if it doesn't exist
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)
        print(f"✅ Created directory: {PHOTOS_DIR}\n")
    
    print(f"Generating sample images for {len(KEYWORDS)} keywords...\n")
    
    for keyword in KEYWORDS:
        # Normalize filename
        filename = keyword.lower().replace(" ", "_") + ".png"
        filepath = os.path.join(PHOTOS_DIR, filename)
        
        # Check if already exists
        if os.path.exists(filepath):
            print(f"⏭️  Skipped '{keyword}' (already exists)")
            continue
        
        try:
            # Generate image
            img = create_sample_image(keyword)
            
            # Save image
            img.save(filepath, 'PNG', optimize=True)
            file_size = os.path.getsize(filepath) / 1024  # KB
            
            print(f"✅ Created '{filename}' ({file_size:.1f} KB)")
            
        except Exception as e:
            print(f"❌ Failed to create '{keyword}': {e}")
    
    print("\n" + "="*60)
    print(f"✅ Done! Images saved to: {os.path.abspath(PHOTOS_DIR)}")
    print("="*60 + "\n")
    print("Next steps:")
    print("1. Check the generated images")
    print("2. Replace them with your own professional images if needed")
    print("3. Run: python test_image_post.py")
    print("4. Test scraping with: python scraper.py --upload")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTip: Make sure PIL/Pillow is installed:")
        print("     pip install Pillow")
