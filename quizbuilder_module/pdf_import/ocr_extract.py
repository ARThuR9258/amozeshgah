from __future__ import annotations

import io
from pathlib import Path

import fitz

from .utils import clean_text, page_is_readable


def _sort_ocr_boxes(results: list) -> list[str]:
    """مرتب‌سازی بلوک‌های OCR از بالا به پایین، راست به چپ (تقریبی RTL)."""
    items = []
    for box, text, conf in results:
        if not text or float(conf) < 0.15:
            continue
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        items.append((min(ys), max(xs), text.strip()))
    if not items:
        return []
    items.sort(key=lambda t: (round(t[0] / 12), -t[1]))
    return [t[2] for t in items]


def ocr_page_easyocr(page: fitz.Page, reader, zoom: float = 2.0) -> str:
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_bytes = pix.tobytes('png')
    import numpy as np
    from PIL import Image

    img = Image.open(io.BytesIO(img_bytes))
    arr = np.array(img)
    results = reader.readtext(arr, detail=1, paragraph=False)
    lines = _sort_ocr_boxes(results)
    return '\n'.join(lines)


def extract_page_text(page: fitz.Page, reader=None, zoom: float = 2.0) -> str:
    direct = page.get_text('text')
    if page_is_readable(direct):
        return clean_text(direct)
    if reader is None:
        return clean_text(direct)
    return clean_text(ocr_page_easyocr(page, reader, zoom=zoom))


def extract_pdf_text(pdf_path: Path, reader=None, skip_pages: int = 0) -> list[str]:
    doc = fitz.open(pdf_path)
    pages: list[str] = []
    try:
        for i in range(doc.page_count):
            if i < skip_pages:
                pages.append('')
                continue
            pages.append(extract_page_text(doc[i], reader=reader))
    finally:
        doc.close()
    return pages


def extract_page_images(page: fitz.Page, out_dir: Path, page_num: int) -> list[str]:
    """ذخیره تصاویر صفحه؛ مسیر نسبی نسبت به out_dir.parent را برمی‌گرداند."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        try:
            base = page.parent.extract_image(xref)
        except Exception:
            continue
        ext = base.get('ext', 'png')
        if ext == 'jpeg':
            ext = 'jpg'
        name = f'page{page_num:03d}_img{img_index + 1:02d}.{ext}'
        rel = Path(out_dir.name) / name
        full = out_dir / name
        full.write_bytes(base['image'])
        paths.append(str(rel).replace('\\', '/'))
    return paths
