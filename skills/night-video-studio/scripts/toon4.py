"""Season 2 characters, v10: drawn from scratch after the creator's model (a semi-realistic portrait) and the
Spider-Verse-style "animatic -> render -> final" reference (chazee_xiao): every shape gets a height map (skull, brow
ridge, sockets, cheekbones, nose, lips, chin, hair clumps, cloth folds), is lit like a 3D render, then turned into a
2D comic image: three flat tones, halftone dots in the half-shadow, engraved hatching in the deep shadow, a coloured
rim light, ink whose weight grows on the shadow side, a slight print misregistration and paper grain.

Themes: night city (a warm sodium key light from the right, a cold moonlight rim from the left, sepia grade), dark
fantasy (gold metal: the moon brooch, the chain, the glasses, the double's cracks), comic engraving.

bust4(who, look=(x, y), brow, mouth, wide, blink, sway) -> RGBA 1000x1250 image.
who: "toi", "samir", "maman", "double"; mouth: "line", "smile", "o", "fear"."""
import math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter

S = 2                                    # supersampling
W, H = 1000, 1250
INK = np.array([22, 16, 30], np.float32)
KEY = np.array([0.55, -0.5, 0.67]); KEY /= np.linalg.norm(KEY)          # sodium street lamp, upper right
RIM = np.array([-0.9, -0.25, -0.15]); RIM /= np.linalg.norm(RIM)        # moonlight from behind, left
HALF = KEY + np.array([0, 0, 1.0]); HALF /= np.linalg.norm(HALF)
RAMP = (np.array([0.47, 0.43, 0.62]), np.array([0.86, 0.8, 0.79]), np.array([1.06, 0.99, 0.88]))   # shadow, mid, light
RIM_C = np.array([120, 150, 255], np.float32)
GOLD = (206, 166, 84); GOLD_D = (128, 96, 44)


def bez(p0, p1, p2, p3, n=24):
    return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0],
             (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]) for t in (k / n for k in range(n + 1))]


def taper(center, w0, w1=2):
    n = len(center); left, right = [], []
    for i, (x, y) in enumerate(center):
        a, b = center[max(0, i - 1)], center[min(n - 1, i + 1)]; dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        w = w0 + (w1 - w0) * i / (n - 1); left.append((x - dy / l * w, y + dx / l * w)); right.append((x + dy / l * w, y - dx / l * w))
    return left + right[::-1]


def P(pts): return [(x * S, y * S) for x, y in pts]
def mpoly(pts):
    m = Image.new("L", (W * S, H * S), 0); ImageDraw.Draw(m).polygon(P(pts), fill=255); return np.asarray(m) > 0
def mell(box):
    m = Image.new("L", (W * S, H * S), 0); ImageDraw.Draw(m).ellipse([v * S for v in box], fill=255); return np.asarray(m) > 0
def mline(pts, w):
    m = Image.new("L", (W * S, H * S), 0); ImageDraw.Draw(m).line(P(pts), fill=255, width=int(w * S), joint="curve"); return np.asarray(m) > 0


YY, XX = np.mgrid[0:H * S, 0:W * S].astype(np.float32) / S


def g(cx, cy, sx, sy, amp):
    return amp * np.exp(-(((XX - cx) / sx) ** 2 + ((YY - cy) / sy) ** 2) / 2)


def seg(p0, p1, sigma, amp):
    """A gaussian ridge (amp > 0) or crease (amp < 0) along a segment."""
    (x0, y0), (x1, y1) = p0, p1; dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy or 1
    t = np.clip(((XX - x0) * dx + (YY - y0) * dy) / L2, 0, 1)
    d2 = (XX - x0 - t * dx) ** 2 + (YY - y0 - t * dy) ** 2
    return amp * np.exp(-d2 / (2 * sigma * sigma))


def dome(m, R):
    d = cv2.distanceTransform(m.astype(np.uint8), cv2.DIST_L2, 5) / S
    t = np.clip(d / R, 0, 1); return (R * np.sqrt(1 - (1 - t) ** 2)).astype(np.float32)


def ss(a, b, x): t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)


