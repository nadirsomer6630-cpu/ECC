"""Season 2 characters, v18: redrawn from zero after the creators the user sent (politiquepixels, pixels.stories,
proteine.facile, lucdgain, daybyday1to30, zak.kho), in their shared language: big heads, big expressive eyes, thick
brows, thick black outlines, flat colours with ONE soft shadow shape, hair drawn by hand as a few designed shapes, one
bright garment. One theme kept: dark fantasy (violet night shadows, a thin moonlight rim, the moon brooch, the double).

Lessons from v10-v17, applied here: no procedural hair (it made gaps, scallops and spikes); no stacked effects
(height maps, halftone, hatching, misregistration made faces noisy and plastic); no realistic proportions (small eyes
and long necks lost the expressions on a phone screen); identities stay fixed from one version to the next.

bust5(who, look=(x, y), brow, mouth, wide, blink, sway) -> RGBA 1000x1000.
who: "toi", "samir", "maman", "double"; mouth: "line", "smile", "o", "fear"."""
import math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageChops

SS = 2
INK = (22, 16, 30, 255)
NIGHT = (0.80, 0.74, 0.92)                 # shadows lean violet: the night of the series
MOON = (176, 168, 236, 255)                # the thin moonlight rim on the right edge


def bez(p0, p1, p2, p3, n=24):
    return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0],
             (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]) for t in (k / n for k in range(n + 1))]


def mirror(pts, cx): return [(2 * cx - x, y) for x, y in reversed(pts)]


def taper(c, w0, w1=1.5):
    n = len(c); L, R = [], []
    for i, (x, y) in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(n - 1, i + 1)]; dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        w = w0 + (w1 - w0) * i / (n - 1); L.append((x - dy / l * w, y + dx / l * w)); R.append((x + dy / l * w, y - dx / l * w))
    return L + R[::-1]


def tone(c, k=1.0):
    """The single shadow tone of a colour: darker and leaning violet."""
    return tuple(int(v * f * k) for v, f in zip(c[:3], NIGHT)) + (255,)


def lite(c, k=1.18): return tuple(min(255, int(v * k + 10)) for v in c[:3]) + (255,)


