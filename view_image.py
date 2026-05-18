from PIL import Image
import sys

def image_to_ascii(image_path, width=80):
    img = Image.open(image_path).convert('L')
    aspect_ratio = img.height / img.width
    new_height = int(aspect_ratio * width * 0.5)
    img = img.resize((width, new_height))
    
    pixels = img.getdata()
    chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
    
    ascii_str = ""
    for pixel in pixels:
        ascii_str += chars[pixel // 25]
    
    ascii_str_len = len(ascii_str)
    ascii_img = ""
    for i in range(0, ascii_str_len, width):
        ascii_img += ascii_str[i:i+width] + "\n"
        
    print(ascii_img)

image_to_ascii('Lab4/page_0_img_5.png', 100)
