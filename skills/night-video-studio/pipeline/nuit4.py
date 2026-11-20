"""LIVREUR DE NUIT, nuit 4, partie 1: "Le visage de Samir". About 65 s, in the format of the series that average
240 k views: first person (your hand and your phone at the bottom of the frame), a friend who talks with you on a
video call (shot / reverse shot, his jokes), your mother's texts as notifications at the top, a title card on frame 0,
one in-video choice with both outcomes, and an end card with two costed options and "abonne-toi pour la partie 2".
usage: HF_HOME=... nuit4.py <out.mp4>   (EI_STEP, EI_RANGE, EI_AUDIO_ONLY as before)"""
import os, sys, json, glob, subprocess, functools, re
_out = sys.argv[1]; sys.argv = ["nuit2.py", "/tmp/unused.mp4"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import nuit2 as N2
import tags as TG
N1, E, G, T2, MO = N2.N1, N2.E, N2.G, N2.T2, N2.MO
W, H, FPS, VSR, F, RED, NEW = E.W, E.H, E.FPS, E.VSR, E.F, E.RED, E.NEW
hero, put, cl, ease, xf, blink = N1.hero, N1.put, N1.cl, N1.ease, N1.xf, N1.blink
handheld, rain, motes, NOISE = N2.handheld, N2.rain, N2.motes, N2.NOISE
TG.setup(E.MONT, E.HAND)
VO, TMP = NEW + "elv11/fin/", NEW + "n4tmp/"; os.makedirs(TMP, exist_ok=True)
ORDER = ["n1", "n2", "s1", "n3", "s2", "n4", "pm1", "mm1", "fs1", "pm2", "s3", "c1", "x1", "s4", "x2", "r8", "y1", "y2", "s5", "c2"]
SCRIPT = {n: re.sub(r"\[[^\]]*\]\s*", "", t) for n, w, t in json.load(open(NEW + "elv11/lines.json")) if n in ORDER}
VO_A = {k: G.voice(VO + f"{k}.wav", lp=None) for k in ORDER}
_cache = TMP + "rel.json"; _sig = {k: [SCRIPT[k], len(VO_A[k])] for k in ORDER}
if os.path.exists(_cache) and json.load(open(_cache))["sig"] == _sig: REL = json.load(open(_cache))["rel"]
else:
    REL = {}
    for k in VO_A:
        p = TMP + f"{k}_pre.wav"; sf.write(p, VO_A[k], VSR); REL[k] = E.align(G.word_times(p, 0, None), SCRIPT[k])
    json.dump({"sig": _sig, "rel": REL}, open(_cache, "w"))
# one second of silence inside x1, after "Elle ouvre.": then the shock on "Sur le palier, Samir."
_ws = REL["x1"]; _j = next(n for n, w in enumerate(_ws) if E.norm(w["w"]).startswith("sur")); _cut = int((_ws[_j - 1]["e"] + _ws[_j]["s"]) / 2 * VSR)
VO_A["x1"] = np.concatenate([VO_A["x1"][:_cut], np.zeros(VSR), VO_A["x1"][_cut:]]); REL["x1"] = [dict(w, s=w["s"] + (1 if n >= _j else 0), e=w["e"] + (1 if n >= _j else 0)) for n, w in enumerate(_ws)]
dur = {k: len(v) / VSR for k, v in VO_A.items()}
T = 0.05; line_t = {}
def at(k, gap):
    global T
    line_t[k] = T; T += dur[k] + gap
at("n1", 0.3); at("n2", 0.25); at("s1", 0.3); at("n3", 0.25); at("s2", 0.35); at("n4", 0.3); at("pm1", 0.2); at("mm1", 0.3); at("fs1", 0.35); at("pm2", 0.35); at("s3", 0.35); at("c1", 1.0)
at("x1", 0.3); at("s4", 0.4); at("x2", 0.5); at("r8", 0.4)
t_rew = T; T += 0.9
at("y1", 0.3); at("y2", 0.35); at("s5", 0.4); at("c2", 3.2)
D = round(T, 2); N = int(D * FPS); print("duration", D)
def L_(k): return line_t[k] - 0.12
def wt(k, frag, n=0): return line_t[k] + [w["s"] for w in REL[k] if frag in E.norm(w["w"])][n]
def we(k): return line_t[k] + dur[k]
T_ACC = wt("n1", "quelqu") - 0.1; T_SONNE = wt("n4", "sonne") - 0.1; T_BAS = wt("n4", "bas") - 0.1; T_10 = wt("s3", "dix") - 0.1; T_SEC = wt("pm2", "sec") - 0.1; T_PLUIE = wt("pm2", "pleut") - 0.1
T_PALIER = wt("x1", "palier") - 0.05; T_TROP = wt("x1", "trop") - 0.1; T_FRAPPE = wt("y2", "frappe") - 0.1; T_VOIX = wt("y2", "voix") - 0.1
words = []
for k, t0 in line_t.items(): words += [dict(w, s=w["s"] + t0 + 0.1, e=w["e"] + t0 + 0.1, line=k) for w in REL[k]]
ST = N2.ST; SW, SH = ST["street2"].size; PSW, PSH = N1.PSW, N1.PSH


def amp(key, t, gain=9):
    a = VO_A[key]; i0 = int((t - line_t[key]) * VSR)
    return float(np.abs(a[max(0, i0):max(0, i0) + 1470]).mean() * gain) if 0 <= i0 < len(a) else 0.0
def speaking(key, t): return amp(key, t) if L_(key) < t < we(key) else 0.0
def samir_line(t): return next((k for k in ("s1", "s2", "s3", "s4", "s5") if L_(k) < t < we(k)), None)


# ---------------------------------------------------------------- Samir's camera (the reverse shot)
def samir_cam(t, mood="happy"):
    """What his phone films: Samir on his scooter in the rain, his face close, the camera bouncing with the road."""
    k = samir_line(t); a = speaking(k, t) if k else 0.0
    face = dict(happy=dict(brow=-0.2, mouth="open" if a > 0.3 else "smile"), worried=dict(brow=0.8, wide=1.15, mouth="o" if a > 0.3 else "line", look=(0.5, 0.0)),
                scared=dict(brow=1.0, wide=1.3, mouth="o", sweat=True), angry=dict(brow=-0.6, mouth="open" if a > 0.3 else "line", look=(0.3, 0.0)))[mood]
    kw = dict(samir=True, blink=blink(t, 0.5), **face); kw.update(MO.alive(t, 21, 1.2, a))
    sp = hero(2400, **kw); bg = ST["street2"].transform(ST["street2"].size, Image.AFFINE, (-1, 0, SW, 0, 1, 0)).filter(ImageFilter.GaussianBlur(10))   # his street, mirrored
    bg = Image.eval(bg, lambda v: int(v * 0.8)); im = put(bg, sp, SW * 0.5 + 20 * NOISE.noise2(t * 3, 4), SH * 1.33 + 18 * abs(NOISE.noise2(t * 6, 5)), shadow=False, mul=(0.85, 0.88, 1.0), rim=((255, 190, 120), -14, 0.6))
    im = E.spill(im, SW * 0.5, SH * 0.6, 520, 360, (150, 190, 255), 0.12)
    im = rain(E.view(im, t, 0, 1, 1.0, 1.0, 0.5, 0.5, drift=0.2), t, 140, 0.45); d = ImageDraw.Draw(im, "RGBA"); rg = np.random.default_rng(31)
    for k in range(16):                                               # he is soaked: drops run down his cap and his face
        x = rg.uniform(260, 820); y0 = rg.uniform(420, 1100); y = y0 + ((t * rg.uniform(60, 160) + rg.uniform(0, 300)) % 260)
        d.ellipse((x - 9, y - 14, x + 9, y + 14), fill=(190, 220, 255, 170)); d.ellipse((x - 3, y - 8, x + 2, y - 2), fill=(255, 255, 255, 200))
    # Always the same frame for his camera, so a viewer never mistakes him for you: the call UI, your face in the
    # corner, and his name on a green pill.
    sv = _self_view(200); m = Image.new("L", sv.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sv.width - 1, sv.height - 1), 26, fill=255)
    im.paste(sv, (W - sv.width - 70, 380), m); d = ImageDraw.Draw(im); d.rounded_rectangle((W - sv.width - 70, 380, W - 70, 380 + sv.height), 26, outline=(255, 255, 255), width=4)
    d.rounded_rectangle((70, 1360, 360, 1430), 35, fill=(30, 140, 80)); d.ellipse((92, 1384, 114, 1406), fill=(160, 255, 190))
    d.text((128, 1395), "SAMIR", font=ImageFont.truetype(E.MONT, 38), fill=(255, 255, 255), anchor="lm")
    d.rounded_rectangle((60, 200, 330, 250), 25, fill=(0, 0, 0, 160)); d.ellipse((80, 214, 102, 236), fill=(60, 220, 110))
    d.text((116, 225), "appel vidéo", font=ImageFont.truetype(E.MONT, 26), fill=(255, 255, 255), anchor="lm")
    return handheld(im, t, 2.0 if mood in ("scared", "angry") else 1.3, seed=3)


