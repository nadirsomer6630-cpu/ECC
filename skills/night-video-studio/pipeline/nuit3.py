"""LIVREUR DE NUIT, nuit 3: "La nuit de ta mère". About 2 min. A mix of our night series with what the most-viewed
formats do: the vote of nuit 2 paid off inside the video (both hands), a flip to the mother's point of view with warm
memories in bright colour and her reactions, labels stuck on people and objects every few seconds, the double's grin
as a recurring motif, two choices with a rule each, and an end card that names the next night.
usage: HF_HOME=... nuit3.py <out.mp4>   (EI_STEP, EI_RANGE, EI_AUDIO_ONLY as before)"""
import os, sys, json, glob, subprocess, functools, re
_out = sys.argv[1]; sys.argv = ["nuit2.py", "/tmp/unused.mp4"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import nuit2 as N2
import tags as TG
N1, E, G, T2, MO = N2.N1, N2.E, N2.G, N2.T2, N2.MO
W, H, FPS, VSR, F, RED, NEW = E.W, E.H, E.FPS, E.VSR, E.F, E.RED, E.NEW
hero, put, mixp, walk, bob, cl, ease, xf, blink = N1.hero, N1.put, N1.mixp, N1.walk, N1.bob, N1.cl, N1.ease, N1.xf, N1.blink
handheld, rain, motes, reveal, NOISE = N2.handheld, N2.rain, N2.motes, N2.reveal, N2.NOISE
TG.setup(E.MONT, E.HAND)
VO, TMP = NEW + "elv10/fin/", NEW + "n3tmp/"; os.makedirs(TMP, exist_ok=True)
ORDER = ["h0", "v0", "v1", "v2", "v3", "r6", "w1", "mm1", "fb0", "fb1", "fb2", "fb3", "mm2", "p1", "c1", "x1", "x2", "x3", "r7",
         "y1", "dd", "mm3", "y2", "y3", "e1", "c2"]
SCRIPT = {n: re.sub(r"\[[^\]]*\]\s*", "", t) for n, w, t in json.load(open(NEW + "elv10/lines.json")) if n in ORDER}
VO_A = {k: G.voice(VO + f"{k}.wav", lp=None) for k in ORDER}
_cache = TMP + "rel.json"; _sig = {k: [SCRIPT[k], len(VO_A[k])] for k in ORDER}
if os.path.exists(_cache) and json.load(open(_cache))["sig"] == _sig: REL = json.load(open(_cache))["rel"]
else:
    REL = {}
    for k in VO_A:
        p = TMP + f"{k}_pre.wav"; sf.write(p, VO_A[k], VSR); REL[k] = E.align(G.word_times(p, 0, None), SCRIPT[k])
    json.dump({"sig": _sig, "rel": REL}, open(_cache, "w"))
# one second of silence inside x2, between "Il n'y a plus d'ampoule." and "Il était juste derrière la porte.": then the shock
_ws = REL["x2"]; _j = next(n for n, w in enumerate(_ws) if n > 0 and E.norm(w["w"]).startswith("il")); _cut = int((_ws[_j - 1]["e"] + _ws[_j]["s"]) / 2 * VSR)
VO_A["x2"] = np.concatenate([VO_A["x2"][:_cut], np.zeros(VSR), VO_A["x2"][_cut:]]); REL["x2"] = [dict(w, s=w["s"] + (1 if n >= _j else 0), e=w["e"] + (1 if n >= _j else 0)) for n, w in enumerate(_ws)]
dur = {k: len(v) / VSR for k, v in VO_A.items()}
T = 0.05; line_t = {}
def at(k, gap):
    global T
    line_t[k] = T; T += dur[k] + gap
at("h0", 0.35); at("v0", 0.9)                                                                   # the hook; yesterday's choice
at("v1", 0.3); at("v2", 0.35); at("v3", 0.5); at("r6", 0.4)                                   # you let go of the left hand
t_rew1 = T; T += 0.9
at("w1", 0.3); at("mm1", 0.45)                                                                  # you let go of the right one
at("fb0", 0.3); at("fb1", 0.3); at("fb2", 0.3); at("fb3", 0.35); at("mm2", 0.5)              # three weeks, from her side
at("p1", 0.3); at("c1", 1.0)                                                                    # his room, choice
at("x1", 0.3); at("x2", 0.35); at("x3", 0.5); at("r7", 0.4)                                   # you pressed the switch
t_rew2 = T; T += 0.9
at("y1", 0.25); at("dd", 0.3); at("mm3", 0.4); at("y2", 0.3); at("y3", 0.5); at("e1", 0.35); at("c2", 2.6)
D = round(T, 2); N = int(D * FPS); print("duration", D)
def L_(k): return line_t[k] - 0.12
def wt(k, frag, n=0): return line_t[k] + [w["s"] for w in REL[k] if frag in E.norm(w["w"])][n]
def we(k): return line_t[k] + dur[k]
T_DINE = wt("h0", "dîné") - 0.1; T_SOIR = wt("h0", "soir") - 0.25; T_SOUR = wt("h0", "sourire") - 0.1
T_LEFT = wt("v1", "gauche") - 0.1; T_SERRE = wt("v2", "serre") - 0.1; T_JOUR = wt("v2", "jour") - 0.1
T_DROITE = wt("w1", "droite") - 0.1; T_GLISSE = wt("w1", "glisse") - 0.1; T_CONTRE = wt("w1", "serre") - 0.1
T_LAMPE = wt("fb1", "lampe") - 0.1; T_VIDE = wt("fb2", "vide") - 0.1; T_FRIGO = wt("fb3", "frigo") - 0.1; T_SOUV = wt("fb3", "souvenais") - 0.1
T_COULE = wt("p1", "coule") - 0.1; T_CLIC = wt("x1", "clic") - 0.05; T_RIEN = wt("x1", "rien") - 0.05; T_DERR = wt("x2", "juste") - 0.05
T_FEN = wt("y2", "fenêtre") - 0.1; T_ETAGE = wt("y2", "étage") - 0.1; T_VIBRE = wt("e1", "vibre") - 0.1; T_ADR = wt("e1", "adresse") - 0.1
words = []
for k, t0 in line_t.items(): words += [dict(w, s=w["s"] + t0 + 0.1, e=w["e"] + t0 + 0.1, line=k) for w in REL[k]]

HD3 = NEW + "n3hd/"
ST = dict(N2.ST); ST.update({k: E.still(HD3 + f"{k}_0001.png") for k in ("bdark", "blit", "wclosed", "wopen")})
SW, SH = ST["bdark"].size
BP = json.load(open(HD3 + "bdark_pos.json")); WP = json.load(open(HD3 + "wopen_pos.json")); KP = N2.KP; FAR = N2.FAR
PSW, PSH = N1.PSW, N1.PSH
BSOFT = Image.blend(ST["bdark"], ST["blit"], 0.5)                     # what a phone torch shows: lit, not floodlit


def amp(key, t, gain=6):
    a = VO_A[key]; i0 = int((t - line_t[key]) * VSR)
    return float(np.abs(a[max(0, i0):max(0, i0) + 1470]).mean() * gain) if 0 <= i0 < len(a) else 0.0
def talk(key, t): return "o" if amp(key, t, 9) > 0.3 else "line"
def speaking(key, t): return amp(key, t, 9) if L_(key) < t < we(key) else 0.0


def memory(im, k=1.0):
    """The past, from the mother's side: warm, bright, a little faded at the edges, like a good evening remembered."""
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    a = a ** 0.8 * np.array([1.12, 1.0, 0.8]) + np.array([0.06, 0.035, 0.0])
    l = (a @ np.array([0.3, 0.6, 0.1]))[..., None]; a = l + (a - l) * 1.25                                   # richer colour
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]; r = ((xx / a.shape[1] - 0.5) ** 2 + (yy / a.shape[0] - 0.5) ** 2)
    a = a * (1 - 0.35 * np.clip(r * 3 - 0.2, 0, 1))[..., None] + np.array([0.08, 0.05, 0.02]) * np.clip(r * 3 - 0.2, 0, 1)[..., None]
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return Image.blend(im.convert("RGB"), out, k) if k < 1 else out


