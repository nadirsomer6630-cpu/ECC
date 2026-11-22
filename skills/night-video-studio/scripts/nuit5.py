"""LIVREUR DE NUIT, nuit 4, partie 2: the season finale, about 65 s.
What the account's numbers taught (Nov 22): 93-98 % of viewers come from For You and never saw the earlier nights,
so frame 0 states the whole premise on its own (Samir on a video call in the rain + your mother's text "Samir frappe
à la porte"). The vote is paid off inside the video: A (let him go up) ends in a loss with rule 9 and a rewind,
B (stop him, light the landing: rule 5) survives and loops into the first line of Nuit 1.
usage: HF_HOME=... nuit5.py <out.mp4>   (EI_STEP, EI_RANGE, EI_AUDIO_ONLY as in nuit4)"""
import os, sys, json, glob, subprocess, functools, re
_out = sys.argv[1]; sys.argv = ["nuit4.py", "/tmp/unused.mp4"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import nuit4 as N4
N2, N1, E, G, T2, MO, TG = N4.N2, N4.N1, N4.E, N4.G, N4.T2, N4.MO, N4.TG
W, H, FPS, VSR, F, RED, NEW = E.W, E.H, E.FPS, E.VSR, E.F, E.RED, E.NEW
hero, put, cl, ease, blink = N1.hero, N1.put, N1.cl, N1.ease, N1.blink
handheld, rain, NOISE = N2.handheld, N2.rain, N2.NOISE
ST = N2.ST; SW, SH = ST["street2"].size; PSW, PSH = N1.PSW, N1.PSH
VO, TMP = NEW + "elv12/fin/", NEW + "n5tmp/"; os.makedirs(TMP, exist_ok=True)
ORDER = ["n1", "n2", "s1", "c1", "a1", "a2", "s2", "a3", "a4", "r9", "b1", "m1", "b2", "s3", "m2", "b3", "c2"]
SCRIPT = {n: re.sub(r"\[[^\]]*\]\s*", "", t) for n, w, t in json.load(open(NEW + "elv12/lines.json")) if n in ORDER}
VO_A = {k: G.voice(VO + f"{k}.wav", lp=None) for k in ORDER}
_cache = TMP + "rel.json"; _sig = {k: [SCRIPT[k], len(VO_A[k])] for k in ORDER}
if os.path.exists(_cache) and json.load(open(_cache))["sig"] == _sig: REL = json.load(open(_cache))["rel"]
else:
    REL = {}
    for k in VO_A:
        p = TMP + f"{k}_pre.wav"; sf.write(p, VO_A[k], VSR); REL[k] = E.align(G.word_times(p, 0, None), SCRIPT[k])
    json.dump({"sig": _sig, "rel": REL}, open(_cache, "w"))
dur = {k: len(v) / VSR for k, v in VO_A.items()}
T = 0.05; line_t = {}
def at(k, gap):
    global T
    line_t[k] = T; T += dur[k] + gap
at("n1", 0.25); at("n2", 0.3); at("s1", 0.3); at("c1", 1.0)
at("a1", 0.25); at("a2", 0.3); at("s2", 0.3); at("a3", 1.05)                  # one second of silence, then the shock
at("a4", 0.3); at("r9", 0.4)
t_rew = T; T += 0.9
at("b1", 0.3); at("m1", 0.3); at("b2", 0.35); at("s3", 0.35); at("m2", 0.35); at("b3", 0.6); at("c2", 1.4)
D = round(T, 2); N = int(D * FPS); print("duration", D)
def L_(k): return line_t[k] - 0.12
def wt(k, frag, n=0): return line_t[k] + [w["s"] for w in REL[k] if frag in E.norm(w["w"])][n]
def we(k): return line_t[k] + dur[k]
T_SHOCK = L_("a4") + 0.05; T_CLIC = wt("b2", "clic") - 0.05; T_TICKET = wt("m2", "avec") - 0.15; T_LOOP = wt("b3", "client") - 0.1
KNOCK1 = [L_("n2") + 0.3 + k * 0.5 for k in range(5)]; KNOCK2 = [L_("m1") - 0.2 + k * 0.5 for k in range(4)]
words = []
for k, t0 in line_t.items(): words += [dict(w, s=w["s"] + t0 + 0.1, e=w["e"] + t0 + 0.1, line=k) for w in REL[k]]


def amp(key, t, gain=9):
    a = VO_A[key]; i0 = int((t - line_t[key]) * VSR)
    return float(np.abs(a[max(0, i0):max(0, i0) + 1470]).mean() * gain) if 0 <= i0 < len(a) else 0.0
def speaking(key, t): return amp(key, t) if L_(key) < t < we(key) else 0.0
def samir_line(t): return next((k for k in ("s1", "s2", "s3") if L_(k) < t < we(k)), None)


# ---------------------------------------------------------------- Samir's camera, the same frame every time
def samir_cam(t, mood, bg="street2", wet=True, double=False):
    """His phone's camera: his face close, the call UI, your face in the corner, his name on the green pill.
    wet: the real Samir is soaked (drops run down). double: the thing wearing his face (white eyes, the grin), dry."""
    k = samir_line(t); a = speaking(k, t) if k else 0.0
    face = dict(happy=dict(brow=-0.2, mouth="open" if a > 0.3 else "smile"), scared=dict(brow=1.0, wide=1.3, mouth="o" if a > 0.2 else "wavy", sweat=True),
                panic=dict(brow=1.0, wide=1.25, mouth="open" if a > 0.3 else "o", sweat=True))[mood]
    src = ST[bg] if bg in ST else ST["street2"]
    base = src.resize((SW, SH)) if src.size != (SW, SH) else src
    if bg == "street2": base = base.transform(base.size, Image.AFFINE, (-1, 0, SW, 0, 1, 0))
    base = Image.eval(base.filter(ImageFilter.GaussianBlur(10)), lambda v: int(v * 0.8))
    if double: sp = N4.fake_samir(2400)
    else: kw = dict(samir=True, blink=blink(t, 0.5), **face); kw.update(MO.alive(t, 21, 1.2, a)); sp = hero(2400, **kw)
    bob = 30 * abs(NOISE.noise2(t * 7, 5)) if mood == "panic" else 18 * abs(NOISE.noise2(t * 6, 5))
    im = put(base, sp, SW * 0.5 + 20 * NOISE.noise2(t * 3, 4), SH * 1.33 + bob, shadow=False, mul=(0.85, 0.88, 1.0), rim=((255, 190, 120), -14, 0.6))
    im = E.view(im, t, 0, 1, 1.0, 1.0, 0.5, 0.5, drift=0.2)
    if bg == "street2": im = rain(im, t, 140, 0.45)
    d = ImageDraw.Draw(im, "RGBA"); rg = np.random.default_rng(31)
    if wet and not double:
        for q in range(16):
            x = rg.uniform(260, 820); y0 = rg.uniform(420, 1100); y = y0 + ((t * rg.uniform(60, 160) + rg.uniform(0, 300)) % 260)
            d.ellipse((x - 9, y - 14, x + 9, y + 14), fill=(190, 220, 255, 170)); d.ellipse((x - 3, y - 8, x + 2, y - 2), fill=(255, 255, 255, 200))
    sv = N4._self_view(200); m = Image.new("L", sv.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sv.width - 1, sv.height - 1), 26, fill=255)
    im.paste(sv, (W - sv.width - 70, 380), m); d = ImageDraw.Draw(im); d.rounded_rectangle((W - sv.width - 70, 380, W - 70, 380 + sv.height), 26, outline=(255, 255, 255), width=4)
    d.rounded_rectangle((70, 1360, 360, 1430), 35, fill=(30, 140, 80)); d.ellipse((92, 1384, 114, 1406), fill=(160, 255, 190))
    d.text((128, 1395), "SAMIR", font=ImageFont.truetype(E.MONT, 38), fill=(255, 255, 255), anchor="lm")
    d.rounded_rectangle((60, 200, 330, 250), 25, fill=(0, 0, 0, 160)); d.ellipse((80, 214, 102, 236), fill=(60, 220, 110))
    d.text((116, 225), "appel vidéo", font=ImageFont.truetype(E.MONT, 26), fill=(255, 255, 255), anchor="lm")
    return handheld(im, t, 2.2 if mood == "panic" else 1.4, seed=3)


