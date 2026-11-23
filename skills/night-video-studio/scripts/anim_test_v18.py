"""3 s test of the two Grease Pencil tutorials' lessons with our characters: 12 drawings a second held two frames
(on twos), line boil per drawing, a candle whose moving light moves the one shadow shape, a long held pose then a
short brutal one (irregular pose-to-pose for horror), a blurred foreground for depth, a vignette and a cold grade."""
import math, sys, numpy as np, cv2
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import toon5
from PIL import Image, ImageDraw, ImageFilter
W, H, FPS = 1080, 1920, 24
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vign = np.clip(1 - (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2), 0, 1) ** 0.7
def bg(t, flick):
    a = np.zeros((H, W, 3), np.float32) + np.array([22, 20, 34], np.float32)
    cx_ = W * (0.75 - 0.5 * min(1, t / 1.8)); glow = np.exp(-(((xx - cx_) / 380) ** 2 + ((yy - 1300) / 380) ** 2)) * (0.8 + 0.2 * flick)
    a += glow[..., None] * np.array([90, 60, 30], np.float32)
    return a, cx_
frames = int(3 * FPS)
for f in range(0, frames, 2):                                       # one drawing every two frames
    t = f / FPS; d = f // 2; flick = 0.5 + 0.5 * math.sin(d * 2.3) * math.sin(d * 0.7)
    a, cxl = bg(t, flick)
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    if t < 2.0:                                                     # the long hold: you, the light turning round you
        light = 1 - 2 * min(1, t / 1.8); blink = 0.9 < t < 1.0
        b = toon5.bust5("toi", light=light, blink=blink, look=(-0.3 * light, 0.1), boil=d, size=1000)
        im.alpha_composite(b, (40, 700))
    else:                                                           # the snap: the double, already close, bigger
        k = 1.0 if t < 2.0 + 1 / 12 else 1.0                       # no in-between: one drawing and he is there
        b = toon5.bust5("double", light=-1.0, boil=d, size=1500)
        im.alpha_composite(b, (-210, 380))
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(fg)  # a blurred candle in the foreground (depth)
    g.rectangle([cxl - 40, 1640, cxl + 40, 1920], fill=(230, 214, 180, 255)); g.ellipse([cxl - 26, 1560 - 30 * flick, cxl + 26, 1650], fill=(255, 200, 90, 255))
    im.alpha_composite(fg.filter(ImageFilter.GaussianBlur(16)))
    o = np.asarray(im.convert("RGB")).astype(np.float32)
    o = o * (0.35 + 0.65 * vign[..., None])                         # vignette
    o = o * np.array([0.92, 0.95, 1.08]) - 4                        # cold dark-fantasy grade, crushed blacks
    out = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8))
    for k in (0, 1): out.save(f"anim18/f{f + k:04d}.png")
print("ok", frames)