@functools.lru_cache(maxsize=4)
def _self_view(h=260):
    sp = T2.char(1000, look=(0.0, 0.2), brow=0.7, mouth="line"); f = sp.crop((150, 60, 550, 460)).resize((h, h))
    bg = Image.new("RGBA", (h, int(h * 1.35)), (30, 34, 48, 255)); bg.alpha_composite(f, (0, int(h * 0.35))); return bg


def call_screen(t):
    """The video call inside his phone: Samir fills the screen, your face in the little box."""
    sc = samir_cam(t, MOOD(t)).resize((PSW, int(PSW * H / W))).crop((0, int((PSW * H / W - PSH) / 2), PSW, int((PSW * H / W - PSH) / 2) + PSH)).convert("RGBA")
    sv = _self_view(170); m = Image.new("L", sv.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sv.width - 1, sv.height - 1), 22, fill=255)
    sc.paste(sv, (PSW - sv.width - 30, PSH - sv.height - 170), m); d = ImageDraw.Draw(sc)
    for x, col in ((PSW * 0.3, (225, 50, 50)), (PSW * 0.7, (70, 72, 90))): d.ellipse((x - 50, PSH - 130, x + 50, PSH - 30), fill=col)
    return sc


def MOOD(t):
    if t < L_("s3"): return "happy"
    if t < L_("x1"): return "worried"
    if t < L_("y1"): return "scared"
    return "angry"


