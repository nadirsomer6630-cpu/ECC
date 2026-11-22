"""LIVREUR DE NUIT, nuit 2: "La maison". About 2 min. It picks up the end of nuit 1 (his mother thinks he is home,
he is still in the street) and pays off the vote inside the video: both outcomes are shown. Two choices, each wrong
one ends in a loss with a clue shown before and a rule written on the slip; the end is an A/B that only returning
viewers can solve (the red bracelet). Reuses the helpers of nuit1.py.
usage: HF_HOME=... nuit2.py <out.mp4>   (EI_STEP, EI_RANGE, EI_AUDIO_ONLY as in nuit1)"""
import os, sys, json, glob, subprocess, functools, re
_out = sys.argv[1]; sys.argv = ["nuit1.py", "/tmp/unused.mp4"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from opensimplex import OpenSimplex
import nuit1 as N1
E, G, T2 = N1.E, N1.G, N1.T2
W, H, FPS, VSR, F, RED, NEW = E.W, E.H, E.FPS, E.VSR, E.F, E.RED, E.NEW
hero, put, mixp, walk, bob, cl, ease, xf, blink = N1.hero, N1.put, N1.mixp, N1.walk, N1.bob, N1.cl, N1.ease, N1.xf, N1.blink
VO, TMP = NEW + "elv9/fin/", NEW + "n2tmp/"; os.makedirs(TMP, exist_ok=True)
ORDER = ["h0", "h1", "c0", "a1", "a2", "av", "a3", "a4", "r4", "b1", "b2", "b3", "b4", "m1", "d1", "c1", "k1", "k2", "k3", "r5",
         "l1", "l2", "l3", "l4", "l5", "c2"]
SCRIPT = {n: re.sub(r"\[[^\]]*\]\s*", "", t) for n, w, t in json.load(open(NEW + "elv9/lines.json")) if n in ORDER}
VO_A = {k: G.voice(VO + f"{k}.wav", lp=None) for k in ORDER}
_cache = TMP + "rel.json"; _sig = {k: [SCRIPT[k], len(VO_A[k])] for k in ORDER}
if os.path.exists(_cache) and json.load(open(_cache))["sig"] == _sig: REL = json.load(open(_cache))["rel"]
else:
    REL = {}
    for k in VO_A:
        p = TMP + f"{k}_pre.wav"; sf.write(p, VO_A[k], VSR); REL[k] = E.align(G.word_times(p, 0, None), SCRIPT[k])
    json.dump({"sig": _sig, "rel": REL}, open(_cache, "w"))
# One second of silence inside k1, between "Tu restes dans le noir." and "Une main froide...": the shock comes after it.
_ws = REL["k1"]; _j = next(n for n, w in enumerate(_ws) if E.norm(w["w"]).startswith("une")); _cut = int((_ws[_j - 1]["e"] + _ws[_j]["s"]) / 2 * VSR)
VO_A["k1"] = np.concatenate([VO_A["k1"][:_cut], np.zeros(VSR), VO_A["k1"][_cut:]]); REL["k1"] = [dict(w, s=w["s"] + (1 if n >= _j else 0), e=w["e"] + (1 if n >= _j else 0)) for n, w in enumerate(_ws)]
dur = {k: len(v) / VSR for k, v in VO_A.items()}
T = 0.05; line_t = {}
def at(k, gap):
    global T
    line_t[k] = T; T += dur[k] + gap
at("h0", 0.35); at("h1", 0.35); at("c0", 1.0)                                                  # the hook, last night's choice
at("a1", 0.3); at("a2", 0.3); at("av", 0.4); at("a3", 0.35); at("a4", 0.5); at("r4", 0.4)      # you called her
t_rew1 = T; T += 0.9
at("b1", 0.3); at("b2", 0.35); at("b3", 0.35); at("b4", 0.25); at("m1", 0.3); at("d1", 0.35); at("c1", 1.0)   # you ran home
at("k1", 0.3); at("k2", 0.35); at("k3", 0.5); at("r5", 0.4)                                   # you stayed in the dark
t_rew2 = T; T += 0.9
at("l1", 0.3); at("l2", 0.35); at("l3", 0.35); at("l4", 0.6); at("l5", 0.4); at("c2", 1.8)    # you turned the torch on
D = round(T, 2); N = int(D * FPS); print("duration", D)
def L_(k): return line_t[k] - 0.12
def wt(k, frag, n=0): return line_t[k] + [w["s"] for w in REL[k] if frag in E.norm(w["w"])][n]
def we(k): return line_t[k] + dur[k]
T_RUE = wt("h0", "toi") - 0.1; T_NOIR = wt("h1", "noir") - 0.1; T_DEC = wt("a2", "décroche") - 0.1; T_CLE = wt("a3", "clé") - 0.1
T_KM = line_t["b1"]; T_SCOOT = wt("b2", "scooter") - 0.1; T_CHAUD = wt("b2", "chaud") - 0.1; T_AMP = wt("b3", "ampoules") - 0.1
T_MAIN = wt("k1", "main") - 0.05; T_PORTE = wt("k2", "ferme") - 0.1; T_EXT = wt("k2", "extérieur") - 0.1
T_TORCH = wt("l1", "lampe") - 0.1; T_VIDE = wt("l1", "vide") - 0.1; T_SAC = wt("l3", "sac") - 0.1; T_OFF = wt("l4", "teint") - 0.05
T_GAUCHE = wt("l5", "gauche") - 0.1; T_DROITE = wt("l5", "droite") - 0.1; T_BRAC = wt("l5", "bracelet") - 0.1
words = []
for k, t0 in line_t.items(): words += [dict(w, s=w["s"] + t0 + 0.1, e=w["e"] + t0 + 0.1, line=k) for w in REL[k]]

HD = NEW + "n2hd/"
ST = dict(N1.ST); ST.update({k: E.still(HD + f"{k}_0001.png") for k in ("kitlit", "kitdark", "kitlitbag", "kitdarkbag", "entlit", "entdark")})
SW, SH = ST["kitdark"].size
KP = json.load(open(HD + "kitlitbag_pos.json"))
NOISE = OpenSimplex(7)
import n2motion as MO; MO.bind(sys.modules[__name__])
PSW, PSH = N1.PSW, N1.PSH
FAR = 0.505 * 2304


def amp(key, t, gain=6):
    a = VO_A[key]; i0 = int((t - line_t[key]) * VSR)
    return float(np.abs(a[max(0, i0):max(0, i0) + 1470]).mean() * gain) if 0 <= i0 < len(a) else 0.0


def talk(key, t):
    """Mouth shape from the loudness of her own line: closed, half, open."""
    a = amp(key, t, 9)
    return "o" if a > 0.3 else "line"


# ---------------------------------------------------------------- organic motion
def handheld(im, t, amp_=1.0, seed=0.0):
    """A held camera: slow noise drift plus a tremor that grows with the tension (amp_). Scaled up 2 % so no edge shows."""
    if amp_ <= 0.01: return im
    nx = NOISE.noise2(t * 0.9, seed) * 9 + NOISE.noise2(t * 7, seed + 3) * 2.2 * amp_; ny = NOISE.noise2(t * 0.8, seed + 7) * 9 + NOISE.noise2(t * 6.5, seed + 9) * 2.2 * amp_
    rot = NOISE.noise2(t * 0.6, seed + 11) * 0.35 * amp_; z = 1.02 + 0.004 * amp_
    return im.rotate(rot, resample=Image.BICUBIC, center=(W / 2, H / 2), translate=(nx * amp_, ny * amp_)).transform((W, H), Image.EXTENT, (W * (1 - 1 / z) / 2, H * (1 - 1 / z) / 2, W * (1 + 1 / z) / 2, H * (1 + 1 / z) / 2), Image.BICUBIC)


def rain(im, t, n=170, a=0.5):
    """Fine rain, falling slightly slanted; each drop has its own speed and length (deterministic, no flicker)."""
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); rg = np.random.default_rng(11); w_, h_ = im.size
    for k in range(n):
        x0, y0, sp, ln = rg.uniform(0, w_ + 300), rg.uniform(0, h_), rg.uniform(1400, 2300), rg.uniform(26, 60)
        y = (y0 + t * sp) % (h_ + 80) - 40; x = (x0 - t * sp * 0.18) % (w_ + 300) - 150
        d.line((x, y, x - ln * 0.18, y - ln), fill=(185, 200, 230, int(255 * a * rg.uniform(0.3, 1))), width=2)
    out = im.convert("RGBA"); out.alpha_composite(lay); return out.convert("RGB")