class Canvas:
    def __init__(self, w=1000, h=1000):
        self.W, self.H = w * SS, h * SS; self.im = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
    def P(self, pts): return [(x * SS, y * SS) for x, y in pts]
    def mask(self, pts=None, ell=None):
        m = Image.new("L", (self.W, self.H), 0); d = ImageDraw.Draw(m)
        if pts is not None: d.polygon(self.P(pts), fill=255)
        if ell is not None: d.ellipse([v * SS for v in ell], fill=255)
        return m
    def put(self, m, fill, line=7):
        """A flat shape with its ink outline (the mask grown by `line`)."""
        if line:
            r = int(line * SS); k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
            self.im.paste(Image.new("RGBA", self.im.size, INK), (0, 0), Image.fromarray(cv2.dilate(np.asarray(m), k)))
        self.im.paste(Image.new("RGBA", self.im.size, fill), (0, 0), m)
        return m
    def poly(self, pts, fill, line=7): return self.put(self.mask(pts), fill, line)
    def ell(self, box, fill, line=7): return self.put(self.mask(ell=box), fill, line)
    def inside(self, clip, pts=None, ell=None, fill=(0, 0, 0, 255), blur=0):
        """Paint a shape only inside another (a shadow on a face, a highlight on hair)."""
        m = self.mask(pts, ell)
        if blur: m = m.filter(ImageFilter.GaussianBlur(blur * SS))
        a = ImageChops.multiply(m, clip)
        if len(fill) == 4 and fill[3] < 255: a = a.point(lambda v: v * fill[3] // 255)
        lay = Image.new("RGBA", self.im.size, fill[:3] + (0,)); lay.putalpha(a); self.im.alpha_composite(lay)   # blended, not pasted
    def stroke(self, pts, w, fill=INK):
        ImageDraw.Draw(self.im).line(self.P(pts), fill=fill, width=max(1, int(w * SS)), joint="curve")
    def rim(self, clip, side=1, w=3):
        """Moonlight: a thin lavender line inside the right edge of a shape."""
        a = np.asarray(clip) > 0; k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(w * SS) * 2 + 1,) * 2)
        edge = a & ~(cv2.erode(a.astype(np.uint8), k) > 0)
        xs = np.nonzero(a.any(axis=0))[0]
        if len(xs) == 0: return
        cxm = (xs.min() + xs.max()) / 2; X = np.arange(a.shape[1])[None, :]
        edge &= (X > cxm + (xs.max() - xs.min()) * 0.18) if side > 0 else (X < cxm - (xs.max() - xs.min()) * 0.18)
        self.im.paste(Image.new("RGBA", self.im.size, MOON), (0, 0), Image.fromarray((edge * 150).astype(np.uint8)))
    def done(self, size=1000): return self.im.resize((self.W // SS * size // 1000, self.H // SS * size // 1000), Image.LANCZOS)


LOOK = dict(
    toi=dict(skin=(238, 198, 164, 255), hair=(44, 30, 26, 255), hair_d=(24, 16, 14, 255), hair_l=(112, 82, 66, 255),
             lock=(36, 62, 160, 255), lock_l=(110, 150, 240, 255), iris=(46, 80, 186, 255), top=(112, 72, 214, 255),
             top_d=(80, 50, 168, 255), inner=(38, 36, 50, 255), chin=672, jaw=1.0),
    samir=dict(skin=(190, 136, 98, 255), hair=(32, 24, 20, 255), iris=(104, 66, 38, 255), top=(54, 156, 98, 255),
               top_d=(34, 116, 70, 255), inner=(118, 122, 136, 255), chin=676, jaw=1.12),
    maman=dict(skin=(240, 204, 176, 255), hair=(132, 120, 118, 255), hair_d=(96, 86, 86, 255), hair_l=(196, 188, 186, 255),
               iris=(108, 78, 52, 255), top=(218, 128, 156, 255), top_d=(180, 96, 124, 255), inner=(246, 234, 218, 255), chin=664, jaw=1.04),
)
LOOK["double"] = dict(LOOK["toi"], skin=(176, 182, 196, 255), hair=(26, 22, 26, 255), hair_d=(12, 10, 14, 255), hair_l=(70, 62, 70, 255),
                      lock=(14, 14, 20, 255), lock_l=(60, 60, 80, 255), iris=(230, 30, 34, 255), top=(52, 38, 88, 255), top_d=(34, 24, 62, 255),
                      inner=(18, 16, 24, 255), chin=696, jaw=0.9)


def head_pts(cx, L):
    """A big round head: full temples and cheeks, a soft jaw, a rounded chin."""
    c, j = L["chin"], L["jaw"]
    right = bez((cx, 150), (cx + 150, 148), (cx + 212, 238), (cx + 210, 370)) + bez((cx + 210, 370), (cx + 208, 500), (cx + 150 * j, 640), (cx, c))[1:]
    return right + mirror(right, cx)[1:-1]


def eye(cv, cx, cy, side, L, look, wide, blink, who, smile):
    """Big expressive almond, slightly slanted: white, a large iris, a pupil, two highlights, a thick upper lid with a
    flick, a thin lower lid, and the soft tired crescent below (night workers)."""
    w, h, lift = 62, 38 + 26 * max(0.0, wide - 1.0) * 2, 12
    def top(u): return (cx + side * u * w, cy - lift * (u + 1) / 2 + lift * 0.4 - h * (1 - u * u) ** 0.75)
    def bot(u): return (cx + side * u * w, cy - lift * (u + 1) / 2 + lift * 0.4 + h * (0.55 if smile else 0.8) * (1 - u * u) ** 1.1)
    if blink:
        cv.stroke([bot(u / 12)[:1] + (bot(u / 12)[1] - h * 0.5,) for u in range(-12, 13)], 8); return
    up = [top(u / 16) for u in range(-16, 17)]; lo = [bot(u / 16) for u in range(16, -17, -1)]
    m = cv.mask(up + lo); cv.put(m, (250, 248, 244, 255), 0)
    lay = Image.new("RGBA", cv.im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ir = 27 if wide < 1.15 else 19; ix, iy = cx + look[0] * 26, cy + look[1] * 10 + 2
    def E(x, y, r, c): d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=c)
    E(ix, iy, ir, tuple(int(v * 0.5) for v in L["iris"][:3]) + (255,)); E(ix, iy, ir * 0.84, L["iris"])
    E(ix, iy + ir * 0.32, ir * 0.5, lite(L["iris"], 1.3))
    if who == "double":
        d.ellipse([(ix - 3) * SS, (iy - ir * 0.7) * SS, (ix + 3) * SS, (iy + ir * 0.7) * SS], fill=(10, 6, 8, 255))   # a slit
    else:
        E(ix, iy, ir * 0.42, (16, 12, 22, 255)); E(ix - ir * 0.36, iy - ir * 0.38, ir * 0.26, (255, 255, 255, 255)); E(ix + ir * 0.34, iy + ir * 0.3, ir * 0.12, (255, 255, 255, 230))
    d.polygon(cv.P(up + [(x, y + 9) for x, y in reversed(up)]), fill=(60, 40, 70, 60))           # the lid's shadow on the eye
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m)); cv.im.alpha_composite(lay)
    if who == "double":
        g = Image.new("RGBA", cv.im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([(ix - 34) * SS, (iy - 34) * SS, (ix + 34) * SS, (iy + 34) * SS], fill=(255, 40, 30, 90))
        cv.im.alpha_composite(g.filter(ImageFilter.GaussianBlur(10 * SS)))
    cv.stroke(lo[2:-2], 3.5); cv.stroke(up, 9)
    oc = up[-1]; cv.stroke([oc, (oc[0] + side * 14, oc[1] - 10)], 7)                                  # the flick
    if who != "double":
        cv.stroke([(x, y + 9 + 3 * math.sin(i / 20 * math.pi)) for i, (x, y) in enumerate(lo[6:-6])], 2.5, tone(L["skin"], 0.85))   # tired crescent
    if who == "maman":
        for k_ in (0.5, 0.75): p = top(k_); cv.stroke([p, (p[0] + side * 6, p[1] - 11)], 3.5)


def brows(cv, cx, L, who, brow, wide):
    col = {"maman": (96, 84, 82, 255), "samir": (26, 18, 14, 255)}.get(who, L.get("hair_d", INK))
    th = {"samir": 17, "maman": 8, "double": 12}.get(who, 14); sl = {"double": 1.0, "toi": -0.3}.get(who, 0.0)
    for s in (-1, 1):
        x0 = cx + s * 94; y0 = 368 - (10 if wide > 1.15 else 0)
        c = bez((x0 - s * 54, y0 + 8 - brow * 24 + sl * 4), (x0 - s * 14, y0 - 6 - brow * 10), (x0 + s * 26, y0 - 8 - brow * 2 - sl * 6), (x0 + s * 58, y0 + 4 + brow * 12 - sl * 12), 14)
        cv.poly(taper(c, th * 0.5, 2), col, 0)


def mouth(cv, cx, L, kind, who, look):
    mx, my = cx + look[0] * 8, 588
    if who == "double":                                                     # the grin, too wide, sharp teeth
        g = bez((mx - 120, my - 24), (mx - 80, my + 56), (mx + 80, my + 56), (mx + 120, my - 24)) + bez((mx + 120, my - 24), (mx + 50, my + 8), (mx - 50, my + 8), (mx - 120, my - 24))
        cv.poly(g, (74, 10, 22, 255), 6)
        for k in range(-5, 6):
            x = mx + k * 20; y = my - 6 + abs(k) * 3.4
            cv.poly([(x - 8, y), (x + 8, y), (x, y + 18)], (246, 240, 226, 255), 0)
        return
    if kind == "o":
        cv.ell((mx - 20, my - 22, mx + 20, my + 26), (92, 26, 38, 255), 6)
        cv.poly([(mx - 12, my - 14), (mx + 12, my - 14), (mx + 10, my - 6), (mx - 10, my - 6)], (246, 240, 230, 255), 0)
    elif kind == "smile":                                                    # an open smile: upper teeth, a tongue
        m = cv.poly(bez((mx - 48, my - 10), (mx - 26, my + 34), (mx + 26, my + 34), (mx + 48, my - 10)), (92, 26, 38, 255), 6)
        cv.inside(m, pts=[(mx - 50, my - 14), (mx + 50, my - 14), (mx + 46, my), (mx - 46, my)], fill=(246, 240, 230, 255))
        cv.inside(m, ell=(mx - 20, my + 8, mx + 20, my + 34), fill=(214, 96, 104, 255))
    elif kind == "fear":
        cv.poly([(mx - 40, my + 6), (mx - 20, my - 8), (mx, my), (mx + 20, my - 8), (mx + 40, my + 6), (mx + 24, my + 14), (mx, my + 8), (mx - 24, my + 14)], (92, 26, 38, 255), 5)
    else:
        cv.stroke(bez((mx - 34, my + 2), (mx - 12, my - 6), (mx + 12, my - 6), (mx + 34, my + 2), 12), 7)
        cv.stroke(bez((mx - 16, my + 16), (mx - 6, my + 22), (mx + 6, my + 22), (mx + 16, my + 16), 8), 5, tone(L["skin"], 0.92))


def hair_toi(cv, cx, L, sway, hm):
    """Slicked back, messy, smooth waves, dark brown-black: one designed silhouette, five combed-back waves, three
    highlights following them, the blue lock and one loose strand. Drawn by hand, point by point, and symmetric
    except the waves and the lock."""
    H0, HD, HL = L["hair"], L["hair_d"], L["hair_l"]
    for s in (-1, 1):                                                        # short sideburns in front of the ears
        cv.poly(taper(bez((cx + s * 194, 372), (cx + s * 198, 410), (cx + s * 200, 440), (cx + s * 196, 466), 10), 7, 1), HD, 3)
    sil = (bez((cx - 196, 400), (cx - 228, 330), (cx - 228, 250), (cx - 200, 196)) + bez((cx - 200, 196), (cx - 186, 116), (cx - 116, 86), (cx - 58, 98))[1:]
           + bez((cx - 58, 98), (cx - 26, 64), (cx + 44, 58), (cx + 84, 82))[1:] + bez((cx + 84, 82), (cx + 146, 76), (cx + 204, 118), (cx + 216, 192))[1:]
           + bez((cx + 216, 192), (cx + 236, 254), (cx + 228, 340), (cx + 196, 400))[1:])
    hairline = ([(cx + 190, 376)] + bez((cx + 178, 300), (cx + 142, 248), (cx + 84, 230), (cx + 32, 238)) + [(cx, 258)]
                + bez((cx - 32, 238), (cx - 84, 230), (cx - 142, 248), (cx - 178, 300)) + [(cx - 190, 376)])
    top = cv.poly(sil + hairline, H0, 8)
    cv.inside(top, pts=sil[:30] + [(cx - 150, 300), (cx - 190, 420)], fill=tone(H0, 0.75))          # the shadow side
    waves = [((cx - 150, 280), (cx - 186, 220), (cx - 160, 150), (cx - 120, 112)), ((cx - 80, 240), (cx - 100, 180), (cx - 70, 120), (cx - 30, 92)),
             ((cx - 6, 246), (cx - 20, 180), (cx + 20, 116), (cx + 60, 82)), ((cx + 70, 236), (cx + 70, 170), (cx + 120, 116), (cx + 160, 104)),
             ((cx + 146, 266), (cx + 170, 210), (cx + 196, 170), (cx + 206, 150))]
    for w_ in waves: cv.stroke(bez(*w_, 20), 5, HD)                           # combed-back waves
    for (p0, p1, p2, p3) in (((cx - 118, 210), (cx - 132, 170), (cx - 110, 132), (cx - 84, 116)), ((cx - 40, 196), (cx - 46, 160), (cx - 22, 124), (cx + 10, 106)),
                             ((cx + 40, 190), (cx + 44, 156), (cx + 82, 124), (cx + 116, 114))):
        cv.inside(top, pts=taper(bez(p0, p1, p2, p3, 16), 6, 1), fill=HL)    # highlights along the waves
    c = [(cx - 50 + (30 + sway * 60) * u + 14 * math.sin(u * 5.2), 244 + 166 * u) for u in (k / 15 for k in range(16))]
    lk = cv.poly(taper(c, 15, 2.5), L["lock"], 5)                            # the lock over the left eye
    if L["lock"][2] > 100: cv.inside(lk, pts=taper([(x + 4, y) for x, y in c[2:9]], 3, 1), fill=L["lock_l"])
    c2 = [(cx + 46 + (24 + sway * 30) * u + 8 * math.sin(u * 4 + 1), 242 + 86 * u) for u in (k / 10 for k in range(11))]
    cv.poly(taper(c2, 8, 1.5), H0, 4)                                        # one loose strand


def bust5(who="toi", look=(0.0, 0.0), brow=0.0, mouth_="line", wide=1.0, blink=False, sway=0.0, size=1000, light=1.0, boil=None):
    L = LOOK[who]; cv = Canvas(); cx = 500
    # ---------- body: one bright garment each
    sh = bez((160, 1000), (170, 820), (300, 756), (430, 744)) + bez((570, 744), (700, 756), (830, 820), (840, 1000))
    if who in ("toi", "double"):
        cv.poly(bez((300, 800), (330, 700), (670, 700), (700, 800)) + [(620, 790), (500, 760), (380, 790)], L["inner"], 6)   # the hood
        body = cv.poly(sh, L["top"])
        cv.inside(body, pts=[(160, 1000), (170, 820), (300, 756), (380, 750), (300, 1000)], fill=tone(L["top"]))
        cv.poly([(440, 760), (560, 760), (590, 1000), (410, 1000)], L["inner"], 6)                                          # the hoodie
        for s in (-1, 1):
            cv.poly([(cx + s * 70, 744), (cx + s * 100, 772), (cx + s * 92, 1000), (cx + s * 62, 1000)], L["top_d"], 5)       # zip edges
            stripe = (240, 240, 248, 255) if who == "toi" else (90, 30, 40, 255)
            cv.stroke(bez((cx + s * 150, 770), (cx + s * 230, 780), (cx + s * 300, 820), (cx + s * 330, 910)), 9, stripe)      # sleeve stripes
            cv.poly([(cx + s * 70, 744), (cx + s * 140, 736), (cx + s * 132, 700), (cx + s * 70, 712)], L["top_d"], 5)         # collar
        g_ = Image.new("RGBA", cv.im.size, (0, 0, 0, 0)); ImageDraw.Draw(g_).ellipse([270 * SS, 800 * SS, 380 * SS, 910 * SS], fill=(255, 220, 120, 90))
        cv.im.alpha_composite(g_.filter(ImageFilter.GaussianBlur(14 * SS)))
        cv.ell((290, 820, 360, 890), (226, 190, 96, 255), 5); cv.ell((306, 832, 344, 872), (150, 116, 52, 255), 0); cv.ell((316, 826, 354, 866), (226, 190, 96, 255), 0)   # the moon brooch
        cv.rim(body)
    elif who == "samir":
        cv.poly(bez((330, 790), (350, 690), (650, 690), (670, 790)) + [(600, 780), (500, 755), (400, 780)], L["inner"], 6)
        body = cv.poly(sh, L["top"])
        cv.inside(body, pts=[(160, 1000), (170, 820), (300, 756), (380, 750), (300, 1000)], fill=tone(L["top"]))
        for k in range(4): y = 830 + k * 50; cv.stroke(bez((215, y + 24), (340, y - 10), (660, y - 10), (785, y + 24)), 5, L["top_d"])
        cv.poly([(430, 735), (570, 735), (575, 790), (425, 790)], L["top_d"], 6); cv.stroke([(500, 790), (500, 1000)], 5)
        cv.rim(body)
    elif who == "maman":
        body = cv.poly(sh, L["top"])
        cv.inside(body, pts=[(160, 1000), (170, 820), (300, 756), (380, 750), (300, 1000)], fill=tone(L["top"]))
        cv.poly([(420, 720), (580, 720), (600, 790), (500, 830), (400, 790)], L["inner"], 6)
        for k in range(3): cv.stroke([(415 + k * 4, 735 + k * 18), (585 - k * 4, 735 + k * 18)], 3, tone(L["inner"], 0.95))
        cv.poly([(420, 790), (500, 1000), (380, 1000), (360, 800)], L["top_d"], 5); cv.poly([(580, 790), (500, 1000), (620, 1000), (640, 800)], L["top_d"], 5)
        for y in (860, 920, 980): cv.ell((428, y, 446, y + 18), (250, 244, 236, 255), 3)
        cv.rim(body)
    # ---------- neck, its shadow under the chin
    neck = cv.poly([(cx - 58, 620), (cx + 58, 620), (cx + 64, 770), (cx, 796), (cx - 64, 770)], L["skin"], 6)
    cv.inside(neck, pts=bez((cx - 80, 640), (cx - 40, 700), (cx + 40, 700), (cx + 80, 640)) + [(cx + 80, 600), (cx - 80, 600)], fill=tone(L["skin"]))
    if who in ("toi", "double"):                                            # headphones round the neck
        cv.stroke(bez((350, 760), (360, 830), (640, 830), (650, 760)), 22, (34, 32, 44, 255))
        for x in (340, 660): cv.ell((x - 46, 700, x + 46, 800), (34, 32, 44, 255), 6); cv.ell((x - 22, 724, x + 22, 776), L["top"], 0)
    if who == "samir": cv.stroke(bez((440, 760), (460, 812), (540, 812), (560, 760)), 4, (214, 176, 84, 255))   # a thin chain
    # ---------- ears, head
    for s in (-1, 1):
        e = cv.ell((cx + s * 206 - 30, 400, cx + s * 206 + 30, 500), L["skin"], 6)
        cv.stroke(bez((cx + s * 200, 420), (cx + s * 218, 430), (cx + s * 218, 470), (cx + s * 204, 482), 8), 3, tone(L["skin"], 0.85))
    if who == "maman":
        for s in (-1, 1): cv.ell((cx + s * 214 - 7, 492, cx + s * 214 + 7, 506), (246, 244, 238, 255), 3)   # pearl earrings
    if who == "samir": cv.ell((cx - 222, 486, cx - 210, 498), (214, 176, 84, 255), 3)
    if who == "maman": cv.ell((cx - 74, 50, cx + 74, 170), L["hair"], 7)                                      # the bun, behind
    hpts = head_pts(cx, L); hm = cv.poly(hpts, L["skin"], 8)
    side = -1 if light >= 0 else 1; depth = 30 + 40 * (1 - abs(light))                                            # ONE shadow shape, on the side
    edge = [p for p in hpts if (p[0] - cx) * side > 30]                                                           # away from the light; it widens
    cv.inside(hm, pts=edge + [(x - side * (depth + 14 * math.sin((y - 150) / 520 * math.pi)), y) for x, y in reversed(edge)], fill=tone(L["skin"]))   # as the light turns
    cv.rim(hm, side=-side)
    if who != "double":
        for s in (-1, 1): cv.inside(hm, ell=(cx + s * 128 - 34, 506, cx + s * 128 + 34, 534), fill=(244, 150, 146, 120) if who != "samir" else (200, 100, 80, 90), blur=4)   # blush
    # ---------- character marks
    if who == "toi":
        cv.stroke([(cx - 132, 334), (cx - 116, 378)], 4, (176, 92, 86, 255))                    # the scar through the left brow
        cv.stroke([(cx - 104, 488), (cx - 96, 510)], 3, (176, 92, 86, 255))
    if who == "samir":                                                                           # a short beard along the jaw, a moustache
        bm = cv.mask(bez((cx - 206, 450), (cx - 196, 620), (cx + 196, 620), (cx + 206, 450)) + bez((cx + 206, 450), (cx + 140, 700), (cx - 140, 700), (cx - 206, 450)))
        hole = cv.mask(ell=(cx - 52, 560, cx + 52, 618))
        cv.im.paste(Image.new("RGBA", cv.im.size, (40, 30, 26, 255)), (0, 0), ImageChops.subtract(ImageChops.multiply(bm, hm), hole))
        cv.poly([(cx - 56, 578), (cx - 40, 552), (cx, 546), (cx + 40, 552), (cx + 56, 578), (cx + 30, 566), (cx, 564), (cx - 30, 566)], (40, 30, 26, 255), 0)
    if who == "double":                                                                          # black tears, a crack
        for s in (-1, 1): cv.stroke([(cx + s * 92, 470), (cx + s * 96, 530), (cx + s * 90, 590)], 6, (10, 8, 12, 255))
        cv.stroke([(cx + 120, 260), (cx + 104, 300), (cx + 124, 334), (cx + 110, 372)], 3, (60, 50, 70, 255))
    # ---------- face
    brows(cv, cx, L, who, brow, wide)
    for s in (-1, 1): eye(cv, cx + s * 94, 440, s, L, look, wide, blink, who, mouth_ == "smile")
    if who == "maman":                                                                           # round glasses
        for s in (-1, 1): ImageDraw.Draw(cv.im).ellipse([(cx + s * 94 - 82) * SS, 376 * SS, (cx + s * 94 + 82) * SS, 506 * SS], outline=(150, 118, 70, 255), width=5 * SS)
        cv.stroke([(cx - 14, 432), (cx + 14, 432)], 5, (150, 118, 70, 255))
    cv.stroke(bez((cx + 6, 486), (cx + 22, 510), (cx + 18, 528), (cx - 6, 530), 12), 5, tone(L["skin"], 0.75))   # a small nose
    mouth(cv, cx, L, mouth_, who, look)
    # ---------- hair, on top
    if who in ("toi", "double"):
        hair_toi(cv, cx, L, sway, hm)
    elif who == "samir":
        for k in range(-5, 6): cv.ell((cx + k * 36 - 26, 250 + abs(k) * 5, cx + k * 36 + 26, 290 + abs(k) * 5), L["hair"], 4)   # curls
        b = cv.poly(bez((cx - 226, 280), (cx - 236, 50), (cx + 236, 50), (cx + 226, 280)), L["top"])                      # the beanie
        cv.inside(b, pts=[(cx - 240, 300), (cx - 240, 40), (cx - 120, 40), (cx - 150, 300)], fill=tone(L["top"]))
        for k in range(-6, 7): cv.stroke([(cx + k * 32, 110 + abs(k) * 8), (cx + k * 33, 236)], 4, L["top_d"])
        cv.poly([(cx - 236, 230), (cx + 236, 230), (cx + 232, 292), (cx - 232, 292)], L["top_d"])
        cv.ell((cx - 44, 6, cx + 44, 94), (240, 238, 228, 255))
    elif who == "maman":
        hl = [(cx + 196, 430), (cx + 186, 330), (cx + 130, 268), (cx + 50, 244), (cx, 256), (cx - 50, 244), (cx - 130, 268), (cx - 186, 330), (cx - 196, 430)]
        top = cv.poly([(cx - 212, 440)] + bez((cx - 224, 330), (cx - 254, 74), (cx + 254, 74), (cx + 224, 330))[1:] + [(cx + 212, 440)] + hl, L["hair"], 8)
        cv.inside(top, pts=[(cx - 240, 460), (cx - 240, 120), (cx - 120, 120), (cx - 150, 460)], fill=tone(L["hair"]))
        for s in (-1, 1):
            for k in range(3): cv.stroke(bez((cx + s * 4, 250 + k * 4), (cx + s * (60 + k * 20), 180), (cx + s * (150 + k * 16), 210 + k * 20), (cx + s * (200 - k * 4), 330 + k * 30), 16), 3, L["hair_d"] if k else L["hair_l"])
        cv.stroke([(cx + 20, 66), (cx + 84, 116)], 5, (150, 118, 70, 255))                     # a hairpin
    out = cv.done(size)
    return line_boil(out, boil) if boil is not None else out


def line_boil(im, seed, amp=1.3, scale=60):
    """The Noise modifier of Grease Pencil, by hand: a smooth random displacement of 1-2 px, different for each
    drawing, so the ink 'lives' like hand-drawn animation. Change the seed every 2 frames (animation on twos)."""
    a = np.asarray(im); h, w = a.shape[:2]; rng = np.random.default_rng(seed)
    gh, gw = max(2, h // scale), max(2, w // scale)
    dx = cv2.resize(rng.normal(0, 1, (gh, gw)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC) * amp * w / 1000
    dy = cv2.resize(rng.normal(0, 1, (gh, gw)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC) * amp * w / 1000
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return Image.fromarray(cv2.remap(a, xx + dx, yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT), "RGBA")


if __name__ == "__main__":
    import sys
    rows = ["toi", "samir", "maman", "double"]
    exps = [("neutre", dict()), ("peur", dict(wide=1.4, brow=1.0, mouth_="o", look=(0.2, 0.0))), ("sourire", dict(mouth_="smile", brow=-0.4, look=(-0.3, 0.1))), ("inquiet", dict(mouth_="fear", brow=0.8, look=(0.0, 0.4)))]
    Sh = Image.new("RGB", (4 * 420 + 40, 4 * 450 + 40), (24, 22, 34)); d = ImageDraw.Draw(Sh)
    for r, who in enumerate(rows):
        for c, (e, kw) in enumerate(exps):
            b = bust5(who, size=400, **kw); Sh.paste(b, (20 + c * 420, 20 + r * 450), b); d.text((30 + c * 420, 425 + r * 450), f"{who.upper()} · {e}", fill=(200, 190, 220))
    Sh.save(sys.argv[1], quality=92); print("ok")
