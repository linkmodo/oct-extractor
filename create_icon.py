from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a new image with a white background
    size = (256, 256)
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a blue circle
    circle_bbox = [10, 10, 246, 246]
    draw.ellipse(circle_bbox, fill=(70, 130, 180), outline=(0, 0, 0, 0))
    
    # Add text (OCT)
    try:
        # Try to load a font
        font = ImageFont.truetype("arial.ttf", 100)
    except IOError:
        # Fallback to default font if Arial is not available
        font = ImageFont.load_default()
    
    text = "OCT"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Calculate position to center the text
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2 - 10
    
    # Draw the text
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    # Save the image as ICO
    icon_path = os.path.join("assets", "icon.ico")
    img.save(icon_path, format='ICO', sizes=[(256, 256)])
    print(f"Icon created at: {icon_path}")

if __name__ == "__main__":
    if not os.path.exists("assets"):
        os.makedirs("assets")
    create_icon()
