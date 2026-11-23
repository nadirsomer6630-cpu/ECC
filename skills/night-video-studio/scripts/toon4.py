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

    def shade(self, mask, albedo, h=None, R=40, line=(2.4, 5.5), dots=True, spec=0.0, rim=1.0, gloss=0.86, flat=None, noink=None):
        """Light a shape, then draw it as flat 2D: `flat` (default FLAT) pulls the normals toward the viewer."""
        flat = FLAT if flat is None else flat; spec = spec * SPEC
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
        sm = ((d < 0.39) & m).astype(np.uint8)                                  # clean the tones: a shadow island too small to
        n_, lab, st, _ = cv2.connectedComponentsWithStats(sm, connectivity=8)   # mean anything is a stain, so it goes
        small = st[:, cv2.CC_STAT_AREA] < 7000; small[0] = False
        d = np.where(small[lab], np.maximum(d, 0.45), d)
        t1, t2 = ss(0.345, 0.365, d), ss(0.70, 0.72, d)                        # three flat tones, crisp 2D edges
        ramp = RAMP[0][None, None] + (RAMP[1] - RAMP[0])[None, None] * t1[..., None] + (RAMP[2] - RAMP[1])[None, None] * t2[..., None]
        alb = np.broadcast_to(np.array(albedo, np.float32)[:3], hh.shape + (3,)) if isinstance(albedo, tuple) else albedo[y0:y1, x0:x1]
        col = alb * ramp
        col *= (0.75 + 0.25 * ao)[..., None]
        if dots:                                                             # halftone in the half-shadow
            u, v = (X + Y) * 0.7071, (X - Y) * 0.7071; p = 6.5
            fu, fv = (u % p) - p / 2, (v % p) - p / 2
            dark = np.clip((0.40 - d) / 0.24, 0, 1) * (d > 0.13)
            col[(fu * fu + fv * fv) < (p * 0.42 * dark) ** 2] *= 0.84
            col[(((X - Y) % 6.0) < 1.0) & (d <= 0.13)] *= 0.72                 # hatching in the deep shadow
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
        if noink is not None: inkm &= ~noink[y0:y1, x0:x1]
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
    toi=dict(T=148, C=160, cby=424, J=126, jy=552, K=20, chy=640, round=0.55, ey=394, esp=66, ew=35, eh=10, lift=3, ir=13,
             by=368, bw=12, bs=-1.3, nb=500, nw=24, nh=21, my=554, mw=37, lipf=1.25, brow_r=1.7, cb=1.6, hollow=1.0, socket=1.5, chin=1.3,
             philtrum=4.0, hood=1.0, adam=1.0, corners=-1.5,
             skin=(222, 180, 148), lip=(178, 112, 100), iris=(54, 92, 200), neck=90),
    samir=dict(T=168, C=180, cby=430, J=150, jy=556, K=34, chy=626, round=0.55, ey=398, esp=70, ew=33, eh=11, lift=1, ir=13,
               by=370, bw=15, bs=-0.8, nb=500, nw=32, nh=17, my=552, mw=39, lipf=1.4, brow_r=1.5, cb=1.3, hollow=0.6, socket=1.2, chin=1.0,
               philtrum=3.5, hood=0.8, adam=1.2, corners=-0.5,
               skin=(176, 122, 88), lip=(128, 74, 64), iris=(104, 66, 38), neck=94),
    maman=dict(T=156, C=164, cby=436, J=134, jy=528, K=24, chy=610, round=0.85, ey=400, esp=64, ew=31, eh=11, lift=-1, ir=12,
               by=360, bw=6, bs=0.4, nb=488, nw=20, nh=13, my=536, mw=31, lipf=0.9, brow_r=0.8, cb=1.1, hollow=0.3, socket=1.0, chin=0.7,
               philtrum=2.5, hood=0.5, adam=0.0, corners=0.0,
               skin=(232, 196, 170), lip=(184, 120, 116), iris=(104, 74, 48), neck=76),
    double=dict(T=146, C=158, cby=420, J=112, jy=556, K=12, chy=664, round=0.5, ey=392, esp=66, ew=37, eh=10, lift=12, ir=13,
                by=356, bw=10, bs=1.4, nb=506, nw=20, nh=24, my=566, mw=34, lipf=0.6, brow_r=2.0, cb=2.0, hollow=1.6, socket=2.2, chin=1.4,
                philtrum=3.0, hood=1.2, adam=1.0, corners=0.0,
                skin=(176, 180, 188), lip=(120, 110, 120), iris=(240, 30, 30), neck=70),
)
CLOTH = dict(toi=((80, 58, 120), (40, 38, 48)), double=((80, 58, 120), (30, 28, 36)), samir=((92, 110, 72), (120, 124, 136)), maman=((104, 58, 86), (238, 226, 206)))


