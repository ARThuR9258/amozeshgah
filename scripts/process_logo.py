"""Process logo: transparent icon + favicon."""
from PIL import Image
import os

BASE = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
SRC = os.path.join(BASE, 'logo.png')


def make_transparent(img, threshold=25):
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r < threshold and g < threshold and b < threshold:
                pixels[x, y] = (0, 0, 0, 0)


def main():
    src = Image.open(SRC).convert('RGBA')
    w, h = src.size

    # Icon: top emblem only (without wordmark text)
    icon_bottom = int(h * 0.50)
    icon = src.crop((int(w * 0.10), int(h * 0.02), int(w * 0.90), icon_bottom))
    make_transparent(icon)
    bbox = icon.getbbox()
    if bbox:
        icon = icon.crop(bbox)

    icon_path = os.path.join(BASE, 'logo-icon.png')
    icon.save(icon_path, 'PNG')
    print('icon:', icon.size)

    # Full logo with transparent background
    full = src.copy()
    make_transparent(full)
    bbox2 = full.getbbox()
    if bbox2:
        full = full.crop(bbox2)
    full_path = os.path.join(BASE, 'logo-full.png')
    full.save(full_path, 'PNG')
    print('full:', full.size)

    # Favicon from icon
    fav_size = 64
    scale = min(fav_size * 0.82 / icon.width, fav_size * 0.82 / icon.height)
    nw, nh = int(icon.width * scale), int(icon.height * scale)
    resized = icon.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (fav_size, fav_size), (15, 18, 25, 255))
    ox, oy = (fav_size - nw) // 2, (fav_size - nh) // 2
    canvas.paste(resized, (ox, oy), resized)
    canvas.save(os.path.join(BASE, 'favicon.png'), 'PNG')
    print('favicon done')


if __name__ == '__main__':
    main()