class Canvas:
    def __init__(self):
        self.rgb = np.zeros((H * S, W * S, 3), np.float32); self.a = np.zeros((H * S, W * S), np.float32)
        self.inkl = np.zeros((H * S, W * S), np.float32)         # ink coverage, for the misregistration pass
    def over(self, rgb, a, box=None, ink=False):
        y0, y1, x0, x1 = box or (0, H * S, 0, W * S)
        R, A = self.rgb[y0:y1, x0:x1], self.a[y0:y1, x0:x1]
        a3 = a[..., None]; R[:] = rgb * a3 + R * (1 - a3); A[:] = a + A * (1 - a)
        I = self.inkl[y0:y1, x0:x1]
        I[:] = np.maximum(I * (1 - a), a) if ink else I * (1 - a)
    def layer(self):
        im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)
    def put(self, im):
        a = np.asarray(im).astype(np.float32) / 255; self.over(a[..., :3] * 255, a[..., 3])

    def shade(self, mask, albedo, h=None, R=40, line=(2.4, 5.5), dots=True, spec=0.0, rim=1.0, gloss=0.86, flat=0.0):
        """Light a shape like a 3D render, then draw it as a comic panel."""
        ys, xs = np.nonzero(mask)
        if len(ys) == 0: return
        pad = int(10 * S); y0, y1 = max(0, ys.min() - pad), min(H * S, ys.max() + pad); x0, x1 = max(0, xs.min() - pad), min(W * S, xs.max() + pad)
        m = mask[y0:y1, x0:x1]; X, Y = XX[y0:y1, x0:x1], YY[y0:y1, x0:x1]
        hh = dome(m, R) if h is None else h[y0:y1, x0:x1].astype(np.float32)
        hb = cv2.GaussianBlur(hh, (0, 0), 1.2 * S)
        hx = np.gradient(hb, axis=1) * S; hy = np.gradient(hb, axis=0) * S
        nz = 1 / np.sqrt(hx * hx + hy * hy + 1); nx, ny = -hx * nz, -hy * nz
        if flat: nx, ny, nz = nx * (1 - flat), ny * (1 - flat), nz * (1 - flat) + flat
        d = np.clip(nx * KEY[0] + ny * KEY[1] + nz * KEY[2], 0, 1)
        ao = np.clip(1 - np.maximum(0, cv2.GaussianBlur(hb, (0, 0), 7 * S) - hb) * 0.05, 0.5, 1)
        d = d * (0.55 + 0.45 * ao)
        t1, t2 = ss(0.33, 0.37, d), ss(0.70, 0.73, d)                          # three flat tones
        ramp = RAMP[0][None, None] + (RAMP[1] - RAMP[0])[None, None] * t1[..., None] + (RAMP[2] - RAMP[1])[None, None] * t2[..., None]
        alb = np.broadcast_to(np.array(albedo, np.float32)[:3], hh.shape + (3,)) if isinstance(albedo, tuple) else albedo[y0:y1, x0:x1]
        col = alb * ramp
        col *= (0.75 + 0.25 * ao)[..., None]
        if dots:                                                             # halftone in the half-shadow
            u, v = (X + Y) * 0.7071, (X - Y) * 0.7071; p = 6.5
            fu, fv = (u % p) - p / 2, (v % p) - p / 2
            dark = np.clip((0.40 - d) / 0.24, 0, 1) * (d > 0.13)
            col[(fu * fu + fv * fv) < (p * 0.48 * dark) ** 2] *= 0.74
            col[(((X - Y) % 6.0) < 1.1) & (d <= 0.13)] *= 0.62                 # hatching in the deep shadow
        if rim:
            r = np.clip(nx * RIM[0] + ny * RIM[1] + nz * RIM[2], 0, 1) * (1 - nz) ** 1.1
            col += RIM_C * 0.38 * rim * ss(0.3, 0.34, r)[..., None]
        if spec:
            s_ = np.clip(nx * HALF[0] + ny * HALF[1] + nz * HALF[2], 0, 1) ** 60
            col += 255 * spec * ss(gloss - 0.04, gloss, s_ ** 0.25)[..., None]
        k1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * line[0] * S) | 1,) * 2)
        k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * line[1] * S) | 1,) * 2)
        mu = m.astype(np.uint8); cxm = xs.mean() / S
        thin = cv2.dilate(mu, k1) > 0; thick = (cv2.dilate(mu, k2) > 0) & ((X < cxm) | (Y > ys.max() / S - 30))
        inkm = (thin | thick) & ~m
        if line[0] > 0:
            ink_a = cv2.GaussianBlur(inkm.astype(np.float32), (0, 0), 0.5 * S)
            self.over(np.broadcast_to(INK, hh.shape + (3,)), ink_a, (y0, y1, x0, x1), ink=True)
        a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5 * S)
        self.over(np.clip(col, 0, 255), a, (y0, y1, x0, x1))

    def ink(self, pts, w, col=(22, 16, 30), alpha=1.0):
        im, d = self.layer(); d.line(P(pts), fill=tuple(col) + (int(255 * alpha),), width=max(1, int(w * S)), joint="curve"); self.put(im)

    def done(self, grade=True):
        rgb = self.rgb.copy(); a = self.a
        if grade:                                                            # night-city grade, signature colours kept
            keep = (rgb.max(axis=2) - rgb.min(axis=2)) > 110
            lum = rgb.mean(axis=2, keepdims=True); gr = (rgb * 0.8 + lum * 0.2) * np.array([1.0, 0.96, 0.88])
            rgb = np.where(keep[..., None], rgb, gr)
        sh = np.roll(self.inkl, (int(1.5 * S), int(1.5 * S)), axis=(0, 1))       # print misregistration: a red ghost of the ink
        rgb[..., 0] = rgb[..., 0] * (1 - sh * 0.35 * (1 - self.inkl)) + 150 * sh * 0.35 * (1 - self.inkl)
        rgb += np.random.default_rng(4).normal(0, 5, rgb.shape).astype(np.float32) * (a[..., None] > 0)   # paper grain
        out = np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8)
        return Image.fromarray(out, "RGBA").resize((W, H), Image.LANCZOS)


# ---------------------------------------------------------------- the characters
FACE = dict(
    toi=dict(T=150, C=158, cby=440, J=130, jy=548, K=38, chy=620, ey=396, esp=66, ew=34, eh=13, lift=5, ir=13,
             by=362, bw=9, bs=-0.6, nb=488, nw=23, nh=16, my=540, mw=34, lipf=1.0, brow_r=1.0, cb=1.0, hollow=0.5, socket=1.0, chin=1.0,
             skin=(222, 180, 148), lip=(178, 112, 100), iris=(54, 92, 200), neck=82),
    samir=dict(T=168, C=178, cby=446, J=160, jy=560, K=74, chy=616, ey=398, esp=70, ew=33, eh=13, lift=1, ir=13,
               by=364, bw=12, bs=0.0, nb=494, nw=32, nh=14, my=546, mw=38, lipf=1.4, brow_r=1.1, cb=0.8, hollow=0.2, socket=0.9, chin=0.8,
               skin=(176, 122, 88), lip=(128, 74, 64), iris=(104, 66, 38), neck=94),
    maman=dict(T=158, C=164, cby=446, J=144, jy=540, K=58, chy=604, ey=400, esp=64, ew=31, eh=12, lift=-1, ir=12,
               by=358, bw=5, bs=0.6, nb=484, nw=20, nh=11, my=532, mw=30, lipf=0.7, brow_r=0.6, cb=0.7, hollow=0.0, socket=0.8, chin=0.6,
               skin=(232, 196, 170), lip=(184, 120, 116), iris=(104, 74, 48), neck=76),
    double=dict(T=146, C=152, cby=430, J=116, jy=560, K=26, chy=650, ey=392, esp=66, ew=36, eh=12, lift=10, ir=13,
                by=352, bw=8, bs=1.2, nb=500, nw=18, nh=20, my=560, mw=34, lipf=0.6, brow_r=1.4, cb=1.4, hollow=1.3, socket=2.0, chin=1.2,
                skin=(176, 180, 188), lip=(120, 110, 120), iris=(240, 30, 30), neck=70),
)
CLOTH = dict(toi=((80, 58, 120), (40, 38, 48)), double=((80, 58, 120), (30, 28, 36)), samir=((92, 110, 72), (120, 124, 136)), maman=((104, 58, 86), (238, 226, 206)))