def call_screen(t):
    """The video call inside your phone: Samir under the rain fills the screen, your face in the little box."""
    sc = samir_cam(t, "panic").resize((PSW, int(PSW * H / W))).crop((0, int((PSW * H / W - PSH) / 2), PSW, int((PSW * H / W - PSH) / 2) + PSH)).convert("RGBA")
    sv = N4._self_view(170); m = Image.new("L", sv.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sv.width - 1, sv.height - 1), 22, fill=255)
    sc.paste(sv, (PSW - sv.width - 30, PSH - sv.height - 170), m); d = ImageDraw.Draw(sc)
    for x, col in ((PSW * 0.3, (225, 50, 50)), (PSW * 0.7, (70, 72, 90))): d.ellipse((x - 50, PSH - 130, x + 50, PSH - 30), fill=col)
    return sc


def chat_screen(t):
    """Your thread with your mother: her text, then yours typed in with the voice."""
    sc = Image.new("RGBA", (PSW, PSH), (12, 13, 20, 255)); d = ImageDraw.Draw(sc)
    d.rectangle((0, 0, PSW, 150), fill=(24, 25, 36)); d.ellipse((40, 86, 96, 142), fill=(230, 120, 150)); d.text((68, 114), "M", font=E.fI("Bold", 32), fill=(255, 255, 255), anchor="mm"); d.text((116, 114), "Maman", font=E.fI("Bold", 36), fill=(255, 255, 255), anchor="lm")
    f = E.fI("Regular", 34)
    def bub(y, lines, mine, hot=False):
        w = max(d.textlength(l, font=f) for l in lines) + 56; hh = 30 + 46 * len(lines); x0 = PSW - 30 - w if mine else 30
        d.rounded_rectangle((x0, y, x0 + w, y + hh), 28, fill=(40, 110, 230) if mine else ((70, 30, 34) if hot else (46, 48, 62)), outline=RED if hot else None, width=4)
        for k, l in enumerate(lines): d.text((x0 + 28, y + 38 + k * 46), l, font=f, fill=(255, 255, 255), anchor="lm")
    bub(190, ["Samir frappe à la porte."], False, hot=True)
    full = "Allume le palier. Tout de suite."; n = int(max(0, t - wt("b1", "cris")) * 20); typed = full[:n]
    if typed: br = full.index("Tout"); bub(330, [typed[:br].strip(), typed[br:]] if len(typed) > br else [typed], True)
    if t >= L_("m1"): bub(500, ["Il frappe encore…"], False, hot=True)
    return sc