def seat(base, who, side, t, key=None, scale=760, look=(0.6, 0.1), mood="calm"):
    """Characters on the kitchen chairs (same placement as nuit 2): the table hides them from the chest down."""
    cx = KP["chairL" if side < 0 else "chairR"][0] * SW; a = speaking(key, t) if key else 0.0
    if who == "mum":
        kw = dict(mum=True, look=look, blink=blink(t, 0.7), mouth=talk(key, t) if a > 0 else ("smile" if mood == "happy" else "line"), brow=0.2 + (0.6 if mood == "sad" else 0) + 0.3 * min(1, a))
        kw.update(MO.gesture(t, 3, a)); kw.update(MO.alive(t, 3, 1.0, a)); sp = hero(scale, **kw)
    else:                                                             # the double, wearing his face: only the eyes are wrong (no pupils)
        kw = dict(look=(-0.6, 0.1), mouth="smile", blink=False); kw.update(MO.alive(t, 9, 0.5)); sp = hero(scale, wide=0.9, **kw)
        a_ = np.asarray(sp).copy(); sp = Image.fromarray(a_)
    sp = sp.copy(); vis = 0.56; cut = Image.new("L", sp.size, 0); ImageDraw.Draw(cut).rectangle((0, 0, sp.width, int(sp.height * vis)), fill=255); sp.putalpha(Image.fromarray(np.minimum(np.asarray(sp.getchannel("A")), np.asarray(cut))))
    base = base.copy(); d = ImageDraw.Draw(base); bw = 185
    d.rounded_rectangle((cx - bw, FAR - 175, cx + bw, FAR + 10), 28, fill=(26, 20, 18), outline=(12, 10, 10), width=8)
    return put(base, sp, cx, FAR + sp.height * (1 - vis), shadow=False)


# ---------------------------------------------------------------- shots
def bedroom_grin(t, t0, t1, lit=0.0, torch=None):
    """His room from the door: glow stars on the ceiling, the plush rabbit, and the grin painted on the wall, still running."""
    base = ST["bdark"] if not torch else reveal(ST["bdark"], BSOFT, torch[0], torch[1], torch[2])
    im = base.copy(); gx, gy = BP["grin"]; TG.grin(im, t - t0 + 2.0, 0.0, (gx * SW, gy * SH - 40), 190)
    im = motes(im, t, gx * SW, gy * SH, 380, 40, 0.5)
    return handheld(E.view(im, t, t0, t1, 1.0, 1.12, 0.45, 0.45, drift=0.3), t, 0.8)


def kitchen_memory(t, t0, t1, mood="happy", lamp=1.0, focus=None):
    """Three weeks ago: dinner. Mother and 'him' at the table, warm light. lamp < 1 dims it (he switched the lamp off)."""
    base = Image.blend(ST["kitdark"], ST["kitlit"], lamp)
    im = seat(base, "mum", -1, t, None, look=(0.6, 0.1), mood=mood); im = seat(im, "dbl", 1, t)
    z, cx = (1.0, 0.5) if focus is None else (1.6, KP["chairL" if focus < 0 else "chairR"][0])
    return memory(E.view(im, t, t0, t1, z, z + 0.08, cx, KP["table"][1] - 0.1, drift=0.3), 0.6 + 0.4 * lamp)