FLAT, SPEC = 0.55, 0.35   # 2D look: how much the relief is flattened, how much gloss is kept
SOFT = 0.62          # softness after the second reference creator: 1 = the angular v14 faces, lower = softer


def soften(F, k=SOFT):
    """Rounder, gentler faces: less relief, rounder jaw and chin, bigger and calmer eyes, thinner brows."""
    F = dict(F)
    for key in ("cb", "hollow", "brow_r", "socket", "chin", "nh", "philtrum", "hood"):
        if key in F: F[key] = F[key] * k
    F["eh"] = F["eh"] + 3 * (1 - k) / 0.38; F["lift"] = F["lift"] * k; F["bw"] = F["bw"] * (0.6 + 0.4 * k)
    F["bs"] = F["bs"] * k; F["round"] = min(1.0, F.get("round", 0.6) + 0.3 * (1 - k) / 0.38)
    F["corners"] = F.get("corners", 0) * k                                   # the chin stays narrow (a wide chin reads square);
    F["J"] = F["J"] - 8 * (1 - k) / 0.38; F["jy"] = F["jy"] - 8 * (1 - k) / 0.38      # the jaw rounds off higher instead
    F["round"] = min(1.0, F["round"] + 0.15)
    F["C"] = F["C"] - 4 * (1 - k) / 0.38                                     # cheekbones less flared
    return F


OVAL = dict(toi=(150, 130, 632, 0.22), samir=(166, 132, 628, 0.16), maman=(156, 128, 612, 0.14), double=(144, 126, 664, 0.30))


def head_pts(cx, F):
    if "oval" in F:                                                          # an egg: widest at the cheekbones, narrowing to the chin
        a, top, chin, taper = F["oval"]; cy, b = (top + chin) / 2, (chin - top) / 2
        return [(cx + a * math.cos(t) * (1 - taper * max(0.0, math.sin(t)) ** 2), cy + b * math.sin(t)) for t in (2 * math.pi * k / 120 for k in range(120))]
    T, C, cby, J, jy, K, chy = F["T"], F["C"], F["cby"], F["J"], F["jy"], F["K"], F["chy"]
    dome_ = bez((cx - T, 330), (cx - T - 8, 120), (cx + T + 8, 120), (cx + T, 330))
    tx, ty = (J - C), (jy - cby)                                         # the cheek's direction as it reaches the jaw
    l = math.hypot(tx, ty) or 1; tx, ty = tx / l, ty / l; r = F.get("round", 0.5) * (chy - jy)
    right = bez((cx + T, 330), (cx + C + 4, cby - 50), (cx + C - 2, cby + 30), (cx + J, jy), 16) + bez((cx + J, jy), (cx + J + tx * r, jy + ty * r), (cx + K + (J - K) * (0.3 + 0.35 * F.get("round", 0.5)), chy + 2), (cx + K, chy + 4), 16)
    return dome_ + right + [(2 * cx - x, y) for x, y in reversed(right)]


