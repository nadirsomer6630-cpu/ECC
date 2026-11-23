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
        self.shade = Image.new("L", (self.W, self.H), 0)                                          # where the form shadows fall
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
    toi=dict(skin=(236, 196, 160, 255), skin_d=(214, 166, 130, 255), hair=(40, 28, 24, 255), hair_hi=(92, 68, 56, 255), hair_lo=(20, 13, 11, 255), lock=(32, 58, 150, 255), shine=(96, 136, 230, 255),
             iris=(44, 70, 170, 255), top=(110, 70, 220, 255), top_d=(80, 48, 170, 255), tee=(236, 236, 244, 255)),
    samir=dict(skin=(190, 138, 98, 255), skin_d=(160, 110, 76, 255), hair=(36, 26, 22, 255), iris=(110, 70, 40, 255),
               top=(44, 150, 96, 255), top_d=(28, 110, 68, 255), tee=(60, 66, 84, 255)),
    maman=dict(skin=(238, 200, 168, 255), skin_d=(216, 172, 138, 255), hair=(120, 108, 106, 255), iris=(104, 78, 52, 255),
               top=(214, 132, 152, 255), top_d=(178, 100, 122, 255), tee=(250, 238, 240, 255)),
)
GOLD = (196, 160, 84, 255); GOLD_D = (130, 100, 48, 255)
LOOKS5 = dict(
    toi=dict(LOOKS["toi"], skin=(214, 182, 152, 255), skin_d=(174, 138, 112, 255), top=(74, 54, 108, 255), top_d=(52, 38, 80, 255), cloak=(40, 38, 46, 255), cloak_d=(26, 24, 30, 255)),
    samir=dict(LOOKS["samir"], skin=(176, 128, 92, 255), skin_d=(140, 98, 70, 255), top=(84, 104, 70, 255), top_d=(58, 76, 48, 255)),
    maman=dict(LOOKS["maman"], skin=(222, 188, 160, 255), skin_d=(190, 152, 126, 255), top=(92, 52, 78, 255), top_d=(64, 34, 54, 255)),
)
LOOKS["double"] = dict(LOOKS["toi"], skin=(150, 158, 176, 255), skin_d=(120, 128, 150, 255), hair_hi=(54, 46, 50, 255), lock=(14, 14, 22, 255), shine=(40, 40, 60, 255), iris=(210, 20, 30, 255))


def lock_poly(center, w0, w1=2):
    """A tapered strand around a centre line: w0 wide at the root, w1 at the tip."""
    n = len(center); left, right = [], []
    for i, (x, y) in enumerate(center):
        a, b = center[max(0, i - 1)], center[min(n - 1, i + 1)]; dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        w = w0 + (w1 - w0) * i / (n - 1); left.append((x - dy / l * w, y + dx / l * w)); right.append((x + dy / l * w, y - dx / l * w))
    return left + right[::-1]


FACE = dict(   # the bone structure of each face: head (temple T, cheekbone C at cby, jaw corner J at jy, chin half-width
               # K at chy), eyes (width, height, slant, spacing, height, iris), brows (thickness, height, slant), nose
               # (tip height, width, kind), mouth (height, width), and how hollow the cheeks and eye sockets are
    toi=dict(T=214, C=222, cby=468, J=152, jy=592, K=34, chy=712, ew=74, eh=31, lift=22, esp=114, ey=448, ir=30,
             bw=11, by=366, bs=-0.6, nl=550, nw=25, nose="straight", my=622, mw=40, hollow=0.6, socket=0.5),
    samir=dict(T=230, C=244, cby=490, J=210, jy=644, K=86, chy=706, ew=68, eh=33, lift=6, esp=120, ey=452, ir=29,
               bw=16, by=372, bs=0.0, nl=560, nw=40, nose="broad", my=624, mw=52, hollow=0.25, socket=0.35),
    maman=dict(T=220, C=230, cby=490, J=190, jy=586, K=70, chy=692, ew=64, eh=29, lift=-2, esp=114, ey=452, ir=27,
               bw=6, by=360, bs=0.5, nl=540, nw=22, nose="small", my=602, mw=36, hollow=0.0, socket=0.3),
    double=dict(T=206, C=212, cby=450, J=132, jy=620, K=24, chy=752, ew=82, eh=29, lift=36, esp=112, ey=446, ir=30,
                bw=8, by=348, bs=1.2, nl=570, nw=19, nose="sharp", my=640, mw=40, hollow=1.0, socket=1.0),
)


