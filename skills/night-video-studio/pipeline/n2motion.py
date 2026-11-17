"""Nuit 2 fixes: doors that really swing in perspective, drawn hands that grip, and living characters.
Imported by nuit2.py (it needs nuit2's globals through the `ctx` module passed to bind())."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

C = None
def bind(ctx): global C; C = ctx


# ---------------------------------------------------------------- perspective
def _coeffs(dst, src):
    """PIL PERSPECTIVE coefficients that map output points dst[i] to input points src[i]."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; b += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def warp(tex, quad, size):
    """Paint `tex` into the 4-point `quad` (tl, tr, br, bl) of a canvas of `size`; returns an RGBA layer."""
    w, h = tex.size; src = [(0, 0), (w, 0), (w, h), (0, h)]
    lay = tex.convert("RGBA").transform(size, Image.PERSPECTIVE, _coeffs(quad, src), Image.BICUBIC)
    m = Image.new("L", size, 0); ImageDraw.Draw(m).polygon(quad, fill=255); lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(m))))
    return lay


def leaf_tex(w=400, h=1000, wood=(104, 70, 44), seed=3, num=None):
    """A wooden door leaf: grain, two panels, handle, an optional number."""
    import ei3 as E
    im = E.paper_tex(w, h, wood, fiber=0.14, seed=seed).convert("RGB"); a = np.asarray(im).astype(np.float32)
    a *= (0.86 + 0.14 * np.sin(np.linspace(0, 30, w) + np.random.default_rng(seed).normal(0, 0.3, w)))[None, :, None]; im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    for y0, y1 in ((60, 430), (500, 940)): d.rounded_rectangle((50, y0, w - 50, y1), 10, outline=tuple(int(c * 0.65) for c in wood), width=8)
    d.rounded_rectangle((26, 470, 70, 560), 10, fill=(190, 170, 120), outline=(70, 56, 36), width=5)
    if num: d.text((w / 2, 250), num, font=E.fI("Bold", 90), fill=(205, 175, 115), anchor="mm")
    return im