def face_height(cx, F, who, mouth, brow, wide):
    ey, esp, nb, my = F["ey"], F["esp"], F["nb"], F["my"]
    h = np.zeros_like(XX)
    for s in (-1, 1):
        h += g(cx + s * 60, F["by"] + 4, 44, 12, 9 * F["brow_r"])                  # brow ridge
        h += g(cx + s * esp, ey + 2, 36, 22, -15 * F["socket"])                    # eye socket
        h += g(cx + s * esp, ey + 2, 24, 13, 6)                                    # the eyeball under the lids
        h += seg((cx + s * (esp + 6), ey + 40), (cx + s * (esp + 62), ey + 26), 20, 11 * F["cb"])   # cheekbone, a long ridge toward the temple
        h += seg((cx + s * (esp + 46), ey + 62), (cx + s * (F["mw"] + 34), my - 16), 18, -8 * F["hollow"] * (1.0 if s < 0 else 0.0))   # the hollow under it, a long plane down to the mouth
        h += g(cx + s * 140, ey - 70, 30, 40, -3)                                  # temple
        h += seg((cx + s * (F["nw"] + 8), nb - 6), (cx + s * (F["mw"] + 10), my + 6), 9, -3 * (1.4 if who in ("maman", "double") else 0.7))   # nose-to-mouth fold
        h += g(cx + s * F["nw"] * 0.85, nb - 8, 11, 10, 7)                         # nostril wings
        h += g(cx + s * F["nw"] * 0.42, nb + 1, 6, 3.5, -6)                        # nostrils
    h += g(cx, F["by"] + 2, 26, 12, 6)                                             # between the brows
    ramp = np.clip((YY - (ey - 26)) / (nb - ey + 26), 0, 1) ** 1.25 * (YY < nb + 4)
    h += F["nh"] * ramp * np.exp(-((XX - cx) / 11) ** 2 / 2)                       # the nose bridge
    h += g(cx, nb - 13, F["nw"] * 0.55, 13, 10)                                    # nose tip
    for s in (-1, 1): h += seg((cx + s * 6, nb + 8), (cx + s * 8, my - 12), 2.6, 1.6 * F.get("philtrum", 2.5) / 2.5)   # philtrum ridges
    h += g(cx, (nb + my) / 2 - 4, 4.5, 11, -F.get("philtrum", 2.5))                 # philtrum groove
    h += g(cx, my + 2, F["mw"] * 1.1, 16, 4)                                        # the muzzle the lips sit on
    h += seg((cx - 22, my + 24), (cx + 22, my + 24), 4, -5)                        # the fold under the lower lip
    cw = 1 + F["K"] / 40
    h += g(cx, F["chy"] - 24, 22 * cw, 17, 11 * F["chin"])                         # the chin, a ball under the fold
    h += g(cx, F["chy"] - 3, 26 * cw, 6, -2)
    if who == "toi": h += seg((cx, F["chy"] - 32), (cx, F["chy"] - 14), 2.5, -2.2)  # a faint cleft
    if mouth == "smile":
        for s in (-1, 1): h += g(cx + s * (esp + 20), ey + 70, 30, 20, 6)           # cheeks lift
    if who == "maman":
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
    if who != "double":                                                            # soft crescents under the eyes
        bag = [(x, y + 6 + 2 * math.sin(i / 20 * math.pi)) for i, (x, y) in enumerate(lo[6:-6])]
        cv.ink(bag, 1.8, (150, 96, 90), 0.5)
    oc = up[-1]; cv.ink([oc, (oc[0] + side * 7, oc[1] - 4)], 3)                                 # outer corner
    hood = F.get("hood", 0.5)
    crease = [(x, y - 5 - 2 * (1 - abs(i - 16) / 16)) for i, (x, y) in enumerate(up) if 4 <= i <= 30]
    if hood:                                                                        # the brow's fold hangs over the outer lid
        fold = [(x, y - (2 + 5 * hood) * max(0.0, (i - 6) / 24) ** 0.8) for i, (x, y) in enumerate(crease)]
        im2, d2 = cv.layer(); d2.polygon(P(fold + [(x, y - 9) for x, y in reversed(fold)]), fill=(70, 40, 40, int(70 * hood))); cv.put(im2.filter(ImageFilter.GaussianBlur(2 * S)))
    cv.ink(crease, 1.6 + 0.6 * hood, (80, 48, 46), 0.9)                                  # lid crease
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
    lip = np.array(F["lip"], np.float32); up_c = tuple(int(v) for v in lip * 0.86); lo_c = tuple(int(min(255, v * 1.08)) for v in lip)
    dark, teeth = (48, 14, 22), (236, 228, 212)
    def lips(top, line_, bottom):                                                # upper lip, lower lip, then the mouth line
        cv.shade(mpoly(top + line_[::-1]), up_c, R=5, line=(0, 0), dots=False, rim=0)
        cv.shade(mpoly(line_ + bottom), lo_c, R=7, line=(0, 0), dots=False, rim=0, spec=0.5, gloss=0.88)
    w = mw
    if mouth in ("line", "smile"):
        lift = 0 if mouth == "line" else 9
        lf = F.get("lipf", 1.0); top = bez((mx - w, my - lift), (mx - w * 0.6, my - 9 * lf - lift * 0.4), (mx - 12, my - 15 * lf), (mx - 6, my - 13 * lf), 10) + [(mx, my - 9 * lf)] + bez((mx + 6, my - 13 * lf), (mx + 12, my - 15 * lf), (mx + w * 0.6, my - 9 * lf - lift * 0.4), (mx + w, my - lift), 10)
        if mouth == "line":
            dn = -F.get("corners", 0.0); line_ = bez((mx - w, my + dn), (mx - w * 0.4, my + 3), (mx + w * 0.4, my + 3), (mx + w, my + dn), 16)
            bottom = bez((mx + w * 0.85, my + 1 + dn), (mx + w * 0.5, my + 21 * lf), (mx - w * 0.5, my + 21 * lf), (mx - w * 0.85, my + 1 + dn), 16)
            lips(top, line_, bottom)
            cv.ink(line_[2:-2], 2.2, (64, 30, 34)); cv.ink(line_[6:11], 3.0, (54, 24, 28))
            for s_ in (-1, 1): cv.ink([(mx + s_ * (w - 3), my - 1), (mx + s_ * (w + 4), my + 1)], 2.4, (70, 34, 36))   # the corners
        else:                                                                    # a smile: corners up, the upper teeth show
            upper = bez((mx - w - 2, my - lift), (mx - w * 0.4, my - 2), (mx + w * 0.4, my - 2), (mx + w + 2, my - lift), 16)
            lower = bez((mx + w + 2, my - lift), (mx + w * 0.4, my + 13), (mx - w * 0.4, my + 13), (mx - w - 2, my - lift), 16)
            cv.shade(mpoly(top + upper[::-1]), up_c, R=4, line=(0, 0), dots=False, rim=0)
            cv.shade(mpoly(upper + lower), dark, R=3, line=(1.4, 1.8), dots=False, rim=0)
            cv.shade(mpoly(upper + [(x, y + 6) for x, y in upper[::-1]]), teeth, R=2, line=(0, 0), dots=False, rim=0)
            cv.shade(mpoly(lower + bez((mx - w * 0.8, my + 4), (mx - w * 0.5, my + 24), (mx + w * 0.5, my + 24), (mx + w * 0.8, my + 4), 14)), lo_c, R=6, line=(0, 0), dots=False, rim=0, spec=0.5)
            for s_ in (-1, 1): cv.ink(bez((mx + s_ * (w + 6), my - lift - 8), (mx + s_ * (w + 11), my - lift - 2), (mx + s_ * (w + 11), my - lift + 4), (mx + s_ * (w + 7), my - lift + 8), 6), 1.8, (90, 50, 46), 0.75)   # dimples
        return
    if mouth == "o":                                                             # surprise: a round open mouth framed by the lips
        cv.shade(mell((mx - 20, my - 20, mx + 20, my + 28)), lo_c, R=8, line=(1.2, 2.0), dots=False, rim=0, spec=0.4)
        cv.shade(mell((mx - 13, my - 13, mx + 13, my + 20)), dark, R=4, line=(0, 0), dots=False, rim=0)
        cv.shade(mpoly(bez((mx - 11, my - 9), (mx - 6, my - 14), (mx + 6, my - 14), (mx + 11, my - 9), 8) + [(mx + 9, my - 5), (mx - 9, my - 5)]), teeth, R=2, line=(0, 0), dots=False, rim=0)
        cv.shade(mell((mx - 9, my + 8, mx + 9, my + 19)), (150, 70, 80), R=3, line=(0, 0), dots=False, rim=0)   # tongue
        cv.shade(mpoly(bez((mx - 21, my - 6), (mx - 16, my - 22), (mx + 16, my - 22), (mx + 21, my - 6), 12) + bez((mx + 13, my - 8), (mx + 8, my - 14), (mx - 8, my - 14), (mx - 13, my - 8), 12)), up_c, R=3, line=(0, 0), dots=False, rim=0)
        return
    # fear: stretched wide, corners pulled down, both rows of teeth
    upper = bez((mx - w - 4, my + 4), (mx - w * 0.4, my - 6), (mx + w * 0.4, my - 6), (mx + w + 4, my + 4), 16)
    lower = bez((mx + w + 4, my + 4), (mx + w * 0.4, my + 16), (mx - w * 0.4, my + 16), (mx - w - 4, my + 4), 16)
    cv.shade(mpoly(bez((mx - w - 4, my + 4), (mx - w * 0.5, my - 14), (mx + w * 0.5, my - 14), (mx + w + 4, my + 4), 14) + upper[::-1]), up_c, R=3, line=(0, 0), dots=False, rim=0)
    cv.shade(mpoly(upper + lower), dark, R=3, line=(1.4, 1.8), dots=False, rim=0)
    cv.shade(mpoly(upper[3:-3] + [(x, y + 5) for x, y in upper[3:-3][::-1]]), teeth, R=2, line=(0, 0), dots=False, rim=0)
    cv.shade(mpoly(lower[4:-4] + [(x, y - 4) for x, y in lower[4:-4][::-1]]), (220, 212, 196), R=2, line=(0, 0), dots=False, rim=0)
    cv.shade(mpoly(lower + bez((mx - w * 0.9, my + 8), (mx - w * 0.5, my + 26), (mx + w * 0.5, my + 26), (mx + w * 0.9, my + 8), 14)), lo_c, R=5, line=(0, 0), dots=False, rim=0, spec=0.4)