def head_pts(cx, F):
    """A skull dome, the temple to the cheekbone, the cheekbone to the jaw corner, the jaw to the chin, mirrored."""
    T, C, cby, J, jy, K, chy = F["T"], F["C"], F["cby"], F["J"], F["jy"], F["K"], F["chy"]
    dome = bez((cx - T, 380), (cx - T - 12, 160), (cx + T + 12, 160), (cx + T, 380))
    right = bez((cx + T, 380), (cx + C + 6, cby - 70), (cx + C, cby + 10), (cx + J, jy), 16) + bez((cx + J, jy), (cx + J - (J - K) * 0.22, jy + (chy - jy) * 0.55), (cx + K + (J - K) * 0.3, chy), (cx + K, chy), 16)
    return dome + right + [(2 * cx - x, y) for x, y in reversed(right)]


def eye(cv, cx, cy, side, L, look, wide, blink, who, F=None):
    """Hybrid eye: an almond whose outer corner lifts (slanted), big enough for cartoon acting, a coloured iris with a
    dark ring, a pupil, two highlights, a heavy upper lid with a flick at the outer corner and a thin lower lid.
    Its proportions come from the character's FACE."""
    F = F or FACE["toi"]
    w, h = F["ew"], F["eh"] + 30 * max(0.0, wide - 1.0) * 2.2; lift = F["lift"]
    def top(u): return (cx + side * u * w, cy - lift * (u + 1) / 2 + lift * 0.4 - h * (1 - u * u) ** 0.7)
    def bot(u): return (cx + side * u * w, cy - lift * (u + 1) / 2 + lift * 0.4 + h * 0.8 * (1 - u * u) ** 1.1)
    if blink:
        cv.stroke([bot(u / 10)[0:1] + (bot(u / 10)[1] - h * 0.55,) for u in range(-10, 11)], 8); return
    up = [top(u / 14) for u in range(-14, 15)]; lo = [bot(u / 14) for u in range(14, -15, -1)]
    m = cv.mask(); ImageDraw.Draw(m).polygon(cv.P(up + lo), fill=255); cv.put(m, (252, 252, 250, 255), 0)
    lay = Image.new("RGBA", cv.im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ir = F["ir"] if wide < 1.15 else F["ir"] * 0.8; ix, iy = cx + look[0] * 28, cy + look[1] * 10 + 2
    def E(x, y, r, col): ld.ellipse(((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS), fill=col)
    E(ix, iy, ir, tuple(int(v * 0.55) for v in L["iris"][:3]) + (255,)); E(ix, iy, ir * 0.82, L["iris"])
    E(ix, iy + ir * 0.25, ir * 0.55, tuple(min(255, int(v * 1.35)) for v in L["iris"][:3]) + (255,))       # lighter lower iris
    E(ix, iy, ir * (0.42 if who != "double" else 0.16), (14, 12, 22, 255))
    if who != "double": E(ix - ir * 0.38, iy - ir * 0.4, ir * 0.24, (255, 255, 255, 255)); E(ix + ir * 0.35, iy + ir * 0.3, ir * 0.11, (255, 255, 255, 230))
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m)); cv.im.alpha_composite(lay)
    cv.stroke(lo, 3.5); cv.stroke(up, 13 if who == "samir" else 10)
    cv.stroke([(x, y - 15 - 6 * (1 - abs(i - 14) / 14)) for i, (x, y) in enumerate(up) if 5 <= i <= 23], 3.5, tuple(int(v * 0.72) for v in L["skin_d"][:3]) + (255,))   # lid crease
    oc = up[-1]; fl = 26 if who == "double" else 16; cv.stroke([oc, (oc[0] + side * fl, oc[1] - fl * 0.75)], 8)   # the flick
    if who == "maman":
        for k in (-10, 4): cv.stroke([(oc[0] + side * 10, oc[1] + k), (oc[0] + side * 30, oc[1] + k * 1.6)], 3, tuple(int(v * 0.75) for v in L["skin_d"][:3]) + (255,))   # crow's feet
    if who == "maman":
        for k in (0.55, 0.8): p = top(k); cv.stroke([p, (p[0] + side * 6, p[1] - 12)], 4)               # lashes


def bust(who="toi", look=(0.0, 0.0), brow=0.0, mouth="line", wide=1.0, blink=False, sway=0.0, tilt=0.0, size=1000, grim=False):
    L = LOOKS[who]; cv = Canvas(1000, 1000); cx = 500 + tilt * 30
    if grim:
        L = dict(LOOKS5.get(who, LOOKS5["toi"] if who == "double" else L))
        if who == "double": L.update(skin=(178, 180, 186, 255), skin_d=(140, 142, 152, 255), lock=(14, 14, 22, 255), shine=(40, 40, 60, 255), iris=(230, 30, 30, 255), hair_hi=(54, 46, 50, 255))
        return grim_bust(who, L, look, brow, mouth, wide, blink, sway, tilt, size)
    return _draw(cv, who, L, cx, look, brow, mouth, wide, blink, sway, size, False)


