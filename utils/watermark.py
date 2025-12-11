from typing import Tuple
from PIL import Image, ImageDraw, ImageFont


def _parse_color(color: str) -> Tuple[int, int, int]:
    color = color.strip()
    if color.startswith("#"):
        color = color[1:]
    if len(color) == 3:
        color = "".join(c * 2 for c in color)
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return r, g, b


def _pos_xy(w: int, h: int, tw: int, th: int, position: str, margin: int):
    if position == "top_left":
        return margin, margin
    if position == "top_right":
        return w - tw - margin, margin
    if position == "bottom_left":
        return margin, h - th - margin
    if position == "center":
        return (w - tw) // 2, (h - th) // 2
    return w - tw - margin, h - th - margin


def add_text_watermark(image_path: str, text: str, output_path: str, position: str = "bottom_right", font_size: int = 32, color: str = "#ffffff", opacity: float = 0.6, margin: int = 16):
    base = Image.open(image_path).convert("RGBA")
    layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(layer)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    tw, th = draw.textbbox((0, 0), text, font=font)[2:4]
    x, y = _pos_xy(base.width, base.height, tw, th, position, margin)
    r, g, b = _parse_color(color)
    draw.text((x, y), text, font=font, fill=(r, g, b, int(255 * opacity)))
    out = Image.alpha_composite(base, layer)
    out.convert("RGB").save(output_path)


def add_image_watermark(image_path: str, wm_path: str, output_path: str, position: str = "bottom_right", scale: float = 0.25, opacity: float = 0.6, margin: int = 16):
    base = Image.open(image_path).convert("RGBA")
    wm = Image.open(wm_path).convert("RGBA")
    target_w = int(base.width * scale)
    ratio = target_w / wm.width
    wm = wm.resize((target_w, int(wm.height * ratio)), Image.Resampling.LANCZOS)
    r, g, b, a = wm.split()
    alpha = a.point(lambda p: int(p * opacity))
    wm.putalpha(alpha)
    layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
    x, y = _pos_xy(base.width, base.height, wm.width, wm.height, position, margin)
    layer.paste(wm, (x, y), wm)
    out = Image.alpha_composite(base, layer)
    out.convert("RGB").save(output_path)


def add_text_watermark_image(base: Image.Image, text: str, position: str = "bottom_right", font_size: int = 32, color: str = "#ffffff", opacity: float = 0.6, margin: int = 16) -> Image.Image:
    base = base.convert("RGBA")
    layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(layer)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    tw, th = draw.textbbox((0, 0), text, font=font)[2:4]
    x, y = _pos_xy(base.width, base.height, tw, th, position, margin)
    r, g, b = _parse_color(color)
    draw.text((x, y), text, font=font, fill=(r, g, b, int(255 * opacity)))
    out = Image.alpha_composite(base, layer)
    return out.convert("RGB")


def add_image_watermark_image(base: Image.Image, wm_image: Image.Image, position: str = "bottom_right", scale: float = 0.25, opacity: float = 0.6, margin: int = 16) -> Image.Image:
    base = base.convert("RGBA")
    wm = wm_image.convert("RGBA")
    target_w = int(base.width * scale)
    ratio = target_w / wm.width
    wm = wm.resize((target_w, int(wm.height * ratio)), Image.Resampling.LANCZOS)
    r, g, b, a = wm.split()
    alpha = a.point(lambda p: int(p * opacity))
    wm.putalpha(alpha)
    layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
    x, y = _pos_xy(base.width, base.height, wm.width, wm.height, position, margin)
    layer.paste(wm, (x, y), wm)
    out = Image.alpha_composite(base, layer)
    return out.convert("RGB")