def plate_insert(t, t0):
    """Close on his plate: empty, the fork clean. Under the table, the dog's bowl is full."""
    im = E.paper_tex(W, H, (150, 104, 70), fiber=0.2, seed=41).convert("RGB"); d = ImageDraw.Draw(im)
    for y in range(0, H, 46): d.line((0, y + 8 * np.sin(y), W, y + 8 * np.cos(y)), fill=(128, 88, 58), width=3)
    d.ellipse((190, 600, 890, 1300), fill=(238, 236, 228), outline=(170, 166, 156), width=10); d.ellipse((300, 710, 780, 1190), outline=(214, 210, 200), width=6)
    d.rounded_rectangle((900, 640, 940, 1250), 14, fill=(200, 202, 210)); [d.rectangle((892 + k * 14, 600, 900 + k * 14, 680), fill=(200, 202, 210)) for k in range(4)]
    d.rounded_rectangle((120, 640, 160, 1250), 14, fill=(200, 202, 210))
    q = ease((t - T_VIDE) / 0.4)
    if q > 0: d = ImageDraw.Draw(im); [d.ellipse((540 + 260 * np.cos(a) - 6, 950 + 260 * np.sin(a) - 6, 540 + 260 * np.cos(a) + 6, 950 + 260 * np.sin(a) + 6), fill=(214, 120, 70)) for a in np.linspace(0.3, 2.6, 7)]   # a ring of sauce: it was full
    im = memory(im, 1.0)
    return handheld(E.view(im.resize((int(W * 1.2), int(H * 1.2))), t, t0, t0 + 4, 1.0, 1.12, 0.5, 0.5, drift=0.3), t, 0.5)


@functools.lru_cache(maxsize=1)
def drawing():
    """His drawing at six: his mother with a crown, a small him holding her hand, a sun, a house, wax crayon."""
    w, h = 640, 820; im = Image.new("RGBA", (w, h), (252, 250, 240, 255)); d = ImageDraw.Draw(im); rg = np.random.default_rng(6)
    def cray(pts, col, wd=9):
        for _ in range(3): d.line([(x + rg.normal(0, 2), y + rg.normal(0, 2)) for x, y in pts], fill=col, width=wd, joint="curve")
    cray([(60 + k * 30, 700 + 6 * np.sin(k)) for k in range(20)], (60, 160, 70), 12)
    for a in range(0, 360, 30): cray([(520, 120), (520 + 90 * np.cos(np.radians(a)), 120 + 90 * np.sin(np.radians(a)))], (240, 190, 30), 7)
    d.ellipse((480, 80, 560, 160), fill=(250, 210, 40))
    cray([(200, 290), (200, 560)], (220, 70, 120), 12); cray([(200, 380), (140, 460)], (220, 70, 120)); cray([(200, 380), (290, 430)], (220, 70, 120)); cray([(200, 560), (160, 680)], (60, 60, 160)); cray([(200, 560), (240, 680)], (60, 60, 160))
    d.ellipse((150, 190, 250, 290), outline=(200, 120, 90), width=8); cray([(150, 190), (165, 135), (185, 175), (200, 125), (215, 175), (235, 135), (250, 190)], (240, 190, 30), 9)   # the crown
    cray([(380, 470), (380, 600)], (110, 80, 220), 10); cray([(380, 500), (300, 440)], (110, 80, 220)); cray([(380, 600), (350, 680)], (60, 60, 160)); cray([(380, 600), (410, 680)], (60, 60, 160))
    d.ellipse((345, 400, 415, 470), outline=(200, 120, 90), width=7); d.text((60, 30), "MAMAN", fill=(220, 40, 40), font=ImageFont.truetype(E.HAND, 80))
    d.text((330, 720), "moi", fill=(110, 80, 220), font=ImageFont.truetype(E.HAND, 60))
    return im


def fridge_insert(t, t0):
    """The fridge door, close: the drawing under a red magnet. On "souvenais" a hand takes it down; a clean rectangle stays."""
    im = Image.new("RGB", (W, H), (226, 228, 230)); a = np.asarray(im).astype(np.float32) * (0.92 + 0.08 * np.linspace(1, 0, W))[None, :, None]; im = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 300, 120, 1500), 20, fill=(180, 182, 188))
    q = ease((t - T_SOUV) / 0.6); dw = drawing(); x, y = 230, 560 - int(q * 900)
    d.rectangle((228, 558, 872, 1382), fill=(236, 238, 240))                                     # where the sun did not reach
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.paste(dw.rotate(-2 + 8 * q, expand=True), (x, y)); im = Image.alpha_composite(im.convert("RGBA"), lay)
    d = ImageDraw.Draw(im)
    if q < 0.2: d.ellipse((530, 560, 590, 620), fill=(200, 30, 30)); d.ellipse((545, 570, 565, 590), fill=(240, 120, 120))
    if q > 0.05:
        ld = ImageDraw.Draw(im); MO.sleeve(ld, 900, -200, 660, y + 80, T2.HOOD, 150); MO.hand(ld, 620, y + 60, np.radians(170), 1.2, T2.SKIN, grip=0.7)
    im = memory(im.convert("RGB"), 1.0)
    return handheld(E.view(im.resize((int(W * 1.2), int(H * 1.2))), t, t0, t0 + 5, 1.0, 1.1, 0.5, 0.48, drift=0.3), t, 0.5)


def mum_close(t, t0, t1, key, warm=False, drawing_in_hand=False, sad=0.6):
    """Her face, close: she speaks; the camera breathes with her. Warm when she remembers, cold in the dark kitchen."""
    a = speaking(key, t); kw = dict(mum=True, look=(0.1, 0.05), blink=blink(t, 0.3), mouth=talk(key, t) if a > 0 else "line", brow=sad + 0.3 * min(1, a), wide=1.05)
    kw.update(MO.gesture(t, 5, a)); kw.update(MO.alive(t, 5, 1.0, a)); sp = hero(2300, **kw)
    bg = (ST["kitlit"] if warm else ST["kitdark"]).filter(ImageFilter.GaussianBlur(9))
    im = put(bg, sp, SW * 0.5, SH * 1.32, shadow=False, mul=None if warm else (0.62, 0.66, 0.82), rim=((150, 180, 255), 12, 0.6) if not warm else None)
    if drawing_in_hand:
        dw = drawing().resize((420, 538)).rotate(6, expand=True); lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); lay.paste(dw, (int(SW * 0.55), int(SH * 0.62)), dw); im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")
    if a > 0 and warm and key == "mm2" and t > we(key) - 1.2:                                   # a tear, at the end of the line
        d = ImageDraw.Draw(im); ty = SH * 0.47 + (t - (we(key) - 1.2)) * 160; d.ellipse((SW * 0.41 - 12, ty - 18, SW * 0.41 + 12, ty + 18), fill=(170, 210, 255))
    im = E.view(im, t, t0, t1, 1.0, 1.08, 0.5, 0.42, drift=0.3)
    return memory(im, 0.85) if warm else im