def motes(im, t, cx, cy, R, n=60, a=0.8):
    """Dust floating in a beam of light: only visible inside the beam, drifting on noise."""
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); rg = np.random.default_rng(5)
    for k in range(n):
        bx, by = rg.uniform(-1, 1), rg.uniform(-1, 1)
        x = cx + R * (bx + 0.25 * NOISE.noise2(t * 0.25, k)); y = cy + R * (by + 0.25 * NOISE.noise2(k, t * 0.25))
        f = max(0.0, 1 - ((x - cx) ** 2 + (y - cy) ** 2) / R ** 2)
        if f > 0: r = rg.uniform(1.5, 3.6); d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 248, 235, int(255 * a * f * rg.uniform(0.3, 1))))
    out = im.convert("RGBA"); out.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.8))); return out.convert("RGB")


def steam(im, t, x, y, a=1.0):
    """Warm steam rising from the bag: a few soft curls on noise."""
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(7):
        ph = (t * 0.45 + k / 7) % 1; yy = y - ph * 330; xx = x + NOISE.noise2(ph * 2.2, k) * 70 + (k - 3) * 9; r = 16 + ph * 46
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=(240, 240, 245, int(70 * a * np.sin(np.pi * ph))))
    out = im.convert("RGBA"); out.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14))); return out.convert("RGB")


def reveal(dark, lit, x, y, R, lo=0.12):
    """The phone torch: the lit render shows through a soft cone around (x, y); everything else is the dark render, darker."""
    q = 4; w_, h_ = dark.size; yy, xx = np.mgrid[0:h_ // q, 0:w_ // q].astype(np.float32) * q
    m = np.clip(1.25 - ((xx - x) ** 2 + (yy - y) ** 2) / (R * R), 0, 1) ** 1.6
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((w_, h_), Image.BILINEAR)).astype(np.float32)[..., None] / 255
    a = np.asarray(dark).astype(np.float32) * (lo + (1 - lo) * 0.45) * (1 - m) + np.asarray(lit).astype(np.float32) * m * 1.1
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def breathe(t, k=1.0): return dict(lean=round(0.012 * k * float(np.sin(t * 2.4)), 3))


# ---------------------------------------------------------------- shots
def street_open(t, t0, t1):
    """Still in the street, phone in hand, rain. He stands, then starts to look up the road."""
    kw = mixp(dict(look=(0.0, 0.8), brow=0.6, armR=(0.3, 2.0)), dict(look=(0.7, 0.0), brow=1.0, wide=1.2, armR=(0.3, 1.8)), ease((t - t0 - 0.6) / 0.5)); kw.update(MO.alive(t, 1))
    sp = hero(1380, phone="R", mouth="line", blink=blink(t), **kw)
    im = put(ST["street2"], sp, SW * 0.42, SH * 1.0, mul=(0.78, 0.8, 0.95), rim=((255, 200, 140), -10, 0.6))
    im = E.spill(im, SW * 0.47, SH * 0.6, 220, 220, (120, 160, 255), 0.18)
    return rain(E.view(im, t, t0, t1, 1.0, 1.08, 0.5, 0.52, drift=0.3), t)


@functools.lru_cache(maxsize=1)
def _home_plate():
    """His building: five floors, every window dark. One of them, the fourth floor, is his."""
    im = Image.new("RGB", (SW, SH), (7, 9, 18)); d = ImageDraw.Draw(im)
    for y in range(0, SH, 4): d.rectangle((0, y, SW, y + 4), fill=(int(6 + 10 * y / SH), int(8 + 11 * y / SH), int(16 + 22 * y / SH)))
    rg = np.random.default_rng(8)
    for _ in range(110): x, y = rg.integers(0, SW), rg.integers(0, int(SH * 0.4)); d.point((x, y), fill=(150, 160, 190))
    d.ellipse((SW * 0.72, SH * 0.07, SW * 0.72 + 120, SH * 0.07 + 120), fill=(220, 224, 236))
    for bx, bw, bh, c in ((-60, 330, 0.48, 15), (1010, 360, 0.55, 13)): d.rectangle((bx, SH * (0.9 - bh), bx + bw, SH * 0.9), fill=(c, c + 1, c + 8))
    x0, x1, y0, y1 = int(SW * 0.18), int(SW * 0.82), int(SH * 0.3), int(SH * 0.88)
    d.rectangle((x0, y0, x1, y1), fill=(34, 30, 34)); d.rectangle((x0 - 14, y0 - 20, x1 + 14, y0 + 10), fill=(44, 40, 46))
    cols, rows = 4, 5; cw = (x1 - x0 - 60) / cols; rh = (y1 - y0 - 330) / rows; WIN.clear()
    for r in range(rows):
        for c in range(cols):
            wx, wy = x0 + 30 + c * cw + 22, y0 + 50 + r * rh + 18; ww, wh = cw - 44, rh - 46
            d.rectangle((wx - 6, wy - 6, wx + ww + 6, wy + wh + 6), fill=(18, 16, 20)); d.rectangle((wx, wy, wx + ww, wy + wh), fill=(10, 12, 22))
            d.line((wx + ww / 2, wy, wx + ww / 2, wy + wh), fill=(22, 22, 30), width=5); d.rectangle((wx - 10, wy + wh + 4, wx + ww + 10, wy + wh + 14), fill=(52, 48, 54))
            WIN[(r, c)] = (wx, wy, wx + ww, wy + wh)
    dx = SW * 0.5; d.rectangle((dx - 80, y1 - 250, dx + 80, y1), fill=(14, 12, 14)); d.rectangle((dx - 64, y1 - 236, dx + 64, y1), fill=(36, 30, 26))
    d.rectangle((0, y1, SW, SH), fill=(16, 17, 24)); d.rectangle((0, y1, SW, y1 + 16), fill=(44, 45, 56))
    d.rectangle((1100, y1 - 620, 1112, y1), fill=(10, 10, 14)); d.rectangle((1012, y1 - 620, 1112, y1 - 608), fill=(10, 10, 14)); d.ellipse((996, y1 - 612, 1036, y1 - 590), fill=(255, 220, 160))
    im = E.spill(im, 1016, y1 - 330, 300, 440, (255, 200, 130), 0.22)
    return im