def hero_face(t, t0, t1):
    """Your face, lit by the phone, under the rain: the choice is yours."""
    kw = dict(look=(0.0, 0.6), brow=1.0, wide=1.2, mouth="wavy", sweat=True, blink=blink(t)); kw.update(MO.alive(t, 1, 1.0))
    sp = hero(2500, **kw); bg = Image.eval(ST["street2"].filter(ImageFilter.GaussianBlur(6)), lambda v: int(v * 0.6))
    bg = TG.burst(bg, SW * 0.47, SH * 0.45, (120, 70, 230), cl(1 - (t - t0) / 1.5), seed=7)
    im = put(bg, sp, SW * 0.47, SH * 1.275, shadow=False, mul=(0.68, 0.7, 0.82), rim=((255, 190, 120), -14, 0.5))
    im = E.spill(im, SW * 0.47, SH * 0.78, 520, 330, (120, 160, 255), 0.12)
    im = rain(E.view(im, t, t0, t1, 1.0, 1.08, 0.5, 0.47, drift=0.6), t, 140, 0.4); d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 1360, 290, 1430), 35, fill=(91, 51, 201)); d.text((180, 1395), "TOI", font=ImageFont.truetype(E.MONT, 38), fill=(255, 255, 255), anchor="mm")
    return im


def door_inside(t, t0, t1, knocks=(), lit=0.0):
    """Your front door seen from the dark hall: it shakes with each knock; when the landing is lit, light pours under it."""
    wall = Image.eval(ST["entdark"].resize((W, H)), lambda v: int(v * 0.7))
    sh = sum(np.exp(-(t - k_) * 25) * (t > k_) for k_ in knocks) * 12
    im = MO.door_open(wall, (0, 0, 0), (330 + sh, 420, 750 + sh, 1500), 0.0, hinge="right", leaf=N2._LEAF2)
    im = E.spill(im, 540, 1520, 300 + 200 * lit, 30 + 40 * lit, (255, 220, 160), 0.35 + 0.3 * np.sin(t * 3) * (1 - lit) + 0.9 * lit)
    if lit: im = E.spill(im, 540, 1500, 700, 500, (255, 225, 170), 0.25 * lit)
    return handheld(E.view(im.resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, 1.0, 1.12, 0.5, 0.52, drift=0.3), t, 1.0)


def stairs_up(t, t0, t1):
    """A: Samir, soaked, runs up the stairwell, seen from below; the timer light ticks."""
    base = ST["stairs"].resize((SW, SH)) if ST["stairs"].size != (SW, SH) else ST["stairs"]
    u = cl((t - t0) / (t1 - t0)); sp = T2.char(int(1500 - 500 * u), samir=True, back=True, legs=(0.4 * np.sin(t * 12), -0.4 * np.sin(t * 12)), armL=(0.3, 0.6 + 0.4 * np.sin(t * 12)), armR=(0.3, 0.6 - 0.4 * np.sin(t * 12)))
    im = put(base, sp, SW * 0.52, SH * (1.02 - 0.22 * u), shadow=True, mul=(0.75, 0.78, 0.9))
    return handheld(E.view(im, t, t0, t1, 1.0, 1.12, 0.5, 0.45, drift=0.3), t, 1.6, seed=9)


