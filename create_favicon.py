from PIL import Image, ImageDraw

# Create a 32x32 image with a blue background
img = Image.new('RGB', (32, 32), color='#1a73e8')
draw = ImageDraw.Draw(img)

# Draw a simple 'S' for Steganography
draw.text((8, 4), 'S', fill='white', size=24)

# Save as ICO
img.save('static/favicon.ico', format='ICO')