WIN = {}


def home_facade(t, t0, t1):
    """His window, fourth floor: a weak blue light, like a screen. On "il aime le noir" it goes out."""
    im = _home_plate().copy(); x0_, y0_, x1_, y1_ = WIN[(1, 2)]; on = 1 - ease((t - T_NOIR) / 0.12)
    fl = 0.6 + 0.4 * (0.5 + 0.5 * NOISE.noise2(t * 6, 1.0))
    if on > 0:
        d = ImageDraw.Draw(im); d.rectangle((x0_, y0_, x1_, y1_), fill=tuple(int(c * on * fl) for c in (60, 90, 170)))
        d.line(((x0_ + x1_) / 2, y0_, (x0_ + x1_) / 2, y1_), fill=(22, 22, 30), width=5)
        im = E.spill(im, (x0_ + x1_) / 2, (y0_ + y1_) / 2, 220, 200, (90, 130, 255), 0.35 * on * fl)
        d = ImageDraw.Draw(im); d.ellipse(((x0_ + x1_) / 2 - 26, y1_ - 120, (x0_ + x1_) / 2 + 26, y1_ - 68), fill=(6, 6, 10)); d.rounded_rectangle(((x0_ + x1_) / 2 - 40, y1_ - 72, (x0_ + x1_) / 2 + 40, y1_), 16, fill=(6, 6, 10))
    im = rain(im, t, 120, 0.35)
    return E.view(im, t, t0, t1, 1.0, 1.18, 0.5, 0.42, drift=0.4)


def win_xy(t, t0, t1):
    x0_, y0_, x1_, y1_ = WIN[(1, 2)]; return E.view_xy((SW, SH), t, t0, t1, 1.0, 1.18, 0.5, 0.42, (x0_ + x1_) / 2 / SW, (y0_ + y1_) / 2 / SH, drift=0.4)


@functools.lru_cache(maxsize=1)
def hook_screen():
    """Frame 0: her last message from nuit 1, and the red tag that says what is wrong, as the reference videos do."""
    sc = N1.mum_screen(N1.T_NOIRQ + 3).copy(); d = ImageDraw.Draw(sc); f = E.fI("Bold", 34); txt = "TU N'ES PAS ENCORE RENTRÉ."; w_ = d.textlength(txt, font=f) + 50
    d.rounded_rectangle((PSW / 2 - w_ / 2, 760, PSW / 2 + w_ / 2, 830), 14, fill=(200, 25, 25)); d.text((PSW / 2, 795), txt, font=f, fill=(255, 255, 255), anchor="mm")
    return sc


def call_screen(t):
    """Calling Maman. It rings for a long time; then someone picks up and the timer starts. The voice line moves on her side."""
    sc = Image.new("RGBA", (PSW, PSH), (12, 13, 22, 255)); d = ImageDraw.Draw(sc)
    g = Image.new("RGBA", (PSW, PSH), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((40, 60, PSW - 40, 560), fill=(150, 60, 90, 90)); sc.alpha_composite(g.filter(ImageFilter.GaussianBlur(70))); d = ImageDraw.Draw(sc)
    up = t >= T_DEC; d.text((70, 52), "02:52", font=E.fI("SemiBold", 30), fill=(255, 255, 255))
    pr = 112 + (10 * np.sin(t * 6) if not up else 0); d.ellipse((PSW / 2 - pr - 14, 300 - pr - 14, PSW / 2 + pr + 14, 300 + pr + 14), outline=(230, 120, 150), width=5)
    d.ellipse((PSW / 2 - 110, 190, PSW / 2 + 110, 410), fill=(230, 120, 150)); d.text((PSW / 2, 300), "M", font=E.fI("Bold", 110), fill=(255, 255, 255), anchor="mm")
    d.text((PSW / 2, 480), "Maman", font=E.fI("Bold", 76), fill=(255, 255, 255), anchor="mm")
    if not up: d.text((PSW / 2, 556), "appel en cours" + "." * (1 + int(t * 2) % 3), font=E.fI("Medium", 32), fill=(190, 195, 215), anchor="mm")
    else:
        s_ = int(t - T_DEC); d.text((PSW / 2, 556), f"00:{s_:02d}", font=ImageFont.truetype(E.MONO, 38), fill=(120, 230, 150), anchor="mm")
        a_ = amp("av", t, 9)
        for q in range(15): hh = 4 + 46 * min(1.0, a_) * abs(np.sin(q * 1.3 + t * 15)); d.rounded_rectangle((PSW / 2 - 150 + q * 21, 640 - hh, PSW / 2 - 138 + q * 21, 640 + hh), 5, fill=(120, 230, 150))
    for x, col in ((PSW * 0.3, (225, 50, 50)), (PSW * 0.7, (70, 72, 90))): d.ellipse((x - 58, 740, x + 58, 856), fill=col)
    d.rounded_rectangle((PSW * 0.3 - 30, 789, PSW * 0.3 + 30, 807), 9, fill=(255, 255, 255))
    return sc


def key_shot(t, t0, t1):
    """His own front door. The key will not go in: the lock has been changed. The hand shakes harder at every try."""
    global _DOOR
    if _DOOR is None:
        im = E.paper_tex(W, H, (92, 62, 40), fiber=0.12, seed=21).convert("RGB"); a = np.asarray(im).astype(np.float32)
        a *= (0.85 + 0.15 * np.sin(np.linspace(0, 40, W) + np.random.default_rng(3).normal(0, 0.3, W)))[None, :, None]; im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((420, 760, 660, 1240), 40, fill=(150, 130, 90), outline=(70, 56, 36), width=10); d.ellipse((470, 820, 610, 960), fill=(190, 170, 120), outline=(70, 56, 36), width=8)
        d.ellipse((510, 860, 570, 920), fill=(222, 210, 170)); d.rounded_rectangle((532, 860, 548, 930), 6, fill=(20, 16, 12))
        d.rounded_rectangle((470, 1060, 620, 1110), 22, fill=(170, 150, 100), outline=(70, 56, 36), width=8)
        d.text((540, 600), "4B", font=E.fI("Bold", 90), fill=(200, 170, 110), anchor="mm"); _DOOR = im
    im = _DOOR.copy(); u = t - T_CLE; tries = int(max(0, u) / 0.7); ph = (max(0, u) % 0.7) / 0.7
    push = 0 if u < 0 else (np.sin(np.pi * min(1, ph * 1.6)) * 30)
    shake = (2 + 4 * min(3, tries)) * NOISE.noise2(t * 18, 2); kx, ky = 560 + shake + 120 - push, 890 + shake * 0.5
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); o = (22, 18, 34, 255)
    d.polygon([(kx - 40, ky - 10), (kx + 40, ky - 26), (kx + 40, ky + 26), (kx - 40, ky + 10)], fill=(200, 200, 210, 255), outline=o)
    d.ellipse((kx + 20, ky - 60, kx + 130, ky + 60), fill=(205, 205, 215, 255), outline=o, width=6); d.ellipse((kx + 60, ky - 14, kx + 88, ky + 14), fill=(0, 0, 0, 0))
    hx, hy = kx + 170, ky + 30; MO.sleeve(d, hx + 460, hy + 520, hx + 70, hy + 90, T2.HOOD, 150, cuff=T2.REDB)
    MO.hand(d, hx, hy, np.radians(-62), 1.25, T2.SKIN, grip=0.85)
    im.paste(lay, (0, 0), lay)
    im = E.torch(im, 540 + 30 * NOISE.noise2(t, 5), 900, 760, 0.18, 1.1)                       # lit only by the phone in the other hand
    return E.view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t1, 1.0, 1.08, 0.5, 0.48, drift=0.3)
