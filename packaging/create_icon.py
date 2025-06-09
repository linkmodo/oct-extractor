#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create a simple icon for the OCT Image Extraction application
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create a directory for the icon if it doesn't exist
resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
os.makedirs(resources_dir, exist_ok=True)

# Create a new image with a white background
img = Image.new('RGB', (256, 256), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

# Draw a blue rectangle
draw.rectangle([(20, 20), (236, 236)], outline=(0, 0, 255), width=4)

# Draw a representation of OCT layers
for i in range(10):
    y = 60 + i * 15
    draw.line([(40, y), (216, y + 5 * ((-1) ** i))], fill=(0, 100, 200), width=3)

# Add text
try:
    # Try to use a font if available
    font = ImageFont.truetype("arial.ttf", 24)
    draw.text((128, 30), "OCT", fill=(0, 0, 0), font=font, anchor="mm")
    draw.text((128, 220), "Extractor", fill=(0, 0, 0), font=font, anchor="mm")
except:
    # Fallback if font not available
    draw.text((100, 30), "OCT", fill=(0, 0, 0))
    draw.text((80, 220), "Extractor", fill=(0, 0, 0))

# Save the image
icon_path = os.path.join(resources_dir, "icon.png")
img.save(icon_path)

print(f"Icon created at: {icon_path}")

# For Windows, we would convert this to .ico format
# Since we're in a Linux environment, we'll just use the PNG
# In a real Windows environment, you would use a library like pillow to convert to .ico
ico_path = os.path.join(resources_dir, "icon.ico")
with open(ico_path, 'w') as f:
    f.write("# This is a placeholder for the .ico file\n")
    f.write("# In a real Windows environment, convert the PNG to ICO format\n")

print(f"Icon placeholder created at: {ico_path}")
