from io import BytesIO
from PIL import Image, ImageOps
import qrcode


def normalize_image_to_orientation(file_bytes: bytes, target: str = 'portrait') -> bytes:
    """
    Auto-rotate using EXIF, then letterbox to full-screen canvas matching target orientation.
    target: 'portrait' or 'landscape'
    Returns processed image bytes (PNG).
    """
    with Image.open(BytesIO(file_bytes)) as im:
        # auto-orient
        im = ImageOps.exif_transpose(im)

        # decide canvas size (1080x1920 for portrait; 1920x1080 for landscape)
        if target == 'landscape':
            canvas_w, canvas_h = 1920, 1080
        else:
            canvas_w, canvas_h = 1080, 1920

        # fit image within canvas preserving aspect ratio
        im = ImageOps.contain(im, (canvas_w, canvas_h))

        # create black canvas and paste centered
        canvas = Image.new('RGB', (canvas_w, canvas_h), (0, 0, 0))
        x = (canvas_w - im.width) // 2
        y = (canvas_h - im.height) // 2
        canvas.paste(im, (x, y))

        out = BytesIO()
        canvas.save(out, format='PNG', optimize=True)
        return out.getvalue()


def generate_activation_qr(url: str) -> bytes:
    """
    Generate a PNG QR code for the provided URL.
    """
    img = qrcode.make(url)
    out = BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()