_DOOR = None


def run_shot(t, t0, t1):
    """He runs home through the rain: high knees, arms pumping, leaning forward; the camera runs with him."""
    ph = (t - t0) / 0.62; kw = walk(ph, 1.35); s = float(np.sin(2 * np.pi * ph))
    kw.update(lean=0.1 + 0.02 * s)
    sp = hero(1420, look=(0.3, 0.0), wide=1.15, brow=0.9, mouth="o", sweat=True, **kw)
    im = put(ST["street2"], sp, SW * 0.45, SH * 1.02 - bob(ph) * 30, mul=(0.78, 0.8, 0.95), rim=((255, 200, 140), -10, 0.6))
    return handheld(rain(E.view(im, t, t0, t1, 1.0, 1.1, 0.5, 0.52, drift=0.3), t), t, 3.0)


def arrive_shot(t, t0, t1):
    """In front of his building: his scooter is already there. He bends over, out of breath; heat still shimmers over the engine."""
    base = ST["street"]; q = ease((t - T_SCOOT) / 0.6); ph = t * 1.6
    kw = mixp(dict(lean=0.16, armL=(0.1, 0.4), armR=(0.1, 0.4), look=(0.0, 0.5), brow=0.8), dict(lean=0.02, armL=(0.1, 0.3), armR=(0.2, 0.6), look=(0.8, 0.1), brow=1.0, wide=1.25), q)
    kw["lean"] = round(kw["lean"] + 0.02 * float(np.sin(ph * 3)), 3)
    sp = hero(1300, mouth="o", sweat=True, blink=blink(t), **kw)
    im = put(base, sp, SW * 0.3, SH * 1.0, mul=(0.8, 0.82, 0.95), rim=((255, 200, 140), -10, 0.6))
    if t >= T_CHAUD - 0.4:                                            # heat haze over the engine: the image above it ripples
        a = np.asarray(im).copy(); x0_, x1_, y0_, y1_ = int(SW * 0.66), int(SW * 0.86), int(SH * 0.62), int(SH * 0.75); k_ = cl((t - T_CHAUD + 0.4) / 0.4)
        for y in range(y0_, y1_, 2): a[y:y + 2, x0_:x1_] = np.roll(a[y:y + 2, x0_:x1_], int(5 * k_ * np.sin(y * 0.07 + t * 14)), axis=1)
        im = Image.fromarray(a)
    return rain(E.view(im, t, t0, t1, 1.0, 1.1, 0.5, 0.55, drift=0.4), t, 120, 0.4)


def corridor_shot(t, t0, t1):
    """Inside, door behind him: the corridor in the dark. Every ceiling socket is empty. Dust in the moonlight from the kitchen."""
    im = Image.blend(ST["entdark"], Image.eval(ST["entlit"], lambda v: int(v * 0.4)), 0.3 + 0.2 * ease((t - t0) / 3))    # his eyes adjust to the dark
    im = motes(im, t, SW * 0.5, SH * 0.55, 330, 50, 0.5)
    return handheld(E.view(im, t, t0, t1, 1.0, 1.16, 0.5, 0.48, drift=0.4), t, 1.2)


def socket_xy(t, t0, t1): return E.view_xy((SW, SH), t, t0, t1, 1.0, 1.16, 0.5, 0.48, 0.5, 0.075, drift=0.4)


def seated(base, who, side, t, lit=1.0):
    """A character on a real chair behind the table: drawn whole, cut at the table's far edge, breathing and moving."""
    cx = KP["chairL" if side < 0 else "chairR"][0] * SW
    if who in ("mum", "mum_l"):
        key = "m1" if who == "mum" else "l2"; a = amp(key, t, 9) if L_(key) < t < we(key) else 0.0
        kw = dict(mum=True, look=(0.6, 0.1), brow=0.2 + 0.3 * min(1, a), blink=blink(t, 0.7), mouth=talk(key, t) if a > 0 else "line"); kw.update(MO.gesture(t, 3, a)); kw.update(MO.alive(t, 3, 1.0, a))
        sp = hero(760, **kw)
    else:
        kw = MO.alive(t, 9, 0.6); sp = T2.char(760, dark=True, look=(-0.6 + 0.2 * NOISE.noise2(t * 0.4, 2), 0.0), head=kw["head"])
    # Seated: the hips are on the seat, so only the chest, the arms and the head rise above the table's far edge,
    # and the chair's backrest shows around the shoulders.
    sp = sp.copy(); vis = 0.56; cut = Image.new("L", sp.size, 0); ImageDraw.Draw(cut).rectangle((0, 0, sp.width, int(sp.height * vis)), fill=255); sp.putalpha(Image.fromarray(np.minimum(np.asarray(sp.getchannel("A")), np.asarray(cut))))
    base = base.copy(); d = ImageDraw.Draw(base); bw = 150                      # the chair's tufted backrest, behind the shoulders
    bw = 185; d.rounded_rectangle((cx - bw, FAR - 175, cx + bw, FAR + 10), 28, fill=(26, 20, 18), outline=(12, 10, 10), width=8)
    for k in range(3):
        for j in (0, 1, 4, 5): d.ellipse((cx - 150 + j * 60 - 5, FAR - 140 + k * 50 - 5, cx - 150 + j * 60 + 5, FAR - 140 + k * 50 + 5), fill=(14, 11, 10))
    return put(base, sp, cx, FAR + sp.height * (1 - vis), shadow=False, mul=tuple(np.array((0.55, 0.58, 0.72)) * lit) if who != "dbl" else None, rim=((150, 180, 255), -side * 9, 0.7))


def kitchen_dark(t, t0, t1, dbl=True):
    """From the kitchen door: his mother at one end of the table, and at the other end, in the dark, someone with his voice."""
    im = seated(ST["kitdark"], "mum", -1, t)
    if dbl: im = seated(im, "dbl", 1, t)
    sp_ = 1 if L_("m1") < t < we("m1") + 0.4 else 0
    ty = KP["table"][1] - 0.12                                       # one sentence, one framing: wide, then her face, then his grin
    if L_("m1") <= t < L_("d1"): v = E.view(im, t, L_("m1"), L_("d1"), 1.7, 1.8, KP["chairL"][0], ty, drift=0.3)
    elif L_("d1") <= t < L_("c1"): v = E.view(im, t, L_("d1"), L_("c1"), 1.75, 1.95, KP["chairR"][0], ty, drift=0.3)
    else: v = E.view(im, t, t0, t1, 1.0, 1.14, 0.5, 0.5, drift=0.3)
    return handheld(v, t, 0.8 + 0.6 * (t > L_("d1")))