def head_pts(cx, F):
    T, C, cby, J, jy, K, chy = F["T"], F["C"], F["cby"], F["J"], F["jy"], F["K"], F["chy"]
    dome_ = bez((cx - T, 330), (cx - T - 8, 120), (cx + T + 8, 120), (cx + T, 330))
    right = bez((cx + T, 330), (cx + C + 4, cby - 50), (cx + C, cby + 10), (cx + J, jy), 16) + bez((cx + J, jy), (cx + J - (J - K) * 0.25, jy + (chy - jy) * 0.6), (cx + K + (J - K) * 0.3, chy), (cx + K, chy), 16)
    return dome_ + right + [(2 * cx - x, y) for x, y in reversed(right)]


def face_height(cx, F, who, mouth, brow, wide):
    ey, esp, nb, my = F["ey"], F["esp"], F["nb"], F["my"]
    h = np.zeros_like(XX)
    for s in (-1, 1):
        h += g(cx + s * 60, F["by"] + 4, 44, 12, 9 * F["brow_r"])                  # brow ridge
        h += g(cx + s * esp, ey + 2, 36, 22, -15 * F["socket"])                    # eye socket
        h += g(cx + s * esp, ey + 2, 24, 13, 6)                                    # the eyeball under the lids
        h += g(cx + s * (esp + 36), ey + 44, 38, 24, 12 * F["cb"])                 # cheekbone
        h += g(cx + s * (esp + 28), ey + 104, 34, 32, -10 * F["hollow"])           # hollow under it
        h += g(cx + s * 140, ey - 70, 30, 40, -3)                                  # temple
        h += seg((cx + s * (F["nw"] + 8), nb - 6), (cx + s * (F["mw"] + 10), my + 6), 4.5, -4 * (1.6 if who in ("maman", "double") else 0.8))   # nose-to-mouth fold
        h += g(cx + s * F["nw"] * 0.85, nb - 8, 11, 10, 7)                         # nostril wings
        h += g(cx + s * F["nw"] * 0.42, nb + 1, 6, 3.5, -6)                        # nostrils
    h += g(cx, F["by"] + 2, 26, 12, 6)                                             # between the brows
    ramp = np.clip((YY - (ey - 26)) / (nb - ey + 26), 0, 1) ** 1.25 * (YY < nb + 4)
    h += F["nh"] * ramp * np.exp(-((XX - cx) / 11) ** 2 / 2)                       # the nose bridge
    h += g(cx, nb - 13, F["nw"] * 0.55, 13, 10)                                    # nose tip
    h += g(cx, nb + 18, 7, 11, -2.5)                                               # philtrum
    open_ = mouth in ("o", "fear")
    if not open_:
        h += g(cx, my - 6, F["mw"] * 0.75, 6, 5 * F["lipf"]); h += g(cx, my + 9, F["mw"] * 0.68, 8, 7 * F["lipf"])   # lips
        h += g(cx, my + (0 if mouth != "smile" else -2), F["mw"], 2.0, -6)          # the mouth line
    h += g(cx, my + 30, 22, 6, -4)                                                 # under the lower lip
    h += g(cx, F["chy"] - 26, 34, 22, 9 * F["chin"])                               # chin
    if mouth == "smile":
        for s in (-1, 1): h += g(cx + s * (esp + 20), ey + 70, 30, 20, 6)           # cheeks lift
    if who == "maman":
        for y in (296, 314, 330): h += seg((cx - 80, y + 4), (cx + 80, y + 4), 2.2, -1.2)   # forehead lines
        for s in (-1, 1):
            for k in (-8, 4): h += seg((cx + s * (esp + F["ew"] + 2), ey + k * 0.6), (cx + s * (esp + F["ew"] + 22), ey + k * 1.8), 2, -3)   # crow's feet
    if who == "double":
        for s in (-1, 1): h += seg((cx + s * 74, ey + 30), (cx + s * 86, ey + 130), 4, -6)   # gaunt lines down the cheeks
    return h