def bust4(who="toi", look=(0.0, 0.0), brow=0.0, mouth="line", wide=1.0, blink=False, sway=0.0):
    F = soften(FACE[who]); F["oval"] = OVAL[who]; cv = Canvas(); cx = 500
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
    nh = dome(nk, 70) + seg((cx - 40, 620), (cx - 60, 720), 8, 5) + seg((cx + 40, 620), (cx + 60, 720), 8, 5) + g(cx, F["chy"] + 10, 60, 30, -30) + g(cx, F["chy"] + 46, 10, 14, 7 * F.get("adam", 0))
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
    if who in ("toi", "double"):                                                # the hair at the back, down the nape
        H0 = (44, 30, 26) if who == "toi" else (30, 24, 26)
        for s in (-1, 1):
            pts = [(cx + s * (F["T"] - 30), 300)]                                # one mass behind the ears, ending in a few points
            for k, (dx, y1) in enumerate(((-6, 520), (12, 500), (26, 530), (40, 470), (46, 400))):
                pts += [(cx + s * (F["T"] + dx - 8), y1 - 40), (cx + s * (F["T"] + dx + 4), y1)]
            pts += [(cx + s * (F["T"] + 40), 300)]
            cv.shade(mpoly(pts), H0, R=14, spec=0.3, line=(1.6, 2.8))
    # ---------- ears
    for s in (-1, 1):
        e = mpoly(bez((cx + s * (F["T"] - 4), F["ey"] - 30), (cx + s * (F["T"] + 30), F["ey"] - 40), (cx + s * (F["T"] + 30), F["ey"] + 60), (cx + s * (F["T"] - 2), F["ey"] + 80)))
        eh = dome(e, 14) + seg((cx + s * (F["T"] + 12), F["ey"] - 20), (cx + s * (F["T"] + 16), F["ey"] + 50), 4, -6)
        cv.shade(e, F["skin"], h=eh, rim=1.2)
        if who == "samir" and s < 0: cv.shade(mell((cx - F["T"] - 16, F["ey"] + 60, cx - F["T"] - 4, F["ey"] + 72)), GOLD, R=3, spec=1, dots=False, line=(1, 1.2))
    # ---------- head
    if who in ("toi", "double"): hair_ribbons(cv, cx, F, who, sway, "back")
    hm = mpoly(head_pts(cx, F))
    hh = dome(hm, 80) + 1.35 * face_height(cx, F, who, mouth, brow, wide)
    alb = np.broadcast_to(np.array(F["skin"], np.float32), hm.shape + (3,)).copy()
    lipm = g(cx, F["my"] + 2, F["mw"] * 0.9, 12, 1)                                # the mouth zone, kept clean of stubble
    if who == "toi":                                                             # stubble: a blue-grey cast on the jaw and upper lip
        stub = np.clip(g(cx, F["my"] + 30, 120, 60, 1) + g(cx, F["my"] - 22, 40, 8, 0.7) - lipm * 2, 0, 1) * ss(F["nb"] + 2, F["nb"] + 26, YY)
        alb *= (1 - 0.12 * stub)[..., None]; alb[..., 2] += 6 * stub
    for s in (-1, 1): alb += np.array([16, -2, -4], np.float32) * g(cx + s * (F["esp"] + 20), F["ey"] + 52, 26, 14, 1)[..., None] * (who != "double")   # warm cheeks
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
    skin_m, noink = hm, None
    if who in ("toi", "double"):                                                 # the forehead ends on a natural, uneven hairline
        hlx = hairline(cx, F); xs_ = [p[0] for p in reversed(hlx)]; ys_ = [p[1] for p in reversed(hlx)]
        yh = np.interp(XX, xs_, ys_) + 2.5 * np.sin(XX / 6.0) + 1.5 * np.sin(XX / 2.3)
        skin_m = hm & (YY > yh); noink = YY < yh + 6
    cv.shade(skin_m, alb, h=hh, spec=0.12, gloss=0.95, R=80, noink=noink, line=(3.2, 4.6))
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
            if hm[int(y * S), int(x * S)] and not (abs(x - cx) < F["mw"] + 6 and abs(y - F["my"] - 3) < 18) and y > F["nb"] + 14: d.line([(x * S, y * S), ((x + 1) * S, (y + 3) * S)], fill=(60, 50, 56, 80), width=S)
        cv.put(im)
        cv.ink([(cx - 112, 318), (cx - 98, 360), (cx - 92, 390)], 3.2, (150, 62, 60)); cv.ink([(cx - 84, 426), (cx - 76, 462)], 2.6, (150, 62, 60))
    if who == "double":                                                          # gold-repaired cracks, black tears
        for path in (bez((cx - 96, 290), (cx - 80, 340), (cx - 110, 380), (cx - 90, 430), 8), bez((cx + 90, 270), (cx + 70, 330), (cx + 104, 380), (cx + 80, 450), 8), bez((cx + 30, F["my"] + 20), (cx + 50, F["my"] + 50), (cx + 40, F["my"] + 70), (cx + 60, F["chy"] - 10), 6)):
            cv.ink(path, 4.5, GOLD_D); cv.ink(path, 2.2, (240, 200, 110))
        for s in (-1, 1): cv.ink(bez((cx + s * 62, F["ey"] + 12), (cx + s * 66, F["ey"] + 60), (cx + s * 58, F["ey"] + 100), (cx + s * 64, F["ey"] + 150), 10), 4, (10, 8, 12))
    if who == "maman":                                                           # forehead lines, drawn faintly
        for k, y in enumerate((300, 316, 331)): cv.ink(bez((cx - 74 + k * 8, y + 4), (cx - 30, y - 2), (cx + 30, y - 2), (cx + 74 - k * 8, y + 4), 14), 1.3, (120, 80, 70), 0.4)
    # ---------- facial features
    browc = dict(toi=(26, 18, 16), double=(18, 16, 20), samir=(24, 16, 12), maman=(96, 86, 82))[who]
    for s in (-1, 1): brow4(cv, cx, F, s, brow, wide, browc)
    for s in (-1, 1): eye4(cv, cx + s * F["esp"], F["ey"], s, F, look, wide, blink, who)
    nb, nw = F["nb"], F["nw"]                                                    # nose ink: only where the light breaks
    cv.ink(bez((cx - 7, F["ey"] + 14), (cx - 9, nb - 50), (cx - 13, nb - 30), (cx - nw * 0.7, nb - 14), 12), 1.8, (90, 54, 50), 0.6)   # the bridge, on the shadow side
    cv.ink(bez((cx - nw * 0.95, nb - 18), (cx - nw * 1.15, nb - 2), (cx - nw * 0.8, nb + 6), (cx - nw * 0.45, nb + 4), 10), 2.4)
    cv.ink(bez((cx + nw * 0.95, nb - 18), (cx + nw * 1.15, nb - 2), (cx + nw * 0.8, nb + 6), (cx + nw * 0.45, nb + 4), 10), 1.6, (60, 36, 34), 0.8)
    mouth4(cv, cx, F, mouth, who, look)
    if who == "samir":                                                           # the moustache falls over the upper lip
        mx, my, mw = cx + look[0] * 4, F["my"], F["mw"]
        mo = mpoly(bez((mx - mw - 10, my + 6), (mx - mw * 0.8, my - 22), (mx - 14, nb + 10), (mx, nb + 16), 12) + bez((mx, nb + 16), (mx + 14, nb + 10), (mx + mw * 0.8, my - 22), (mx + mw + 10, my + 6), 12)
                   + bez((mx + mw + 4, my), (mx + mw * 0.4, my - 10), (mx - mw * 0.4, my - 10), (mx - mw - 4, my), 12))
        cv.shade(mo, (46, 34, 30), R=8, line=(1.0, 1.6), rim=0.6)
        im, d = cv.layer()
        for k in range(26):
            t = k / 25; x = mx - mw - 6 + (2 * mw + 12) * t; y0 = nb + 14 + abs(t - 0.5) * 30
            d.line([(x * S, y0 * S), ((x + (t - 0.5) * 10) * S, (y0 + 16) * S)], fill=(96, 74, 62, 200) if k % 3 else (16, 10, 8, 220), width=S)
        cv.put(im)
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