def black_hands(t, mode):
    """In the dark. 'cold': a cold hand closes on his. 'two': two hands take his two hands, a warm one on the left and,
    on the right, one with a red thread bracelet like his. Fingers close, the grip tightens, everything trembles."""
    im = Image.new("RGB", (W, H), (3, 3, 6)); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    tr = lambda k: 6 * NOISE.noise2(t * 9, k)
    COLD_SK, COLD_SL, WARM_SL = (70, 74, 96, 255), (14, 14, 20, 255), (196, 128, 138, 255)
    def mine(x, y, side):                                             # his hands, palms up, from the bottom
        MO.sleeve(d, x + side * 160, H + 80, x + tr(1), y + 90, T2.HOOD, 150, cuff=T2.REDB if side > 0 else None)
        MO.hand(d, x + tr(1), y, np.radians(side * 10), 1.25, T2.SKIN, grip=0.2)
    def theirs(x, y, side, cold, q):                                  # theirs come in from above and close over his
        ox = x + side * 520 * (1 - q); oy = y - 130 - 260 * (1 - q)
        MO.sleeve(d, ox + side * 560, oy - 600, ox + tr(3), oy - 40, COLD_SL if cold else WARM_SL, 150, cuff=T2.REDB if cold else None)
        g = min(1.0, max(0.0, (q - 0.6) / 0.4)); MO.hand(d, ox + tr(3), oy + 40, np.radians(180 - side * 15), 1.25, COLD_SK if cold else T2.SKIN, grip=0.2 + 0.7 * g)
    if mode == "cold":
        q = ease((t - T_MAIN) / 0.45); mine(560, 1300, 1)
        if q > 0: theirs(560, 1300, 1, True, q)
        lit = 0.75
    else:
        q0 = ease((t - wt("l5", "mains")) / 0.5); ql, qr = max(q0 * 0.85, ease((t - T_GAUCHE) / 0.4)), max(q0 * 0.85, ease((t - T_DROITE) / 0.4))
        mine(330, 1300, -1); mine(750, 1300, 1)
        if q0 > 0: theirs(330, 1300, -1, False, ql); theirs(750, 1300, 1, True, qr)
        lit = 0.75
    im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB"); im = E.torch(im, 540, 1200, 820, 0.1, lit + 0.3)
    if mode == "two" and t >= T_BRAC: im = E.spill(im, 760, 1060, 140, 100, (255, 40, 30), 0.4 * cl((t - T_BRAC) / 0.3))
    if mode == "two":                                                 # the camera goes to the hand that is named, then back to both
        z, cx = 1.0, 540
        for tt, zz, xx in ((T_GAUCHE, 1.45, 330), (T_DROITE, 1.45, 750), (wt("c2", "gauche"), 1.6, 330), (wt("c2", "droite"), 1.6, 750), (wt("c2", "toi"), 1.0, 540)):
            if t >= tt: q = ease((t - tt) / 0.35); z, cx = z + (zz - z) * q, cx + (xx - cx) * q
        cw, ch = W / z, H / z; cy = 1250 - (1250 - 960) * (1 - (z - 1) / 0.6); x0 = min(max(cx - cw / 2, 0), W - cw); y0 = min(max(cy - ch / 2, 0), H - ch)
        im = im.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)
    return handheld(im, t, 1.5)


def bedroom_door(t):
    """Seen from inside his room: the door swings shut, the wedge of moonlight on the floor narrows with it, he is in the
    gap until the last moment; then the key turns, from outside."""
    room = Image.new("RGB", (W, H), (6, 6, 10)); d = ImageDraw.Draw(room)
    d.rectangle((0, 1500, W, H), fill=(12, 11, 16)); d.rectangle((0, 1490, W, 1504), fill=(20, 18, 24))
    ins = Image.eval(ST["entdark"].resize((420, 1080)), lambda v: int(min(255, v * 2.2)))
    sp = T2.char(900, dark=True, look=(-0.5, 0.0)); ins.paste(sp, (int(210 - sp.width / 2), 1080 - sp.height + 60), sp)
    a = 0.7 * (1 - ease((t - T_PORTE) / 0.9))
    im = MO.door_open(room, ins, (330, 420, 750, 1500), a, hinge="right", leaf=_LEAF2, light=((120, 150, 220), 0.9))
    if a <= 0.01 and t >= T_EXT - 0.2:                                # the lock: the thumb-turn rotates by itself
        d = ImageDraw.Draw(im); r = ease((t - T_EXT) / 0.3); cx, cy = 380, 960
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=(150, 130, 90)); d.line((cx - 16 * np.cos(r * 1.57), cy - 16 * np.sin(r * 1.57), cx + 16 * np.cos(r * 1.57), cy + 16 * np.sin(r * 1.57)), fill=(40, 30, 20), width=8)
    return handheld(im.filter(ImageFilter.GaussianBlur(0.8)), t, 1.0)
_LEAF2 = MO.leaf_tex(seed=5)


_LEAF4B = MO.leaf_tex(seed=7, num="4B")
def front_door(t, t0, t1):
    """His own front door, on the landing: not locked. He pushes it; it swings into the dark."""
    global _WALL
    if _WALL is None: _WALL = E.paper_tex(W, H, (120, 112, 100), fiber=0.05, seed=31).convert("RGB")
    ins = Image.eval(ST["entdark"].resize((420, 1080)), lambda v: int(min(255, v * 1.6)))
    a = 0.55 * ease((t - (t0 + 0.4)) / 1.6)
    im = MO.door_open(_WALL, ins, (330, 420, 750, 1500), a, hinge="right", leaf=_LEAF4B)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); ex = 750 - 420 * np.cos(np.radians(80 * a))
    MO.sleeve(d, ex + 520, 1500, ex + 70, 1010, T2.HOOD, 150, cuff=T2.REDB); MO.hand(d, ex + 10, 960, np.radians(-80), 1.1, T2.SKIN, grip=0.1)
    im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")
    im = E.torch(im, 560, 900, 820, 0.25, 1.1)
    return handheld(E.view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t1, 1.0, 1.1, 0.5, 0.5, drift=0.3), t, 1.0)
_WALL = None


def torch_kitchen(t, t0, t1):
    """The phone torch sweeps the kitchen: nobody at the table, his plate half eaten. Then it finds the pulled-out chair and his bag on it."""
    tx, ty = KP["table"]; bx, by = KP["bag"]
    if t < L_("l3"): p = ease((t - T_TORCH) / 1.8); x = SW * (0.22 + 0.4 * p); y = SH * (ty - 0.03)
    else: p = ease((t - L_("l3")) / 0.7); x = SW * (0.62 + (bx - 0.62) * p); y = SH * ((ty - 0.03) + (by - ty + 0.03) * p)
    x += 18 * NOISE.noise2(t * 1.5, 7); y += 14 * NOISE.noise2(7, t * 1.5)                   # a torch held in a shaking hand
    on = 1.0 if t >= T_TORCH else 0.0
    if T_OFF - 0.6 < t < T_OFF: on = 0.4 + 0.6 * (NOISE.noise2(t * 30, 4) > -0.1)
    if t >= T_OFF: on = 0.0
    im = reveal(ST["kitdarkbag"], ST["kitlitbag"], x, y, 520 * on + 1)
    if on and t >= L_("l3") - 0.2: im = steam(im, t, bx * SW, by * SH - 40, 1.0)
    if on > 0: im = motes(im, t, x, y, 420, 70, 0.9)
    if on <= 0: im = Image.eval(im, lambda v: int(v * 0.1))
    return handheld(E.view(im, t, t0, t1, 1.0, 1.12, 0.5, 0.5, drift=0.3), t, 1.0)


