import os
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from datetime import datetime

ASCII_CHARS = " .:-=+*#%@"

def remove_background(image_path):
    """Optional: isolates the subject before grayscale conversion.
    Requires: pip install rembg"""
    try:
        from rembg import remove
        with open(image_path, "rb") as f:
            input_bytes = f.read()
        output_bytes = remove(input_bytes)
        import io
        return Image.open(io.BytesIO(output_bytes)).convert("RGB")
    except ImportError:
        print("rembg not installed, skipping background removal (pip install rembg)")
        return Image.open(image_path)

def generate(image_path, new_width=200, strip_background=False):
    if strip_background:
        image = remove_background(image_path)
    else:
        image = Image.open(image_path)

    image = image.convert("L")

    # Contrast pipeline — stretches midtones, clips outlier pixels, sharpens edges
    image = ImageEnhance.Contrast(image).enhance(1.5)
    image = ImageOps.autocontrast(image, cutoff=2)
    image = image.filter(ImageFilter.SHARPEN)

    width, height = image.size
    new_height = int((height / width) * new_width * 0.5)  # 0.5 corrects terminal char aspect ratio
    image = image.resize((new_width, new_height), Image.LANCZOS)
    width, height = image.size

    ascii_chars = [
        ASCII_CHARS[int(pixel) * (len(ASCII_CHARS) - 1) // 255]
        for pixel in image.get_flattened_data()
    ]

    rows = ["".join(ascii_chars[i:i + width]) for i in range(0, len(ascii_chars), width)]
    return "\n".join(rows)

if __name__ == "__main__":
    image_path = os.path.expanduser(
        input("Enter the path your image is placed in or simply just drag and drop it here: ")
    )
    use_bg_removal = input("Remove background first? (y/N): ").strip().lower() == "y"

    result = generate(image_path, strip_background=use_bg_removal)
    timedata = datetime.now().strftime("%Y%m%d-%H%M%S")
    output = open(f"output-{timedata}.txt", "w")
    output.write(result)
    output.close()
    print(result)
