"""Create simple icon files for Chrome extension"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create simple icon with "CT" text
def create_icon(size, filename):
    # Create a new image with green background
    img = Image.new('RGB', (size, size), color='#10a37f')
    draw = ImageDraw.Draw(img)
    
    # Add white text "CT" (ChatGPT Trading)
    text = "CT"
    # Try to use a basic font, fallback to default if not available
    try:
        font_size = int(size * 0.4)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw white text
    draw.text((x, y), text, fill='white', font=font)
    
    # Save the image
    img.save(filename)
    print(f"Created {filename}")

# Create icons in different sizes
create_icon(16, 'icon16.png')
create_icon(48, 'icon48.png')
create_icon(128, 'icon128.png')

print("Icons created successfully!")