def mum_behind(t, t0, t1):
    """He turns: his mother is standing in the corridor behind him, caught in the torch, worried."""
    base = reveal(ST["entdark"], ST["entlit"], SW * 0.5, SH * 0.5, 650)
    a_ = amp("l2", t, 9) if L_("l2") < t < we("l2") else 0.0
    kw = dict(mum=True, look=(0.0, 0.0), wide=1.15, brow=0.7 + 0.3 * min(1, a_), mouth=talk("l2", t) if a_ > 0 else "line", blink=blink(t, 0.4)); kw.update(MO.gesture(t, 5, a_)); kw.update(MO.alive(t, 5, 1.0, a_))
    sp = hero(1500, **kw); im = put(base, sp, SW * 0.5, SH * 0.98, mul=(0.95, 0.95, 1.0), rim=((200, 220, 255), 9, 0.4))
    return handheld(E.view(im, t, t0, t1, 1.04, 1.12, 0.5, 0.5, drift=0.3), t, 0.8)


# ---------------------------------------------------------------- overlays
def hud(im, t):
    d = ImageDraw.Draw(im); fs = ImageFont.truetype(E.MONT, 28)
    place = "RUE" if t < L_("b3") and not (L_("a3") <= t < t_rew1) else ("TA PORTE" if t < t_rew1 else ("COULOIR" if t < L_("b4") else "CUISINE"))
    sec = 2 * 3600 + 51 * 60 + 5 + t if t < t_rew1 else 2 * 3600 + 51 * 60 + 25 + (t - L_("b1")) * 3
    d.text((124, 232), "NUIT 2 · " + place, font=fs, fill=(235, 235, 238), stroke_width=3, stroke_fill=(0, 0, 0))
    s_ = int(sec); d.text((122, 266), f"{s_ // 3600:02d}:{s_ // 60 % 60:02d}:{s_ % 60:02d}", font=ImageFont.truetype(E.MONO, 62), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    if t < L_("b3") and not (L_("a1") <= t < t_rew1):                 # distance to home, then the battery
        km = 1.8 if t < T_KM else max(0.0, 1.8 * (1 - (t - T_KM) / max(0.1, L_("b2") + 0.5 - T_KM)))
        d.text((956, 232), "CHEZ TOI", font=fs, fill=(235, 235, 238), anchor="ra", stroke_width=3, stroke_fill=(0, 0, 0))
        d.text((956, 272), f"{km:.1f} KM".replace(".", ","), font=ImageFont.truetype(E.MONO, 42), fill=(255, 60, 44), anchor="ra", stroke_width=4, stroke_fill=(0, 0, 0))
    else:
        bat = 4 if t < T_TORCH else max(1, 4 - int((t - T_TORCH) / 3.0)); bat = 0 if t >= T_OFF and t > t_rew2 else bat
        d.text((956, 232), "BATTERIE", font=fs, fill=(235, 235, 238), anchor="ra", stroke_width=3, stroke_fill=(0, 0, 0))
        d.text((956, 272), f"{bat} %", font=ImageFont.truetype(E.MONO, 42), fill=(255, 60, 44), anchor="ra", stroke_width=4, stroke_fill=(0, 0, 0))
        d.rounded_rectangle((850, 326, 956, 346), 5, outline=(255, 255, 255), width=3); d.rectangle((853, 329, 853 + int(100 * bat / 100 * 3), 343), fill=(255, 60, 44))


RULES = (["RÈGLE 1", "Ce que tu acceptes, tu le livres."], ["RÈGLE 2", "Ne prends rien de sa main."], ["RÈGLE 3", "Quand la nuit est payée : rentre."],
         ["RÈGLE 4", "Quand il est chez toi,", "n'appelle personne."], ["RÈGLE 5", "Il ne vit que dans le noir.", "Allume."])
_REC = None
def receipt(t, t0, stage):
    """The slip of nuit 1, folded and taken out again: the first three rules, and a new one written in red."""
    global _REC
    if _REC is None:
        w, h = 760, 1260; p = E.paper_tex(w, h, (246, 244, 236), fiber=0.04, seed=52); d = ImageDraw.Draw(p); fm = ImageFont.truetype(E.MONO, 26)
        d.ellipse((335, 30, 425, 120), fill=N1.PURPLE); d.ellipse((366, 40, 434, 108), fill=(246, 244, 236))
        d.text((380, 164), "NUIT EXPRESS", font=E.fI("Bold", 50), fill=(30, 30, 34), anchor="mm"); d.text((380, 208), "commande #0013 · client : TOI", font=fm, fill=(110, 110, 116), anchor="mm")
        for y_ in (420, 840): d.line((40, y_, w - 40, y_ + 6), fill=(214, 210, 198), width=3)            # the folds
        f = ImageFont.truetype(E.HAND, 44); y = 270
        for r in RULES[:3]:
            d.text((60, y), r[0] + " · " + r[1], font=f, fill=(205, 24, 24)); y += 62
        m = Image.new("L", (w, h), 255); md = ImageDraw.Draw(m)
        for x in range(0, w, 40): md.polygon([(x, h), (x + 20, h - 26), (x + 40, h)], fill=0)
        p.putalpha(m); _REC = p
    fr = _REC.copy(); d = ImageDraw.Draw(fr); f = ImageFont.truetype(E.HAND, 62); rg = np.random.default_rng(3)
    def write(lines, y, n):
        for ln in lines:
            part = ln[:max(0, n)]; n -= len(ln); x = 60
            for ch in part: d.text((x + rg.normal(0, 0.8), y + rg.normal(0, 1.2)), ch, font=f, fill=(205, 24, 24)); x += d.textlength(ch, font=f)
            y += 70
    write(RULES[3], 500, int(np.clip((t - t0 - 0.6) * 24, 0, 99)) if stage == 4 else 99)
    if stage == 5: write(RULES[4], 760, int(np.clip((t - t0 - 0.6) * 24, 0, 99)))
    bg = ST["entdark"].resize((W, H)).filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.6)).convert("RGBA")
    fr = fr.resize((int(fr.width * 0.84), int(fr.height * 0.84)), Image.LANCZOS).rotate(2.0 + np.sin(t * 8) * 0.2, expand=True, resample=Image.BICUBIC)
    E.drop_shadow(bg, fr, (int(W / 2 - fr.width / 2), int(860 - fr.height / 2)), blur=26, off=(14, 26), alpha=170)
    im = E.torch(bg, 540 + np.sin(t * 1.3) * 50, 900 + np.cos(t * 1.1) * 50, 1250, 0.5, 1.12)
    q = ease((t - t0 - 0.6) / 1.2); cy = 0.5 + q * (0.06 if stage == 4 else 0.13)        # the camera follows the pen to the new rule
    return E.view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t0 + 2.0, 1.0, 1.35, 0.5, cy, drift=0.4)


C0 = ("L'APPELER", "COURIR"); C1 = ("ALLUMER", "RESTER DANS LE NOIR"); C2 = ("LA GAUCHE", "LA DROITE")
CUTS = [T_RUE, L_("m1"), L_("d1"), L_("c1"), wt("b3", "entrée") - 0.1] + [L_(k) for k in ("h1", "c0", "a1", "a3", "r4", "b1", "b2", "b3", "b4", "r5", "l1", "l3", "c2")] + [L_("l2") - 0.05, we("l2") + 0.1, L_("k2")]