def eye4(cv, cx, cy, side, F, look, wide, blink, who):
    w = F["ew"]; h = F["eh"] * (1 + 0.9 * max(0.0, wide - 1)); lift = F["lift"]
    def top(u): return (cx + side * u * w, cy - lift * (u + 1) / 2 + lift * 0.3 - h * (1 - u * u) ** 0.75)
    def bot(u): return (cx + side * u * w, cy - lift * (u + 1) / 2 + lift * 0.3 + h * 0.75 * (1 - u * u) ** 1.2)
    up = [top(u / 16) for u in range(-16, 17)]; lo = [bot(u / 16) for u in range(16, -17, -1)]
    if blink:
        cv.ink([bot(u / 12)[0:1] + (bot(u / 12)[1] - h * 0.4,) for u in range(-12, 13)], 3.2); return
    im, d = cv.layer()
    d.polygon(P(up + lo), fill=(232, 226, 220, 255))
    ix, iy, ir = cx + look[0] * w * 0.42, cy + look[1] * h * 0.5 + 1, F["ir"] * (0.85 if wide > 1.15 else 1)
    iris = F["iris"]
    def E(x, y, r, c): d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=c)
    E(ix, iy, ir, tuple(int(v * 0.45) for v in iris) + (255,)); E(ix, iy, ir * 0.86, iris + (255,))
    E(ix, iy + ir * 0.3, ir * 0.5, tuple(min(255, int(v * 1.35)) for v in iris) + (255,))
    for a_ in range(0, 360, 20):
        ca, sa = math.cos(math.radians(a_)), math.sin(math.radians(a_))
        d.line([((ix + ca * ir * 0.42) * S, (iy + sa * ir * 0.42) * S), ((ix + ca * ir * 0.82) * S, (iy + sa * ir * 0.82) * S)], fill=tuple(int(v * 0.65) for v in iris) + (255,), width=S)
    E(ix, iy, ir * (0.4 if who != "double" else 0.14), (12, 10, 18, 255))
    d.polygon(P(up + [(x, y + h * 0.55) for x, y in reversed(up)]), fill=(40, 24, 30, 70))   # the lid's shadow on the eye
    if who != "double": E(ix + ir * 0.32, iy - ir * 0.34, ir * 0.2, (255, 255, 255, 235))
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).polygon(P(up + lo), fill=255)
    im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(m)))); cv.put(im)
    if who == "double":                                                     # the red eyes glow
        gl, gd = cv.layer(); E2 = lambda r, a: gd.ellipse([(ix - r) * S, (iy - r) * S, (ix + r) * S, (iy + r) * S], fill=(255, 40, 30, a))
        E2(ir * 2.0, 70); cv.put(gl.filter(ImageFilter.GaussianBlur(6 * S)))
    cv.ink(up, 3.4); cv.ink(lo[3:-3], 1.3, (120, 70, 66), 0.8)
    oc = up[-1]; cv.ink([oc, (oc[0] + side * 7, oc[1] - 4)], 3)                                 # outer corner
    cv.ink([(x, y - 7 - 3 * (1 - abs(i - 16) / 16)) for i, (x, y) in enumerate(up) if 6 <= i <= 28], 1.4, (90, 56, 52), 0.85)   # lid crease
    for k in range(5):                                                                            # lashes at the outer half
        x, y = up[18 + k * 3]; cv.ink([(x, y), (x + side * (3 + k), y - 4 - k * 0.6)], 1.2)


def brow4(cv, cx, F, side, brow, wide, col):
    x0 = cx + side * F["esp"]; y0 = F["by"] - (6 if wide > 1.15 else 0); bs = F["bs"]
    c = [(x0 - side * 40, y0 + 6 - brow * 14 + bs * 3), (x0 - side * 10, y0 - 3 - brow * 7), (x0 + side * 22, y0 - 4 - brow * 2 - bs * 3), (x0 + side * 44, y0 + 4 + brow * 8 - bs * 8)]
    path = bez(*c, 20); im, d = cv.layer()
    d.polygon(P(taper(path, F["bw"] * 0.55, 1.2)), fill=col + (235,))
    hi = tuple(min(255, v + 50) for v in col)
    for j in range(0, 20):                                                       # single hairs combed outwards
        x, y = path[j]; wj = F["bw"] * 0.6 * (1 - j / 24)
        d.line([((x - side * 3) * S, (y + wj) * S), ((x + side * 7) * S, (y - wj) * S)], fill=(hi if j % 3 == 0 else col) + (255,), width=S)
    cv.put(im)


def mouth4(cv, cx, F, mouth, who, look):
    my, mw = F["my"], F["mw"]; mx = cx + look[0] * 4
    if who == "double":                                                          # the grin, as wide as the jaw allows
        gw = min(110, F["J"] - 10)
        cv.shade(mpoly(bez((mx - gw, my - 18), (mx - gw * 0.6, my + 44), (mx + gw * 0.6, my + 44), (mx + gw, my - 18)) + bez((mx + gw, my - 18), (mx + 40, my + 6), (mx - 40, my + 6), (mx - gw, my - 18))),
                 (90, 14, 26), R=8, line=(2.0, 3.4), dots=False, rim=0)
        im, d = cv.layer()
        for k in range(-6, 7):
            x = mx + k * gw / 7.2; yt = my - 4 + abs(k) * 2.6
            d.polygon(P([(x - 6, yt), (x + 6, yt), (x, yt + 16 - abs(k) * 0.6)]), fill=(240, 232, 214, 255))
            d.polygon(P([(x - 5, yt + 30 - abs(k) * 2), (x + 5, yt + 30 - abs(k) * 2), (x, yt + 18 - abs(k) * 1.4)]), fill=(222, 212, 194, 255))
        cv.put(im); return
    lip = F["lip"]
    if mouth == "o":
        cv.shade(mell((mx - 15, my - 18, mx + 15, my + 20)), (60, 18, 26), R=6, line=(2.2, 3.0), dots=False, rim=0)
        cv.shade(mell((mx - 10, my - 15, mx + 10, my - 9)), (226, 218, 204), R=3, line=(0, 0), dots=False, rim=0)
        return
    if mouth == "fear":
        cv.shade(mpoly([(mx - mw * 0.8, my + 2), (mx - mw * 0.3, my - 4), (mx + mw * 0.3, my - 4), (mx + mw * 0.8, my + 2), (mx + mw * 0.3, my + 12), (mx - mw * 0.3, my + 12)]), (60, 18, 26), R=4, line=(1.8, 2.4), dots=False, rim=0)
        cv.shade(mpoly([(mx - mw * 0.5, my - 2), (mx + mw * 0.5, my - 2), (mx + mw * 0.42, my + 3), (mx - mw * 0.42, my + 3)]), (226, 218, 204), R=2, line=(0, 0), dots=False, rim=0)
        return
    up = 0 if mouth != "smile" else 1
    line = bez((mx - mw, my - 2 * up * 4), (mx - mw * 0.4, my + 3 + up * 6), (mx + mw * 0.4, my + 3 + up * 6), (mx + mw, my - 2 * up * 4), 14)
    cv.ink(line, 2.4, (70, 36, 38))
    for s in (-1, 1): cv.ink([(mx + s * mw, my - 1 - up * 8), (mx + s * (mw + 5), my + 2 - up * 12)], 1.8, (90, 50, 48), 0.8)   # mouth corners