def landing(t, t0, t1, real=True, dbl=True, light=1.0, z=(1.0, 1.08), cy=0.5, one=False):
    """The landing in front of your door. real: Samir soaked, from behind, in the foreground. dbl: the thing at your
    door wearing his face (white eyes, the grin), dry. light < 1 fades the landing to black."""
    im = (ST["land"] if light > 0.5 else ST["closed"]).copy()
    if dbl: fs = N4.fake_samir(780); im = put(im, fs, SW * 0.5, SH * 0.79, shadow=True, mul=(0.95, 0.95, 1.0))
    if one: sp = T2.char(800, samir=True, mouth="smile", brow=-0.3, look=(0.0, 0.0)); im = put(im, sp, SW * 0.5, SH * 0.79, shadow=True, mul=(0.95, 0.95, 1.0))
    if real:
        sp = T2.char(1650, samir=True, back=True, head=(0.15 * np.sin(t * 2), 0.0)); im = put(im, sp, SW * 0.3, SH * 1.12, shadow=False, mul=(0.7, 0.74, 0.86))
        d = ImageDraw.Draw(im, "RGBA"); rg = np.random.default_rng(8)
        for q in range(10):                                            # he is dripping on the floor
            x = SW * 0.3 + rg.uniform(-160, 160); y = SH * 0.92 + ((t * 300 + rg.uniform(0, 300)) % 260)
            d.line((x, y, x, y + 18), fill=(190, 220, 255, 160), width=4)
    if light < 1: im = Image.eval(im, lambda v: int(v * max(0.04, light)))
    if dbl and light < 0.35:                                          # in the dark, only his eyes are left
        k_ = (0.35 - light) / 0.35; ex, ey = SW * 0.5, SH * 0.79 - 780 + 230
        glow = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
        for sx in (-1, 1): gd.ellipse((ex + sx * 48 - 16, ey - 9, ex + sx * 48 + 16, ey + 9), fill=(255, 40, 30, int(230 * k_)))
        im = im.convert("RGBA"); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6))); im.alpha_composite(glow); im = im.convert("RGB")
    return handheld(E.view(im, t, t0, t1, z[0], z[1], 0.5, cy, drift=0.3), t, 1.2, seed=11)


def grin_close(t):
    """The light comes back: his face, right in front of the lens."""
    im = ST["land"].copy(); fs = N4.fake_samir(2300); im = put(im, fs, SW * 0.5, SH * 1.42, shadow=False, mul=(1.0, 0.95, 0.95))
    return handheld(E.view(im, t, T_SHOCK, T_SHOCK + 1, 1.0, 1.04, 0.5, 0.45, drift=0.1), t, 2.0)


def mum_door(t, t0, t1):
    """Your mother in the dark hall, her hand on the switch; on 'J'allume' the light snaps on."""
    a = speaking("m1", t); on = t >= wt("m1", "allume") + 0.25
    kw = dict(mum=True, look=(0.7, -0.1), blink=blink(t, 0.4), mouth="o" if a > 0.25 else "wavy", brow=1.0, wide=1.25, sweat=True, armR=(0.5, 2.3))
    kw.update(MO.alive(t, 5, 1.2, a)); sp = hero(2300, **kw)
    bg = Image.eval(ST["entlit" if on else "entdark"].filter(ImageFilter.GaussianBlur(9)), lambda v: int(v * 0.9))
    im = put(bg, sp, SW * 0.44, SH * 1.18, shadow=False, mul=(0.95, 0.95, 1.0) if on else (0.7, 0.72, 0.86), rim=((255, 220, 160), 14, 0.7))
    sh = sum(np.exp(-(t - k_) * 25) * (t > k_) for k_ in KNOCK2) * 14
    return handheld(E.view(im, t, t0, t1, 1.05, 1.12, 0.48 + sh / 4000, 0.42, drift=0.3), t, 1.0 + sh / 10, seed=5)


def landing_bag(t, t0, t1):
    """B: the landing, lit, empty. On the doormat, a delivery bag. The camera walks to it."""
    return handheld(E.view(ST["landbag"], t, t0, t1, 1.0, 1.45, 0.5, 0.66, drift=0.2), t, 0.8, seed=13)