def raw(i, t):
    """(image, grade, caption y, show hud, buttons) at time t, before overlays."""
    g = ("night", 0.4); cap = 1500; hd = True; btn = None
    if t < T_RUE: im = N1._phone(hook_screen(), t, 0.0, vib_at=0.0); g = None
    elif t < L_("h1"): im = street_open(t, T_RUE, L_("h1")); g = ("night", 0.45)
    elif t < L_("c0"): im = home_facade(t, L_("h1"), L_("c0")); g = ("night", 0.5)
    elif t < L_("a1"):
        im = N1.face_shot(t, L_("c0"), L_("a1"), still="street2", scared=True); im = rain(im, t, 120, 0.35); g = ("night", 0.2); btn = (C0, L_("c0"), L_("a1"), None)
    elif t < L_("a3"):
        im = N1._phone(call_screen(t), t, L_("a1")); g = None
        if t < L_("a1") + 1.1: btn = (C0, 0, 1, "L'APPELER")
    elif t < L_("r4"): im = key_shot(t, L_("a3"), L_("r4")); g = ("night", 0.4)
    elif t < t_rew1: im = receipt(t, L_("r4"), 4); g = ("paper", 0.4); hd = False
    elif t < L_("b1"): return None
    elif t < L_("b2"):
        im = run_shot(t, L_("b1"), L_("b2")); g = ("night", 0.5)
        if t < L_("b1") + 1.1: btn = (C0, 0, 1, "COURIR")
    elif t < L_("b3"): im = arrive_shot(t, L_("b2"), L_("b3")); g = ("night", 0.5)
    elif t < wt("b3", "entrée") - 0.1: im = front_door(t, L_("b3"), wt("b3", "entrée")); g = ("night", 0.45)
    elif t < L_("b4"): im = corridor_shot(t, wt("b3", "entrée") - 0.1, L_("b4")); g = ("night", 0.5)
    elif t < L_("k1"):
        im = kitchen_dark(t, L_("b4"), L_("k1")); g = ("night", 0.55)
        if t >= L_("c1") - 0.05: btn = (C1, L_("c1"), L_("k1"), None)
    elif t < L_("k2"):
        im = Image.new("RGB", (W, H), (3, 3, 6)) if t < T_MAIN else black_hands(t, "cold"); g = None
        if t < L_("k1") + 1.1: btn = (C1, 0, 1, "RESTER DANS LE NOIR")
    elif t < L_("r5"): im = bedroom_door(t); g = None
    elif t < t_rew2: im = receipt(t, L_("r5"), 5); g = ("paper", 0.4); hd = False
    elif t < L_("l1"): return None
    elif t < L_("l2") - 0.05:
        im = torch_kitchen(t, L_("l1"), L_("l3")); g = ("night", 0.45)
        if t < L_("l1") + 1.1: btn = (C1, 0, 1, "ALLUMER")
    elif t < we("l2") + 0.1: im = mum_behind(t, L_("l2"), we("l2")); g = ("night", 0.45)
    elif t < L_("l5"): im = torch_kitchen(t, L_("l1"), L_("l5")); g = ("night", 0.45)
    else:
        im = black_hands(t, "two"); g = None
        if t >= L_("c2") - 0.05: btn = (C2, 0, 1, None, True)
    return im, g, cap, hd, btn


_CH = {}
def choice_img(key, tc):
    if key not in _CH: _CH[key] = finish(0, tc, raw(0, tc), captions=False)
    return _CH[key]