def bust4(who="toi", look=(0.0, 0.0), brow=0.0, mouth="line", wide=1.0, blink=False, sway=0.0):
    F = FACE[who]; cv = Canvas(); cx = 500
    top, sec = CLOTH[who]
    # ---------- body and clothes
    sh = [(cx - F["neck"] - 4, 640), (cx - 290, 700), (cx - 410, 800), (cx - 450, 1250), (cx + 450, 1250), (cx + 410, 800), (cx + 290, 700), (cx + F["neck"] + 4, 640)]
    if who in ("toi", "double"):                                                 # frayed cloak behind
        cl = [(cx - 470, 1250), (cx - 452, 840), (cx - 300, 730), (cx + 300, 730), (cx + 452, 840), (cx + 470, 1250)]
        cv.shade(mpoly(cl), (36, 34, 42) if who == "toi" else (22, 20, 26), R=60)
        hood = mpoly(bez((cx - 190, 780), (cx - 170, 640), (cx + 170, 640), (cx + 190, 780)))
        cv.shade(hood, sec, R=40)
        hb = mpoly(sh); hh = dome(hb, 120)
        for s in (-1, 1):                                                        # leather folds
            hh = hh + seg((cx + s * 200, 900), (cx + s * 260, 1200), 10, -8) + seg((cx + s * 330, 880), (cx + s * 350, 1150), 8, -6)
        cv.shade(hb, top, h=hh, spec=0.3, gloss=0.94)
        cv.shade(mpoly([(cx - 92, 760), (cx + 92, 760), (cx + 120, 1250), (cx - 120, 1250)]), sec, R=40)   # the hoodie between the panels
        for s in (-1, 1):
            cv.shade(mpoly([(cx + s * 92, 700), (cx + s * 150, 690), (cx + s * 160, 640), (cx + s * 100, 655)]), tuple(int(v * 0.8) for v in top), R=10, spec=0.4)   # collar
            cv.ink(bez((cx + s * 80, 760), (cx + s * 150, 800), (cx + s * 230, 900), (cx + s * 300, 1250)), 4, GOLD)                     # gold piping
        cv.shade(mell((cx - 250, 820, cx - 170, 900)), GOLD, R=12, spec=1.0, gloss=0.8, rim=0.3)                                          # the moon brooch
        cv.shade(mell((cx - 236, 832, cx - 196, 872)), GOLD_D, R=6, line=(0, 0), dots=False)
        cv.shade(mell((cx - 226, 828, cx - 186, 866)), GOLD, R=6, line=(0, 0), spec=1.0)
    elif who == "samir":
        hood = mpoly(bez((cx - 200, 790), (cx - 180, 650), (cx + 180, 650), (cx + 200, 790)))
        cv.shade(hood, sec, R=40)
        hb = mpoly(sh); hh = dome(hb, 140)
        for k in range(6): y = 850 + k * 70; hh = hh + seg((cx - 460, y + 20), (cx, y - 8), 6, -10) + seg((cx, y - 8), (cx + 460, y + 20), 6, -10)   # quilting
        cv.shade(hb, top, h=hh, spec=0.12, gloss=0.94)
        cv.shade(mpoly([(cx - 110, 680), (cx + 110, 680), (cx + 116, 760), (cx - 116, 760)]), tuple(int(v * 0.85) for v in top), R=20)   # collar
        cv.ink([(cx, 760), (cx, 1250)], 3)
    elif who == "maman":
        hb = mpoly(sh); hh = dome(hb, 130)
        for s in (-1, 1): hh = hh + seg((cx + s * 120, 820), (cx + s * 160, 1250), 12, -10)
        cv.shade(hb, top, h=hh)
        cv.shade(mpoly([(cx - 100, 670), (cx + 100, 670), (cx + 112, 760), (cx, 800), (cx - 112, 760)]), sec, R=26)          # turtleneck
        for k in range(3): cv.ink([(cx - 96 + k * 3, 690 + k * 20), (cx + 96 - k * 3, 690 + k * 20)], 1.5, (170, 156, 140), 0.8)
        for s in (-1, 1): cv.shade(mpoly([(cx + s * 112, 770), (cx + s * 20, 1250), (cx + s * 140, 1250), (cx + s * 190, 800)]), tuple(int(v * 0.78) for v in top), R=30)
        for s in (-1, 1): cv.ink([(cx + s * 112, 770), (cx + s * 20, 1250)], 3, GOLD)                 # gold trim on the cardigan
    # ---------- neck, with the jaw's shadow on it
    nk = mpoly([(cx - F["neck"], 540), (cx + F["neck"], 540), (cx + F["neck"] + 10, 720), (cx - F["neck"] - 10, 720)])
    nh = dome(nk, 70) + seg((cx - 40, 620), (cx - 60, 720), 8, 4) + seg((cx + 40, 620), (cx + 60, 720), 8, 4) + g(cx, F["chy"] + 10, 60, 30, -30)
    cv.shade(nk, F["skin"], h=nh)
    if who in ("toi", "double"):                                                 # headphones round the neck
        cv.shade(mline(bez((cx - 170, 700), (cx - 150, 790), (cx + 150, 790), (cx + 170, 700)), 16), (36, 34, 44), R=6, spec=0.6)
        for s in (-1, 1):
            cv.shade(mell((cx + s * 180 - 44, 650, cx + s * 180 + 44, 760)), (36, 34, 44), R=20, spec=0.7)
            cv.shade(mell((cx + s * 180 - 22, 676, cx + s * 180 + 22, 734)), top, R=8, line=(0, 0))
    if who == "samir":                                                           # the gold chain
        for k in range(18):
            t = k / 17; x = cx - 90 + 180 * t; y = 700 + 60 * math.sin(t * math.pi)
            cv.shade(mell((x - 6, y - 4, x + 6, y + 4)), GOLD, R=3, line=(1.0, 1.4), spec=1.0, dots=False)
    if who == "maman":                                                           # the rosary
        for k in range(16):
            t = k / 15; x = cx - 60 + 120 * t; y = 790 + 150 * math.sin(t * math.pi)
            cv.shade(mell((x - 6, y - 6, x + 6, y + 6)), (130, 60, 52), R=4, line=(1.0, 1.4), spec=0.8, dots=False)
    # ---------- ears
    for s in (-1, 1):
        e = mpoly(bez((cx + s * (F["T"] - 4), F["ey"] - 30), (cx + s * (F["T"] + 30), F["ey"] - 40), (cx + s * (F["T"] + 30), F["ey"] + 60), (cx + s * (F["T"] - 2), F["ey"] + 80)))
        eh = dome(e, 14) + seg((cx + s * (F["T"] + 12), F["ey"] - 20), (cx + s * (F["T"] + 16), F["ey"] + 50), 4, -6)
        cv.shade(e, F["skin"], h=eh, rim=1.2)
        if who == "samir" and s < 0: cv.shade(mell((cx - F["T"] - 16, F["ey"] + 60, cx - F["T"] - 4, F["ey"] + 72)), GOLD, R=3, spec=1, dots=False, line=(1, 1.2))
    # ---------- head
    hm = mpoly(head_pts(cx, F))
    hh = dome(hm, 80) + 1.35 * face_height(cx, F, who, mouth, brow, wide)
    alb = np.broadcast_to(np.array(F["skin"], np.float32), hm.shape + (3,)).copy()
    lipm = (g(cx, F["my"] - 6, F["mw"] * 0.75, 6, 1) + g(cx, F["my"] + 9, F["mw"] * 0.68, 8, 1)) if mouth not in ("o", "fear") else np.zeros_like(XX)
    alb += (np.array(F["lip"], np.float32) - alb) * np.clip(lipm * 1.6, 0, 1)[..., None] * (who != "double")
    if who == "toi":                                                             # stubble: a blue-grey cast on the jaw and upper lip
        stub = np.clip(g(cx, F["my"] + 30, 120, 60, 1) + g(cx, F["my"] - 22, 40, 8, 0.8) - lipm * 2, 0, 1) * (YY > F["nb"] + 6)
        alb *= (1 - 0.18 * stub)[..., None]; alb[..., 2] += 8 * stub
    if who == "maman":
        for s in (-1, 1): alb += np.array([30, -8, -6], np.float32) * g(cx + s * (F["esp"] + 18), F["ey"] + 56, 24, 12, 1)[..., None]   # blush
    if who == "samir":                                                           # the beard, from the sideburns down the jaw
        bx = np.abs(XX - cx); yb = np.interp(bx, [0, 40, 90, 140, 175], [F["my"] + 20, F["my"] + 10, F["cby"] + 50, F["cby"] + 10, F["ey"] + 10])
        beard = (YY > yb) & ~((((XX - cx) / (F["mw"] * 0.95)) ** 2 + ((YY - F["my"] - 4) / 15) ** 2) < 1)
        mous = mpoly([(cx - F["mw"] - 8, F["my"] + 2), (cx - F["mw"] * 0.7, F["my"] - 14), (cx - 10, F["nb"] + 14), (cx, F["nb"] + 18), (cx + 10, F["nb"] + 14), (cx + F["mw"] * 0.7, F["my"] - 14), (cx + F["mw"] + 8, F["my"] + 2), (cx + F["mw"] * 0.5, F["my"] - 6), (cx, F["my"] - 8), (cx - F["mw"] * 0.5, F["my"] - 6)])
        bm = (beard | mous).astype(np.float32); bm = cv2.GaussianBlur(bm, (0, 0), 1.5 * S)
        alb = alb * (1 - bm[..., None]) + np.array([46, 34, 30], np.float32) * bm[..., None]
        hh = hh + bm * 5
    if who == "double":
        alb = alb * (1 - 0.35 * np.clip(g(cx - 66, F["ey"], 40, 26, 1) + g(cx + 66, F["ey"], 40, 26, 1), 0, 1))[..., None]   # bruised sockets
    cv.shade(hm, alb, h=hh, spec=0.14, gloss=0.95, R=80)
    if who == "samir":                                                           # beard hairs
        im, d = cv.layer(); rng = np.random.default_rng(2)
        ys_, xs_ = np.nonzero(hm & (bm > 0.5))
        for i in rng.choice(len(ys_), 900, replace=False):
            x, y = xs_[i] / S, ys_[i] / S; ang = 1.2 + (x - cx) / 300
            d.line([(x * S, y * S), ((x + 5 * math.cos(ang)) * S, (y + 5 * math.sin(ang)) * S)], fill=(92, 72, 60, 200) if i % 3 else (20, 14, 12, 220), width=S)
        cv.put(im)
    if who == "toi":
        im, d = cv.layer(); rng = np.random.default_rng(3)                       # fine stubble hairs, the scar
        for _ in range(500):
            x = cx + rng.uniform(-120, 120); y = rng.uniform(F["my"] - 26, F["chy"] - 6)
            if hm[int(y * S), int(x * S)] and not (abs(x - cx) < F["mw"] and abs(y - F["my"] - 3) < 14): d.line([(x * S, y * S), ((x + 1) * S, (y + 3) * S)], fill=(60, 50, 56, 110), width=S)
        cv.put(im)
        cv.ink([(cx - 112, 318), (cx - 98, 360), (cx - 92, 390)], 3.2, (150, 62, 60)); cv.ink([(cx - 84, 426), (cx - 76, 462)], 2.6, (150, 62, 60))
    if who == "double":                                                          # gold-repaired cracks, black tears
        for path in (bez((cx - 96, 290), (cx - 80, 340), (cx - 110, 380), (cx - 90, 430), 8), bez((cx + 90, 270), (cx + 70, 330), (cx + 104, 380), (cx + 80, 450), 8), bez((cx + 30, F["my"] + 20), (cx + 50, F["my"] + 50), (cx + 40, F["my"] + 70), (cx + 60, F["chy"] - 10), 6)):
            cv.ink(path, 4.5, GOLD_D); cv.ink(path, 2.2, (240, 200, 110))
        for s in (-1, 1): cv.ink(bez((cx + s * 62, F["ey"] + 12), (cx + s * 66, F["ey"] + 60), (cx + s * 58, F["ey"] + 100), (cx + s * 64, F["ey"] + 150), 10), 4, (10, 8, 12))
    # ---------- facial features
    browc = dict(toi=(26, 18, 16), double=(18, 16, 20), samir=(24, 16, 12), maman=(96, 86, 82))[who]
    for s in (-1, 1): brow4(cv, cx, F, s, brow, wide, browc)
    for s in (-1, 1): eye4(cv, cx + s * F["esp"], F["ey"], s, F, look, wide, blink, who)
    nb, nw = F["nb"], F["nw"]                                                    # nose ink: only where the light breaks
    cv.ink(bez((cx - nw * 0.95, nb - 18), (cx - nw * 1.15, nb - 2), (cx - nw * 0.8, nb + 6), (cx - nw * 0.45, nb + 4), 10), 2.4)
    cv.ink(bez((cx + nw * 0.95, nb - 18), (cx + nw * 1.15, nb - 2), (cx + nw * 0.8, nb + 6), (cx + nw * 0.45, nb + 4), 10), 1.6, (60, 36, 34), 0.8)
    mouth4(cv, cx, F, mouth, who, look)
    if who == "maman":                                                           # gold-rimmed round glasses with a glint
        im, d = cv.layer()
        for s in (-1, 1):
            ex = cx + s * F["esp"]
            d.ellipse([(ex - 52) * S, (F["ey"] - 40) * S, (ex + 52) * S, (F["ey"] + 36) * S], outline=GOLD_D + (255,), width=int(4.5 * S))
            d.ellipse([(ex - 51) * S, (F["ey"] - 39) * S, (ex + 51) * S, (F["ey"] + 35) * S], outline=GOLD + (255,), width=int(2 * S))
            d.line([((ex + 18) * S, (F["ey"] - 30) * S), ((ex + 38) * S, (F["ey"] - 10) * S)], fill=(255, 255, 255, 120), width=int(3 * S))
        d.line([((cx - 14) * S, (F["ey"] - 8) * S), ((cx + 14) * S, (F["ey"] - 8) * S)], fill=GOLD + (255,), width=int(3.5 * S))
        cv.put(im)
    # ---------- hair
    hair(cv, cx, F, who, sway, hm)
    return cv.done()