# ---------------------------------------------------------------- first person: your hand, your phone
def iphone(screen, t, sw=430):
    """A phone with the proportions of an iPhone 13 (about 1 : 2.05): narrow, tall, rounded corners, a notch.
    The app screens are drawn at 580 x 880; they are scaled to the phone's width and sit under the status bar."""
    sc = screen.convert("RGB"); k = sw / sc.width; app = sc.resize((sw, int(sc.height * k)), Image.LANCZOS)
    sh = int(sw * 2.16); scr = Image.new("RGB", (sw, sh), sc.getpixel((sc.width // 2, sc.height - 4)))
    top = sc.getpixel((sc.width // 2, 6)); ImageDraw.Draw(scr).rectangle((0, 0, sw, 90), fill=top)
    scr.paste(app, (0, 90)); d = ImageDraw.Draw(scr)
    lum = sum(top) / 3; fg = (255, 255, 255) if lum < 140 else (20, 20, 24)
    d.text((44, 44), "21:4" + str(7 + int(t // 60) % 3), font=E.fI("SemiBold", 26), fill=fg, anchor="lm")
    for q in range(4): d.rectangle((sw - 92 + q * 9, 52 - q * 4, sw - 86 + q * 9, 56), fill=fg)
    d.rounded_rectangle((sw - 52, 38, sw - 20, 56), 5, outline=fg, width=2); d.rectangle((sw - 49, 41, sw - 32, 53), fill=fg)
    d.rounded_rectangle((sw / 2 - 70, 12, sw / 2 + 70, 52), 20, fill=(0, 0, 0))                      # the notch
    d.rounded_rectangle((sw / 2 - 70, sh - 26, sw / 2 + 70, sh - 18), 4, fill=fg)                    # the home bar
    bz = 16; body = Image.new("RGBA", (sw + 2 * bz, sh + 2 * bz), (0, 0, 0, 0)); bd = ImageDraw.Draw(body)
    bd.rounded_rectangle((0, 0, body.width - 1, body.height - 1), 66, fill=(28, 30, 36), outline=(150, 154, 166), width=4)
    m = Image.new("L", scr.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sw - 1, sh - 1), 52, fill=255); body.paste(scr, (bz, bz), m)
    for yy, hh in ((170, 60), (250, 60)): bd.rounded_rectangle((-2, yy, 4, yy + hh), 3, fill=(120, 124, 134))
    bd.rounded_rectangle((body.width - 4, 210, body.width + 2, 300), 3, fill=(120, 124, 134))
    gl = Image.new("RGBA", body.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).polygon([(0, 0), (body.width * 0.6, 0), (0, body.height * 0.4)], fill=(255, 255, 255, 16)); body.alpha_composite(gl)
    return body


def pov(t, screen, bg="street2", dark=0.75, tilt=0.0):
    """First person: the street (or your room) in front of you, out of focus; your hand holds the phone at the bottom."""
    base = Image.eval(ST[bg].filter(ImageFilter.GaussianBlur(12)), lambda v: int(v * dark))
    base = rain(E.view(base, t, 0, 1, 1.0, 1.0, 0.5, 0.45, drift=0.4), t, 160, 0.4) if bg.startswith("street") else E.view(base, t, 0, 1, 1.0, 1.0, 0.5, 0.45, drift=0.4)
    phr = iphone(screen, t, 400); phr = phr.rotate(4 * NOISE.noise2(t * 0.7, 2) + tilt, expand=True, resample=Image.BICUBIC)
    x, y = int(W / 2 - phr.width / 2 + 14 * NOISE.noise2(t * 0.9, 6)), int(H * 0.27 + 14 * NOISE.noise2(6, t * 0.9))
    im = base.convert("RGBA"); im.alpha_composite(phr, (x, y))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)                      # your fingers around the phone
    hx, hy = x + phr.width - 20, y + phr.height - 70                    # your hand holds the bottom-right corner, off the screen
    MO.sleeve(d, W + 60, H + 160, hx + 80, hy + 130, T2.HOOD, 160, cuff=T2.REDB)
    MO.hand(d, hx + 26, hy + 34, np.radians(-40), 1.0, T2.SKIN, grip=0.9)
    for k in range(3): fy = y + phr.height * (0.42 + 0.1 * k); d.rounded_rectangle((x + phr.width - 38, fy, x + phr.width + 24, fy + 64), 28, fill=T2.SKIN, outline=(22, 18, 34, 255), width=7)
    im.alpha_composite(lay); im = E.spill(im.convert("RGB"), W / 2, H * 0.55, 560, 700, (150, 190, 255), 0.1)
    return handheld(im, t, 1.0, seed=8)


import cv2
@functools.lru_cache(maxsize=1)
def _fisheye_maps(w, h, k=0.55):
    """Barrel distortion of a door peephole: the centre is magnified, the edges are squeezed into a circle."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); cx, cy = w / 2, h / 2; R = min(w, h) * 0.47
    dx, dy = (xx - cx) / R, (yy - cy) / R; r = np.sqrt(dx * dx + dy * dy) + 1e-6; rs = np.tan(r * k * 1.9) / np.tan(k * 1.9)
    return (cx + dx / r * rs * R * 1.25).astype(np.float32), (cy + dy / r * rs * R * 1.25).astype(np.float32), (r <= 1.0)


def peephole(t, t0, t1, who=True):
    """What your mother sees through the peephole: the landing bent into a circle, and 'Samir', head down, dry."""
    base = ST["land"].resize((W, H)).copy()
    if who:
        sp = T2.char(1250, samir=True, head=(0.0, 0.9 + 0.1 * np.sin(t * 0.6)), look=(0.0, 0.9), mouth="line", blink=True); base = put(base, sp, W * 0.5, H * 0.98, shadow=True, mul=(0.85, 0.85, 0.9))
    base = Image.eval(base, lambda v: int(min(255, v * 1.15)))
    mx, my, m = _fisheye_maps(W, H); a = cv2.remap(np.asarray(base), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    ring = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 14)[..., None]; a = (a * ring).astype(np.uint8)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for k in range(3): d.ellipse((W / 2 - W * 0.47 - k * 8, H / 2 - W * 0.47 - k * 8, W / 2 + W * 0.47 + k * 8, H / 2 + W * 0.47 + k * 8), outline=(20 + 10 * k, 18, 16), width=6)
    z = 1.0 + 0.25 * ease((t - T_SEC) / 0.6)                        # on "sec", the eye leans in
    return handheld(E.view(im.resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, z, z + 0.04, 0.5, 0.5, drift=0.2), t, 0.6, seed=12)


def mum_door(t, t0, t1):
    """Your mother, close, her face against the door in the dark hall: the reaction shot."""
    a = speaking("mm1", t); kw = dict(mum=True, look=(0.7, -0.1), blink=blink(t, 0.4), mouth="o" if a > 0.3 else "line", brow=0.8, wide=1.1)
    kw.update(MO.alive(t, 5, 1.0, a)); sp = hero(2300, **kw)
    bg = Image.eval(ST["entdark"].filter(ImageFilter.GaussianBlur(9)), lambda v: int(v * 0.9))
    im = put(bg, sp, SW * 0.44, SH * 1.18, shadow=False, mul=(0.7, 0.72, 0.86), rim=((255, 220, 160), 14, 0.7))
    im = E.spill(im, SW * 0.8, SH * 0.45, 200, 600, (255, 210, 150), 0.18)                         # the light from the landing, under the door
    return handheld(E.view(im, t, t0, t1, 1.0, 1.06, 0.48, 0.44, drift=0.3), t, 0.8, seed=5)


def map_screen(t):
    """The delivery app's map: home is the red pin; Samir's green dot is still crossing the bridge, 2.4 km away."""
    sc = Image.new("RGBA", (PSW, PSH), (228, 232, 238, 255)); d = ImageDraw.Draw(sc); rg = np.random.default_rng(4)
    for k in range(16): x, y = rg.integers(-60, PSW), rg.integers(160, PSH); d.rounded_rectangle((x, y, x + rg.integers(90, 220), y + rg.integers(70, 180)), 10, fill=(214, 218, 226))
    d.rectangle((0, 560, PSW, 640), fill=(160, 196, 232))                                          # the river
    for x in (110, 290, 470): d.line((x, 150, x + 60, PSH), fill=(255, 255, 255), width=26)
    for y in (300, 760): d.line((0, y, PSW, y - 40), fill=(255, 255, 255), width=26)
    route = [(320, 820), (330, 700), (318, 600), (300, 460), (300, 300), (420, 250)]; d.line(route, fill=(91, 51, 201), width=12, joint="curve")
    d.ellipse((396, 196, 444, 244), fill=(205, 24, 24)); d.polygon([(400, 232), (440, 232), (420, 268)], fill=(205, 24, 24)); d.ellipse((410, 210, 430, 230), fill=(255, 255, 255))
    d.rounded_rectangle((300, 150, 560, 196), 14, fill=(255, 255, 255)); d.text((430, 173), "4B · CHEZ TOI", font=E.fI("Bold", 26), fill=(205, 24, 24), anchor="mm")
    p = cl((t - T_10 + 2) / 8); sx, sy = 320 + 4 * p, 820 - 40 * p
    pul = 1 + 0.25 * np.sin(t * 6); d.ellipse((sx - 40 * pul, sy - 40 * pul, sx + 40 * pul, sy + 40 * pul), fill=(40, 170, 90, 70))
    av = T2.char(500, samir=True).crop((35, 15, 315, 295)).resize((64, 64)); m = Image.new("L", (64, 64), 0); ImageDraw.Draw(m).ellipse((0, 0, 63, 63), fill=255)
    d.ellipse((sx - 38, sy - 38, sx + 38, sy + 38), fill=(40, 170, 90)); sc.paste(av, (int(sx - 32), int(sy - 32)), m)
    d.rounded_rectangle((20, PSH - 210, PSW - 20, PSH - 40), 26, fill=(255, 255, 255)); d.text((50, PSH - 165), "SAMIR B. · en route", font=E.fI("Bold", 32), fill=(30, 120, 70), anchor="lm")
    d.text((50, PSH - 100), "arrivée dans 10 min · 2,4 km", font=E.fI("SemiBold", 30), fill=(60, 60, 70), anchor="lm")
    d.rectangle((0, 0, PSW, 130), fill=(91, 51, 201)); d.text((PSW / 2, 80), "SUIVI DE LIVRAISON", font=E.fI("Bold", 34), fill=(255, 255, 255), anchor="mm")
    return sc


def clue_card(t, t0):
    """The two Samirs on one sheet, as the bus story does with its clipboard: a fair comparison the viewer reads in 2 s.
    The lines are handwritten in as the camera arrives, the ticks and crosses land last."""
    bg = Image.eval(ST["entdark"].resize((W, H)).filter(ImageFilter.GaussianBlur(10)), lambda v: int(v * 0.55)).convert("RGBA")
    w, h = 800, 900; p = E.paper_tex(w, h, (248, 246, 236), fiber=0.04, seed=61); d = ImageDraw.Draw(p)
    d.rounded_rectangle((w / 2 - 130, -20, w / 2 + 130, 60), 18, fill=(150, 150, 158)); d.rounded_rectangle((w / 2 - 70, -10, w / 2 + 70, 30), 10, fill=(90, 92, 100))
    fh, fb = ImageFont.truetype(E.HAND, 60), ImageFont.truetype(E.HAND, 54); n = int((t - t0) * 90)
    rows = [("SAMIR AU TÉLÉPHONE", None), ("trempé par la pluie", True), ("à 10 min, sur le pont", True), ("", None),
            ("SAMIR À TA PORTE", None), ("pas une goutte", False), ("déjà là, tête baissée", False)]
    y = 110
    for txt, ok in rows:
        if not txt: y += 40; continue
        part = txt[:max(0, n)]; n -= len(txt)
        col = (205, 24, 24) if ok is None else (30, 30, 40)
        d.text((70, y), part, font=fh if ok is None else fb, fill=col)
        if ok is not None and len(part) == len(txt):
            mx, my = w - 110, y + 32
            if ok: d.line([(mx - 26, my), (mx - 6, my + 22), (mx + 30, my - 26)], fill=(30, 140, 70), width=10, joint="curve")
            else: d.line([(mx - 24, my - 24), (mx + 24, my + 24)], fill=(205, 24, 24), width=10); d.line([(mx + 24, my - 24), (mx - 24, my + 24)], fill=(205, 24, 24), width=10)
        y += 92
    p = p.rotate(-2 + 0.3 * np.sin(t * 2), expand=True, resample=Image.BICUBIC)
    E.drop_shadow(bg, p, (int(W / 2 - p.width / 2), int(1110 - p.height / 2)), blur=24, off=(12, 24), alpha=170)
    return handheld(bg.convert("RGB"), t, 0.6, seed=14)


def hero_face(t, t0, t1):
    """Your face, lit by the phone, under the rain: you have said no, he laughs."""
    kw = dict(look=(0.0, 0.6), brow=0.9, wide=1.1, mouth="frown", blink=blink(t)); kw.update(MO.alive(t, 1, 1.0))
    sp = hero(2500, **kw); im = put(N2.soft("street2") if hasattr(N2, "soft") else ST["street2"].filter(ImageFilter.GaussianBlur(5)), sp, SW * 0.47, SH * 1.275, shadow=False, mul=(0.68, 0.7, 0.82), rim=((255, 190, 120), -14, 0.5))
    im = E.spill(im, SW * 0.47, SH * 0.78, 520, 330, (120, 160, 255), 0.12)
    im = rain(E.view(im, t, t0, t1, 1.0, 1.07, 0.5, 0.47, drift=0.6), t, 140, 0.4); d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 1360, 290, 1430), 35, fill=(91, 51, 201)); d.text((180, 1395), "TOI", font=ImageFont.truetype(E.MONT, 38), fill=(255, 255, 255), anchor="mm")
    return im


def notif(im, t, t0, title, body, y=150, hot=False):
    """A text from his mother, dropping in at the top of the screen like an iPhone banner."""
    if t < t0: return
    u = ease((t - t0) / 0.25); d = ImageDraw.Draw(im); y_ = y - 160 * (1 - u); f = E.fI("SemiBold", 34); lines = []
    words_ = body.split(); cur = ""
    for w_ in words_:
        if d.textlength(cur + " " + w_, font=f) > 760: lines.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    lines.append(cur); hh = 92 + 46 * len(lines)
    d.rounded_rectangle((70, y_, W - 70, y_ + hh), 34, fill=(255, 255, 255) if not hot else (255, 236, 236), outline=RED if hot else (220, 220, 226), width=4)
    d.ellipse((100, y_ + 30, 124, y_ + 54), fill=(60, 200, 100)); d.text((140, y_ + 42), title, font=E.fI("Bold", 32), fill=(30, 30, 36), anchor="lm")
    d.text((W - 100, y_ + 42), "maintenant", font=E.fI("Regular", 26), fill=(140, 140, 150), anchor="rm")
    for k, ln in enumerate(lines): d.text((100, y_ + 88 + k * 46), ln, font=f, fill=(30, 30, 36), anchor="lm")


def app_accepted(t):
    sc, d = N1._app("21:47"); u = ease((t - T_ACC) / 0.3)
    card = Image.new("RGBA", (PSW - 50, 560), (0, 0, 0, 0)); cd = ImageDraw.Draw(card); cd.rounded_rectangle((0, 0, card.width - 1, 559), 30, fill=(255, 255, 255, 255), outline=(200, 25, 25, 255), width=5)
    cd.text((34, 30), "COMMANDE #0015", font=E.fI("Bold", 32), fill=(200, 25, 25)); cd.text((34, 130), "Adresse", font=E.fI("Regular", 28), fill=(120, 120, 130), anchor="lm"); cd.text((card.width - 34, 130), "4B · CHEZ TOI", font=E.fI("Bold", 34), fill=(200, 25, 25), anchor="rm")
    cd.text((34, 210), "Statut", font=E.fI("Regular", 28), fill=(120, 120, 130), anchor="lm"); cd.text((card.width - 34, 210), "REFUSÉE PAR TOI", font=E.fI("Bold", 30), fill=(30, 30, 36), anchor="rm")
    if u > 0:
        cd.rounded_rectangle((28, 280, card.width - 28, 520), 24, fill=(232, 246, 236)); av = T2.char(700, samir=True).crop((70, 30, 420, 380)).resize((150, 150))
        m = Image.new("L", av.size, 0); ImageDraw.Draw(m).ellipse((0, 0, 149, 149), fill=255); card.paste(av, (50, 320), m)
        cd.text((230, 360), "Acceptée par", font=E.fI("Regular", 28), fill=(80, 110, 90), anchor="lm"); cd.text((230, 420), "SAMIR B.", font=E.fI("Bold", 54), fill=(30, 120, 70), anchor="lm")
        cd.text((230, 476), "pourboire +18,00 €", font=E.fI("SemiBold", 28), fill=(30, 120, 70), anchor="lm")
    sc.alpha_composite(card, (25, 200)); return sc


def chat_screen(t):
    """Your messages to your mother, and her answers."""
    sc = Image.new("RGBA", (PSW, PSH), (12, 13, 20, 255)); d = ImageDraw.Draw(sc)
    d.rectangle((0, 0, PSW, 150), fill=(24, 25, 36)); d.ellipse((40, 86, 96, 142), fill=(230, 120, 150)); d.text((68, 114), "M", font=E.fI("Bold", 32), fill=(255, 255, 255), anchor="mm"); d.text((116, 114), "Maman", font=E.fI("Bold", 36), fill=(255, 255, 255), anchor="lm")
    f = E.fI("Regular", 34)
    def bub(y, lines, mine, hot=False):
        w = max(d.textlength(l, font=f) for l in lines) + 56; hh = 30 + 46 * len(lines); x0 = PSW - 30 - w if mine else 30
        d.rounded_rectangle((x0, y, x0 + w, y + hh), 28, fill=(40, 110, 230) if mine else ((70, 30, 34) if hot else (46, 48, 62)), outline=RED if hot else None, width=4)
        for k, l in enumerate(lines): d.text((x0 + 28, y + 38 + k * 46), l, font=f, fill=(255, 255, 255), anchor="lm")
    bub(190, ["Samir est en bas.", "Il sonne."], False)
    n = int(max(0, t - line_t["y1"]) * 22); typed = "Ne bouge pas. N'ouvre à personne."[:n]
    if typed:
        full = "Ne bouge pas. N'ouvre à personne."; br = full.index("N'ouvre")
        bub(360, [typed[:br].strip(), typed[br:]] if len(typed) > br else [typed], True)
    if t >= T_FRAPPE - 0.3: bub(540, ["Il frappe. Il dit mon", "prénom… avec ta voix."], False, hot=True)
    return sc


def facade_downstairs(t, t0, t1):
    """Your building, seen from the street: in front of the door, under the lamp, someone in a green cap."""
    im = N2._home_plate().copy(); y1 = int(SH * 0.88); dx = SW * 0.5
    sp = T2.char(380, dark=True, look=(0.0, -0.3)); a = np.asarray(sp).copy(); top = int(sp.height * 0.2)
    g = a[:top, :, 3] > 0; a[:top][g, 0:3] = np.array([30, 120, 76]); sp = Image.fromarray(a)                      # his cap is green: Samir's
    im = put(im, sp, dx + 110, y1, shadow=True)
    if t >= T_SONNE: im = E.spill(im, dx + 140, y1 - 220, 80, 80, (120, 200, 255), 0.4 * (0.5 + 0.5 * np.sin(t * 14)))
    return rain(E.view(im, t, t0, t1, 1.0, 1.35, 0.55, 0.78, drift=0.3), t, 140, 0.4)


@functools.lru_cache(maxsize=2)
def fake_samir(h):
    """Samir's face on the landing, but the eyes are the double's: white, no pupils, and the grin."""
    sp = T2.char(h, samir=True, mouth="line", blink=True, brow=0.0).copy(); d = ImageDraw.Draw(sp); s = h / 1000; cx, cy, R = sp.width / 2, 268 * s, 156 * s
    sk = (196, 146, 108, 255)
    for side in (-1, 1): d.ellipse((cx + side * 0.40 * R - 0.34 * R, cy + 0.19 * R - 0.36 * R, cx + side * 0.40 * R + 0.34 * R, cy + 0.19 * R + 0.2 * R), fill=sk)   # his own eyes, wiped
    T2.monster_face(d, cx, cy, R, skin=sk)
    return sp


def landing_open(t, t0, t1):
    """Your front door, from inside, opened by your mother: on the landing, Samir. Smiling far too much."""
    q = ease((t - (t0 + 0.2)) / 1.0); ins = Image.eval(ST["land"].resize((420, 1080)), lambda v: int(min(255, v * 1.3)))
    if t >= T_PALIER - 0.3: fs = fake_samir(900); ins = ins.copy(); ins.paste(fs, (int(150 - fs.width / 2), 1080 - fs.height + 60), fs)
    wall = Image.eval(ST["entdark"].resize((W, H)), lambda v: int(v * 0.8))
    im = MO.door_open(wall, ins, (330, 420, 750, 1500), 0.85 * q, hinge="right", leaf=N2._LEAF2, light=((255, 220, 170), 0.6))
    z = 1.0 + 0.9 * ease((t - T_TROP) / 0.8)
    return handheld(E.view(im.resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, z, z, 0.36, 0.42, drift=0.3), t, 1.2)


def door_knock(t, t0, t1):
    """Seen from inside the flat: the closed door shakes with each knock; the light under it moves."""
    wall = Image.eval(ST["entdark"].resize((W, H)), lambda v: int(v * 0.7)); knock = [T_FRAPPE + k * 0.55 for k in range(4)]
    sh = sum(np.exp(-(t - k_) * 25) * (t > k_) for k_ in knock) * 10
    im = MO.door_open(wall, (0, 0, 0), (330 + sh, 420, 750 + sh, 1500), 0.0, hinge="right", leaf=N2._LEAF2)
    im = E.spill(im, 540, 1520, 300, 30, (255, 220, 160), 0.6 + 0.3 * np.sin(t * 3))
    return handheld(E.view(im.resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, 1.0, 1.1, 0.5, 0.5, drift=0.3), t, 1.0)


def title_card(im, t):
    """Frame 0: what the best series in the niche open on: who, when, and the dilemma."""
    a = 1.0 if t < we("n1") else max(0.0, 1 - (t - we("n1")) / 0.3)
    if a <= 0: return im
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((90, 360, 990, 760), 30, fill=(10, 10, 16, int(225 * a)))
    d.text((540, 430), "LIVREUR DE NUIT", font=ImageFont.truetype(E.MONT, 64), fill=(255, 255, 255, int(255 * a)), anchor="mm")
    d.rounded_rectangle((400, 480, 680, 528), 10, fill=RED + (int(255 * a),)); d.text((540, 504), "NUIT 4 · PARTIE 1", font=ImageFont.truetype(E.MONT, 28), fill=(255, 255, 255, int(255 * a)), anchor="mm")
    d.text((540, 580), "21:47 · Jeudi · Toi, 19 ans", font=E.fI("SemiBold", 34), fill=(210, 210, 220, int(255 * a)), anchor="mm")
    d.text((540, 640), "Tu as refusé la commande pour chez toi.", font=E.fI("SemiBold", 36), fill=(255, 255, 255, int(255 * a)), anchor="mm")
    d.text((540, 690), "Quelqu'un d'autre l'a acceptée.", font=E.fI("Bold", 38), fill=(255, 210, 60, int(255 * a)), anchor="mm")
    out = im.convert("RGBA"); out.alpha_composite(lay); return out.convert("RGB")


_REC = None
def receipt(t, t0):
    """The slip: seven rules in small, and number eight in red."""
    global _REC
    rules = [r[0] + " · " + " ".join(r[1:]) for r in (["RÈGLE 1", "Ce que tu acceptes, tu le livres."], ["RÈGLE 2", "Ne prends rien de sa main."], ["RÈGLE 3", "Quand la nuit est payée : rentre."],
             ["RÈGLE 4", "Quand il est chez toi, n'appelle personne."], ["RÈGLE 5", "Il ne vit que dans le noir. Allume."], ["RÈGLE 6", "Ne lâche jamais la main tiède."], ["RÈGLE 7", "Chez toi, apporte ta propre lumière."])]
    if _REC is None:
        w, h = 760, 1260; p = E.paper_tex(w, h, (246, 244, 236), fiber=0.04, seed=54); d = ImageDraw.Draw(p)
        d.ellipse((335, 30, 425, 120), fill=N1.PURPLE); d.ellipse((366, 40, 434, 108), fill=(246, 244, 236)); d.text((380, 164), "NUIT EXPRESS", font=E.fI("Bold", 50), fill=(30, 30, 34), anchor="mm")
        f = ImageFont.truetype(E.HAND, 32); y = 230
        for r in rules: d.text((50, y), r, font=f, fill=(205, 24, 24)); y += 44
        m = Image.new("L", (w, h), 255); md = ImageDraw.Draw(m)
        for x in range(0, w, 40): md.polygon([(x, h), (x + 20, h - 26), (x + 40, h)], fill=0)
        p.putalpha(m); _REC = p
    fr = _REC.copy(); d = ImageDraw.Draw(fr); f = ImageFont.truetype(E.HAND, 66); rg = np.random.default_rng(3); n = int(np.clip((t - t0 - 0.6) * 24, 0, 999)); y = 620
    for ln in ("RÈGLE 8", "Il peut prendre le visage", "de ceux que tu aimes."):
        part = ln[:max(0, n)]; n -= len(ln); x = 50
        for ch in part: d.text((x + rg.normal(0, 0.8), y + rg.normal(0, 1.2)), ch, font=f, fill=(205, 24, 24)); x += d.textlength(ch, font=f)
        y += 76
    bg = ST["entdark"].resize((W, H)).filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.6)).convert("RGBA")
    fr = fr.resize((int(fr.width * 0.84), int(fr.height * 0.84)), Image.LANCZOS).rotate(-2 + np.sin(t * 8) * 0.2, expand=True, resample=Image.BICUBIC)
    E.drop_shadow(bg, fr, (int(W / 2 - fr.width / 2), int(860 - fr.height / 2)), blur=26, off=(14, 26), alpha=170)
    im = E.torch(bg, 540, 900, 1250, 0.5, 1.12); q = ease((t - t0 - 0.6) / 1.2)
    return E.view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t0 + 2.0, 1.0, 1.3, 0.5, 0.5 + 0.1 * q, drift=0.4)


def end_card(im, t, t0):
    """'TU FERAIS QUOI ?', two options with what each one costs, the comment prompt, the next part."""
    u = ease((t - t0) / 0.4); im = Image.blend(im, Image.new("RGB", (W, H), (8, 6, 12)), 0.7 * u); d = ImageDraw.Draw(im)
    if u <= 0: return im
    d.text((540, 470), "TU FERAIS QUOI ?", font=ImageFont.truetype(E.MONT, 76), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
    for k, (lab, sub, col) in enumerate((("A · LAISSER SAMIR MONTER", "Il le verra en face… seul.", (40, 170, 90)), ("B · L'ARRÊTER", "Ta mère reste seule avec lui.", (200, 30, 30)))):
        y = 580 + k * 230; d.rounded_rectangle((150, y, 930, y + 104), 52, fill=col); d.text((540, y + 52), lab, font=ImageFont.truetype(E.MONT, 44), fill=(255, 255, 255), anchor="mm")
        d.text((540, y + 150), sub, font=E.fI("SemiBold", 36), fill=(225, 225, 232), anchor="mm")
    if t > t0 + 0.8: d.text((540, 1110), "Écris-le en commentaire 👇".replace(" 👇", ""), font=ImageFont.truetype(E.MONT, 40), fill=(255, 210, 60), anchor="mm")
    if t > t0 + 1.2: d.rounded_rectangle((260, 1180, 820, 1260), 40, fill=(250, 30, 90)); d.text((540, 1220), "ABONNE-TOI POUR LA PARTIE 2", font=ImageFont.truetype(E.MONT, 34), fill=(255, 255, 255), anchor="mm")
    return im


def hud(im, t):
    d = ImageDraw.Draw(im); fs = ImageFont.truetype(E.MONT, 28); s_ = int(21 * 3600 + 47 * 60 + 10 + t)
    d.text((124, 232), "NUIT 4 · " + ("TA RUE" if t < L_("y2") else "CHEZ TOI"), font=fs, fill=(235, 235, 238), stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((122, 266), f"{s_ // 3600:02d}:{s_ // 60 % 60:02d}:{s_ % 60:02d}", font=ImageFont.truetype(E.MONO, 62), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))


C1 = ("OUVRE", "NE BOUGE PAS")
CUTS = [T_10, wt("s1", "fais") - 0.15] + [L_(k) for k in ("n2", "s1", "n3", "s2", "n4", "pm1", "fs1", "s3", "x1", "s4", "y1", "y2", "s5")]


def raw(i, t):
    g = ("night", 0.4); hd = True; btn = None; labels = []; nt = []
    if t < L_("n2"): im = pov(t, app_accepted(t)); g = None
    elif t < L_("s1"): im = pov(t, call_screen(t)); g = None; labels = [("plate", L_("n2") + 0.2, "TON MEILLEUR POTE")]
    elif t < wt("s1", "fais") - 0.15: im = samir_cam(t, "happy"); g = None; labels = [("stamp", wt("s1", "dix") - 0.1, "+18 €")]
    elif t < L_("n3"): im = hero_face(t, wt("s1", "fais") - 0.15, L_("s2")); g = ("night", 0.2)
    elif t < L_("s2"): im = hero_face(t, L_("n3"), L_("s2")); g = ("night", 0.2)
    elif t < L_("n4"): im = samir_cam(t, "happy"); g = None
    elif t < L_("pm1"):
        im = facade_downstairs(t, L_("n4"), L_("pm1")); g = ("night", 0.5); nt = [(L_("n4") + 0.1, "Maman", "Samir est en bas. Il sonne.", False)]
    elif t < L_("mm1"): im = mum_door(t, L_("pm1"), L_("fs1")); g = ("night", 0.4); labels = [("plate", L_("pm1") + 0.2, "TA MÈRE")]
    elif t < L_("fs1"): im = mum_door(t, L_("pm1"), L_("fs1")); g = ("night", 0.4)
    elif t < L_("s3"):
        im = peephole(t, L_("fs1"), L_("s3")); g = ("night", 0.35); labels = [("label", L_("fs1") + 0.3, "PAR LE JUDAS")]
        if t >= T_SEC: labels = [("stampL", T_SEC + 0.05, "PAS UNE GOUTTE")]
    elif t < T_10: im = samir_cam(t, "worried"); g = None; labels = [("label", L_("s3") + 0.2, "LE VRAI · TREMPÉ")]
    elif t < L_("c1"): im = pov(t, map_screen(t)); g = None
    elif t < L_("x1"):
        im = clue_card(t, L_("c1") - 0.1); g = None; btn = (C1, L_("c1"), L_("x1"), None)
    elif t < L_("s4"):
        im = landing_open(t, L_("x1"), L_("s4")) if t < wt("x1", "ouvre") + 0.6 or t >= T_PALIER - 0.3 else Image.new("RGB", (W, H), (3, 3, 6)); g = None
        if t < L_("x1") + 1.1: btn = (C1, 0, 1, "OUVRE")
    elif t < L_("r8"): im = samir_cam(t, "scared"); g = None
    elif t < t_rew: im = receipt(t, L_("r8")); g = ("paper", 0.4); hd = False
    elif t < L_("y1"): return None
    elif t < L_("y2"):
        im = pov(t, chat_screen(t)); g = None
        if t < L_("y1") + 1.1: btn = (C1, 0, 1, "NE BOUGE PAS")
    elif t < L_("s5"):
        im = door_knock(t, L_("y2"), L_("s5")) if t < T_VOIX + 0.3 else pov(t, chat_screen(t), bg="entdark", dark=0.5); g = ("night", 0.4) if t < T_VOIX + 0.3 else None
        nt = [(L_("y2"), "Maman", "Il frappe. Il dit mon prénom… avec ta voix.", True)]
    else: im = samir_cam(t, "angry"); g = None
    return im, g, hd, btn, labels, nt


_CH = {}
def choice_img(tc):
    if "c" not in _CH: _CH["c"] = finish(0, tc, raw(0, tc), captions=False)
    return _CH["c"]


def finish(i, t, r, captions=True):
    im, g, hd, btn, labels, nt = r
    if g: im = N1.GRADE(im, i, exp=g[1], warm=True, glow=g[0] != "paper")
    for kind, t0, txt in labels:
        if kind == "plate": TG.name_plate(im, t, t0, txt, (540, 470))
        elif kind == "stamp": TG.stamp_tag(im, t, t0, txt, (620, 720), 96)
        elif kind == "stampL": TG.stamp_tag(im, t, t0, txt, (540, 1300), 72)
        else: TG.label(im, t, t0, txt, (540, 1330), 38)
    if hd: hud(im, t)
    for t0, who, body, hot in nt: notif(im, t, t0, who, body, y=390, hot=hot)
    if L_("x2") + 0.2 <= t < L_("r8"): N1.stamp(im, t, L_("x2") + 0.3, "FIN DE SERVICE", y=900, size=92)
    if L_("s2") <= t < L_("n4"):                                      # half-way: the next part is announced
        d = ImageDraw.Draw(im); d.rounded_rectangle((90, 380, 520, 430), 25, fill=(0, 0, 0, 170)); d.text((110, 405), "Abonné · la partie 2 arrive", font=E.fI("SemiBold", 28), fill=(255, 255, 255), anchor="lm")
    if btn: N1.buttons(im, btn[0], t, btn[1], btn[2], btn[3])
    if t < we("n1") + 0.3: im = title_card(im, t)
    if t >= we("c2") - 0.3: im = end_card(im, t, we("c2") - 0.3)
    elif captions: G.karaoke(im, words, t, "present", hl=RED, box=False, y0=1500 if g else 1575, size0=70, stroke=7)
    return im


def render(i, t):
    r = raw(i, t)
    if r is None and t_rew <= t < t_rew + 0.9: return N1.rewind(i, t, t_rew, choice_img(L_("x1") - 0.3))
    k = int(round((t - T_PALIER) / F))                               # the one shock: after the second of silence, "Samir"
    if -2 <= k < 0: return N1.smear(finish(i, T_PALIER + 0.3, raw(i, T_PALIER + 0.3), captions=False), k)
    if k == 0: return N1.negative(finish(i, T_PALIER + 0.3, raw(i, T_PALIER + 0.3), captions=False))
    return finish(i, t, r)


def frame(i):
    t = i * F; c = next((c for c in CUTS if 0 <= t - c < 0.15), None)
    if c is not None and raw(i, c - F) is not None:
        q = (t - c) / 0.15; im = Image.blend(render(i, c - F), render(i, t), q * q * (3 - 2 * q))
    else: im = render(i, t)
    im.save(TMP + f"f{i:05d}.jpg", quality=93)


if __name__ == "__main__":
    from multiprocessing import Pool
    from scipy.signal import butter, sosfiltfilt
    STEP = os.environ.get("EI_STEP"); RANGE = os.environ.get("EI_RANGE"); sig = json.dumps(sorted(line_t.items()))
    if not os.environ.get("EI_AUDIO_ONLY"):
        todo = [i for i in range(N) if not STEP or i % int(STEP) == 0]
        if RANGE:
            if not os.path.exists(TMP + "timeline.sig") or open(TMP + "timeline.sig").read() != sig or len(glob.glob(TMP + "f*.jpg")) != N: sys.exit("EI_RANGE needs the frames of a full render with the same timeline")
            spans = [tuple(float(v) for v in r.split("-")) for r in RANGE.split(",")]; todo = [i for i in range(N) if any(a_ - 0.25 <= i * F <= b_ + 0.25 for a_, b_ in spans)]
        else:
            for f in glob.glob(TMP + "f*.jpg"): os.remove(f)
        with Pool(os.cpu_count() or 4) as pool: pool.map(frame, todo, chunksize=6)
        if not STEP: open(TMP + "timeline.sig", "w").write(sig)
    if STEP: print("test ok", D); sys.exit(0)
    NS = int(D * VSR) + VSR; ts = np.arange(NS) / VSR; mix = np.zeros(NS); rng = np.random.default_rng(5)
    def add(s_, at_, g=1.0):
        i0 = int(at_ * VSR); j0 = min(NS, i0 + len(s_))
        if j0 > i0 and i0 >= 0: mix[i0:j0] += s_[: j0 - i0] * g
    def tone(f, d_, decay): x = np.arange(int(d_ * VSR)) / VSR; return np.sin(2 * np.pi * f * x) * np.exp(-x * decay)
    def boom(): x = np.arange(int(1.4 * VSR)) / VSR; return np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x * 4) + 30) / VSR) * np.exp(-x * 2.6)
    def thump(): x = np.arange(int(0.25 * VSR)) / VSR; return np.sin(2 * np.pi * 52 * x) * np.exp(-x * 22)
    def click(): n = int(0.012 * VSR); return rng.standard_normal(n) * np.exp(-np.arange(n) / VSR * 500)
    def sweep(): x = np.arange(int(0.9 * VSR)) / VSR; return np.sin(2 * np.pi * np.cumsum(1800 - 1500 * x / 0.9) / VSR) * 0.25 + rng.standard_normal(len(x)) * 0.12
    def band(lo, hi, n): return sosfiltfilt(butter(2, [lo, hi], btype="band", fs=VSR, output="sos"), rng.standard_normal(n))
    def heart(a_, b_, per=0.55, g=0.9):
        for q in np.arange(a_, b_, per): add(thump(), q, g); add(thump(), q + 0.19, g * 0.65)
    def ping(at_): add(tone(1318, 0.3, 9) + tone(1760, 0.3, 10) * 0.6, at_, 0.3)
    def buzz(at_): x = np.arange(int(0.4 * VSR)) / VSR; add(np.sin(2 * np.pi * 150 * x) * (np.sin(2 * np.pi * 6 * x) > 0) * 0.5, at_, 0.45)
    outside = (ts < L_("y2")) & ~((ts >= L_("pm1")) & (ts < L_("s3"))); mix += band(1500, 7000, NS) * 0.3 * outside
    on_call = ((ts >= L_("n2")) & (ts < L_("pm1"))) | ((ts >= L_("s3")) & (ts < L_("x1"))) | ((ts >= L_("s4")) & (ts < L_("x2"))) | (ts >= L_("s5"))
    mix += band(80, 300, NS) * 0.25 * on_call * (1 + 0.3 * np.sin(ts * 9))                                 # Samir's scooter engine through the call
    add(boom(), 0.0, 0.5); buzz(0.02); ping(T_ACC); ping(L_("n2") + 0.2); add(tone(523, 0.25, 6) + tone(659, 0.25, 6) * 0.7, L_("n2") + 0.4, 0.3)
    buzz(L_("n4")); ping(L_("n4") + 0.05); x = np.arange(int(0.45 * VSR)) / VSR; add(np.sign(np.sin(2 * np.pi * 420 * x)) * 0.5 * np.exp(-x * 2), T_SONNE, 0.35)
    add(click() * 2, L_("pm1") + 0.9, 0.7); add(tone(2200, 0.05, 80), L_("pm1") + 0.92, 0.3); add(boom(), T_SEC, 0.7)          # the peephole cover
    add(boom(), T_10 + 0.3, 0.6); heart(L_("s3"), L_("x1"), 0.5)
    for k in range(3): add(tone(1200, 0.05, 60), we("c1") + 0.1 + k * 0.26, 0.45)
    xx = np.arange(int(0.8 * VSR)) / VSR; add(np.sin(2 * np.pi * np.cumsum(140 + 160 * xx) / VSR) * np.exp(-xx * 3) * 0.3, wt("x1", "ouvre"), 0.6)
    mute = (ts >= wt("x1", "ouvre") + 0.6) & (ts < T_PALIER - 0.05)
    add(np.convolve(rng.standard_normal(int(0.14 * VSR)), np.ones(25) / 25, "same") * 9, T_PALIER - 0.08, 0.5); add(boom(), T_PALIER, 1.2); add(boom(), T_TROP, 0.7)
    add(boom(), L_("x2") + 0.3, 0.8)
    for k in range(46): add(click() * 0.5, L_("r8") + 0.5 + k * 0.05, 0.5)
    add(sweep(), t_rew, 0.8)
    for k in range(int(dur["y1"] * 8)): add(click() * 0.4, line_t["y1"] + 0.2 + k * 0.12, 0.4)                    # typing
    ping(T_FRAPPE - 0.3)
    for k in range(4): add(thump() * 1.4, T_FRAPPE + k * 0.55, 1.0); add(np.convolve(rng.standard_normal(int(0.05 * VSR)), np.ones(10) / 10, "same") * 3, T_FRAPPE + k * 0.55, 0.4)
    add(boom(), T_VOIX, 0.8); heart(L_("y2"), D, 0.47, 0.9)
    x = np.arange(int(1.2 * VSR)) / VSR; add(band(60, 400, len(x)) * np.sin(np.pi * x / 1.2) * 6, L_("s5") + 0.2, 0.5)                    # he revs the engine
    add(tone(1046, 0.4, 6) + tone(1568, 0.4, 7) * 0.6, we("c2") + 0.9, 0.3)
    vox = np.zeros(NS)
    for k, t0 in line_t.items():
        v = VO_A[k]
        if k == "fs1": v = sosfiltfilt(butter(3, 1800, btype="low", fs=VSR, output="sos"), v) * 1.2                         # through the front door
        if k.startswith("s"): v = sosfiltfilt(butter(3, [250, 4200], btype="band", fs=VSR, output="sos"), v) * 1.4          # through the phone
        i0 = int(t0 * VSR); j0 = min(NS, i0 + len(v)); vox[i0:j0] += v[: j0 - i0]
    act = np.convolve((np.convolve(np.abs(vox), np.ones(2205) / 2205, "same") > 0.01).astype(float), np.ones(13230) / 13230, "same")
    mix = mix / np.abs(mix).max() * 0.55 * (1 - 0.6 * np.clip(act, 0, 1)) * (1 - np.convolve(mute.astype(float), np.ones(2205) / 2205, "same")) + vox / (np.abs(vox).max() + 1e-9) * 0.9
    mix = mix[: int(D * VSR)]; mix *= np.clip((D - ts[: len(mix)]) / 0.3, 0, 1); sf.write(TMP + "mix.wav", mix / np.abs(mix).max() * 0.9, VSR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", TMP + "f%05d.jpg", "-i", TMP + "mix.wav",
                    "-c:v", "libx264", "-crf", "24", "-maxrate", "3200k", "-bufsize", "6400k", "-preset", "slow", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-g", "60",
                    "-af", "loudnorm=I=-13:TP=-1.0:LRA=9,volume=1.3,alimiter=limit=0.89", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", _out], check=True)
    print("ok", _out, D)