def finish(i, t, r, captions=True):
    im, g, cap, hd, btn = r
    if g: im = N1.GRADE(im, i, exp=g[1], warm=True, glow=g[0] != "paper")
    if L_("h1") + 0.4 <= t < L_("c0"): im = E.callout(im, t, L_("h1") + 0.4, L_("c0") - 0.1, win_xy(t, L_("h1"), L_("c0")), (-240, 340), "4e ÉTAGE · CHEZ TOI", "quelqu'un regarde la télé", RED)
    if T_SCOOT + 0.3 <= t < L_("b3"): im = E.callout(im, t, T_SCOOT + 0.3, L_("b3") - 0.1, (int(W * 0.62), int(H * 0.6)), (-120, -380), "TON SCOOTER", "le moteur est chaud", RED)
    if T_AMP + 0.2 <= t < L_("b4"): im = E.callout(im, t, T_AMP + 0.2, L_("b4") - 0.1, socket_xy(t, L_("b3"), L_("b4")), (120, 300), "LES AMPOULES", "toutes dévissées", RED)
    if hd: hud(im, t)
    if L_("a4") + 0.2 <= t < L_("r4"): N1.stamp(im, t, L_("a4") + 0.3, "FIN DE SERVICE", y=600, size=92)
    if L_("k3") + 0.2 <= t < L_("r5"): N1.stamp(im, t, L_("k3") + 0.3, "FIN DE SERVICE", y=600, size=92)
    if btn: N1.buttons(im, btn[0], t, btn[1], btn[2], btn[3], ab=len(btn) > 4, title="TOI, TU FAIS QUOI ?" if len(btn) > 4 and t >= wt("c2", "toi") - 0.1 else None)
    if t >= D - 2.6:                                                  # the sequel is promised on screen, not with a date
        d = ImageDraw.Draw(im); d.text((540, 690), "À SUIVRE · NUIT 3", font=ImageFont.truetype(E.MONT, 44), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
    if captions: G.karaoke(im, words, t, "present", hl=RED, box=False, y0=cap if g else 1575, size0=70, stroke=7)
    return im


def render(i, t):
    r = raw(i, t)
    if r is None:
        for t0, key, tc in ((t_rew1, "c0", L_("a1") - 0.3), (t_rew2, "c1", L_("k1") - 0.3)):
            if t0 <= t < t0 + 0.9: return N1.rewind(i, t, t0, choice_img(key, tc))
    k = int(round((t - T_MAIN) / F))                                 # the one shock: after the second of silence, the cold hand
    if -2 <= k < 0: return N1.smear(finish(i, T_MAIN + 0.4, raw(i, T_MAIN + 0.4), captions=False), k)
    if k == 0: return N1.negative(finish(i, T_MAIN + 0.4, raw(i, T_MAIN + 0.4), captions=False))
    im = finish(i, t, r)
    if t > D - 0.4: im = Image.blend(im, render0(), cl((t - (D - 0.4)) / 0.4))
    return im


_R0 = []
def render0():
    if not _R0: _R0.append(finish(0, 0.0, raw(0, 0.0), captions=False))
    return _R0[0]


def frame(i):
    t = i * F; c = next((c for c in CUTS if 0 <= t - c < 0.2), None)
    if c is not None and raw(i, c - F) is not None:
        q = (t - c) / 0.2; im = Image.blend(render(i, c - F), render(i, t), q * q * (3 - 2 * q))
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
    def step(g=6): n = int(0.09 * VSR); return np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same") * np.exp(-np.arange(n) / VSR * 45) * g
    def sweep(): x = np.arange(int(0.9 * VSR)) / VSR; return np.sin(2 * np.pi * np.cumsum(1800 - 1500 * x / 0.9) / VSR) * 0.25 + rng.standard_normal(len(x)) * 0.12
    def band(lo, hi, n): return sosfiltfilt(butter(2, [lo, hi], btype="band", fs=VSR, output="sos"), rng.standard_normal(n))
    def breath(at_, d_=0.5, g=1.0): n = int(d_ * VSR); x = np.arange(n) / VSR; add(band(500, 2400, n) * np.sin(np.pi * x / d_) ** 2 * 2.5, at_, g)
    def heart(a_, b_, per=0.55, g=0.9):
        for q in np.arange(a_, b_, per): add(thump(), q, g); add(thump(), q + 0.19, g * 0.65)
    def clack(at_, g=1.0): add(click() * 3, at_, g); add(tone(900, 0.05, 80), at_, 0.5 * g); add(thump(), at_ + 0.01, 0.6 * g)
    outside = (ts < L_("b3")) & ~((ts >= L_("a1")) & (ts < L_("a3")))
    rainn = band(1500, 7000, NS) * 0.35 * (1 + 0.3 * np.sin(ts * 0.7)); mix += rainn * outside
    wind = np.convolve(rng.standard_normal(NS), np.ones(400) / 400, "same") * 0.5 * (1 + 0.5 * np.sin(ts * 0.9)); mix += wind * outside
    fridge = (np.sin(2 * np.pi * 50 * ts) + 0.5 * np.sin(2 * np.pi * 100 * ts)) * 0.04; mix += fridge * (~outside) * (ts < t_rew2 + 50)
    add(boom(), 0.0, 0.5); x = np.arange(int(0.35 * VSR)) / VSR; add(np.sin(2 * np.pi * 150 * x) * (np.sin(2 * np.pi * 6 * x) > 0) * 0.5, 0.02, 0.5); add(tone(880, 0.3, 9) + tone(1318, 0.3, 9) * 0.5, 0.05, 0.25)
    add(boom(), T_NOIR, 0.6); heart(L_("h1"), L_("a1"), 0.6)
    for a_, b_ in ((we("c0") + 0.1, 3), (we("c1") + 0.1, 3)):
        for k in range(b_): add(tone(1200, 0.05, 60), a_ + k * 0.26, 0.45)
    for q in np.arange(L_("a1") + 0.3, T_DEC - 0.3, 2.0): add(tone(440, 1.0, 0.5), q, 0.25)                                 # the ring-back tone
    add(click() * 3, T_DEC, 0.8); mix += band(300, 3000, NS) * 0.04 * ((ts > T_DEC) & (ts < L_("a3")))
    for k in range(int((L_("a4") - T_CLE) / 0.7) + 1): add(band(2000, 6000, int(0.25 * VSR)) * np.exp(-np.arange(int(0.25 * VSR)) / VSR * 10) * 2, T_CLE + k * 0.7 + 0.15, 0.5)   # metal on metal
    heart(T_CLE, L_("r4"), 0.42); add(boom(), L_("a4") + 0.3, 0.8)
    for t0_ in (L_("r4"), L_("r5")):
        for k in range(46): add(click() * 0.5, t0_ + 0.5 + k * 0.05, 0.5)
    for t0_ in (t_rew1, t_rew2): add(sweep(), t0_, 0.8)
    for k in range(int((L_("b2") - L_("b1")) / 0.31)): add(step(9), L_("b1") + 0.05 + k * 0.31, 0.6); add(band(2000, 6000, int(0.05 * VSR)) * 0.6, L_("b1") + 0.06 + k * 0.31, 0.3)   # running on wet pavement
    for k in range(int((L_("b3") - L_("b1")) / 0.55)): breath(L_("b1") + k * 0.55, 0.35, 0.5)
    for k in range(10): add(tone(3000 + 300 * (k % 2), 0.02, 200), T_CHAUD + k * 0.33, 0.12)                                      # the engine ticking as it cools
    xx = np.arange(int(0.8 * VSR)) / VSR; add(np.sin(2 * np.pi * np.cumsum(140 + 160 * xx) / VSR) * np.exp(-xx * 3) * 0.3, L_("b3") + 0.2, 0.6)   # the door creaks
    for k in range(5): add(step(4), L_("b3") + 1.0 + k * 0.6, 0.35)
    for k in range(4): add(tone(2600, 0.15, 30) + tone(3900, 0.15, 40) * 0.4, wt("m1", "p") + k * 0.7, 0.12)                    # a fork on a plate
    heart(L_("d1"), L_("k1"), 0.5)
    mute = (ts >= wt("k1", "noir") + 0.3) & (ts < T_MAIN - 0.05)
    add(np.convolve(rng.standard_normal(int(0.14 * VSR)), np.ones(25) / 25, "same") * 9, T_MAIN - 0.08, 0.5); add(boom(), T_MAIN, 1.2)
    for k in range(6): add(step(4), L_("k2") + 0.2 + k * 0.5, 0.35)
    xx = np.arange(int(0.7 * VSR)) / VSR; add(np.sin(2 * np.pi * np.cumsum(220 + 120 * xx) / VSR) * np.exp(-xx * 3) * 0.3, T_PORTE, 0.6); clack(T_EXT + 0.3, 1.2); add(boom(), we("k2"), 0.6)
    add(click() * 3, T_TORCH, 0.9); heart(L_("l1"), L_("l4"), 0.6, 0.6); add(boom(), L_("l2") - 0.05, 0.5)
    add(np.convolve(rng.standard_normal(int(0.4 * VSR)), np.ones(60) / 60, "same") * 2, T_SAC, 0.3)
    add(tone(600, 0.3, 12) + tone(400, 0.3, 12) * 0.7, T_OFF, 0.4); add(boom(), T_OFF + 0.1, 0.7)
    heart(L_("l5"), D - 0.5, 0.47, 0.9); add(boom(), T_BRAC, 0.7)
    vox = np.zeros(NS)
    for k, t0 in line_t.items():
        v = VO_A[k]
        if k == "av": v = sosfiltfilt(butter(3, [420, 3000], btype="band", fs=VSR, output="sos"), v) * 1.6        # through the phone
        if k == "d1": v = sosfiltfilt(butter(2, [150, 5000], btype="band", fs=VSR, output="sos"), v) * 0.85        # from the far end of the kitchen
        i0 = int(t0 * VSR); j0 = min(NS, i0 + len(v)); vox[i0:j0] += v[: j0 - i0]
    act = np.convolve((np.convolve(np.abs(vox), np.ones(2205) / 2205, "same") > 0.01).astype(float), np.ones(13230) / 13230, "same")
    mix = mix / np.abs(mix).max() * 0.55 * (1 - 0.6 * np.clip(act, 0, 1)) * (1 - np.convolve(mute.astype(float), np.ones(2205) / 2205, "same")) + vox / (np.abs(vox).max() + 1e-9) * 0.9
    mix = mix[: int(D * VSR)]; mix *= np.clip((D - ts[: len(mix)]) / 0.3, 0, 1); sf.write(TMP + "mix.wav", mix / np.abs(mix).max() * 0.9, VSR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", TMP + "f%05d.jpg", "-i", TMP + "mix.wav",
                    "-c:v", "libx264", "-crf", "24", "-maxrate", "3200k", "-bufsize", "6400k", "-preset", "slow", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-g", "60",
                    "-af", "loudnorm=I=-13:TP=-1.0:LRA=9,volume=1.3,alimiter=limit=0.89", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", _out], check=True)
    print("ok", _out, D)
