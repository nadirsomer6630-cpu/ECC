"""Image effects for the episodes, after "8 MIND-BLOWING Photoshop Effects In Under 8 Minutes!" (Wave Index), rebuilt
in numpy/PIL so they run on every frame. Each takes and returns a PIL image.

halation      film halation: the brightest parts, blurred, screened back on, tinted red (lamps, neons, phone light)
frosted       a frosted-glass panel: blur + noise + glass ripple inside a rounded box, drop shadow, white inner glow
halftone      grungy halftone: circular dots, pen-like edges, film grain (flashbacks, the clue replayed)
text_behind   big text between the background and the subject (title cards, covers)
pixel_stretch one column of pixels stretched sideways with a fade and noise (glitch when the double appears)
line_drawing  find edges + black and white + curves: a pen drawing of the frame (the rule card, memories)"""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _a(im): return np.asarray(im.convert("RGB")).astype(np.float32)
def _im(a): return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def halation(im, thresh=200, blur=28, strength=0.9, tint=(255, 60, 40)):
    a = _a(im); lum = a.mean(axis=2)
    mask = (lum > thresh).astype(np.float32)[..., None] * a                                  # threshold: only the brightest parts
    glow = cv2.GaussianBlur(mask, (0, 0), blur)
    glow = glow * 0.55 + np.array(tint, np.float32) * (glow.mean(axis=2, keepdims=True) / 255) * 0.45   # the faded red tone
    out = 255 - (255 - a) * (255 - glow * strength) / 255                                     # screen blend
    return _im(out)


def frosted(im, box, radius=36, blur=18, ripple=6):
    a = _a(im); x0, y0, x1, y1 = box
    sub = cv2.GaussianBlur(a[y0:y1, x0:x1], (0, 0), blur)
    h, w = sub.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rng = np.random.default_rng(3); n = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 3) * ripple * 3
    sub = cv2.remap(sub, xx + n, yy + n, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)   # glass distortion
    sub = sub * 0.8 + 255 * 0.12 + rng.normal(0, 5, sub.shape)                                # lift and noise
    out = im.convert("RGBA")
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0 + 10, y0 + 24, x1 + 10, y1 + 24), radius, fill=(0, 0, 0, 120))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))                               # drop shadow
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
    out.paste(_im(sub), (x0, y0), m)
    gl = Image.new("RGBA", out.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle(box, radius, outline=(255, 255, 255, 150), width=6)
    out.alpha_composite(gl.filter(ImageFilter.GaussianBlur(3))); ImageDraw.Draw(out).rounded_rectangle(box, radius, outline=(255, 255, 255, 90), width=2)   # inner glow
    return out.convert("RGB")


def halftone(im, cell=10, grain=10):
    g = _a(im).mean(axis=2); h, w = g.shape; out = Image.new("L", (w, h), 255); d = ImageDraw.Draw(out)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            v = 1 - g[y:y + cell, x:x + cell].mean() / 255; r = cell * 0.62 * v ** 0.8
            if r > 0.4: d.ellipse((x + cell / 2 - r, y + cell / 2 - r, x + cell / 2 + r, y + cell / 2 + r), fill=0)
    edges = cv2.Canny(g.astype(np.uint8), 60, 140); o = np.asarray(out).astype(np.float32); o[edges > 0] = 0   # pen strokes
    o += np.random.default_rng(5).normal(0, grain, o.shape)                                    # film grain
    tint = np.stack([o * 0.96 + 10, o * 0.92 + 8, o * 0.84 + 6], axis=2)                       # old paper
    return _im(tint)


def text_behind(bg, subject_rgba, xy, text, font, fill=(255, 212, 56), stroke=(20, 17, 30)):
    """Text drawn on the background, then the subject pasted over it: the title sits behind the character."""
    out = bg.convert("RGBA"); d = ImageDraw.Draw(out)
    d.text(xy, text, font=font, fill=fill, anchor="mm", stroke_width=10, stroke_fill=stroke)
    return out


def pixel_stretch(im, x, width=6, fade=0.85, noise=18, side=1):
    a = _a(im); h, w = a.shape[:2]; col = a[:, x:x + width].mean(axis=1, keepdims=True)
    span = (w - x) if side > 0 else x; out = a.copy()
    for k in range(span):
        xx = x + side * k
        if not (0 <= xx < w): break
        f = (1 - k / span) ** 0.6 * fade
        out[:, xx] = out[:, xx] * (1 - f) + col[:, 0] * f
    rng = np.random.default_rng(9); n = rng.normal(0, noise, out.shape)
    ramp = np.clip((np.arange(w) - x) * side / max(1, span), 0, 1)[None, :, None]
    return _im(out + n * ramp)


def line_drawing(im, darkness=1.6):
    g = cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2GRAY)
    inv = 255 - g; blur = cv2.GaussianBlur(inv, (0, 0), 6)
    sketch = cv2.divide(g, 255 - blur, scale=256)                                              # find edges, pencil style
    sketch = np.clip(255 - (255 - sketch.astype(np.float32)) * darkness, 0, 255)               # the curves push
    return _im(np.stack([sketch] * 3, axis=2))