def _draw(cv, who, L, cx, look, brow, mouth, wide, blink, sway, size, grim):
    # clothes, after the reference creators: an open track jacket over a hoodie (the hero), a quilted puffer (Samir),
    # a cardigan over a turtleneck (the mother)
    shoulders = bez((160, 1000), (170, 815), (300, 755), (420, 742)) + bez((580, 742), (700, 755), (830, 815), (840, 1000))
    if who in ("toi", "double"):
        hood = (36, 34, 48, 255) if who == "toi" else (24, 24, 32, 255)
        cv.poly(bez((300, 800), (330, 700), (670, 700), (700, 800)) + [(620, 790), (500, 760), (380, 790)], hood, 6)          # the hood behind the neck
        cv.poly(shoulders, L["top"])
        cv.poly([(440, 760), (560, 760), (590, 1000), (410, 1000)], hood, 6)                                                   # the hoodie between the open panels
        for s_ in (-1, 1):
            cv.poly([(500 + s_ * 70, 742), (500 + s_ * 100, 770), (500 + s_ * 92, 1000), (500 + s_ * 62, 1000)], L["top_d"], 5)   # zip edges
            if not grim:
                cv.stroke(bez((500 + s_ * 150, 760), (500 + s_ * 230, 770), (500 + s_ * 300, 810), (500 + s_ * 330, 900)), 9, (240, 240, 248, 255))   # sleeve stripes
                cv.stroke(bez((500 + s_ * 150, 790), (500 + s_ * 220, 800), (500 + s_ * 285, 835), (500 + s_ * 310, 920)), 9, (240, 240, 248, 255))
            else:
                cv.stroke(bez((500 + s_ * 160, 800), (500 + s_ * 220, 830), (500 + s_ * 250, 900), (500 + s_ * 260, 1000)), 5, L["top_d"])   # leather seams
            cv.poly([(500 + s_ * 70, 742), (500 + s_ * 140, 735), (500 + s_ * 132, 700), (500 + s_ * 70, 712)], L["top_d"], 5)       # stand-up collar
        if not grim:
            for k in range(8): cv.stroke([(500 + 89, 790 + k * 26), (500 + 83, 800 + k * 26)], 4, (200, 200, 210, 255))                # zip teeth
            cv.ell((650, 870, 726, 946), (246, 244, 252, 255), 5); cv.ell((670, 862, 740, 932), L["top"], 0)                       # the moon patch
    elif who == "samir":
        cv.poly(bez((330, 790), (350, 690), (650, 690), (670, 790)) + [(600, 780), (500, 755), (400, 780)], (120, 124, 138, 255), 6)   # grey hood
        cv.poly(shoulders, L["top"])
        for k in range(4):                                                                                                     # quilted puffer lines
            y = 830 + k * 50; cv.stroke(bez((215, y + 24), (340, y - 10), (660, y - 10), (785, y + 24)), 5, L["top_d"])
        cv.poly([(430, 735), (570, 735), (575, 790), (425, 790)], L["top_d"], 6)                                              # high collar
        cv.stroke([(500, 790), (500, 1000)], 6, (30, 70, 46, 255))
    elif who == "maman":
        cv.poly(shoulders, L["top"])
        cv.poly([(420, 720), (580, 720), (600, 790), (500, 830), (400, 790)], (240, 228, 210, 255), 6)                       # cream turtleneck
        for k in range(3): cv.stroke([(415 + k * 4, 735 + k * 18), (585 - k * 4, 735 + k * 18)], 3, (210, 196, 176, 255))
        cv.poly([(420, 790), (500, 1000), (380, 1000), (360, 800)], L["top_d"], 5); cv.poly([(580, 790), (500, 1000), (620, 1000), (640, 800)], L["top_d"], 5)   # cardigan fronts
        for y in (860, 920, 980): cv.ell((428, y, 446, y + 18), (250, 244, 236, 255), 3)
    F = FACE[who]; ey, esp = F["ey"], F["esp"]
    nw_ = 64 if who == "samir" else (50 if who == "double" else 58)
    neck = cv.poly([(500 - nw_, 640), (500 + nw_, 640), (500 + nw_ + 6, 770), (500, 800), (500 - nw_ - 6, 770)], L["skin_d"], 6)   # the neck
    dark = tuple(int(v * 0.72) for v in L["skin_d"][:3])
    nsh = Image.new("RGBA", cv.im.size, (0, 0, 0, 0))                                                    # the chin's shadow on the neck
    ImageDraw.Draw(nsh).ellipse([(cx - F["K"] - 90) * SS, (F["chy"] - 60) * SS, (cx + F["K"] + 70) * SS, (F["chy"] + 46) * SS], fill=dark + (230,))
    nsh.putalpha(ImageChops.multiply(nsh.getchannel("A"), neck)); cv.im.alpha_composite(nsh)
    if who in ("toi", "double"):                                # headphones around the neck: a signature prop
        cv.stroke(bez((350, 760), (360, 830), (640, 830), (650, 760)), 22, (34, 32, 44, 255))
        for x in (340, 660): cv.ell((x - 46, 700, x + 46, 800), (34, 32, 44, 255), 6); cv.ell((x - 22, 724, x + 22, 776), L["top"], 0)
    # head: each character has its own bone structure (FACE)
    for s_ in (-1, 1): cv.ell((cx + s_ * (F["T"] + 6) - 30, ey - 44, cx + s_ * (F["T"] + 6) + 30, ey + 52), L["skin_d"], 6)   # ears
    if who == "samir": cv.ell((cx - F["T"] - 16, ey + 40, cx - F["T"] + 2, ey + 58), GOLD, 3)                # a gold stud in his ear
    hm = cv.poly(head_pts(cx, F), L["skin"])
    # form shadows, light from the upper right: the left edge of the face, the eye sockets, under the cheekbones,
    # the side of the nose, under the nose and the lower lip. They are also kept in `cv.shade` for the hatching.
    sh = Image.new("RGBA", cv.im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh); md = ImageDraw.Draw(cv.shade)
    def plane(pts, a, col=dark, ellipse=False):
        f = col + (int(a),)
        if ellipse: sd.ellipse([v * SS for v in pts], fill=f); md.ellipse([v * SS for v in pts], fill=255 if a > 120 else 0)
        else: sd.polygon(cv.P(pts), fill=f); md.polygon(cv.P(pts), fill=255 if a > 120 else 0)
    hp = head_pts(cx, F); left = hp[-34:] + [p for p in hp[:12] if p[0] < cx - 10 and p[1] > 260]     # the left contour, chin to temple
    plane(left + [(x + (78 if y < F["cby"] else 64) * (1 - max(0, y - F["jy"]) / 260), y) for x, y in reversed(left)], 200)
    sock = (60, 40, 64) if who == "double" else dark
    for s_ in (-1, 1):
        ex = cx + s_ * esp; a = (150 if s_ < 0 else 90) * F["socket"] + 40
        plane((ex - F["ew"] - 16, F["by"] + 4, ex + F["ew"] + 14, ey + F["eh"] * 0.75), a, sock, True)
        if F["hollow"] > 0:                                                                               # the hollow under the cheekbone
            cb = (cx + s_ * (F["C"] - 8), F["cby"] + 6)
            plane(bez(cb, (cx + s_ * (F["C"] - 30), F["cby"] + 90), (cx + s_ * (F["J"] + 20), F["jy"] - 60), (cx + s_ * (F["J"] - 4), F["jy"] - 6), 12)
                  + bez((cx + s_ * (F["J"] - 30), F["jy"] - 40), (cx + s_ * (F["C"] - 90), F["cby"] + 120), (cx + s_ * (F["C"] - 80), F["cby"] + 40), cb, 12),
                  (170 if s_ < 0 else 110) * F["hollow"])
    nl, nwd = F["nl"], F["nw"]
    plane([(cx - 8, ey - 8), (cx - 10 - nwd * 0.5, nl - 40), (cx - nwd - 8, nl + 4), (cx - 6, nl + 6)], 170)   # left side of the nose
    plane((cx - nwd, nl + 8, cx + nwd * 0.6, nl + 24), 130, dark, True)                                    # under the nose
    plane((cx - F["mw"] * 0.6, F["my"] + 20, cx + F["mw"] * 0.5, F["my"] + 40), 140, dark, True)          # under the lower lip
    sh.putalpha(ImageChops.multiply(sh.getchannel("A"), hm)); cv.im.alpha_composite(sh)
    cv.shade = ImageChops.multiply(cv.shade, hm)
    lite = tuple(min(255, int(v * 1.1) + 8) for v in L["skin"][:3]) + (255,)                             # plane lights on the right
    cv.stroke(bez((cx + 4, ey - 6), (cx + 8, nl - 50), (cx + 10, nl - 30), (cx + 8, nl - 14), 10), 7, lite)    # the nose bridge
    cv.stroke(bez((cx + F["C"] - 40, F["cby"] - 30), (cx + F["C"] - 30, F["cby"]), (cx + F["C"] - 40, F["cby"] + 30), (cx + F["C"] - 60, F["cby"] + 50), 10), 9, lite)   # the cheekbone
    fold = tuple(int(v * 0.7) for v in L["skin_d"][:3]) + (255,)
    if who in ("maman", "samir", "double", "toi"):                                                         # lines that age and mark the face
        depth = dict(toi=3, samir=4, maman=4, double=5)[who]
        for s_ in (-1, 1): cv.stroke(bez((cx + s_ * (nwd + 10), nl - 4), (cx + s_ * (nwd + 34), nl + 30), (cx + s_ * (F["mw"] + 18), F["my"] - 20), (cx + s_ * (F["mw"] + 12), F["my"] + 4), 10), depth, fold)
    if who == "maman":
        for y in (296, 318): cv.stroke(bez((cx - 110, y + 6), (cx - 40, y - 4), (cx + 40, y - 4), (cx + 110, y + 6), 12), 3, fold)   # forehead lines
    if not grim or who == "maman":
        for s_ in (-1, 1): cv.ell((cx + s_ * 125 - 34, F["cby"] + 40, cx + s_ * 125 + 34, F["cby"] + 66), (246, 160, 150, 255) if not grim else (214, 150, 140, 255), 0)  # blush
    # hair, by character
    if who in ("toi", "double"):
        H0, HI, LO = L["hair"], L["hair_hi"], L["hair_lo"]
        for s_ in (-1, 1):                                                                                   # short sides at the temples only
            cv.poly([(cx + s_ * 238, 300), (cx + s_ * 244, 450), (cx + s_ * 214, 440), (cx + s_ * 200, 330)], LO, 6)
        hl = [(cx - 232, 320), (cx - 206, 270), (cx - 160, 244), (cx - 104, 232), (cx - 46, 226), (cx + 12, 232), (cx + 70, 224), (cx + 128, 236), (cx + 184, 256), (cx + 232, 310)]
        crown = []
        for k, (x, y) in enumerate(bez((cx + 240, 318), (cx + 320, 20), (cx - 320, 20), (cx - 240, 322), 30)):
            crown.append((x, y - 10 * math.sin(k * 0.9) ** 2))                                                 # wavy outline, swept back
        top = cv.poly(hl + crown, H0)
        lay = Image.new("RGBA", cv.im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for k in range(9):                                                                                     # waves combed back
            x0 = cx - 200 + k * 50; y0 = 262 - 26 * math.sin(k / 8 * math.pi)
            path = bez((x0, y0), (x0 - 30 + 10 * (k % 2), y0 - 70), (x0 + 40, y0 - 130), (x0 + (k - 4) * 22, 110), 16)
            ld.line(cv.P(path), fill=HI if k % 2 == 0 else LO, width=int((9 if k % 2 == 0 else 6) * SS), joint="curve")
        lay.putalpha(ImageChops.multiply(lay.getchannel("A"), top)); cv.im.alpha_composite(lay)
        for (x0, y0, x1, y1, w0, col, sw) in ((cx - 70, 232, cx - 20 + sway * 70, 440, 26, L["lock"], 1.0), (cx + 90, 230, cx + 140 + sway * 30, 330, 16, H0, 0.5)):
            c = []
            for k in range(14):                                                                                # loose wavy strands falling forward
                u = k / 13; c.append((x0 + (x1 - x0) * u + 18 * math.sin(u * 5.5) * sw, y0 + (y1 - y0) * u))
            cv.poly(lock_poly(c, w0, 3), col, 6)
        if who == "toi": cv.stroke([(cx - 66 + 18 * math.sin(k / 13 * 5.5), 246 + 12 * k) for k in range(8)], 6, L["shine"])
    elif who == "samir":
        for k in range(-5, 6): cv.ell((cx + k * 40 - 30, 262 + abs(k) * 6, cx + k * 40 + 30, 306 + abs(k) * 6), L["hair"], 4)       # curls under the beanie
        cv.poly(bez((cx - 250, 290), (cx - 260, 60), (cx + 260, 60), (cx + 250, 290)), L["top"])            # the green beanie
        for k in range(-6, 7): cv.stroke([(cx + k * 34, 120 + abs(k) * 9), (cx + k * 36, 260)], 5, L["top_d"])
        cv.poly([(cx - 262, 240), (cx + 262, 240), (cx + 258, 300), (cx - 258, 300)], L["top_d"])
        cv.ell((cx - 50, 12, cx + 50, 112), (240, 240, 232, 255))
        F = FACE["samir"]; W_, H_ = cv.im.size                                        # a full, trimmed beard that follows the jaw:
        xs = np.arange(W_) / SS - cx; ys = np.arange(H_)[:, None] / SS                    # it starts at the sideburns and comes down
        yb = np.interp(np.abs(xs), [0, 60, 120, 180, 245], [F["my"] + 26, F["my"] + 14, F["cby"] + 74, F["cby"] + 34, F["ey"] + 14])
        bm = Image.fromarray(((ys > yb[None, :]) * 255).astype(np.uint8)); bm = ImageChops.multiply(bm, hm)
        cv.put(bm, (52, 38, 32, 255), 0)
        lay = Image.new("RGBA", cv.im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)                 # a few lighter hairs for texture
        for k in range(140):
            x = cx + ((k * 47) % 440) - 220; y = F["cby"] + ((k * 71) % 230)
            ld.line([(x * SS, y * SS), ((x + 4) * SS, (y + 12) * SS)], fill=(88, 66, 54, 255), width=2 * SS)
        lay.putalpha(ImageChops.multiply(lay.getchannel("A"), bm)); cv.im.alpha_composite(lay)
    elif who == "maman":
        cv.ell((cx + 40, 95, cx + 210, 235), L["hair"])                                                   # the bun, resting on the crown
        cv.poly(bez((cx - 250, 480), (cx - 300, 140), (cx + 300, 140), (cx + 250, 480)) + [(cx + 212, 430), (cx + 170, 300), (cx + 40, 262), (cx - 80, 300), (cx - 150, 290), (cx - 212, 430)], L["hair"])
    # brows
    for s_ in (-1, 1):                                        # brows: thick and straight (Samir), thin and arched (the mother),
        x0 = cx + s_ * esp; y0 = F["by"] - (10 if wide > 1.15 else 0); bs = F["bs"]   # low and brooding (you), sharp and rising (the double)
        arch = 16 if who == "maman" else 6
        c = [(x0 - s_ * 56, y0 + 8 - brow * 26 + bs * 6), (x0 - s_ * 12, y0 - arch - brow * 12), (x0 + s_ * 30, y0 - arch - 2 - brow * 4 - bs * 6), (x0 + s_ * 62, y0 + 4 + brow * 14 - bs * 16)]
        cv.poly(lock_poly(bez(c[0], c[1], c[2], c[3], 10), F["bw"], 3), L.get("hair_lo", INK) if who in ("toi", "double") else ((90, 80, 78, 255) if who == "maman" else (30, 20, 16, 255)), 2)
    for s_ in (-1, 1): eye(cv, cx + s_ * esp, ey, s_, L, look, wide, blink, who, F)
    if who == "maman":                                                                                    # thin round glasses
        for s_ in (-1, 1): ImageDraw.Draw(cv.im).ellipse([(cx + s_ * esp - 90) * SS, (ey - 66) * SS, (cx + s_ * esp + 90) * SS, (ey + 60) * SS], outline=GOLD_D, width=5 * SS)
        cv.stroke([(cx - 24, ey - 10), (cx + 24, ey - 10)], 5, GOLD_D)
    # nose, by kind
    nl, nwd = F["nl"], F["nw"]; sk = tuple(int(v * 0.8) for v in L["skin_d"][:3]) + (255,)
    if F["nose"] == "sharp":                                  # long and thin, a hooked point
        cv.stroke(bez((cx - 6, ey - 10), (cx - 2, nl - 60), (cx - 14, nl - 20), (cx - 4, nl + 4), 12), 5, sk)
        cv.stroke(bez((cx - 18, nl - 2), (cx - 6, nl + 10), (cx + 8, nl + 8), (cx + 16, nl - 4), 10), 5)
    else:
        cv.stroke(bez((cx - 8, ey - 6), (cx - 4, nl - 50), (cx - 12, nl - 26), (cx - 14, nl - 8), 10), 4, sk)   # the bridge, in shadow colour
        cv.stroke(bez((cx - nwd, nl - 6), (cx - nwd * 0.4, nl + 12), (cx + nwd * 0.4, nl + 12), (cx + nwd, nl - 6), 10), 5)   # the tip
        if F["nose"] in ("broad", "straight"):                # nostril wings
            for s_ in (-1, 1): cv.stroke(bez((cx + s_ * nwd, nl - 6), (cx + s_ * (nwd + 12), nl - 14), (cx + s_ * (nwd + 14), nl - 30), (cx + s_ * (nwd + 4), nl - 36), 8), 4)
    # mouth
    my = F["my"]; mx = cx + look[0] * 10; k_ = F["mw"] / 40
    if who == "samir":                                        # the moustache joins the beard
        cv.poly([(mx - 58, my + 4), (mx - 40, my - 24), (mx, my - 30), (mx + 40, my - 24), (mx + 58, my + 4), (mx + 30, my - 10), (mx, my - 14), (mx - 30, my - 10)], (52, 38, 32, 255), 0)
    if who == "double":                                       # the grin: far too wide, pointed teeth
        gw = 150 if F["J"] > 140 else 118                     # as wide as the jaw allows, never past it
        g = bez((mx - gw, my - 30), (mx - gw * 0.66, my + 70), (mx + gw * 0.66, my + 70), (mx + gw, my - 30)) + bez((mx + gw, my - 30), (mx + 60, my + 10), (mx - 60, my + 10), (mx - gw, my - 30))
        cv.poly(g, (70, 10, 20, 255), 6)
        for k in range(-5, 6): x = mx + k * 25 * gw / 150; cv.poly([(x - 10, my - 10 + abs(k) * 4), (x + 10, my - 10 + abs(k) * 4), (x, my + 22)], (246, 240, 228, 255), 0)
    elif mouth == "o": cv.ell((mx - 22, my - 26, mx + 22, my + 26), (90, 26, 36, 255), 6)
    elif mouth == "smile": cv.stroke(bez((mx - 50 * k_, my - 12), (mx - 20 * k_, my + 22), (mx + 20 * k_, my + 22), (mx + 50 * k_, my - 12)), 9)
    elif mouth == "fear": cv.stroke([(mx - 44 * k_, my + 4), (mx - 22 * k_, my - 8), (mx, my + 4), (mx + 22 * k_, my - 8), (mx + 44 * k_, my + 4)], 8)
    else:
        cv.stroke(bez((mx - 40 * k_, my + 2), (mx - 14 * k_, my - 6), (mx + 14 * k_, my - 6), (mx + 40 * k_, my + 2), 10), 7)
        lw = 9 if who == "samir" else 5                       # the lower lip: full for Samir, thin for the mother
        cv.stroke(bez((mx - 22 * k_, my + 18), (mx - 8 * k_, my + 26), (mx + 8 * k_, my + 26), (mx + 22 * k_, my + 18), 8), lw, L["skin_d"])
    return cv.done(size)


def grim_bust(who, L, look, brow, mouth, wide, blink, sway, tilt, size):
    """The hybrid dark-fantasy / gritty-urban version: worn clothes with gold-thread details, a frayed cloak, grit on
    the faces, then an engraved finish (hatching in the shadows, a gold rim light, grain)."""
    cv = Canvas(1000, 1000); cx = 500 + tilt * 30
    if who in ("toi", "double"):                                   # the frayed cloak behind the shoulders, fastened on the left
        frayed = [(120, 1000), (150, 860), (230, 770), (360, 730), (640, 730), (770, 770), (850, 860), (880, 1000)]
        cv.poly(frayed, L.get("cloak", (30, 28, 34, 255)) if who == "toi" else (16, 14, 20, 255), 7)
        for k in range(9): x = 140 + k * 92; cv.poly([(x, 1000), (x + 30, 960), (x + 60, 1000)], (24, 22, 28, 255), 0)
    _draw(cv, who, L, cx, look, brow, mouth, wide, blink, sway, size, True)
    d = ImageDraw.Draw(cv.im)
    if who in ("toi", "double"):
        cv.stroke(bez((160, 1000), (170, 815), (300, 755), (420, 742)), 9, GOLD); cv.stroke(bez((580, 742), (700, 755), (830, 815), (840, 1000)), 9, GOLD)   # gold piping
        cv.ell((300, 770, 380, 850), GOLD, 6); cv.ell((318, 788, 362, 832), GOLD_D, 0); cv.ell((328, 784, 370, 826), GOLD, 0)   # the moon brooch on the cloak
        if who == "toi":
            for k in range(60):                                   # stubble
                rx = (k * 37) % 300 - 150; ry = (k * 53) % 120
                x = cx + rx * 0.9; y = 590 + ry * 0.7 - abs(rx) * 0.15
                if 430 < y < 690: d.ellipse(((x - 2) * SS, (y - 2) * SS, (x + 2) * SS, (y + 2) * SS), fill=(110, 84, 70, 200))
            cv.stroke([(cx - 150, 330), (cx - 128, 372)], 5, (150, 96, 90, 255))               # the scar through the left eyebrow
            F = FACE["toi"]; e_, y_ = F["esp"], F["ey"] + 36
            for s_ in (-1, 1): cv.stroke(bez((cx + s_ * (e_ + 44), y_ - 4), (cx + s_ * (e_ + 14), y_ + 10), (cx + s_ * (e_ - 16), y_ + 10), (cx + s_ * (e_ - 40), y_), 8), 4, tuple(int(v * 0.8) for v in L["skin_d"][:3]) + (255,))   # tired under-eyes
        else:                                                     # the double: gold-repaired cracks, black tears
            for (x0, y0, pts) in ((cx - 140, 300, [(30, 60), (10, 120), (40, 190)]), (cx + 120, 260, [(-20, 70), (10, 140), (-30, 230)]), (cx + 30, 620, [(40, 30), (20, 70)])):
                path = [(x0, y0)] + [(x0 + a, y0 + b) for a, b in pts]; cv.stroke(path, 6, GOLD)
            for s_ in (-1, 1): cv.stroke([(cx + s_ * 112, 478), (cx + s_ * 118, 540), (cx + s_ * 110, 610)], 7, (10, 8, 12, 255))
    elif who == "samir":                                          # a gold chain, a heavier beard
        cv.stroke(bez((420, 760), (450, 840), (550, 840), (580, 760)), 6, GOLD)
        for k in range(12): x = 430 + k * 13; y = 790 + 30 * math.sin((k / 11) * math.pi); d.ellipse(((x - 4) * SS, (y - 4) * SS, (x + 4) * SS, (y + 4) * SS), outline=GOLD_D, width=2 * SS)
    elif who == "maman":                                          # gold embroidery on the shawl, a rosary, a hairpin
        for k in range(10): x = 230 + k * 58; cv.stroke([(x, 820 + 18 * math.sin(k)), (x + 28, 840)], 4, GOLD)
        for k in range(14): t_ = k / 13; x = 460 + 80 * t_; y = 800 + 160 * math.sin(t_ * math.pi) ; d.ellipse(((x - 5) * SS, (y - 5) * SS, (x + 5) * SS, (y + 5) * SS), fill=(120, 60, 50, 255))
        cv.stroke([(cx + 90, 120), (cx + 190, 190)], 6, GOLD)
    return engrave(cv.done(size), shade=cv.shade.resize((size, size), Image.BILINEAR))


def engrave(img, hatch=9, rim=(214, 176, 96), shade=None):
    """Engraved finish: diagonal hatching only in the darker parts, a thin gold rim light on the right edge, grain."""
    a = np.asarray(img).astype(np.float32); rgb, al = a[..., :3], a[..., 3:]
    lum = rgb.mean(axis=2); h, w = lum.shape; yy, xx = np.mgrid[0:h, 0:w]
    body = al[..., 0] > 200
    keep = (rgb.max(axis=2) - rgb.min(axis=2)) > 100                                            # signature colours (blue lock, red eyes) stay vivid
    orig = rgb.copy()
    gray = lum[..., None]; rgb[:] = rgb * 0.72 + gray * 0.28                                     # gritty-urban grade: 28 % less colour,
    rgb *= np.array([1.0, 0.97, 0.86])                                                          # then a warm sepia cast
    rgb[keep] = orig[keep]
    shade = (np.asarray(shade) > 128) & body if shade is not None else np.zeros_like(body)     # the form shadows of the face
    lines = ((xx + yy) % hatch < 1.6) & ((lum < 120) | shade) & body
    rgb[lines] *= 0.55
    cross = ((xx - yy) % hatch < 1.4) & shade & (lum < 90)                                      # cross-hatching in the deepest shadow
    rgb[cross] *= 0.6
    edge = cv2.dilate((al[..., 0] > 128).astype(np.uint8), np.ones((5, 5), np.uint8)) - (al[..., 0] > 128).astype(np.uint8)
    shift = np.roll(edge, -4, axis=1).astype(bool) & (al[..., 0] > 128) & (xx > w * 0.5)
    rgb[shift] = rgb[shift] * 0.3 + np.array(rim) * 0.7
    rgb += np.random.default_rng(7).normal(0, 6, rgb.shape) * (al > 0)
    return Image.fromarray(np.clip(np.concatenate([rgb, al], axis=2), 0, 255).astype(np.uint8), "RGBA")


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
    G = "--grim" in sys.argv
    if G:
        S = Image.new("RGB", (4 * 420 + 40, 4 * 450 + 40), (28, 30, 34)); d = ImageDraw.Draw(S)
        for r, (who, name) in enumerate(rows):
            for c, (e, kw) in enumerate(exps):
                if who == "double" and c > 0: kw = dict(kw, mouth="line")
                b = bust(who, size=400, grim=True, **kw); S.paste(b, (20 + c * 420, 20 + r * 450), b); d.text((30 + c * 420, 425 + r * 450), f"{name} · {e}", fill=(200, 190, 160))
    S.save(sys.argv[1] if len(sys.argv) > 1 else "/home/user/persos_v3.jpg", quality=90); print("ok")