def hug_shot(t, t0, t1):
    """The right hand slips away; his mother pulls him against her in the dark kitchen."""
    q = ease((t - T_CONTRE) / 0.6); base = ST["kitdark"]
    me = hero(1500, look=(0.3, 0.1), wide=1.2, brow=0.9, mouth="o", sweat=True, **MO.alive(t, 1))
    mum = hero(1450, mum=True, look=(-0.4, 0.1), brow=0.8, mouth="line", blink=blink(t, 0.2), armL=(0.6 + 0.5 * q, 1.4 + 0.6 * q), armR=(0.6 + 0.5 * q, 1.4 + 0.6 * q), **MO.alive(t, 3))
    im = put(base, mum, SW * (0.62 - 0.08 * q), SH * 1.05, shadow=False, mul=(0.6, 0.62, 0.78), rim=((150, 180, 255), 10, 0.6))
    im = put(im, me, SW * (0.4 + 0.04 * q), SH * 1.08, shadow=False, mul=(0.6, 0.62, 0.78), rim=((150, 180, 255), -10, 0.6))
    if t >= T_GLISSE:                                                 # the red thread falls to the floor
        d = ImageDraw.Draw(im); fy = SH * (0.86 + 0.08 * ease((t - T_GLISSE) / 0.5)); d.arc((SW * 0.7, fy - 30, SW * 0.78, fy + 10), 0, 300, fill=(214, 30, 30), width=8)
    return handheld(E.view(im, t, t0, t1, 1.05, 1.15, 0.5, 0.55, drift=0.3), t, 0.9)


def hands_choice(t, t0, mode):
    """Yesterday's last image, the two hands; mode 'left' lets go of the warm one, 'right' of the cold one."""
    im = Image.new("RGB", (W, H), (3, 3, 6)); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); tr = lambda k: 5 * NOISE.noise2(t * 9, k)
    gone_l = ease((t - T_LEFT) / 0.6) if mode == "left" else 0.0; gone_r = ease((t - T_DROITE) / 0.6) if mode == "right" else 0.0
    for x, side in ((330, -1), (750, 1)):
        MO.sleeve(d, x + side * 160, H + 80, x + tr(1), 1390, T2.HOOD, 150, cuff=T2.REDB if side > 0 else None); MO.hand(d, x + tr(1), 1300, np.radians(side * 10), 1.25, T2.SKIN, grip=0.2)
    for x, side, cold, gone in ((330, -1, False, gone_l), (750, 1, True, gone_r)):
        ox, oy = x + side * 600 * gone, 1170 - 300 * gone
        MO.sleeve(d, ox + side * 560, oy - 600, ox + tr(3), oy - 40, (14, 14, 20, 255) if cold else (196, 128, 138, 255), 150, cuff=T2.REDB if cold else None)
        MO.hand(d, ox + tr(3), oy + 40, np.radians(180 - side * 15), 1.25, (70, 74, 96, 255) if cold else T2.SKIN, grip=0.9 - 0.7 * gone)
    if mode == "left" and t >= T_SERRE:                               # the cold hand pulls him away, into the black
        k = ease((t - T_SERRE) / 1.2); lay = lay.transform((W, H), Image.AFFINE, (1, 0, -260 * k, 0, 1, 240 * k), Image.BICUBIC)
    im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB"); im = E.torch(im, 540, 1200, 820, 0.1, 1.05)
    im = E.spill(im, 760, 1060, 140, 100, (255, 40, 30), 0.35)
    if mode == "left" and t >= T_JOUR:                                # morning comes, without him
        k = ease((t - T_JOUR) / 1.5); im = Image.blend(im, Image.new("RGB", (W, H), (230, 170, 110)), 0.6 * k)
    return handheld(im, t, 1.4)


def door_to_room(t, t0, t1):
    """His bedroom door, ajar, from the corridor: inside, the stars, and the grin on the wall."""
    ins = Image.eval(BSOFT.resize((420, 1080), Image.LANCZOS), lambda v: int(v * 0.6)); TG.grin(ins, 3.0, 0.0, (int(420 * BP["grin"][0]), int(1080 * BP["grin"][1]) - 20), 70)
    wall = Image.eval(ST["entdark"].resize((W, H)), lambda v: int(v * 0.9))
    a = 0.45 + 0.15 * ease((t - (t0 + 0.4)) / 2.0)
    im = MO.door_open(wall, ins, (330, 420, 750, 1500), a, hinge="right", leaf=N2._LEAF2, light=((110, 140, 210), 0.5))
    im = E.torch(im, 470, 900, 760, 0.35, 1.05)
    return handheld(E.view(im.resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, 1.0, 1.25, 0.4, 0.45, drift=0.3), t, 1.0)


def switch_insert(t, t0):
    """The light switch, close: his finger presses it. Click. Nothing. Again. Nothing."""
    im = Image.eval(ST["bdark"].resize((W, H)).filter(ImageFilter.GaussianBlur(14)), lambda v: int(v * 0.7)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((380, 760, 700, 1160), 30, fill=(214, 214, 206), outline=(120, 120, 116), width=6)
    pr = (T_CLIC <= t < T_CLIC + 0.25) or (T_RIEN + 0.3 <= t < T_RIEN + 0.55)
    d.rounded_rectangle((440, 820 + (14 if pr else 0), 640, 1100), 18, fill=(232, 232, 226), outline=(150, 150, 146), width=5)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); hy = 980 + (40 if pr else 0) + 400 * (1 - ease((t - t0) / 0.6))
    MO.sleeve(ld, 1100, hy + 700, 640, hy + 140, T2.HOOD, 160, cuff=T2.REDB); MO.hand(ld, 560, hy + 40, np.radians(-35), 1.3, T2.SKIN, grip=0.75)
    im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB"); im = E.torch(im, 540, 960, 700, 0.3, 1.0)
    return handheld(im, t, 0.8)