_TK = {}
def ticket(t, t0):
    """The slip stapled to the bag: the last order of the night, for you. Typed in with the voice."""
    if "p" not in _TK:
        w, h = 760, 1100; p = E.paper_tex(w, h, (246, 244, 236), fiber=0.04, seed=77); d = ImageDraw.Draw(p)
        d.ellipse((335, 30, 425, 120), fill=N1.PURPLE); d.ellipse((366, 40, 434, 108), fill=(246, 244, 236)); d.text((380, 164), "NUIT EXPRESS", font=E.fI("Bold", 50), fill=(30, 30, 34), anchor="mm")
        d.line((60, 220, w - 60, 220), fill=(200, 200, 205), width=3)
        m = Image.new("L", (w, h), 255); md = ImageDraw.Draw(m)
        for x in range(0, w, 40): md.polygon([(x, h), (x + 20, h - 26), (x + 40, h)], fill=0)
        p.putalpha(m); _TK["p"] = p
    fr = _TK["p"].copy(); d = ImageDraw.Draw(fr); f = ImageFont.truetype(E.HAND, 60); n = int(np.clip((t - t0) * 30, 0, 999)); y = 280
    for ln, col in (("Client :", (30, 30, 40)), ("TOI", (205, 24, 24)), ("4B · chez toi", (30, 30, 40)), ("", None), ("Dernière commande", (30, 30, 40)), ("de la nuit.", (30, 30, 40))):
        if not ln: y += 40; continue
        part = ln[:max(0, n)]; n -= len(ln); d.text((70, y), part, font=f, fill=col); y += 92
    bg = ST["landbag"].resize((W, H)).filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.55)).convert("RGBA")
    fr = fr.resize((int(fr.width * 0.9), int(fr.height * 0.9)), Image.LANCZOS).rotate(-3 + np.sin(t * 6) * 0.3, expand=True, resample=Image.BICUBIC)
    E.drop_shadow(bg, fr, (int(W / 2 - fr.width / 2), int(900 - fr.height / 2)), blur=26, off=(14, 26), alpha=170)
    return E.view(bg.convert("RGB").resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t0 + 3.0, 1.0, 1.2, 0.5, 0.48, drift=0.3)


_N1 = {}
def nuit1_frame(t, t0):
    """The loop: the first image of Nuit 1, the same courier at 02:14, as the line 'le client porte ton nom' ends."""
    if "i" not in _N1: _N1["i"] = Image.open(NEW + "acct/n1first.png").convert("RGB").resize((W, H))
    z = 1.08 - 0.08 * ease((t - t0) / 1.2); cw, ch = W / z, H / z
    return _N1["i"].transform((W, H), Image.EXTENT, ((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2), Image.BICUBIC)


_REC = None
def receipt(t, t0):
    """The slip of rules: eight in small, number nine typed in red."""
    global _REC
    rules = ["RÈGLE 1 · Ce que tu acceptes, tu le livres.", "RÈGLE 2 · Ne prends rien de sa main.", "RÈGLE 3 · Quand la nuit est payée : rentre.",
             "RÈGLE 4 · Quand il est chez toi, n'appelle personne.", "RÈGLE 5 · Il ne vit que dans le noir. Allume.", "RÈGLE 6 · Ne lâche jamais la main tiède.",
             "RÈGLE 7 · Chez toi, apporte ta propre lumière.", "RÈGLE 8 · Il peut prendre le visage de ceux que tu aimes."]
    if _REC is None:
        w, h = 760, 1260; p = E.paper_tex(w, h, (246, 244, 236), fiber=0.04, seed=54); d = ImageDraw.Draw(p)
        d.ellipse((335, 30, 425, 120), fill=N1.PURPLE); d.ellipse((366, 40, 434, 108), fill=(246, 244, 236)); d.text((380, 164), "NUIT EXPRESS", font=E.fI("Bold", 50), fill=(30, 30, 34), anchor="mm")
        f = ImageFont.truetype(E.HAND, 30); y = 230
        for r in rules: d.text((50, y), r, font=f, fill=(205, 24, 24)); y += 44
        m = Image.new("L", (w, h), 255); md = ImageDraw.Draw(m)
        for x in range(0, w, 40): md.polygon([(x, h), (x + 20, h - 26), (x + 40, h)], fill=0)
        p.putalpha(m); _REC = p
    fr = _REC.copy(); d = ImageDraw.Draw(fr); f = ImageFont.truetype(E.HAND, 66); rg = np.random.default_rng(3); n = int(np.clip((t - t0 - 0.4) * 24, 0, 999)); y = 660
    for ln in ("RÈGLE 9", "Ne l'envoie jamais", "face à son double."):
        part = ln[:max(0, n)]; n -= len(ln); x = 50
        for ch in part: d.text((x + rg.normal(0, 0.8), y + rg.normal(0, 1.2)), ch, font=f, fill=(205, 24, 24)); x += d.textlength(ch, font=f)
        y += 76
    bg = ST["entdark"].resize((W, H)).filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.6)).convert("RGBA")
    fr = fr.resize((int(fr.width * 0.84), int(fr.height * 0.84)), Image.LANCZOS).rotate(-2 + np.sin(t * 8) * 0.2, expand=True, resample=Image.BICUBIC)
    E.drop_shadow(bg, fr, (int(W / 2 - fr.width / 2), int(860 - fr.height / 2)), blur=26, off=(14, 26), alpha=170)
    im = E.torch(bg, 540, 900, 1250, 0.5, 1.12)
    return E.view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t0 + 2.0, 1.0, 1.3, 0.5, 0.58, drift=0.4)


