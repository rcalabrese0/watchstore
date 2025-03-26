from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder(filename, text, size=(400, 400), bg_color=(200, 200, 200), text_color=(50, 50, 50)):
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw text in center
    text_bbox = draw.textbbox((0, 0), text)
    text_position = ((size[0] - text_bbox[2]) / 2, (size[1] - text_bbox[3]) / 2)
    draw.text(text_position, text, fill=text_color)
    
    img.save(filename)

# Create placeholder images
images = [
    ('gshock.jpg', 'Casio G-Shock\nDW5600'),
    ('runner.jpg', 'X-Time Runner\nPro'),
    ('pop.jpg', 'Lemon Pop\nColor'),
    ('edifice.jpg', 'Casio Edifice\nEF-539'),
]

for filename, text in images:
    create_placeholder(filename, text)
