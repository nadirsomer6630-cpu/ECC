"""Season 2 characters, a new design from scratch (busts for close-ups and dialogue).

Brief from the creator: unique, mixing what the reference creators do (big expressive heads and thick outlines from
the animated-series pages, sharper features and a signature hairstyle from the cinematic 3D sketches), with one
dark-blue lock of hair and hybrid eyes, almond and slanted. Every part is a mask: the ink outline is the mask grown
by a few pixels, so shapes can overlap freely and the line stays clean.

bust(who, look=(x, y), brow, mouth, wide, blink, sway, tilt, size) -> RGBA image.
who: "toi" (the night worker), "samir", "maman", "double" (wears your face: red irises, a grin too wide)."""
import math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageChops

INK = (20, 17, 30, 255)
SS = 2                                                         # supersampling


def bez(p0, p1, p2, p3, n=24):
    return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0],
             (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]) for t in (k / n for k in range(n + 1))]


class Canvas:
    def __init__(self, w, h):
        self.W, self.H = w * SS, h * SS; self.im = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
    def P(self, pts): return [(x * SS, y * SS) for x, y in pts]
    def mask(self): return Image.new("L", (self.W, self.H), 0)
    def put(self, m, fill, line=7, ink=INK):
        """Paint a mask with an ink outline of `line` px around it."""
        if line:
            r = int(line * SS); k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
            grown = Image.fromarray(cv2.dilate(np.asarray(m), k)); self.im.paste(Image.new("RGBA", self.im.size, ink), (0, 0), grown)
        self.im.paste(Image.new("RGBA", self.im.size, fill), (0, 0), m)
    def poly(self, pts, fill, line=7):
        m = self.mask(); ImageDraw.Draw(m).polygon(self.P(pts), fill=255); self.put(m, fill, line); return m
    def ell(self, box, fill, line=7):
        m = self.mask(); ImageDraw.Draw(m).ellipse([v * SS for v in box], fill=255); self.put(m, fill, line); return m
    def stroke(self, pts, width, fill=INK):
        ImageDraw.Draw(self.im).line(self.P(pts), fill=fill, width=int(width * SS), joint="curve")
    def done(self, size):
        return self.im.resize((self.W // SS * size // 1000, self.H // SS * size // 1000), Image.LANCZOS)


LOOKS = dict(
    toi=dict(skin=(236, 196, 160, 255), skin_d=(214, 166, 130, 255), hair=(26, 24, 36, 255), lock=(32, 58, 150, 255), shine=(96, 136, 230, 255),
             iris=(44, 70, 170, 255), top=(110, 70, 220, 255), top_d=(80, 48, 170, 255), tee=(236, 236, 244, 255)),
    samir=dict(skin=(190, 138, 98, 255), skin_d=(160, 110, 76, 255), hair=(36, 26, 22, 255), iris=(110, 70, 40, 255),
               top=(44, 150, 96, 255), top_d=(28, 110, 68, 255), tee=(60, 66, 84, 255)),
    maman=dict(skin=(238, 200, 168, 255), skin_d=(216, 172, 138, 255), hair=(120, 108, 106, 255), iris=(104, 78, 52, 255),
               top=(214, 132, 152, 255), top_d=(178, 100, 122, 255), tee=(250, 238, 240, 255)),
)
LOOKS["double"] = dict(LOOKS["toi"], skin=(150, 158, 176, 255), skin_d=(120, 128, 150, 255), lock=(14, 14, 22, 255), shine=(40, 40, 60, 255), iris=(210, 20, 30, 255))


def eye(cv, cx, cy, side, L, look, wide, blink, who):
    """Hybrid eye: an almond whose outer corner lifts (slanted), big enough for cartoon acting, a coloured iris with a
    dark ring, a pupil, two highlights, a heavy upper lid with a flick at the outer corner and a thin lower lid."""
    w, h = 80, 38 + 30 * max(0.0, wide - 1.0) * 2.2; lift = 20
    def top(u): return (cx + side * u * w, cy - lift * (u + 1) / 2 + lift * 0.4 - h * (1 - u * u) ** 0.7)
    def bot(u): return (cx + side * u * w, cy - lift * (u + 1) / 2 + lift * 0.4 + h * 0.8 * (1 - u * u) ** 1.1)
    if blink:
        cv.stroke([bot(u / 10)[0:1] + (bot(u / 10)[1] - h * 0.55,) for u in range(-10, 11)], 8); return
    up = [top(u / 14) for u in range(-14, 15)]; lo = [bot(u / 14) for u in range(14, -15, -1)]
    m = cv.mask(); ImageDraw.Draw(m).polygon(cv.P(up + lo), fill=255); cv.put(m, (252, 252, 250, 255), 0)
    lay = Image.new("RGBA", cv.im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ir = 35 if wide < 1.15 else 27; ix, iy = cx + look[0] * 32, cy + look[1] * 12 + 2
    def E(x, y, r, col): ld.ellipse(((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS), fill=col)
    E(ix, iy, ir, tuple(int(v * 0.55) for v in L["iris"][:3]) + (255,)); E(ix, iy, ir * 0.82, L["iris"])
    E(ix, iy + ir * 0.25, ir * 0.55, tuple(min(255, int(v * 1.35)) for v in L["iris"][:3]) + (255,))       # lighter lower iris
    E(ix, iy, ir * (0.42 if who != "double" else 0.16), (14, 12, 22, 255))
    if who != "double": E(ix - ir * 0.38, iy - ir * 0.4, ir * 0.24, (255, 255, 255, 255)); E(ix + ir * 0.35, iy + ir * 0.3, ir * 0.11, (255, 255, 255, 230))
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m)); cv.im.alpha_composite(lay)
    cv.stroke(lo, 3.5); cv.stroke(up, 10)
    oc = up[-1]; cv.stroke([oc, (oc[0] + side * 16, oc[1] - 12)], 8)                                  # the flick
    if who == "maman":
        for k in (0.55, 0.8): p = top(k); cv.stroke([p, (p[0] + side * 6, p[1] - 12)], 4)               # lashes


def bust(who="toi", look=(0.0, 0.0), brow=0.0, mouth="line", wide=1.0, blink=False, sway=0.0, tilt=0.0, size=1000):
    L = LOOKS[who]; cv = Canvas(1000, 1000); cx = 500 + tilt * 30
    # body: jacket, collar, tee, neck
    cv.poly(bez((170, 1000), (180, 820), (300, 760), (420, 745)) + bez((580, 745), (700, 760), (820, 820), (830, 1000)), L["top"])
    if who == "toi":                                            # the bomber's ribbed collar and the Nuit Express moon patch
        cv.poly([(400, 760), (500, 840), (600, 760), (590, 735), (500, 800), (410, 735)], L["top_d"], 5)
        cv.ell((640, 860, 720, 940), (246, 244, 252, 255), 5); cv.ell((662, 852, 736, 926), L["top"], 0)
    else:
        cv.poly([(420, 750), (500, 830), (580, 750)], L["tee"], 5)
    if who == "maman":
        for x in (470, 530): cv.ell((x - 9, 860, x + 9, 878), (250, 244, 236, 255), 3)                   # cardigan buttons
    cv.poly([(440, 640), (560, 640), (566, 770), (500, 800), (434, 770)], L["skin_d"], 6)                 # the neck
    if who in ("toi", "double"):                                # headphones around the neck: a signature prop
        cv.stroke(bez((350, 760), (360, 830), (640, 830), (650, 760)), 22, (34, 32, 44, 255))
        for x in (340, 660): cv.ell((x - 46, 700, x + 46, 800), (34, 32, 44, 255), 6); cv.ell((x - 22, 724, x + 22, 776), L["top"], 0)
    # head: a soft egg, wide at the temples, a defined jaw and chin
    head = bez((cx - 225, 380), (cx - 235, 170), (cx + 235, 170), (cx + 225, 380)) + bez((cx + 225, 380), (cx + 215, 560), (cx + 120, 680), (cx, 700)) + bez((cx, 700), (cx - 120, 680), (cx - 215, 560), (cx - 225, 380))
    for s_ in (-1, 1): cv.ell((cx + s_ * 228 - 34, 410, cx + s_ * 228 + 34, 500), L["skin_d"], 6)       # ears
    hm = cv.poly(head, L["skin"])
    sh = Image.new("RGBA", cv.im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)                            # cel shadow on the cheek and jaw
    sd.polygon(cv.P(bez((cx + 225, 380), (cx + 215, 560), (cx + 120, 680), (cx, 700)) + [(cx + 60, 640), (cx + 170, 520), (cx + 190, 400)]), fill=L["skin_d"][:3] + (150,))
    sh.putalpha(ImageChops.multiply(sh.getchannel("A"), hm)); cv.im.alpha_composite(sh)
    for s_ in (-1, 1): cv.ell((cx + s_ * 125 - 34, 520, cx + s_ * 125 + 34, 548), (246, 160, 150, 255), 0)  # blush
    # hair, by character
    if who in ("toi", "double"):
        fringe = [(cx + 228, 400), (cx + 190, 330), (cx + 160, 385), (cx + 110, 315), (cx + 70, 372), (cx + 20, 305), (cx - 30, 360), (cx - 80, 300), (cx - 130, 370), (cx - 170, 310), (cx - 205, 380), (cx - 228, 330)]
        back = bez((cx - 245, 460), (cx - 290, 100), (cx + 290, 100), (cx + 245, 460)) + fringe
        cv.poly(back, L["hair"])
        spikes = [(cx - 240, 330), (cx - 200, 250), (cx - 236, 230), (cx - 150, 190), (cx - 170, 150), (cx - 60, 160), (cx - 40, 112), (cx + 40, 150), (cx + 90, 110),
                  (cx + 130, 175), (cx + 210, 160), (cx + 200, 230), (cx + 248, 250), (cx + 232, 330), (cx + 150, 255), (cx + 80, 300), (cx + 20, 250), (cx - 40, 300), (cx - 110, 250), (cx - 180, 300)]
        cv.poly(spikes, L["hair"])
        tip = (cx + 70 + sway * 70, 455 + abs(sway) * 10)                                              # the dark-blue lock over the left eye
        lock = bez((cx - 120, 230), (cx - 160, 330), (cx - 40, 380), tip) + bez(tip, (cx - 10, 400), (cx - 110, 330), (cx - 50, 230))
        cv.poly(lock, L["lock"], 6)
        if who == "toi": cv.stroke(bez((cx - 110, 250), (cx - 130, 320), (cx - 60, 360), (cx - 5, 380), 12)[2:10], 7, L["shine"])
    elif who == "samir":
        for k in range(-5, 6): cv.ell((cx + k * 40 - 30, 262 + abs(k) * 6, cx + k * 40 + 30, 306 + abs(k) * 6), L["hair"], 4)       # curls under the beanie
        cv.poly(bez((cx - 250, 290), (cx - 260, 60), (cx + 260, 60), (cx + 250, 290)), L["top"])            # the green beanie
        for k in range(-6, 7): cv.stroke([(cx + k * 34, 120 + abs(k) * 9), (cx + k * 36, 260)], 5, L["top_d"])
        cv.poly([(cx - 262, 240), (cx + 262, 240), (cx + 258, 300), (cx - 258, 300)], L["top_d"])
        cv.ell((cx - 50, 12, cx + 50, 112), (240, 240, 232, 255))
        bm = cv.mask(); ImageDraw.Draw(bm).polygon(cv.P(bez((cx - 215, 470), (cx - 200, 640), (cx + 200, 640), (cx + 215, 470)) + bez((cx + 215, 470), (cx + 120, 720), (cx - 120, 720), (cx - 215, 470))), fill=255)
        bm = ImageChops.multiply(bm, hm); cv.put(bm, (52, 38, 32, 255), 0)                                 # short beard on the jaw
        cv.ell((cx - 60, 585, cx + 60, 640), L["skin"], 0)
    elif who == "maman":
        cv.ell((cx + 40, 95, cx + 210, 235), L["hair"])                                                   # the bun, resting on the crown
        cv.poly(bez((cx - 250, 480), (cx - 300, 140), (cx + 300, 140), (cx + 250, 480)) + [(cx + 212, 430), (cx + 170, 300), (cx + 40, 262), (cx - 80, 300), (cx - 150, 290), (cx - 212, 430)], L["hair"])
    # brows
    for s_ in (-1, 1):
        x0 = cx + s_ * 120; y0 = 352 - (10 if wide > 1.15 else 0)
        cv.stroke([(x0 - s_ * 52, y0 + 8 - brow * 26), (x0, y0 - 8 - brow * 8), (x0 + s_ * 58, y0 + 2 + brow * 14)], 11)
    for s_ in (-1, 1): eye(cv, cx + s_ * 118, 445, s_, L, look, wide, blink, who)
    if who == "maman":                                                                                    # thin round glasses
        for s_ in (-1, 1): ImageDraw.Draw(cv.im).ellipse([(cx + s_ * 118 - 96) * SS, 375 * SS, (cx + s_ * 118 + 96) * SS, 512 * SS], outline=(120, 100, 90, 255), width=5 * SS)
        cv.stroke([(cx - 22, 435), (cx + 22, 435)], 5, (120, 100, 90, 255))
    cv.stroke([(cx + 6, 480), (cx - 8, 540), (cx + 14, 548)], 6)                                          # the nose
    my = 600; mx = cx + look[0] * 10
    if who == "double":                                       # the grin: far too wide, pointed teeth
        g = bez((mx - 150, my - 30), (mx - 100, my + 70), (mx + 100, my + 70), (mx + 150, my - 30)) + bez((mx + 150, my - 30), (mx + 60, my + 10), (mx - 60, my + 10), (mx - 150, my - 30))
        cv.poly(g, (70, 10, 20, 255), 6)
        for k in range(-5, 6): x = mx + k * 25; cv.poly([(x - 10, my - 10 + abs(k) * 4), (x + 10, my - 10 + abs(k) * 4), (x, my + 22)], (246, 240, 228, 255), 0)
    elif mouth == "o": cv.ell((mx - 22, my - 26, mx + 22, my + 26), (90, 26, 36, 255), 6)
    elif mouth == "smile": cv.stroke(bez((mx - 50, my - 12), (mx - 20, my + 22), (mx + 20, my + 22), (mx + 50, my - 12)), 9)
    elif mouth == "fear": cv.stroke([(mx - 44, my + 4), (mx - 22, my - 8), (mx, my + 4), (mx + 22, my - 8), (mx + 44, my + 4)], 8)
    else: cv.stroke([(mx - 36, my), (mx + 36, my + 4)], 9)
    return cv.done(size)


if __name__ == "__main__":
    import sys
    from PIL import ImageFont
    rows = [("toi", "TOI"), ("samir", "SAMIR"), ("maman", "MAMAN"), ("double", "LE DOUBLE")]
    exps = [("neutre", dict()), ("peur", dict(wide=1.4, brow=1.0, mouth="o", look=(0.3, 0.0))), ("sourire", dict(mouth="smile", brow=-0.4, look=(-0.3, 0.1))), ("inquiet", dict(mouth="fear", brow=0.8, look=(0.0, 0.4)))]
    S = Image.new("RGB", (4 * 420 + 40, 4 * 450 + 40), (232, 234, 240)); d = ImageDraw.Draw(S)
    for r, (who, name) in enumerate(rows):
        for c, (e, kw) in enumerate(exps):
            if who == "double" and c > 0: kw = dict(kw, mouth="line")
            b = bust(who, size=400, **kw); S.paste(b, (20 + c * 420, 20 + r * 450), b); d.text((30 + c * 420, 425 + r * 450), f"{name} · {e}", fill=(20, 20, 30))
    S.save(sys.argv[1] if len(sys.argv) > 1 else "/home/user/persos_v3.jpg", quality=90); print("ok")