def end_card(im, t, t0):
    """End of the season, and the vote that decides season 2."""
    u = ease((t - t0) / 0.4); im = Image.blend(im, Image.new("RGB", (W, H), (8, 6, 12)), 0.72 * u); d = ImageDraw.Draw(im)
    if u <= 0: return im
    d.text((540, 430), "FIN DE LA SAISON 1", font=ImageFont.truetype(E.MONT, 70), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
    d.text((540, 520), "Prochain métier de nuit ?", font=E.fI("SemiBold", 44), fill=(225, 225, 232), anchor="mm")
    for k, (lab, sub, col) in enumerate((("A · CAISSIER DE NUIT", "Il paie en francs. L'heure recule.", (40, 170, 90)), ("B · GARDIEN DE PISCINE", "Le bassin est vide. La ligne d'eau bouge.", (91, 51, 201)))):
        y = 600 + k * 230; d.rounded_rectangle((130, y, 950, y + 104), 52, fill=col); d.text((540, y + 52), lab, font=ImageFont.truetype(E.MONT, 44), fill=(255, 255, 255), anchor="mm")
        d.text((540, y + 150), sub, font=E.fI("SemiBold", 34), fill=(225, 225, 232), anchor="mm")
    if t > t0 + 0.8: d.text((540, 1130), "Écris A ou B en commentaire", font=ImageFont.truetype(E.MONT, 40), fill=(255, 210, 60), anchor="mm")
    if t > t0 + 1.2: d.rounded_rectangle((250, 1200, 830, 1280), 40, fill=(250, 30, 90)); d.text((540, 1240), "ABONNE-TOI POUR LA SAISON 2", font=ImageFont.truetype(E.MONT, 32), fill=(255, 255, 255), anchor="mm")
    return im


def hud(im, t):
    d = ImageDraw.Draw(im); fs = ImageFont.truetype(E.MONT, 28); s_ = int(21 * 3600 + 58 * 60 + 40 + t)
    d.text((124, 232), "NUIT 4 · FIN", font=fs, fill=(235, 235, 238), stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((122, 266), f"{s_ // 3600:02d}:{s_ // 60 % 60:02d}:{s_ % 60:02d}", font=ImageFont.truetype(E.MONO, 62), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))


C1 = ("LAISSER MONTER", "L'ARRÊTER")
CUTS = [L_(k) for k in ("n2", "s1", "c1", "a1", "a2", "s2", "a3", "r9", "b1", "m1", "b2", "s3", "m2")] + [T_TICKET, T_LOOP, wt("a4", "seul") - 0.15]


def raw(i, t):
    """-> (image, grade, hud, buttons, labels, notifications)"""
    g = ("night", 0.4); hd = True; btn = None; labels = []; nt = []
    if t < L_("n2"):
        im = N4.pov(t, call_screen(t), read=(-1.0, L_("n2") + 0.3)); g = None; nt = [(-1.0, "Maman", "Samir frappe à la porte.", True)]
        labels = [("banner", -0.3, "IL EST À DEUX ENDROITS.")]
    elif t < L_("s1"): im = door_inside(t, L_("n2"), L_("s1"), KNOCK1); nt = [(-1.0, "Maman", "Samir frappe à la porte.", True)]
    elif t < L_("c1"): im = samir_cam(t, "panic"); g = None; labels = [("label", L_("s1") + 0.3, "LE VRAI · TREMPÉ")]
    elif t < L_("a1"): im = hero_face(t, L_("c1"), L_("a1")); g = ("night", 0.2); btn = (C1, L_("c1"), L_("a1"), None)
    elif t < L_("a2"): im = stairs_up(t, L_("a1"), L_("a2")); labels = [("banner", L_("a1") + 0.1, "SI TU AS CHOISI A")]
    elif t < L_("s2"):
        im = landing(t, L_("a2"), L_("s2")); labels = [("banner", wt("a2", "sec") - 0.05, "LEQUEL EST LE VRAI ?"), ("tagR", wt("a2", "samir") + 0.1, "TREMPÉ"), ("tagD", wt("a2", "sec") + 0.1, "SEC")]
    elif t < L_("a3"): im = samir_cam(t, "scared", bg="land"); g = None
    elif t < T_SHOCK: im = landing(t, L_("a3"), T_SHOCK, light=1 - ease((t - wt("a3", "teint")) / 0.5), z=(1.08, 1.12))
    elif t < wt("a4", "seul") - 0.15: im = grin_close(t); labels = [("plate", T_SHOCK + 0.25, "LE DOUBLE")]
    elif t < L_("r9"): im = samir_cam(t, "happy", bg="land", double=True); g = None; labels = [("banner", wt("a4", "sec") - 0.05, "IL EST SEC.")]
    elif t < t_rew: im = receipt(t, L_("r9")); g = ("paper", 0.4); hd = False
    elif t < L_("b1"): return None
    elif t < L_("m1"):
        im = N4.pov(t, chat_screen(t), read=(L_("b1"), L_("m1") + 0.3)); g = None; labels = [("banner", L_("b1") + 0.1, "SI TU AS CHOISI B")]
        if t >= wt("b1", "allume"): labels.append(("label", wt("b1", "allume"), "RÈGLE 5 · IL NE VIT QUE DANS LE NOIR"))
    elif t < L_("b2"): im = mum_door(t, L_("m1"), L_("b2")); labels = [("plate", L_("m1") + 0.15, "TA MÈRE")]
    elif t < L_("s3"): im = door_inside(t, L_("b2"), L_("s3"), [k for k in KNOCK2 if k < T_CLIC] + [T_CLIC - 0.4], lit=ease((t - T_CLIC) / 0.15))
    elif t < L_("m2"): im = samir_cam(t, "happy"); g = None
    elif t < T_TICKET: im = landing_bag(t, L_("m2"), T_TICKET); labels = [("banner", L_("m2") + 0.3, "UN SAC. POUR QUI ?")]
    elif t < T_LOOP: im = ticket(t, T_TICKET); g = ("paper", 0.4); hd = False
    else: im = nuit1_frame(t, T_LOOP); g = None; hd = False
    return im, g, hd, btn, labels, nt


_CH = {}
def choice_img(tc):
    if "c" not in _CH: _CH["c"] = finish(0, tc, raw(0, tc), captions=False)
    return _CH["c"]


def finish(i, t, r, captions=True):
    im, g, hd, btn, labels, nt = r
    if g: im = N1.GRADE(im, i, exp=g[1], warm=True, glow=g[0] != "paper")
    for kind, t0, txt in labels:
        if kind == "banner": TG.banner(im, t, t0, txt, y=470 if txt.startswith("SI TU AS CHOISI B") else 700)
        elif kind == "plate": TG.name_plate(im, t, t0, txt, (540, 470))
        elif kind == "tagR": TG.label(im, t, t0, txt, (300, 1180), 40, color=(40, 110, 230), angle=6)
        elif kind == "tagD": TG.label(im, t, t0, txt, (720, 900), 40, angle=-6)
        else: TG.label(im, t, t0, txt, (540, 1330), 38)
    if hd: hud(im, t)
    for t0, who, body, hot in nt: N4.notif(im, t, t0, who, body, y=390, hot=hot)
    if L_("r9") <= t < t_rew: N1.stamp(im, t, L_("r9") + 0.1, "PERDU", y=1110, size=92)
    if L_("s3") <= t < L_("m2"):                                     # half-way chip, as the part series do
        d = ImageDraw.Draw(im); d.rounded_rectangle((90, 380, 560, 430), 25, fill=(0, 0, 0, 170)); d.text((110, 405), "Abonné · la saison 2 arrive", font=E.fI("SemiBold", 28), fill=(255, 255, 255), anchor="lm")
    if btn: N1.buttons(im, btn[0], t, btn[1], btn[2], btn[3])
    if t >= L_("c2"): im = end_card(im, t, L_("c2"))
    if captions and not t >= L_("c2"): G.karaoke(im, words, t, "present", hl=RED, box=False, y0=1500 if g else 1575, size0=70, stroke=7)
    return im


def render(i, t):
    if t >= L_("c2"):                                                  # the end card sits on the loop image
        return finish(i, t, (nuit1_frame(t, T_LOOP), None, False, None, [], []), captions=False)
    r = raw(i, t)
    if r is None and t_rew <= t < t_rew + 0.9: return N1.rewind(i, t, t_rew, choice_img(L_("a1") - 0.3))
    k = int(round((t - T_SHOCK) / F))                                 # the one shock: after the second of silence, the light comes back on him
    if -2 <= k < 0: return N1.smear(finish(i, T_SHOCK + 0.2, raw(i, T_SHOCK + 0.2), captions=False), k)
    if k == 0: return N1.negative(finish(i, T_SHOCK + 0.2, raw(i, T_SHOCK + 0.2), captions=False))
    return finish(i, t, r)


def frame(i):
    t = i * F; c = next((c for c in CUTS if 0 <= t - c < 0.15), None)
    if c is not None and raw(i, c - F) is not None and t < L_("c2"):
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
    def knock(at_): add(thump() * 1.4, at_, 1.0); add(np.convolve(rng.standard_normal(int(0.05 * VSR)), np.ones(10) / 10, "same") * 3, at_, 0.4)
    rainy = (ts < L_("n2")) | ((ts >= L_("s1")) & (ts < L_("c1"))) | ((ts >= L_("s3")) & (ts < L_("m2")))
    mix += band(1500, 7000, NS) * 0.3 * rainy                                                          # the rain, through the call
    add(boom(), 0.0, 0.5); buzz(0.02); ping(0.05)
    for k in KNOCK1: knock(k)
    heart(L_("s1"), L_("a1"), 0.5)
    for k in range(3): add(tone(1200, 0.05, 60), we("c1") + 0.1 + k * 0.26, 0.45)
    for k in range(int((L_("a2") - L_("a1")) / 0.22)): add(thump() * 0.6, L_("a1") + k * 0.22, 0.6)            # running up the stairs
    add(boom(), wt("a2", "sec"), 0.7); heart(L_("s2"), we("a3"), 0.42)
    add(click() * 2, wt("a3", "teint"), 0.8); add(tone(90, 0.6, 3), wt("a3", "teint"), 0.4)
    mute = (ts >= wt("a3", "teint") + 0.5) & (ts < T_SHOCK - 0.05)
    add(np.convolve(rng.standard_normal(int(0.14 * VSR)), np.ones(25) / 25, "same") * 9, T_SHOCK - 0.08, 0.5); add(boom(), T_SHOCK, 1.2)
    add(boom(), wt("a4", "sec"), 0.7)
    for k in range(40): add(click() * 0.5, L_("r9") + 0.5 + k * 0.05, 0.5)
    add(sweep(), t_rew, 0.8)
    for k in range(int(dur["b1"] * 6)): add(click() * 0.4, wt("b1", "cris") + k * 0.12, 0.4)                  # typing
    for k in KNOCK2: knock(k)
    add(click() * 3, T_CLIC, 0.9); add(tone(2400, 0.04, 90), T_CLIC, 0.4); add(tone(120, 0.5, 5), T_CLIC + 0.05, 0.3)   # the switch
    add(boom(), wt("m2", "nom"), 0.7)
    for k in range(30): add(click() * 0.4, T_TICKET + 0.2 + k * 0.08, 0.35)                                  # the slip being written
    add(boom(), T_LOOP, 0.9)
    add(tone(1046, 0.4, 6) + tone(1568, 0.4, 7) * 0.6, L_("c2") + 0.9, 0.3)
    vox = np.zeros(NS)
    for k, t0 in line_t.items():
        v = VO_A[k]
        if k.startswith("s"): v = sosfiltfilt(butter(3, [250, 4200], btype="band", fs=VSR, output="sos"), v) * 1.4            # through the phone
        i0 = int(t0 * VSR); j0 = min(NS, i0 + len(v)); vox[i0:j0] += v[: j0 - i0]
    act = np.convolve((np.convolve(np.abs(vox), np.ones(2205) / 2205, "same") > 0.01).astype(float), np.ones(13230) / 13230, "same")
    mix = mix / np.abs(mix).max() * 0.55 * (1 - 0.6 * np.clip(act, 0, 1)) * (1 - np.convolve(mute.astype(float), np.ones(2205) / 2205, "same")) + vox / (np.abs(vox).max() + 1e-9) * 0.9
    mix = mix[: int(D * VSR)]; mix *= np.clip((D - ts[: len(mix)]) / 0.3, 0, 1); sf.write(TMP + "mix.wav", mix / np.abs(mix).max() * 0.9, VSR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", TMP + "f%05d.jpg", "-i", TMP + "mix.wav",
                    "-c:v", "libx264", "-crf", "24", "-maxrate", "3200k", "-bufsize", "6400k", "-preset", "slow", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-g", "60",
                    "-af", "loudnorm=I=-13:TP=-1.0:LRA=9,volume=1.3,alimiter=limit=0.89", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", _out], check=True)
    print("ok", _out, D)