def behind(t):
    """He was right behind the door: his face, his cap, too close, and the grin."""
    sp = T2.char(2600, dark=True, look=(0.0, 0.0)); im = Image.new("RGB", (W, H), (4, 4, 8))
    im.paste(sp, (int(W / 2 - sp.width / 2), int(H * 1.35 - sp.height)), sp)
    return handheld(im, t, 2.5)


def show_drawing(t, t0, t1):
    """In his room, lit by his mother's phone: the double by the window. You hold out the drawing."""
    gx, gy = BP["grin"]; im = reveal(ST["bdark"], BSOFT, SW * 0.55, SH * 0.55, 600)
    TG.grin(im, 3.0, 0.0, (gx * SW, gy * SH - 40), 190)
    a = speaking("dd", t); dbl = T2.char(1350, dark=True, look=(0.0, 0.25), head=(0.25 * np.sin(t * 0.8), 0.25 + 0.2 * a))
    im = put(im, dbl, SW * 0.62, SH * 0.93, shadow=True)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); q = ease((t - t0) / 0.8)
    dw = drawing().resize((380, 487)).rotate(-8, expand=True); lay.paste(dw, (int(SW * 0.2), int(SH * (0.62 + 0.15 * (1 - q)))), dw)
    MO.sleeve(d, -60, SH + 60, SW * 0.24, SH * (0.85 + 0.15 * (1 - q)), T2.HOOD, 170, cuff=T2.REDB); MO.hand(d, SW * 0.27, SH * (0.82 + 0.15 * (1 - q)), np.radians(30), 1.3, T2.SKIN, grip=0.6)
    im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")
    return handheld(E.view(im, t, t0, t1, 1.0, 1.12, 0.48, 0.55, drift=0.3), t, 0.8)


def window_shot(t, t0, t1):
    """He backs away to the window; it opens on its own; the curtains lift; he tips over the sill and is gone."""
    o = ease((t - T_FEN) / 0.5); base = xf(ST["wclosed"], ST["wopen"], o); wx, wy = WP["window"]
    k = ease((t - (T_ETAGE - 0.2)) / 0.5); ph = (t - t0) / 1.2; kw = walk(ph, 0.4) if t < T_FEN else {}
    dbl = T2.char(1300, dark=True, look=(0.0, 0.0), lean=-0.1 * k, **{x: v for x, v in kw.items() if x in ("legs", "armL", "armR")})
    if k < 1:
        cx = SW * (0.45 + (wx - 0.45) * min(1, (t - t0) / max(0.1, T_FEN - t0))); foot = SH * 0.9 - 400 * k
        dbl = dbl.rotate(-70 * k, expand=True, resample=Image.BICUBIC) if k > 0 else dbl
        im = put(base, dbl, cx, foot, shadow=k < 0.2)
    else: im = base
    if o > 0:                                                         # cold air in: the curtain lifts on noise
        d = ImageDraw.Draw(im); cxp = wx * SW + 220; sw_ = 40 + 60 * o * (0.5 + 0.5 * NOISE.noise2(t * 1.8, 3))
        d.polygon([(cxp, SH * 0.3), (cxp + 70, SH * 0.3), (cxp + 70 + sw_, SH * 0.62), (cxp + sw_, SH * 0.62)], fill=(110, 40, 36))
    return handheld(E.view(im, t, t0, t1, 1.0, 1.12, 0.6, 0.48, drift=0.3), t, 1.2)


def street_empty(t, t0, t1):
    """His building from the street, fourth floor window open. On the pavement below: nobody."""
    im = N2._home_plate().copy(); x0_, y0_, x1_, y1_ = N2.WIN[(1, 2)]; d = ImageDraw.Draw(im)
    d.rectangle((x0_, y0_, x1_, y1_), fill=(20, 26, 44)); d.polygon([(x1_, y0_), (x1_ + 50, y0_ + 20), (x1_ + 50, y1_ - 20), (x1_, y1_)], fill=(50, 60, 90))
    im = rain(im, t, 120, 0.35)
    return E.view(im, t, t0, t1, 1.15, 1.0, 0.5, 0.55 + 0.1 * ease((t - t0) / 2.0), drift=0.3)


def order_again(t):
    """Next evening: the app. New order. Address: 27 rue... no. His own address. Client: TOI."""
    sc, d = N1._app("21:47"); u = ease((t - T_VIBRE) / 0.3)
    if u > 0:
        card = Image.new("RGBA", (PSW - 50, 520), (0, 0, 0, 0)); cd = ImageDraw.Draw(card); cd.rounded_rectangle((0, 0, card.width - 1, 519), 30, fill=(255, 255, 255, 255), outline=(200, 25, 25, 255), width=5)
        cd.text((34, 30), "NOUVELLE COMMANDE", font=E.fI("Bold", 32), fill=(200, 25, 25)); cd.text((card.width - 34, 34), "#0015", font=ImageFont.truetype(E.MONO, 28), fill=(120, 120, 130), anchor="ra")
        for k, (a_, b_, red) in enumerate((("Client", "???", False), ("Adresse", "4B · CHEZ TOI", t >= T_ADR), ("Livraison", "ce soir · 02:14", False))):
            cd.text((34, 130 + k * 82), a_, font=E.fI("Regular", 28), fill=(120, 120, 130), anchor="lm"); cd.text((card.width - 34, 130 + k * 82), b_, font=E.fI("Bold", 36), fill=(200, 25, 25) if red else (30, 30, 36), anchor="rm")
        cd.rounded_rectangle((34, 400, card.width - 34, 480), 40, fill=N1.PURPLE); cd.text((card.width / 2, 440), "ACCEPTER", font=E.fI("Bold", 34), fill=(255, 255, 255), anchor="mm")
        sc.alpha_composite(card, (25, int(250 + 200 * (1 - u))))
    return N1._phone(sc, t, T_VIBRE, vib_until=0.5)