def wave(y, amp=11.0, lam=170.0):
    """One wave for the whole head, so every clump ripples in step, like combed hair."""
    return amp * math.sin((y - 40) / lam * 2 * math.pi)


def ribbon(c, w):
    """A clump: broad at the root, tapering to a point at the far end."""
    n = len(c); left, right = [], []
    for i, (x, y) in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(n - 1, i + 1)]; dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        t = i / (n - 1); ww = w * (0.9 + 0.1 * math.sin(t * math.pi)) * (1 - t) ** 0.75 + 1.2
        left.append((x - dy / l * ww, y + dx / l * ww)); right.append((x + dy / l * ww, y - dx / l * ww))
    return left + right[::-1]


def streak(c, w, side=1):
    """The hair highlight: a thin crescent along part of a clump, on its lit side, pointed at both ends."""
    n = len(c); left, right = [], []
    for i, (x, y) in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(n - 1, i + 1)]; dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        ww = w * math.sin(i / (n - 1) * math.pi) + 0.3; ox, oy = dy / l * w * 0.5 * side, -dx / l * w * 0.5 * side
        left.append((x + ox - dy / l * ww, y + oy + dx / l * ww)); right.append((x + ox + dy / l * ww, y + oy - dx / l * ww))
    return left + right[::-1]