def hair(cv, cx, F, who, sway, hm):
    T, ey = F["T"], F["ey"]
    if who in ("toi", "double"):
        H0 = (44, 30, 26) if who == "toi" else (30, 24, 26)
        hl = [(cx + T - 2, ey - 40), (cx + T - 10, 312), (cx + 118, 262), (cx + 70, 242), (cx + 26, 236), (cx, 242),
              (cx - 26, 236), (cx - 70, 242), (cx - 118, 262), (cx - T + 10, 312), (cx - T + 2, ey - 40)]
        n = 40; outer = []
        for k in range(n + 1):
            a = math.pi * (1 - k / n); b = 7 * math.sin(k * math.pi / 4) ** 2
            outer.append((cx + (T + 26 + b) * math.cos(a), 340 - (260 + b) * math.sin(a)))
        mask = mpoly([(cx - T - 6, ey - 20)] + outer + [(cx + T + 6, ey - 20)] + hl)
        hh = dome(mask, 50)
        xs = [p[0] for p in reversed(hl)]; ys = [p[1] for p in reversed(hl)]
        paths = []
        for i in range(-7, 8):                                                    # clumps combed back in waves
            u = i / 7; rx = cx + u * (T - 16); ry = float(np.interp(rx, xs, ys))
            base = bez((rx, ry + 4), (rx + u * 20, ry - 60), (cx + u * T * 0.85, 120 + 26 * u * u), (cx + u * 60, 84 + 8 * u * u), 20)
            paths.append([(x + (7 + 4 * (i % 3)) * math.sin(j / 20 * 2.6 * math.pi + i * 0.7) * (1 - abs(u) * 0.4), y) for j, (x, y) in enumerate(base)])
        rid = np.zeros_like(XX)
        for p in paths:
            m_ = Image.new("L", (W * S, H * S), 0); ImageDraw.Draw(m_).line(P(p), fill=255, width=S)
            dist = cv2.distanceTransform((np.asarray(m_) == 0).astype(np.uint8), cv2.DIST_L2, 5) / S
            rid = np.maximum(rid, np.exp(-(dist / (8 + 2 * (int(p[0][0]) % 3))) ** 2) * (8 + (int(p[0][0] * 7) % 5)))
        cv.shade(mask, H0, h=hh + rid, spec=0.35, gloss=0.9, rim=1.0)
        im, d = cv.layer()                                                        # strands and the sheen band
        for p in paths:
            for off in (-6, 0, 6):
                d.line(P([(x + off * (1 - j / 22), y) for j, (x, y) in enumerate(p)]), fill=(16, 10, 10, 150), width=S)
            sg = [q for q in p if 120 < q[1] < 200]
            if len(sg) > 1: d.line(P([(x + 3, y) for x, y in sg]), fill=(150, 118, 96, 200), width=int(2 * S))
        for s in (-1, 1):                                                         # faded sides
            for k in range(9):
                y = 300 + k * 10; x = cx + s * (T - 2 + (k % 3) * 3)
                d.line(P([(x, y), (x + s * 8, y - 10)]), fill=(80, 62, 54, 220), width=S)
        a = np.asarray(im).copy(); a[..., 3] = (a[..., 3] * mask).astype(np.uint8); cv.put(Image.fromarray(a))
        lockc = (40, 70, 190) if who == "toi" else (14, 14, 22)                   # the lock over the left eye
        c = [(cx - 44 + (30 + sway * 60) * u + 12 * math.sin(u * 5.2), 240 + (ey - 34 - 240) * u) for u in (k / 15 for k in range(16))]
        lm = mpoly(taper(c, 13, 2)); cv.shade(lm, lockc, R=6, spec=1.0, gloss=0.8, line=(1.8, 3.2), dots=False)
        c2 = [(cx - 22 + (24 + sway * 40) * u + 8 * math.sin(u * 4.6 + 1), 242 + (ey - 80 - 242) * u) for u in (k / 11 for k in range(12))]
        cv.shade(mpoly(taper(c2, 6, 1.5)), H0, R=4, spec=0.6, line=(1.4, 2.4), dots=False)
        for (p0, p1, p2, p3) in (((cx + 44, 240), (cx + 70, 222), (cx + 100, 230), (cx + 114 + sway * 16, 262)), ((cx + 62, 244), (cx + 92, 236), (cx + 116, 250), (cx + 124 + sway * 16, 288))):
            cv.ink(bez(p0, p1, p2, p3, 12), 2.6, H0)
    elif who == "samir":
        for k in range(-6, 7):                                                    # curls under the beanie
            x = cx + k * 26; y = 262 + abs(k) * 4
            cv.shade(mell((x - 18, y - 12, x + 18, y + 16)), (34, 24, 20), R=8, spec=0.6, line=(1.4, 2.4), dots=False)
        bm = mpoly(bez((cx - 184, 270), (cx - 196, 60), (cx + 196, 60), (cx + 184, 270)))
        bh = dome(bm, 90)
        for k in range(-8, 9): bh = bh + seg((cx + k * 22, 90 + abs(k) * 6), (cx + k * 23, 250), 3.5, -4)   # ribs
        cv.shade(bm, (70, 104, 66), h=bh)
        rm = mpoly([(cx - 192, 210), (cx + 192, 210), (cx + 190, 276), (cx - 190, 276)])
        rh = dome(rm, 20)
        for k in range(-16, 17): rh = rh + seg((cx + k * 12, 214), (cx + k * 12, 272), 2.4, -3)
        cv.shade(rm, (56, 86, 54), h=rh)
        cv.shade(mell((cx - 40, 20, cx + 40, 100)), (232, 228, 214), R=30)          # pompom
    elif who == "maman":
        Hc = (150, 140, 138)
        bun = mell((cx - 62, 70, cx + 62, 180)); bh = dome(bun, 40)
        for k in range(5): bh = bh + seg((cx - 50 + k * 8, 100 + k * 8), (cx + 50 - k * 6, 140 + k * 6), 3, -4)
        cv.shade(bun, Hc, h=bh, spec=0.5, rim=1.2)
        hl = [(cx + T + 2, ey - 6), (cx + T - 8, 312), (cx + 104, 252), (cx + 44, 232), (cx, 240), (cx - 44, 232), (cx - 104, 252), (cx - T + 8, 312), (cx - T - 2, ey - 6)]
        mask = mpoly([(cx - T - 20, ey + 10)] + bez((cx - T - 26, 340), (cx - T - 50, 110), (cx + T + 50, 110), (cx + T + 26, 340), 24) + [(cx + T + 20, ey + 10)] + hl)
        hh = dome(mask, 50)
        paths = []
        for s in (-1, 1):
            for k in range(8):
                paths.append(bez((cx + s * 3, 238 - k * 2), (cx + s * (44 + k * 6), 180 - k * 5), (cx + s * (130 + k * 6), 186 + k * 14), (cx + s * (T + 18), 300 + k * 18), 18))
        rid = np.zeros_like(XX)
        for p in paths:
            m_ = Image.new("L", (W * S, H * S), 0); ImageDraw.Draw(m_).line(P(p), fill=255, width=S)
            dist = cv2.distanceTransform((np.asarray(m_) == 0).astype(np.uint8), cv2.DIST_L2, 5) / S
            rid = np.maximum(rid, np.exp(-(dist / 6) ** 2) * 5)
        cv.shade(mask, Hc, h=hh + rid, spec=0.2, gloss=0.9, rim=1.0)
        im, d = cv.layer()
        for i, p in enumerate(paths): d.line(P(p), fill=((222, 218, 214, 200) if i % 3 == 0 else (96, 88, 88, 160)), width=S)
        a = np.asarray(im).copy(); a[..., 3] = (a[..., 3] * mask).astype(np.uint8); cv.put(Image.fromarray(a))
        cv.ink(bez((cx + 86, 244), (cx + 110, 266), (cx + 118, 300), (cx + 108 + sway * 14, 334), 12), 1.6, (226, 222, 218))   # a loose white strand
        cv.ink([(cx + 20, 86), (cx + 86, 128)], 4, GOLD_D); cv.ink([(cx + 20, 86), (cx + 86, 128)], 2, GOLD)                      # hairpin