def door_open(bg, inside, frame, a, hinge="right", leaf=None, light=None):
    """Draw a door in `frame` (x0, y0, x1, y1) opened by angle a (0 closed .. 1 = 80 degrees, opening away from us).
    `inside` is what shows through the gap (an image of the frame size, or a colour). `light` (rgb, strength) pours
    out of the gap onto the floor, as wide as the gap is."""
    x0, y0, x1, y1 = frame; w = x1 - x0; ang = np.radians(80 * a); px = w * np.cos(ang); shrink = (y1 - y0) * 0.09 * np.sin(ang)
    out = bg.convert("RGBA").copy(); d = ImageDraw.Draw(out)
    gap_img = inside if isinstance(inside, Image.Image) else Image.new("RGB", (int(w), int(y1 - y0)), inside)
    out.paste(gap_img.resize((int(w), int(y1 - y0))), (int(x0), int(y0)))
    if light and a > 0.02:                                            # the light that comes out of the gap
        col, k = light; gx0 = x0 if hinge == "right" else x0 + px; gx1 = x1 - px if hinge == "right" else x1
        lay = Image.new("RGBA", out.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon([(gx0, y1), (gx1, y1), (gx1 + (gx1 - gx0) * 0.6 + 120, out.height), (gx0 - 120, out.height)], fill=col + (int(110 * k * min(1, a * 3)),))
        out.alpha_composite(lay.filter(ImageFilter.GaussianBlur(30)))
    lt = leaf or leaf_tex()
    if hinge == "right": quad = [(x1 - px, y0 + shrink), (x1, y0), (x1, y1), (x1 - px, y1 - shrink)]
    else: quad = [(x0, y0), (x0 + px, y0 + shrink), (x0 + px, y1 - shrink), (x0, y1)]
    shade = 1.0 - 0.35 * np.sin(ang)                                  # the leaf darkens as it turns away from the light
    lt = Image.eval(lt.convert("RGB"), lambda v: int(v * shade))
    if px > 3: out.alpha_composite(warp(lt, quad, out.size))
    d = ImageDraw.Draw(out); d.rectangle((x0 - 16, y0 - 16, x1 + 16, y0), fill=(40, 34, 30, 255))
    for xx in (x0 - 16, x1): d.rectangle((xx, y0 - 16, xx + 16, y1), fill=(40, 34, 30, 255))
    return out.convert("RGB")


# ---------------------------------------------------------------- hands
def hand(d, x, y, ang, scale=1.0, skin=(236, 190, 150, 255), grip=0.0, back=False, ol=(22, 18, 34, 255)):
    """A drawn hand: palm, four fingers that curl with `grip`, a thumb. `ang` points the fingers (radians, 0 = up)."""
    s = scale; ca, sa = np.cos(ang), np.sin(ang)
    def P(u, v): return (x + (u * ca + v * sa) * s, y + (u * sa - v * ca) * s)     # u across the palm, v along the fingers
    palm = [P(-60, -50), P(60, -50), P(66, 50), P(-62, 52)]
    d.polygon(palm, fill=ol); d.polygon([P(-52, -42), P(52, -42), P(58, 44), P(-54, 46)], fill=skin)
    for k, u in enumerate((-45, -15, 15, 45)):
        L = (62 + (8 if k in (1, 2) else 0)) * (1 - 0.55 * grip)
        a0, a1 = P(u, 46), P(u * (1 - 0.1 * grip), 46 + L)
        d.line([a0, a1], fill=ol, width=int(34 * s)); d.line([a0, a1], fill=skin, width=int(24 * s))
        r = 12 * s; d.ellipse((a1[0] - r - 5 * s, a1[1] - r - 5 * s, a1[0] + r + 5 * s, a1[1] + r + 5 * s), fill=ol); d.ellipse((a1[0] - r, a1[1] - r, a1[0] + r, a1[1] + r), fill=skin)
        if grip > 0.3:                                                # knuckle crease when the fingers close
            m = P(u, 46 + L * 0.45); d.line([(m[0] - 8 * s, m[1]), (m[0] + 8 * s, m[1])], fill=ol, width=int(3 * s))
    tb, te = P(-58 if not back else 58, 0), P((-100 if not back else 100) * (1 - 0.4 * grip), 40 + 20 * grip)
    d.line([tb, te], fill=ol, width=int(36 * s)); d.line([tb, te], fill=skin, width=int(26 * s))


def sleeve(d, x0, y0, x1, y1, col, w=150, ol=(22, 18, 34, 255), cuff=None, folds=True):
    """An arm in its sleeve from (x0, y0) to the wrist (x1, y1), with a cuff and two cloth folds."""
    d.line((x0, y0, x1, y1), fill=ol, width=w + 18); d.line((x0, y0, x1, y1), fill=col, width=w)
    if folds:
        for f in (0.35, 0.6):
            fx, fy = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f; nx, ny = -(y1 - y0), (x1 - x0); n = np.hypot(nx, ny) + 1e-6
            d.line((fx - nx / n * w * 0.3, fy - ny / n * w * 0.3, fx + nx / n * w * 0.1, fy + ny / n * w * 0.1), fill=tuple(int(c * 0.78) for c in col[:3]) + (255,), width=6)
    if cuff:
        cx, cy = x0 + (x1 - x0) * 0.93, y0 + (y1 - y0) * 0.93; d.line((cx, cy, x1, y1), fill=cuff, width=w + 4)


# ---------------------------------------------------------------- living characters
def alive(t, seed, k=1.0, talk_amp=0.0):
    """Small involuntary motion: head tilt and nod on noise, weight shifting, plus emphasis while speaking."""
    N = C.NOISE
    return dict(head=(round(0.35 * k * N.noise2(t * 0.6, seed) + 0.25 * talk_amp * N.noise2(t * 3, seed + 1), 2), round(0.3 * k * N.noise2(seed + 2, t * 0.5) + 0.4 * talk_amp * abs(N.noise2(t * 4, seed + 3)), 2)),
                lean=round(0.012 * k * np.sin(t * 2.4 + seed) + 0.02 * k * N.noise2(t * 0.3, seed + 5), 3))


def gesture(t, seed, a):
    """Arms that move while she talks: the louder the word, the more the hands open."""
    N = C.NOISE; g = min(1.0, a)
    return dict(armL=(round(0.35 + 0.25 * g + 0.08 * N.noise2(t * 2, seed), 2), round(1.2 + 0.6 * g * (0.5 + 0.5 * N.noise2(t * 3, seed + 1)), 2)),
                armR=(round(0.3 + 0.1 * g, 2), round(1.3 + 0.3 * g * (0.5 + 0.5 * N.noise2(seed + 4, t * 2.5)), 2)))