def hairline(cx, F):
    T, ey = F["T"], F["ey"]
    return [(cx + T - 2, ey - 44), (cx + T - 8, 300), (cx + 122, 252), (cx + 72, 236), (cx + 30, 238), (cx, 250),
            (cx - 30, 238), (cx - 72, 236), (cx - 122, 252), (cx - T + 8, 300), (cx - T + 2, ey - 44)]


def hair_ribbons(cv, cx, F, who, sway, part="back"):
    """Slicked back with volume, after the creator's reference cut, made of thick clumps: a dark under-mass, 17 clumps
    combed back from an M hairline, the sides swept back over the temples, every clump rippling in step, one crisp
    highlight per clump lining up into a band, two thick strands falling in front of each ear, the blue lock."""
    T, ey = F["T"], F["ey"]
    H0 = np.array((46, 32, 27) if who == "toi" else (32, 26, 28), np.float32)
    HI, HI2 = ((150, 118, 94), (214, 184, 156)) if who == "toi" else ((96, 90, 100), (150, 146, 160))
    hl = hairline(cx, F)
    if part == "front":
        hair_front(cv, cx, F, who, sway, H0, hl); return
    hl_mass = [(x, y + 16) for x, y in hl]                                       # the hair runs on under the skin of the forehead
    outer = [(cx + (T + 30) * math.cos(a), 334 - 280 * math.sin(a)) for a in (math.pi * (1 - k / 48) for k in range(49))]
    cv.shade(mpoly([(cx - T - 8, ey - 16)] + outer + [(cx + T + 8, ey - 16)] + hl_mass), tuple(int(v * 0.8) for v in H0), R=50, rim=0.8)   # the under-mass
    xs = [p[0] for p in reversed(hl)]; ys = [p[1] for p in reversed(hl)]
    clumps = []
    for s_ in (-1, 1):                                                           # the sides, swept back over the temples
        for k in range(3):
            y0 = 322 + k * 26
            c = bez((cx + s_ * (T - 4), y0), (cx + s_ * (T + 20), y0 - 50), (cx + s_ * (T + 26), y0 - 140), (cx + s_ * (T - 16), 130 + k * 18), 24)
            clumps.append((3, [(x + s_ * wave(y, 4), y) for x, y in c], 15, k))
    for i in range(-8, 9):                                                       # the top, combed back
        u = i / 8; rx = cx + u * (T - 8); ry = float(np.interp(rx, xs, ys))
        c = bez((rx, ry + 16), (rx + u * 30, ry - 80), (cx + u * T * 0.95, 110 + 30 * u * u), (cx + u * T * 0.82, 50 + 70 * u * u), 28)
        clumps.append((2 - abs(u), [(x + wave(y) * (1 - abs(u) * 0.3), y) for x, y in c], 24 if i % 2 == 0 else 19, i))
    clumps.sort(key=lambda q: q[0])                                              # outer clumps first, the centre on top
    for depth, c, w, i in clumps:
        tint = 1.0 + 0.08 * ((i * 7) % 3 - 1)
        cv.shade(mpoly(ribbon(c, w)), tuple(int(min(255, v * tint)) for v in H0), R=w * 0.8, line=(0.8, 1.3), rim=0.9)
        band = [q for q in c if 92 < q[1] < 196]
        if len(band) > 3:
            im, d = cv.layer(); d.polygon(P(streak(band, w * 0.32)), fill=HI + (235,)); d.polygon(P(streak(band[1:-1], w * 0.12)), fill=HI2 + (240,)); cv.put(im)
        mid = c[len(c) // 5: len(c) * 3 // 4]
        cv.ink([(x - w * 0.35, y) for x, y in mid], 1.1, (14, 9, 9), 0.55)      # one strand line, no more


def hair_front(cv, cx, F, who, sway, H0, hl):
    """What lies on the face: a soft shadow under the hairline, the strands before the ears, the locks."""
    T, ey = F["T"], F["ey"]
    sh, d = cv.layer(); d.polygon(P(hl + [(x, y + 22) for x, y in reversed(hl)]), fill=(40, 20, 24, 90)); cv.put(sh.filter(ImageFilter.GaussianBlur(6 * S)))
    if True:
        for s_ in (-1, 1):                                                           # two thick strands in front of each ear
            for (x0, y0, y1, w) in ((T - 16, 280, ey + 46, 12), (T - 34, 266, ey + 4, 8)):
                c = [(cx + s_ * (x0 + 14 * u) + wave(y, 7, 120) + sway * 18 * u, y) for u, y in ((k / 20, y0 + (y1 - y0) * k / 20) for k in range(21))]
                cv.shade(mpoly(ribbon(c, w)), tuple(int(v) for v in H0), R=w * 0.8, line=(1.0, 2.0), rim=0.9)
                cv.ink(c[3:14], 1.0, (14, 9, 9), 0.5)
        lockc = (40, 70, 190) if who == "toi" else (14, 14, 22)                    # the lock over the left eye, and one beside it
        c = [(cx - 44 + (26 + sway * 50) * u + wave(y, 9, 120), y) for u, y in ((k / 22, 238 + (ey - 24 - 238) * k / 22) for k in range(23))]
        cv.shade(mpoly(ribbon(c, 12)), lockc, R=8, line=(1.4, 2.6), dots=False, spec=0.6)
        if who == "toi":
            im, d = cv.layer(); d.polygon(P(streak(c[2:12], 4)), fill=(130, 170, 255, 235)); cv.put(im)
        c2 = [(cx - 14 + (22 + sway * 36) * u + wave(y, 7, 120), y) for u, y in ((k / 16, 242 + (ey - 90 - 242) * k / 16) for k in range(17))]
        cv.shade(mpoly(ribbon(c2, 8)), tuple(int(v) for v in H0), R=6, line=(1.2, 2.0), dots=False)


def hair(cv, cx, F, who, sway, hm):
    T, ey = F["T"], F["ey"]
    if who in ("toi", "double"):
        hair_ribbons(cv, cx, F, who, sway, "front")
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
