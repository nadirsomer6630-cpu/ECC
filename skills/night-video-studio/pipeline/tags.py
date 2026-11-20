"""Story labels drawn on top of a shot, in the manner of the recap videos that get the most saves: a word stuck on a
person or an object says a fact in half a second. Every function draws on an RGB PIL image in place and animates
with t - t0 (pops in, settles); colours stay in the series palette (red = danger, gold = name, white = fact).

  stamp_tag(im, t, t0, "FAUX", (x, y))          red rubber stamp, tilted, slams in
  label(im, t, t0, "VEUVE", (x, y))             red label on a dark strip, slides in
  name_plate(im, t, t0, "TA MÈRE", (x, y))      gold-framed name plate
  live_bug(im, t, "EN DIRECT")                  blinking red dot + word, top left
  note(im, t, t0, ["Cher livreur,", ...])       handwritten note close-up, typed in as the voice reads it
  poster(im, t, t0, "DISPARU", face, (x, y))    missing poster with a photo, pinned
  tape(im, t, t0, "NE PAS FRANCHIR", y)         crime-scene tape crossing the frame
  rec_frame(im, t)                              camcorder viewfinder (REC, corners, time code)
  grin(im, t, t0, (x, y), r)                    the double's grin as a sign drawn on a wall (the series motif)
  subscribe(im, t, t0, "NUIT 3")                end card: the button turns to ABONNÉ, then the next episode
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
HAND = None
RED, GOLD, INK = (200, 25, 25), (232, 186, 74), (22, 18, 34)


def setup(bold_font, hand_font):
    global FONT, HAND
    FONT, HAND = bold_font, hand_font


def _f(sz, hand=False): return ImageFont.truetype(HAND if hand and HAND else FONT, int(sz))
def _cl(x): return max(0.0, min(1.0, x))
def _pop(t, t0, d=0.16):
    """Overshoot scale: 1.6 -> 0.95 -> 1.0."""
    u = _cl((t - t0) / d)
    return 1.6 - 0.65 * u if u < 1 else 0.95 + 0.05 * _cl((t - t0 - d) / 0.08)


def _paste_rot(im, lay, xy, angle, scale=1.0):
    if scale != 1.0: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.BICUBIC)
    lay = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    im.paste(lay, (int(xy[0] - lay.width / 2), int(xy[1] - lay.height / 2)), lay)


def stamp_tag(im, t, t0, txt, xy, size=96, angle=-12):
    if t < t0: return
    f = _f(size); w = ImageDraw.Draw(im).textlength(txt, font=f) + size * 0.9; h = size * 1.5
    lay = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((6, 6, w - 6, h - 6), size * 0.12, outline=RED + (235,), width=max(6, int(size * 0.1)))
    d.text((w / 2, h / 2), txt, font=f, fill=RED + (235,), anchor="mm")
    rg = np.random.default_rng(len(txt)); a = np.asarray(lay).copy(); m = rg.random(a.shape[:2]) < 0.12; a[m, 3] = (a[m, 3] * 0.35).astype(np.uint8)   # worn ink
    _paste_rot(im, Image.fromarray(a), xy, angle, _pop(t, t0))


def label(im, t, t0, txt, xy, size=44, color=RED, angle=-4):
    if t < t0: return
    f = _f(size); w = ImageDraw.Draw(im).textlength(txt, font=f) + size; h = size * 1.6; u = _cl((t - t0) / 0.18); u = 1 - (1 - u) ** 3
    lay = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle((0, 0, w * u, h), fill=color + (240,)); d.rectangle((0, h - 6, w * u, h), fill=(0, 0, 0, 90))
    if u > 0.6: d.text((size / 2, h / 2), txt, font=f, fill=(255, 255, 255, 255), anchor="lm")
    _paste_rot(im, lay, xy, angle)


def name_plate(im, t, t0, txt, xy, size=52):
    if t < t0: return
    f = _f(size); w = ImageDraw.Draw(im).textlength(txt, font=f) + size * 1.2; h = size * 1.8
    lay = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 14, fill=(24, 22, 40, 245), outline=GOLD + (255,), width=6)
    for k in range(int(w / 26)): d.ellipse((13 + k * 26, 4, 19 + k * 26, 10), fill=(255, 236, 170, 255 if (k + int(t * 6)) % 3 else 90))    # bulbs
    d.text((w / 2, h / 2 + 4), txt, font=f, fill=GOLD + (255,), anchor="mm")
    _paste_rot(im, lay, xy, 0, _pop(t, t0, 0.2))


def live_bug(im, t, txt="EN DIRECT", xy=(124, 380)):
    d = ImageDraw.Draw(im); f = _f(30); w = d.textlength(txt, font=f) + 70
    d.rounded_rectangle((xy[0], xy[1], xy[0] + w, xy[1] + 50), 8, fill=RED)
    if int(t * 2) % 2 == 0: d.ellipse((xy[0] + 14, xy[1] + 15, xy[0] + 34, xy[1] + 35), fill=(255, 255, 255))
    d.text((xy[0] + 46, xy[1] + 25), txt, font=f, fill=(255, 255, 255), anchor="lm")


def note(im, t, t0, lines, rate=18, xy=(540, 820), w=760, h=560, taped=True):
    """A note stuck on a door: paper, tape, the words written in as the voice reads them."""
    if t < t0: return
    from PIL import ImageDraw as D_
    p = Image.new("RGBA", (w, h), (250, 248, 238, 255)); d = D_.Draw(p); f = _f(52, hand=True); n = int((t - t0) * rate); y = 70
    for ln in lines:
        d.text((50, y), ln[:max(0, n)], font=f, fill=INK + (255,)); n -= len(ln); y += 78
    if taped:
        tp = Image.new("RGBA", (200, 56), (236, 226, 190, 200)); _paste_rot(p, tp, (w / 2, 18), 4)
    sh = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0)); D_.Draw(sh).rectangle((30, 40, w + 30, h + 40), fill=(0, 0, 0, 120)); sh = sh.filter(ImageFilter.GaussianBlur(16))
    _paste_rot(im, sh, (xy[0] + 10, xy[1] + 16), -1.5); _paste_rot(im, p, xy, -1.5, 0.94 + 0.06 * _cl((t - t0) / 0.25))


def poster(im, t, t0, title, face, xy, w=520):
    """A missing-person poster with a photo (any RGBA image), pinned slightly crooked."""
    if t < t0: return
    h = int(w * 1.3); p = Image.new("RGBA", (w, h), (246, 240, 226, 255)); d = ImageDraw.Draw(p)
    d.text((w / 2, 70), title, font=_f(w * 0.17), fill=RED + (255,), anchor="mm")
    ph = face.resize((int(w * 0.72), int(w * 0.72))); p.paste(ph, (int(w * 0.14), 130), ph); d.rectangle((w * 0.14, 130, w * 0.86, 130 + w * 0.72), outline=INK + (255,), width=6)
    for k in range(3): d.rectangle((w * 0.14, 160 + w * 0.72 + k * 40, w * (0.86 - 0.15 * k), 176 + w * 0.72 + k * 40), fill=(150, 146, 140, 255))
    d.ellipse((w / 2 - 14, 8, w / 2 + 14, 36), fill=RED + (255,))
    _paste_rot(im, p, xy, 3, _pop(t, t0, 0.2))


def tape(im, t, t0, txt, y, angle=-8):
    if t < t0: return
    W_ = int(im.width * 1.5); u = _cl((t - t0) / 0.25); lay = Image.new("RGBA", (W_, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle((0, 0, W_ * u, 110), fill=(246, 206, 36, 255)); f = _f(40); x = 30
    while x < W_ * u - 200: d.text((x, 55), txt + "  ·", font=f, fill=INK + (255,), anchor="lm"); x += d.textlength(txt + "  ·  ", font=f)
    _paste_rot(im, lay, (im.width / 2, y), angle)


def rec_frame(im, t, x0=70, y0=380, x1=1010, y1=1560):
    d = ImageDraw.Draw(im); L = 70
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)): d.line((x, y, x + sx * L, y), fill=(255, 255, 255), width=6); d.line((x, y, x, y + sy * L), fill=(255, 255, 255), width=6)
    if int(t * 2) % 2 == 0: d.ellipse((x0 + 30, y0 + 30, x0 + 58, y0 + 58), fill=RED)
    d.text((x0 + 72, y0 + 44), "REC", font=_f(38), fill=(255, 255, 255), anchor="lm"); s = int(t)
    d.text((x1 - 30, y1 - 40), f"00:{s // 60:02d}:{s % 60:02d}", font=_f(34), fill=(255, 255, 255), anchor="rm")


def grin(im, t, t0, xy, r=180, drip=True):
    """The series motif: two round eyes and a toothed grin, drawn on a wall in white paint that runs."""
    if t < t0: return
    u = _cl((t - t0) / 0.6); lay = Image.new("RGBA", (int(r * 2.6), int(r * 3.2)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); c = (r * 1.3, r * 1.2); col = (236, 236, 244, 235)
    import toon2d as _T
    _T.monster_face(d, c[0], c[1] - r * 0.3, r * 1.25, style="paint")
    if drip:
        rg = np.random.default_rng(3)
        for k in range(6):
            x = c[0] + rg.uniform(-0.55, 0.55) * r; y = c[1] + r * (0.62 - 0.35 * (abs(x - c[0]) / r) ** 2); ln = r * rg.uniform(0.3, 1.2) * _cl((t - t0 - 0.4) / 1.5)
            d.line((x, y, x, y + ln), fill=col, width=int(r * 0.04)); d.ellipse((x - r * 0.03, y + ln - r * 0.03, x + r * 0.03, y + ln + r * 0.03), fill=col)
    im.paste(lay, (int(xy[0] - lay.width / 2), int(xy[1] - r * 1.2)), lay)


def subscribe(im, t, t0, nxt="NUIT 3", sub="Pourquoi il t'a laissé partir ?"):
    """End card: a "S'ABONNER" button is pressed and turns to "✓ ABONNÉ", then the next episode's title appears."""
    if t < t0: return
    d = ImageDraw.Draw(im); u = t - t0; on = u > 0.7; bw, bh = 440, 110; x0, y0 = 540 - bw / 2, 700
    press = 0.55 < u < 0.7; sc = 0.94 if press else 1.0; bwp, bhp = bw * sc, bh * sc; x0 += (bw - bwp) / 2; y0 += (bh - bhp) / 2
    d.rounded_rectangle((x0, y0, x0 + bwp, y0 + bhp), bhp / 2, fill=(255, 255, 255) if on else RED, outline=(255, 255, 255), width=5)
    d.text((560 if on else 540, y0 + bhp / 2), "ABONNÉ" if on else "S'ABONNER", font=_f(46), fill=INK if on else (255, 255, 255), anchor="mm")
    if on: d.line((x0 + 62, y0 + bhp * 0.52, x0 + 82, y0 + bhp * 0.7, x0 + 116, y0 + bhp * 0.3), fill=INK, width=9, joint="curve")
    if 0.2 < u < 0.75:                                                # a finger comes to press it
        fx, fy = 540 + 120 * (1 - _cl((u - 0.2) / 0.35)), 760 + 220 * (1 - _cl((u - 0.2) / 0.35)); d.ellipse((fx - 40, fy - 40, fx + 40, fy + 40), fill=(236, 190, 150), outline=INK, width=6)
    if u > 1.0:
        a = _cl((u - 1.0) / 0.3); d.text((540, 930), nxt, font=_f(120 * (0.8 + 0.2 * a)), fill=(232, 186, 74), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
        d.text((540, 1040), sub, font=_f(40), fill=(255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