if __name__ == "__main__":
    import sys
    rows = ["toi", "samir", "maman", "double"]
    exps = [("neutre", dict()), ("peur", dict(wide=1.45, brow=1.0, mouth="o", look=(0.2, 0.0))), ("sourire", dict(mouth="smile", brow=-0.3, look=(-0.3, 0.1))), ("inquiet", dict(mouth="fear", brow=0.9, look=(0.0, 0.4)))]
    only = sys.argv[2:] if len(sys.argv) > 2 else None
    if only and only[0] == "big":
        Sh = Image.new("RGB", (4 * 500, 700), (26, 28, 32))
        for i, who in enumerate(rows):
            b = bust4(who).crop((150, 0, 850, 980)).resize((500, 700)); Sh.paste(b, (i * 500, 0), b)
    else:
        Sh = Image.new("RGB", (4 * 420 + 40, 4 * 520 + 40), (26, 28, 32)); d = ImageDraw.Draw(Sh)
        for r, who in enumerate(rows):
            for c, (e, kw) in enumerate(exps):
                b = bust4(who, **kw).crop((100, 0, 900, 1000)).resize((400, 500)); Sh.paste(b, (20 + c * 420, 20 + r * 520), b)
                d.text((30 + c * 420, 522 + r * 520), f"{who.upper()} · {e}", fill=(200, 190, 160))
    Sh.save(sys.argv[1], quality=92); print("ok")
