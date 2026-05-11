# To run this script, please first execute `pip install -r requirements.txt`
import os
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from pillow_heif import register_heif_opener

# Initialize HEIF support for iPhone photos
register_heif_opener()

# --- PROJECT CONFIGURATION --- #
MODE = "BW"             
FORMAT = "120mm"        # OPTIONS: "35mm", "120mm", "4x5"
DPI = 1200              # 1200 DPI provides maximum smoothness for copy shop prints

# EXPOSURE & DENSITY TUNING (Balanced for Darkroom Exposure)
# DENSITY_FACTOR: 1.4 - 1.6 is usually the 'sweet spot' for laser-printed negatives.
# CONTRAST_FACTOR: 1.2 - 1.3 keeps the tonal range natural without clipping.
DENSITY_FACTOR = 1.5    
CONTRAST_FACTOR = 1.25  

MM_TO_INCH = 1 / 25.4
A4_SIZE = (int(210 * MM_TO_INCH * DPI), int(297 * MM_TO_INCH * DPI))

# --- DYNAMIC DIMENSIONS --- #
if FORMAT == "4x5":
    FRAME_SIZE = (int(101.6 * MM_TO_INCH * DPI), int(127 * MM_TO_INCH * DPI))
    FILM_HEIGHT = int(135 * MM_TO_INCH * DPI)
    PHOTOS_PER_STRIP = 1
elif FORMAT == "120mm":
    FRAME_SIZE = (int(56 * MM_TO_INCH * DPI), int(56 * MM_TO_INCH * DPI))
    FILM_HEIGHT = int(65 * MM_TO_INCH * DPI)
    PHOTOS_PER_STRIP = 3
else:
    FRAME_SIZE = (int(36 * MM_TO_INCH * DPI), int(24 * MM_TO_INCH * DPI)) 
    FILM_HEIGHT = int(38 * MM_TO_INCH * DPI)
    PHOTOS_PER_STRIP = 5

def apply_muth_curve(img_bw):
    """
    Applies a curve to optimize darkroom exposure times and density.
    """
    data = np.array(img_bw).astype(float) / 255.0
    
    # 1. Invert to Negative
    data = 1.0 - data 
    
    # 2. Gamma Adjustment (Density)
    # Lifts midtones and ensures highlights are 'thick' enough for paper exposure
    data = np.power(data, 1.0 / (1.2 * DENSITY_FACTOR))
    
    # 3. Contrast Expansion
    data = (data - 0.5) * CONTRAST_FACTOR + 0.5
    
    # 4. Normalization for Clear Film Base
    # Ensures the darkest shadows are perfectly transparent on the negative
    data = (data - data.min()) / (data.max() - data.min() + 1e-5)
    
    return Image.fromarray((np.clip(data, 0, 1) * 255).astype(np.uint8))

def process_image(img_path):
    with Image.open(img_path) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        
        # Upscale/Downscale to fill the frame exactly
        img = ImageOps.contain(img, FRAME_SIZE, Image.Resampling.LANCZOS)
        
        # White background becomes black toner (clear border on print)
        frame = Image.new("RGB", FRAME_SIZE, (255, 255, 255))
        offset = ((FRAME_SIZE[0] - img.width) // 2, (FRAME_SIZE[1] - img.height) // 2)
        frame.paste(img, offset)
        
        img_bw = ImageOps.grayscale(frame)
        neg = apply_muth_curve(img_bw)
        
        # Blur radius hides digital halftone patterns
        return neg.filter(ImageFilter.GaussianBlur(radius=0.7))

def create_negatives(image_paths, output_name="digital_stock_negatives.pdf"):
    pages = []
    current_idx = 0
    line_color = (180, 180, 180) 

    while current_idx < len(image_paths):
        canvas = Image.new("RGB", A4_SIZE, "white")
        draw = ImageDraw.Draw(canvas)
        y_cursor = int(20 * MM_TO_INCH * DPI)
        
        while y_cursor + FILM_HEIGHT < A4_SIZE[1] - 100 and current_idx < len(image_paths):
            x_start = int((A4_SIZE[0] - (PHOTOS_PER_STRIP * (FRAME_SIZE[0] + 40))) / 2)
            x_offset = x_start
            
            draw.line([(0, y_cursor), (A4_SIZE[0], y_cursor)], fill=line_color, width=3)
            draw.line([(0, y_cursor + FILM_HEIGHT), (A4_SIZE[0], y_cursor + FILM_HEIGHT)], fill=line_color, width=3)

            for _ in range(PHOTOS_PER_STRIP):
                if current_idx >= len(image_paths): break
                
                print(f"Processing: {image_paths[current_idx]}")
                neg = process_image(image_paths[current_idx])
                y_inner = y_cursor + (FILM_HEIGHT - FRAME_SIZE[1]) // 2
                
                canvas.paste(neg, (x_offset, y_inner))
                draw.rectangle([x_offset, y_inner, x_offset + FRAME_SIZE[0], y_inner + FRAME_SIZE[1]], outline=line_color)
                
                x_offset += FRAME_SIZE[0] + 40
                current_idx += 1
            
            y_cursor += FILM_HEIGHT + int(10 * MM_TO_INCH * DPI)
            
        pages.append(canvas)

    if pages:
        pages[0].save(output_name, save_all=True, append_images=pages[1:], resolution=float(DPI))
        print(f"\n✅ Success! Created {len(pages)} page(s) of Digital Stock negatives.")

if __name__ == "__main__":
    valid_extensions = ('.jpg', '.jpeg', '.png', '.heic', '.tiff')
    files = [f for f in os.listdir('.') if f.lower().endswith(valid_extensions)]
    
    if files:
        create_negatives(sorted(files))
    else:
        print("No compatible image files found.")