RULES = N2.RULES + (["RÈGLE 6", "Ne lâche jamais", "la main tiède."], ["RÈGLE 7", "Chez toi, apporte", "ta propre lumière."])
_REC = None
def receipt(t, t0, stage):
    """The slip again: rules 1 to 5 in small, and the new one written in red."""
    global _REC
    if _REC is None:
        w, h = 760, 1260; p = E.paper_tex(w, h, (246, 244, 236), fiber=0.04, seed=53); d = ImageDraw.Draw(p); fm = ImageFont.truetype(E.MONO, 26)
        d.ellipse((335, 30, 425, 120), fill=N1.PURPLE); d.ellipse((366, 40, 434, 108), fill=(246, 244, 236))
        d.text((380, 164), "NUIT EXPRESS", font=E.fI("Bold", 50), fill=(30, 30, 34), anchor="mm"); d.text((380, 208), "commande #0013 · client : TOI", font=fm, fill=(110, 110, 116), anchor="mm")
        f = ImageFont.truetype(E.HAND, 38); y = 262
        for r in RULES[:5]: d.text((60, y), r[0] + " · " + " ".join(r[1:]), font=f, fill=(205, 24, 24)); y += 50
        m = Image.new("L", (w, h), 255); md = ImageDraw.Draw(m)
        for x in range(0, w, 40): md.polygon([(x, h), (x + 20, h - 26), (x + 40, h)], fill=0)
        p.putalpha(m); _REC = p
    fr = _REC.copy(); d = ImageDraw.Draw(fr); f = ImageFont.truetype(E.HAND, 66); rg = np.random.default_rng(3)
    def write(lines, y, n):
        for ln in lines:
            part = ln[:max(0, n)]; n -= len(ln); x = 60
            for ch in part: d.text((x + rg.normal(0, 0.8), y + rg.normal(0, 1.2)), ch, font=f, fill=(205, 24, 24)); x += d.textlength(ch, font=f)
            y += 74
    write(RULES[5], 560, int(np.clip((t - t0 - 0.6) * 24, 0, 99)) if stage == 6 else 99)
    if stage == 7: write(RULES[6], 830, int(np.clip((t - t0 - 0.6) * 24, 0, 99)))
    bg = ST["bdark"].resize((W, H)).filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.6)).convert("RGBA")
    fr = fr.resize((int(fr.width * 0.84), int(fr.height * 0.84)), Image.LANCZOS).rotate(-2.0 + np.sin(t * 8) * 0.2, expand=True, resample=Image.BICUBIC)
    E.drop_shadow(bg, fr, (int(W / 2 - fr.width / 2), int(860 - fr.height / 2)), blur=26, off=(14, 26), alpha=170)
    im = E.torch(bg, 540 + np.sin(t * 1.3) * 50, 900 + np.cos(t * 1.1) * 50, 1250, 0.5, 1.12)
    q = ease((t - t0 - 0.6) / 1.2); cy = 0.5 + q * (0.08 if stage == 6 else 0.15)
    return E.view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t0 + 2.0, 1.0, 1.3, 0.5, cy, drift=0.4)


# ---------------------------------------------------------------- overlays
def hud(im, t):
    d = ImageDraw.Draw(im); fs = ImageFont.truetype(E.MONT, 28)
    if L_("fb0") <= t < L_("p1"): place, clock = "IL Y A 3 SEMAINES", "20:31:00"
    elif t >= L_("e1"): place, clock = "LE LENDEMAIN", "21:47:%02d" % int(t - L_("e1"))
    else:
        place = "CHEZ TOI · " + ("CUISINE" if L_("v0") <= t < L_("p1") and not (T_DINE <= t < T_SOIR) else "TA CHAMBRE"); s_ = int(2 * 3600 + 55 * 60 + 20 + t); clock = f"{s_ // 3600:02d}:{s_ // 60 % 60:02d}:{s_ % 60:02d}"
    d.text((124, 232), "NUIT 3 · " + place, font=fs, fill=(235, 235, 238), stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((122, 266), clock, font=ImageFont.truetype(E.MONO, 62), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))


C1 = ("ALLUMER", "LE DESSIN"); C0 = ("LA GAUCHE", "LA DROITE"); C2 = ("LA LIVRER", "LA REFUSER")
CUTS = [T_DINE, T_SOIR, L_("w1"), T_CONTRE - 0.1, L_("mm1"), L_("fb0"), L_("fb1"), L_("fb2"), L_("fb3"), L_("mm2"), L_("p1"), L_("x1"), L_("y1"), L_("dd"), L_("mm3"), L_("y2"), L_("y3"), L_("e1"), L_("c2")]


def raw(i, t):
    g = ("night", 0.4); hd = True; btn = None; labels = []
    if t < T_DINE: im = bedroom_grin(t, 0, T_DINE, torch=(BP["grin"][0] * SW, BP["grin"][1] * SH, 520)); labels = [("plate", 0.25, "TA CHAMBRE")]
    elif t < T_SOIR: im = kitchen_memory(t, T_DINE, T_SOIR); g = None; labels = [("stamp", T_DINE + 0.4, "3 SEMAINES")]
    elif t < L_("v0"): im = bedroom_grin(t, T_SOIR, L_("v0"), torch=(SW * (BP["grin"][0] - 0.12 + 0.12 * ease((t - T_SOIR) / 1.5)), BP["grin"][1] * SH, 540)); labels = [("label", T_SOUR + 0.2, "PEINT CETTE NUIT")]
    elif t < L_("v1"): im = hands_choice(t, L_("v0"), "none"); g = None; btn = (C0, 0, 1, None, True); labels = [("label", L_("v0") + 0.2, "HIER SOIR")]
    elif t < L_("r6"):
        im = hands_choice(t, L_("v1"), "left"); g = None
        if t < L_("v1") + 1.1: btn = (C0, 0, 1, "LA GAUCHE", True)
    elif t < t_rew1: im = receipt(t, L_("r6"), 6); g = ("paper", 0.4); hd = False
    elif t < L_("w1"): return None
    elif t < T_CONTRE - 0.1:
        im = hands_choice(t, L_("w1"), "right"); g = None
        if t < L_("w1") + 1.1: btn = (C0, 0, 1, "LA DROITE", True)
    elif t < L_("mm1"): im = hug_shot(t, T_CONTRE - 0.1, L_("mm1")); labels = [("label", T_CONTRE + 0.3, "LE BRACELET EST TOMBÉ")]
    elif t < L_("fb0"): im = mum_close(t, L_("mm1"), L_("fb0"), "mm1", sad=0.9); labels = [("plate", L_("mm1") + 0.2, "TA MÈRE")]
    elif t < L_("fb1"): im = kitchen_memory(t, L_("fb0"), L_("fb1")); g = None; labels = [("stamp", L_("fb0") + 0.3, "IL Y A 3 SEMAINES")]
    elif t < L_("fb2"): im = kitchen_memory(t, L_("fb1"), L_("fb2"), mood="calm", lamp=1 - ease((t - T_LAMPE) / 0.4), focus=1); g = None; labels = [("label", L_("fb1") + 0.2, "INDICE 1 · TOUJOURS DANS LE NOIR")]
    elif t < L_("fb3"): im = plate_insert(t, L_("fb2")); g = None; labels = [("label", L_("fb2") + 0.2, "INDICE 2 · ASSIETTE VIDE")]
    elif t < L_("mm2"): im = fridge_insert(t, L_("fb3")); g = None; labels = [("label", L_("fb3") + 0.2, "INDICE 3 · LE DESSIN")]
    elif t < L_("p1"): im = mum_close(t, L_("mm2"), L_("p1"), "mm2", warm=True, drawing_in_hand=True, sad=0.7); g = None
    elif t < L_("x1"):
        im = door_to_room(t, L_("p1"), L_("x1")); labels = [("label", T_COULE, "LA PEINTURE COULE ENCORE")]
        if t >= L_("c1") - 0.05: btn = (C1, L_("c1"), L_("x1"), None)
    elif t < T_DERR: im = switch_insert(t, L_("x1")); g = ("night", 0.45); labels = [("stamp", T_RIEN + 0.1, "CLIC. RIEN.")]
    elif t < L_("r7"): im = behind(t) if t < we("x2") + 0.8 else Image.new("RGB", (W, H), (3, 3, 6)); g = None
    elif t < t_rew2: im = receipt(t, L_("r7"), 7); g = ("paper", 0.4); hd = False
    elif t < L_("y1"): return None
    elif t < L_("mm3"):
        im = show_drawing(t, L_("y1"), L_("mm3"))
        if t < L_("y1") + 1.1: btn = (C1, 0, 1, "LE DESSIN")
    elif t < L_("y2"): im = mum_close(t, L_("mm3"), L_("y2"), "mm3", sad=0.1); labels = [("plate", L_("mm3") + 0.2, "SA VRAIE MÈRE")]
    elif t < L_("y3"): im = window_shot(t, L_("y2"), L_("y3")); labels = [("stamp", T_ETAGE + 0.1, "4e ÉTAGE")]
    elif t < L_("e1"): im = street_empty(t, L_("y3"), L_("e1")); g = ("night", 0.5); labels = [("label", L_("y3") + 0.8, "PERSONNE")]
    elif t < L_("c2"): im = order_again(t); g = None
    else:
        im = N1.face_shot(t, L_("c2"), D, still="street2", scared=True); g = ("night", 0.2); btn = (C2, 0, 1, None, True)
    return im, g, hd, btn, labels


_CH = {}
def choice_img(key, tc):
    if key not in _CH: _CH[key] = finish(0, tc, raw(0, tc), captions=False)
    return _CH[key]


def finish(i, t, r, captions=True):
    im, g, hd, btn, labels = r
    if g: im = N1.GRADE(im, i, exp=g[1], warm=True, glow=g[0] != "paper")
    for kind, t0, txt in labels:                                      # the labels, stuck on the shot as the voice says it
        if kind == "plate": TG.name_plate(im, t, t0, txt, (540, 520))
        elif kind == "stamp": TG.stamp_tag(im, t, t0, txt, (560, 760), 84)
        else: TG.label(im, t, t0, txt, (540, 1330), 40)
    if hd: hud(im, t)
    if L_("v3") + 0.2 <= t < L_("r6"): N1.stamp(im, t, L_("v3") + 0.3, "FIN DE SERVICE", y=600, size=92)
    if L_("x3") + 0.2 <= t < L_("r7"): N1.stamp(im, t, L_("x3") + 0.3, "FIN DE SERVICE", y=600, size=92)
    if btn: N1.buttons(im, btn[0], t, btn[1], btn[2], btn[3], ab=len(btn) > 4, title="TOI, TU FAIS QUOI ?" if len(btn) > 4 and t >= L_("c2") and t >= wt("c2", "toi") - 0.1 else None)
    if t >= D - 2.4:                                                  # end card, as the recaps do: subscribe, then the next night
        dk = cl((t - (D - 2.4)) / 0.3); im = Image.blend(im, Image.new("RGB", (W, H), (8, 6, 12)), 0.75 * dk); TG.subscribe(im, t, D - 2.2, "NUIT 4", "Qui a passé la commande ?")
    if captions and t < D - 2.4: G.karaoke(im, words, t, "present", hl=RED, box=False, y0=1500 if g else 1575, size0=70, stroke=7)
    return im


def render(i, t):
    r = raw(i, t)
    if r is None:
        for t0, key, tc in ((t_rew1, "c0", L_("v1") - 0.3), (t_rew2, "c1", L_("x1") - 0.3)):
            if t0 <= t < t0 + 0.9: return N1.rewind(i, t, t0, choice_img(key, tc))
    k = int(round((t - T_DERR) / F))                                 # the one shock: after the second of silence, his face
    if -2 <= k < 0: return N1.smear(finish(i, T_DERR + 0.3, raw(i, T_DERR + 0.3), captions=False), k)
    if k == 0: return N1.negative(finish(i, T_DERR + 0.3, raw(i, T_DERR + 0.3), captions=False))
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
    def sweep(): x = np.arange(int(0.9 * VSR)) / VSR; return np.sin(2 * np.pi * np.cumsum(1800 - 1500 * x / 0.9) / VSR) * 0.25 + rng.standard_normal(len(x)) * 0.12
    def band(lo, hi, n): return sosfiltfilt(butter(2, [lo, hi], btype="band", fs=VSR, output="sos"), rng.standard_normal(n))
    def heart(a_, b_, per=0.55, g=0.9):
        for q in np.arange(a_, b_, per): add(thump(), q, g); add(thump(), q + 0.19, g * 0.65)
    def clack(at_, g=1.0): add(click() * 3, at_, g); add(tone(900, 0.05, 80), at_, 0.5 * g); add(thump(), at_ + 0.01, 0.6 * g)
    def music_box(a_, b_, g=0.25):                                   # the memories: a soft music-box tune, out of tune like an old toy
        notes = [659, 587, 523, 587, 659, 659, 659, 587, 587, 587, 659, 784, 784]
        for k, q in enumerate(np.arange(a_, b_, 0.42)): add(tone(notes[k % len(notes)] * 0.995, 0.9, 4.0) + tone(notes[k % len(notes)] * 2.01, 0.9, 6.0) * 0.3, q, g)
    memory_t = (ts >= L_("fb0")) & (ts < L_("p1"))
    fridge = (np.sin(2 * np.pi * 50 * ts) + 0.5 * np.sin(2 * np.pi * 100 * ts)) * 0.04; mix += fridge * ~memory_t * (ts < L_("y3"))
    mix += band(1500, 7000, NS) * 0.3 * (ts >= L_("y3")) * (ts < L_("e1"))
    add(boom(), 0.0, 0.6); add(boom(), T_SOUR, 0.6); music_box(T_DINE, T_SOIR, 0.2); music_box(L_("fb0"), L_("p1"), 0.22)
    heart(L_("v0"), L_("r6"), 0.5); add(boom(), T_LEFT, 0.6); add(boom(), L_("v3") + 0.3, 0.8)
    for k in range(3): add(tone(1200, 0.05, 60), we("v0") + 0.1 + k * 0.26, 0.45)
    for t0_ in (L_("r6"), L_("r7")):
        for k in range(46): add(click() * 0.5, t0_ + 0.5 + k * 0.05, 0.5)
    for t0_ in (t_rew1, t_rew2): add(sweep(), t0_, 0.8)
    add(tone(3200, 0.2, 20) + tone(4100, 0.2, 25) * 0.5, T_GLISSE + 0.4, 0.2)                        # the thread lands on the floor
    clack(T_LAMPE + 0.1, 0.6); add(tone(2400, 0.4, 10) + tone(3600, 0.4, 12) * 0.4, T_VIDE, 0.1)
    add(np.convolve(rng.standard_normal(int(0.25 * VSR)), np.ones(30) / 30, "same") * 4, T_SOUV, 0.4)  # paper off the fridge
    heart(L_("p1"), L_("x1"), 0.5); xx = np.arange(int(0.8 * VSR)) / VSR; add(np.sin(2 * np.pi * np.cumsum(140 + 160 * xx) / VSR) * np.exp(-xx * 3) * 0.3, L_("p1") + 0.3, 0.5)
    for k in range(3): add(tone(1200, 0.05, 60), we("c1") + 0.1 + k * 0.26, 0.45)
    clack(T_CLIC, 1.0); clack(T_RIEN + 0.35, 1.0)
    mute = (ts >= wt("x2", "ampoule") + 0.5) & (ts < T_DERR - 0.05)
    add(np.convolve(rng.standard_normal(int(0.14 * VSR)), np.ones(25) / 25, "same") * 9, T_DERR - 0.08, 0.5); add(boom(), T_DERR, 1.2); add(boom(), L_("x3") + 0.3, 0.8)
    heart(L_("y1"), L_("y2"), 0.6, 0.6); add(boom(), T_FEN, 0.5); mix += band(200, 1500, NS) * 0.15 * (ts > T_FEN) * (ts < L_("y3"))     # wind through the open window
    add(boom(), T_ETAGE + 0.3, 0.9)
    x = np.arange(int(0.5 * VSR)) / VSR; add(np.sin(2 * np.pi * 150 * x) * (np.sin(2 * np.pi * 6 * x) > 0) * 0.5, T_VIBRE, 0.5); add(boom(), T_ADR, 0.7)
    heart(L_("c2"), D - 2.4, 0.47, 0.9); add(tone(1046, 0.4, 6) + tone(1568, 0.4, 7) * 0.6, D - 1.5, 0.3)        # the subscribe button
    vox = np.zeros(NS)
    for k, t0 in line_t.items():
        v = VO_A[k]
        if k == "dd": v = sosfiltfilt(butter(2, [200, 4500], btype="band", fs=VSR, output="sos"), v) * 0.9
        i0 = int(t0 * VSR); j0 = min(NS, i0 + len(v)); vox[i0:j0] += v[: j0 - i0]
    act = np.convolve((np.convolve(np.abs(vox), np.ones(2205) / 2205, "same") > 0.01).astype(float), np.ones(13230) / 13230, "same")
    mix = mix / np.abs(mix).max() * 0.55 * (1 - 0.6 * np.clip(act, 0, 1)) * (1 - np.convolve(mute.astype(float), np.ones(2205) / 2205, "same")) + vox / (np.abs(vox).max() + 1e-9) * 0.9
    mix = mix[: int(D * VSR)]; mix *= np.clip((D - ts[: len(mix)]) / 0.3, 0, 1); sf.write(TMP + "mix.wav", mix / np.abs(mix).max() * 0.9, VSR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", TMP + "f%05d.jpg", "-i", TMP + "mix.wav",
                    "-c:v", "libx264", "-crf", "24", "-maxrate", "3200k", "-bufsize", "6400k", "-preset", "slow", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-g", "60",
                    "-af", "loudnorm=I=-13:TP=-1.0:LRA=9,volume=1.3,alimiter=limit=0.89", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", _out], check=True)
    print("ok", _out, D)
