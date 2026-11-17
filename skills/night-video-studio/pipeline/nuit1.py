"""LIVREUR DE NUIT, nuit 1: "La dernière commande". About 2 min 40, 2D characters in 3D sets.
You are the courier; the customer has your name. Three choices inside the video, each wrong one ends in a loss that a
clue announced, a rule written by hand on the order slip, and the tape rewinds. The end is an open A/B.
usage: HF_HOME=... nuit1.py <out.mp4>   (EI_STEP=n layout test, EI_AUDIO_ONLY=1 remix from existing frames)"""
import os, sys, json, glob, subprocess, functools
_out = sys.argv[1]; sys.argv = ["ei3.py", "/tmp/unused.mp4"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import ei3 as E, toon2d as T2
G = E.G; W, H, FPS, VSR, F, RED, NEW = E.W, E.H, E.FPS, E.VSR, E.F, E.RED, E.NEW
VO, TMP = NEW + "elv8/fin/", NEW + "n1tmp/"; os.makedirs(TMP, exist_ok=True)
ORDER = ["h0", "h3", "h4", "h5", "a1", "a2", "a3", "iv", "c1", "w1", "w3", "w4", "w5", "r1", "m1", "m2", "m3", "m4", "dv", "c2",
         "x1", "x2", "x3", "x4", "r2", "p1", "p2", "p3", "c3", "y1", "y2", "y3", "r3", "f1", "f2", "f3", "f4", "c4"]
import re
SCRIPT = {n: re.sub(r"\[[^\]]*\]\s*", "", t) for n, w, t in json.load(open(NEW + "elv8/lines.json")) if n in ORDER}
VO_A = {k: G.voice(VO + f"{k}.wav", lp=None) for k in ORDER}; REL = {}
_cache = TMP + "rel.json"; _sig = {k: [SCRIPT[k], len(VO_A[k])] for k in ORDER}
if os.path.exists(_cache) and json.load(open(_cache))["sig"] == _sig: REL = json.load(open(_cache))["rel"]
else:
    for k in VO_A:
        p = TMP + f"{k}_pre.wav"; sf.write(p, VO_A[k], VSR); REL[k] = E.align(G.word_times(p, 0, None), SCRIPT[k])
    json.dump({"sig": _sig, "rel": REL}, open(_cache, "w"))
dur = {k: len(v) / VSR for k, v in VO_A.items()}
T = 0.05; line_t = {}
def at(k, gap):
    global T
    line_t[k] = T; T += dur[k] + gap
at("h0", 0.35); at("h3", 0.3); at("h4", 0.3); at("h5", 0.5)                       # the hook: the order, the tip, his mother
at("a1", 0.3); at("a2", 0.3); at("a3", 0.2); at("iv", 0.3); at("c1", 1.0)                       # the building, the intercom, choice 1
at("w1", 0.3); at("w3", 0.35); at("w4", 0.35); at("w5", 0.5); at("r1", 0.4)                     # you left the bag downstairs
t_rew1 = T; T += 0.9
at("m1", 0.3); at("m2", 0.35); at("m3", 0.4); at("m4", 0.3); at("dv", 0.3); at("c2", 1.0)       # the stairs, the dark, the hand, choice 2
at("x1", 1.0); at("x2", 0.35); at("x3", 0.35); at("x4", 0.6); at("r2", 0.4)                     # you took the note: one second of silence, the swap
t_rew2 = T; T += 0.9
at("p1", 0.6); at("p2", 0.4); at("p3", 0.3); at("c3", 1.0)                                      # you put the bag down; a new order, choice 3
at("y1", 0.3); at("y2", 0.4); at("y3", 0.5); at("r3", 0.4)                                      # you accepted: thirteen bags
t_rew3 = T; T += 0.9
at("f1", 0.3); at("f2", 0.3); at("f3", 0.4); at("f4", 0.4); at("c4", 1.6)                       # you walk home; her message; the open question
D = round(T, 2); N = int(D * FPS); print("duration", D)
def L_(k): return line_t[k] - 0.12
def wt(k, frag, n=0): return line_t[k] + [w["s"] for w in REL[k] if frag in E.norm(w["w"])][n]
def we(k): return line_t[k] + dur[k]
T_LIV = 0.0; T_NOTIF = wt("h0", "commande") - 0.1; T_TOI0 = wt("h0", "toi") - 0.05; T_PHOTO = T_TOI0 + 0.12; T_TIP = wt("h3", "dix") - 0.1; T_OK = wt("h5", "accept") + 0.25
T_FEN = wt("a1", "seule") - 0.1; T_NOM = wt("a2", "nom") - 0.15; T_SONNE = wt("a3", "sonnes") + 0.15; T_VOIX = wt("a3", "voix") - 0.1
T_VERR = wt("w3", "verrouille") - 0.05; T_NOIR1 = wt("w3", "teint") - 0.1
T_E1 = wt("m1", "premier") - 0.1; T_E2 = wt("m1", "deux") - 0.1; T_E3 = line_t["m2"]; T_L1 = T_E1 + 0.3; T_L2 = T_E2 + 0.3; T_L3 = wt("m1", "teint") - 0.05; T_SHOES = wt("m2", "chaussures") - 0.15
T_CLAC = wt("m3", "claque") - 0.05; T_RESP = wt("m3", "respiration") - 0.2; T_PRES = wt("m3", "près") - 0.1
T_MAIN = wt("m4", "main") - 0.15; T_BRAC = wt("m4", "bracelet") - 0.15
T_DOIGTS = wt("x1", "doigts") - 0.1; T_ECH = wt("x2", "change") - 0.05; T_RESTES = wt("x3", "restes") - 0.1; T_CMD = wt("x4", "toi") - 0.05
T_REF = wt("p1", "referme") - 0.1; T_60 = wt("p2", "soixante") - 0.1; T_VIB = wt("p3", "vibre") - 0.1; T_50 = wt("p3", "cinquante") - 0.1
T_13 = line_t["y2"]; T_AUCUN = wt("y2", "aucun") - 0.1; T_FIN3 = line_t["y3"] + 0.25
T_ENC = wt("f2", "encore") - 0.2; T_MERCI = line_t["f3"]; T_NOIRQ = wt("f3", "pourquoi") - 0.1
words = []
for k, t0 in line_t.items(): words += [dict(w, s=w["s"] + t0 + 0.1, e=w["e"] + t0 + 0.1, line=k) for w in REL[k]]
ST = {k: E.still(NEW + p) for k, p in (("street", "n1hd/street_0001.png"), ("street2", "n1hd/street2_0001.png"), ("entry", "lvhd/entry_0001.png"), ("stairs", "ei3hd/stairsup_0001.png"),
                                       ("land", "n1hd/land_0001.png"), ("landbag", "lvhd/landing_0001.png"), ("appt", "n1hd/appt_0001.png"),
                                       ("closedbag", "n1hd/closedbag_0001.png"), ("closed", "n1hd/closed_0001.png"), ("wide", "n1hd/wide_0001.png"))}
SW, SH = ST["entry"].size
PI = json.load(open(NEW + "lvhd/entry_pos.json"))
PURPLE = (91, 51, 201)
LAMPS = ((SW * 0.2, SH * 0.6), (SW * 0.79, SH * 0.5))
DOOR = (int(SW * 0.372), int(SH * 0.38), int(SW * 0.615), int(SH * 0.668))


_LUT = {}
def fast_grade(im, i, exp=0.35, warm=True, glow=True):
    """Same look as E.night_grade, about four times faster: exposure and bloom in float, then the whole colour
    transform (desaturation that spares red, filmic curve, split toning) as one 3D lookup table, then vignette and grain."""
    from PIL import ImageFilter as IF
    key = (warm, None if glow else exp)
    if key not in _LUT:
        n = 33; g_ = np.linspace(0, 1, n, dtype=np.float32); b_, gg, r_ = np.meshgrid(g_, g_, g_, indexing="ij"); a = np.stack([r_, gg, b_], -1).reshape(-1, 3)
        if not glow: a = a * (2 ** exp)
        r, g, b = a[:, 0], a[:, 1], a[:, 2]; red = np.clip(((r - np.maximum(g, b)) / np.maximum(r, 1e-3) - 0.45) * 4, 0, 1)[:, None]
        lum = a @ G.LUMA; out = a * 0.6 + lum[:, None] * 0.4; out = out * (1 - red) + a * red; out = G.filmic(np.clip(out, 0, 1), 1.25); l_ = (out @ G.LUMA)[:, None]
        out = out + (1 - l_) * np.array([-0.025, 0.006, 0.03]) + l_ * (np.array([0.05, 0.015, -0.03]) if warm else np.array([0.02, 0.01, -0.01]))
        out = out * (np.array([1.04, 0.98, 0.9]) if warm else np.array([0.92, 0.99, 1.06]))
        _LUT[key] = IF.Color3DLUT(n, np.clip(out, 0, 1).astype(np.float32).ravel().tolist())
    if glow:
        a = E.bloom(np.asarray(im.convert("RGB")).astype(np.float32) * np.float32(2 ** exp / 255)); im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    out = np.asarray(im.convert("RGB").filter(_LUT[key])).astype(np.float32)
    if "v" not in _LUT: _LUT["v"] = np.clip(1.12 - G.RR * 0.5, 0.35, 1).astype(np.float32)[..., None]
    out = out * _LUT["v"] + (np.random.default_rng(i).normal(0, 0.015 * 255, (H // 2, W // 2, 1)).astype(np.float32)).repeat(2, 0).repeat(2, 1)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


@functools.lru_cache(maxsize=4)
def soft(name, r=5): return ST[name].filter(ImageFilter.GaussianBlur(r))


def amp(key, t, gain=6):
    a = VO_A[key]; i0 = int((t - line_t[key]) * VSR)
    return float(np.abs(a[max(0, i0):max(0, i0) + 1470]).mean() * gain) if 0 <= i0 < len(a) else 0.0
def xf(a, b, q): return a if q <= 0 else (b if q >= 1 else Image.blend(a, b, float(q * q * (3 - 2 * q))))
def cl(x): return float(np.clip(x, 0, 1))
def ease(x): x = cl(x); return x * x * (3 - 2 * x)
def blink(t, ph=0.0): return ((t + ph + 1.2) % 3.4) < 0.11


_LIT = {}
def put(base, sp, cx, foot, shadow=True, mul=None, rim=None):
    """Composite a sprite on a still (feet at `foot`), with a contact shadow; mul darkens it to the set, rim adds a lit edge."""
    im = base.convert("RGB").copy(); key = (id(sp), tuple(round(float(v), 3) for v in mul) if mul else None, rim)
    if key in _LIT: sp = _LIT[key][1]                                 # the same drawing under the same light: lit once
    else:
        src = sp
        if mul: sp = E.tint(sp, mul)
        if rim and (len(rim) < 3 or rim[2] > 0.02) and rim[1] != 0: sp = E.rim_light(sp, rim[0], rim[1], rim[2] if len(rim) > 2 else 1.0, blur=7)
        if len(_LIT) > 24: _LIT.pop(next(iter(_LIT)))
        _LIT[key] = (src, sp)
    if shadow and foot < im.height + 40:                             # only the patch under the feet is touched
        w_, h_ = int(sp.width * 0.8), int(sp.height * 0.12); x0, y0 = int(cx - w_ / 2), int(foot - h_ / 2); sh = Image.new("L", (w_, h_), 0)
        ImageDraw.Draw(sh).ellipse((w_ * 0.12, h_ * 0.25, w_ * 0.88, h_ * 0.7), fill=150); im.paste((0, 0, 0), (x0, y0), sh.filter(ImageFilter.GaussianBlur(max(2, sp.height * 0.012))))
    im.paste(sp, (int(cx - sp.width / 2), int(foot - sp.height)), sp)
    return im


# ---------------------------------------------------------------- shots in the 3D sets
def _facade_plate():
    """The painted wide shot of 27 rue des Lilas, built once."""
    global _FAC
    if _FAC is None:
        im = Image.new("RGB", (SW, SH), (7, 9, 18)); d = ImageDraw.Draw(im)
        for y in range(0, SH, 4): d.rectangle((0, y, SW, y + 4), fill=(int(7 + 10 * y / SH), int(9 + 11 * y / SH), int(18 + 22 * y / SH)))
        rg = np.random.default_rng(4)
        for _ in range(90): x, y = rg.integers(0, SW), rg.integers(0, int(SH * 0.5)); d.point((x, y), fill=(150, 160, 190))
        for bx, bw, bh, c in ((-40, 300, 0.52, 16), (1050, 320, 0.6, 14)): d.rectangle((bx, SH * (0.9 - bh), bx + bw, SH * 0.9), fill=(c, c + 1, c + 8))
        x0, x1, y0, y1 = int(SW * 0.2), int(SW * 0.82), int(SH * 0.1), int(SH * 0.86)
        d.rectangle((x0, y0, x1, y1), fill=(26, 27, 38)); d.rectangle((x0, y0, x1, y0 + 26), fill=(36, 37, 50)); d.rectangle((x1 - 22, y0, x1, y1), fill=(18, 19, 28))
        cols, rows = 5, 9; cw = (x1 - x0 - 60) / cols; rh = (y1 - y0 - 330) / rows
        for r in range(rows):
            for c in range(cols):
                wx, wy = x0 + 30 + c * cw + 22, y0 + 60 + r * rh + 18; lit = (r, c) == (6, 3)
                d.rectangle((wx - 5, wy - 5, wx + cw - 39, wy + rh - 31), fill=(14, 15, 22))
                d.rectangle((wx, wy, wx + cw - 44, wy + rh - 36), fill=(255, 196, 110) if lit else (9 + int(rg.integers(0, 6)), 11, 20 + int(rg.integers(0, 8))))
                if not lit: d.line((wx + (cw - 44) / 2, wy, wx + (cw - 44) / 2, wy + rh - 36), fill=(20, 22, 32), width=4)
                else:
                    d.line((wx + (cw - 44) / 2, wy, wx + (cw - 44) / 2, wy + rh - 36), fill=(120, 80, 40), width=5); _FACW[:] = [(wx + (cw - 44) / 2) / SW, (wy + (rh - 36) / 2) / SH]
                    d.ellipse((wx + 30, wy + 34, wx + 78, wy + 82), fill=(10, 8, 12)); d.rounded_rectangle((wx + 18, wy + 78, wx + 90, wy + rh - 36), 18, fill=(10, 8, 12))       # someone standing at the window
        dx = SW * 0.5; d.rectangle((dx - 70, y1 - 230, dx + 70, y1), fill=(12, 12, 16)); d.rectangle((dx - 56, y1 - 216, dx + 56, y1), fill=(70, 56, 38)); d.rectangle((dx - 46, y1 - 250, dx + 46, y1 - 238), fill=(255, 214, 150))
        d.rectangle((dx + 96, y1 - 150, dx + 120, y1 - 104), fill=(120, 180, 230))
        d.rectangle((0, y1, SW, SH), fill=(14, 15, 22)); d.rectangle((0, y1, SW, y1 + 16), fill=(40, 41, 52))
        d.rectangle((150, y1 - 560, 162, y1), fill=(10, 10, 14)); d.rectangle((150, y1 - 560, 250, y1 - 548), fill=(10, 10, 14)); d.ellipse((222, y1 - 552, 262, y1 - 530), fill=(255, 220, 160))
        im = E.spill(im, _FACW[0] * SW, _FACW[1] * SH, 230, 200, (255, 170, 80), 0.5); im = E.spill(im, 242, y1 - 300, 300, 420, (255, 200, 130), 0.2); im = E.spill(im, dx, y1 - 60, 260, 200, (255, 190, 120), 0.3)
        _FAC = im
    return _FAC


_FAC = None; _FACW = [0.5, 0.5]


def intercom_ins(t, t0):
    """The intercom, close: a steel plate, four names. Number 13 is lit, and the name on it is yours."""
    global _ICOM
    if _ICOM is None:
        im = E.paper_tex(W, H, (64, 68, 78), fiber=0.02, seed=9).convert("RGB"); a = np.asarray(im).astype(np.float32)
        a += np.random.default_rng(2).normal(0, 5, (H, 1, 1)).repeat(W, 1); im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((150, 330, 930, 1560), 30, fill=(96, 100, 112), outline=(30, 32, 38), width=8)
        d.rounded_rectangle((230, 400, 850, 640), 16, fill=(6, 12, 20)); d.text((540, 480), "27 RUE DES LILAS", font=E.fI("Bold", 44), fill=(150, 215, 255), anchor="mm"); d.text((540, 560), "choisissez un nom", font=ImageFont.truetype(E.MONO, 30), fill=(90, 150, 200), anchor="mm")
        d.ellipse((510, 350, 570, 390), fill=(8, 8, 10)); d.ellipse((530, 362, 550, 378), fill=(40, 50, 80))
        for q in range(7): d.rounded_rectangle((300, 690 + q * 18, 780, 698 + q * 18), 4, fill=(26, 28, 34))
        _ICOM = im
    im = _ICOM.copy(); d = ImageDraw.Draw(im); lit = cl((t - T_NOM) / 0.15); press = t >= T_SONNE - 0.12
    for q, (num, name) in enumerate((("11", "ROUSSEL"), ("12", "—"), ("13", "TOI"), ("14", "DIALLO"))):
        y = 860 + q * 150; me = q == 2
        d.ellipse((230, y, 330, y + 100), fill=(190, 192, 200) if not (me and press) else (120, 122, 130), outline=(40, 42, 50), width=6)
        col = (252, 240, 210) if not me else tuple(int(a_ + (b_ - a_) * lit) for a_, b_ in zip((252, 240, 210), (255, 250, 236)))
        d.rounded_rectangle((370, y + 6, 850, y + 94), 10, fill=col, outline=(40, 42, 50), width=5)
        d.text((400, y + 50), num, font=ImageFont.truetype(E.MONO, 44), fill=(60, 60, 66), anchor="lm")
        d.text((500, y + 50), name, font=E.fI("Bold", 52), fill=(205, 24, 24) if me and lit > 0.5 else (30, 30, 36), anchor="lm")
    if lit > 0: im = E.spill(im, 610, 860 + 300 + 50, 330, 110, (255, 220, 150), 0.1 * lit)
    q = ease((t - (T_SONNE - 0.9)) / 0.7); fx, fy = 280 + (1 - q) * 380, 1215 + (1 - q) * 620 - (8 if press else 0)             # his finger comes up to the button
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.line((fx + 420, fy + 700, fx + 150, fy + 250), fill=(22, 18, 34, 255), width=196); ld.line((fx + 420, fy + 700, fx + 150, fy + 250), fill=T2.HOOD, width=176)
    ld.line((fx + 190, fy + 318, fx + 168, fy + 280), fill=T2.REDB, width=178)
    ld.line((fx + 150, fy + 250, fx, fy), fill=(22, 18, 34, 255), width=92); ld.ellipse((fx - 46, fy - 46, fx + 46, fy + 46), fill=(22, 18, 34, 255))
    ld.line((fx + 150, fy + 250, fx, fy), fill=T2.SKIN, width=74); ld.ellipse((fx - 37, fy - 37, fx + 37, fy + 37), fill=T2.SKIN); ld.ellipse((fx + 60, fy + 150, fx + 240, fy + 330), fill=T2.SKIN, outline=(22, 18, 34, 255), width=9)
    im = im.convert("RGBA"); im.alpha_composite(lay); im = im.convert("RGB")
    z = 1.0 + 0.06 * cl((t - t0) / 5); cw, ch = W / z, H / z
    return im.transform((W, H), Image.EXTENT, (540 - cw / 2, 1010 - ch / 2, 540 + cw / 2, 1010 + ch / 2), Image.BICUBIC)
_ICOM = None


@functools.lru_cache(maxsize=4)
def _bag(h):
    s = h / 250; im = Image.new("RGBA", (int(220 * s), h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); o = (22, 18, 34, 255)
    d.rounded_rectangle((10 * s, 40 * s, 210 * s, 246 * s), 8 * s, fill=T2.BAG, outline=o, width=int(8 * s)); d.rectangle((14 * s, 44 * s, 206 * s, 78 * s), fill=T2.BAG_D)
    d.arc((70 * s, 4 * s, 150 * s, 80 * s), 180, 360, fill=o, width=int(8 * s))
    d.rectangle((60 * s, 112 * s, 160 * s, 196 * s), fill=(244, 242, 236, 255)); d.rectangle((72 * s, 126 * s, 130 * s, 138 * s), fill=T2.REDB); d.rectangle((72 * s, 152 * s, 148 * s, 158 * s), fill=(120, 120, 126, 255)); d.rectangle((72 * s, 170 * s, 116 * s, 176 * s), fill=(120, 120, 126, 255))
    return im


def shoes(im):
    d = ImageDraw.Draw(im)
    for x in (0.462, 0.508):
        cx, cy = SW * x, SH * 0.668; d.rounded_rectangle((cx - 15, cy - 13, cx + 15, cy + 9), 8, fill=(22, 18, 34)); d.rounded_rectangle((cx - 11, cy - 10, cx + 11, cy + 6), 6, fill=(236, 236, 232))
    return im


def door_bg(t, t0, t1, z=1.75):
    im = ST["land"]; cw, ch = SW / 1.2 / z, SH / 1.2 / z; cx, cy = SW * 0.44 + np.sin(t * 0.9) * 1.5, SH * 0.52 + np.cos(t * 0.7) * 1.5
    return im.transform((W, H), Image.EXTENT, (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))


def hand_shot(t, t0, t1):
    """The door, close. An arm comes out of the light: his sleeve, his hand, his red bracelet, a 20 euro note."""
    im = lit_door(door_bg(t, t0, t1)).convert("RGBA"); r = ease((t - T_MAIN) / 0.6)
    if r > 0:
        hd = T2.hand_out(700, bill=t >= L_("dv") - 0.1, reach=0.3 + 0.7 * r).resize((1050, 450), Image.LANCZOS)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.paste(hd, (int(HX0 + 8 * np.sin(t * 2.2)), int(830 + 6 * np.sin(t * 1.7)))); im.alpha_composite(lay)
    im = im.convert("RGB")
    if t >= T_BRAC: im = E.spill(im, HX0 + 345, 1055, 110, 150, (255, 40, 30), 0.25 * cl((t - T_BRAC) / 0.2))
    return im
HX0 = 120


def take_shot(t):
    """You take the note. His fingers close on your wrist."""
    im = lit_door(door_bg(t, 0, 1, z=1.85), 590, 880).convert("RGBA"); q = ease((t - line_t["x1"]) / 0.7); g = ease((t - T_DOIGTS) / 0.22)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); o = (22, 18, 34, 255); y = 1075; hx = -300 + 560 * q
    ax, ay = hx - 520, y + 760; ux, uy = (hx - 40 - ax), (y + 40 - ay); wx, wy = ax + ux * 0.86, ay + uy * 0.86             # your arm, from the bottom left; the wrist
    d.line((ax, ay, hx - 40, y + 40), fill=o, width=186); d.line((ax, ay, hx - 40, y + 40), fill=T2.HOOD, width=166)
    d.line((wx, wy, wx + ux * 0.035, wy + uy * 0.035), fill=T2.REDB, width=168)                                          # your bracelet
    d.ellipse((hx - 80, y - 74, hx + 76, y + 74), fill=T2.SKIN, outline=o, width=10)
    if g > 0.5: d.rounded_rectangle((hx - 30, y - 120, hx + 150, y - 30), 10, fill=(96, 132, 196, 255), outline=o, width=8); d.ellipse((hx - 80, y - 74, hx + 76, y + 74), fill=T2.SKIN, outline=o, width=10)
    hd = T2.hand_out(700, bill=g <= 0.5, reach=1.0).resize((1050, 450), Image.LANCZOS)
    px0, py0 = HX0 + 40, 850; px1, py1 = wx - 279 - 20, wy - 225 - 30                                                      # his hand leaves the note and lands on your wrist
    im.alpha_composite(lay); pos = (int(px0 + (px1 - px0) * g), int(py0 + (py1 - py0) * g)); lay2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay2.paste(hd, pos); im.alpha_composite(lay2)
    im = im.convert("RGB")
    if g > 0: im = E.spill(im, wx, wy, 260, 220, (255, 30, 20), 0.25 * g)
    return im


def appt_shot(t, t0, t1):
    """Flat 13. A table under one lamp. Thirteen delivery bags, all with your name. And in the dark behind them: him."""
    im = ST["appt"].copy(); e = cl((t - T_AUCUN) / 0.4)
    if e > 0:
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); cx, cy = SW * 0.5, SH * 0.335; a = int(235 * e)
        for s_ in (-1, 1): d.ellipse((cx + s_ * 70 - 44, cy - 40, cx + s_ * 70 + 44, cy + 40), fill=(250, 250, 255, a))
        d.chord((cx - 104, cy + 40, cx + 104, cy + 150), 10, 170, fill=(250, 250, 255, a))
        for q in range(-3, 4): d.line((cx + q * 26, cy + 90, cx + q * 26, cy + 150), fill=(8, 8, 14, a), width=5)
        im = Image.alpha_composite(im.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(1.2))).convert("RGB")
    return E.view(im, t, t0, t1, 1.0, 1.22, 0.5, 0.42, drift=0.5)


# ---------------------------------------------------------------- the phone
def _phone(sc, t, t0, vib_until=0.0, zoom=1.24, vib_at=None):
    vib = int(np.sin(t * 90) * 6) if 0 <= (t - t0) < vib_until or (vib_at is not None and 0 <= t - vib_at < 0.45) else 0
    im = E.phone(sc.convert("RGB"), vib); z = zoom + 0.05 * min(1.0, (t - t0) / 4); cw, ch = W / z, H / z; cx_, cy_ = 540, E.PY0 + 425
    return im.transform((W, H), Image.EXTENT, (cx_ - cw / 2, cy_ - ch / 2, cx_ + cw / 2, cy_ + ch / 2), Image.BICUBIC)
PSW, PSH = E.PX1 - E.PX0, E.PY1 - E.PY0


@functools.lru_cache(maxsize=2)
def _avatar(sz):
    c = T2.char(900); f = c.crop((315 - 190, 60, 315 + 190, 440)).resize((sz, sz), Image.LANCZOS)
    av = Image.new("RGBA", (sz, sz), (60, 66, 96, 255)); av.alpha_composite(f); m = Image.new("L", (sz, sz), 0); ImageDraw.Draw(m).ellipse((0, 0, sz - 1, sz - 1), fill=255); av.putalpha(m); return av


def _app(clock):
    sc = Image.new("RGBA", (PSW, PSH), (244, 245, 248, 255)); d = ImageDraw.Draw(sc)
    d.rectangle((0, 0, PSW, 150), fill=PURPLE); d.text((70, 52), clock, font=E.fI("SemiBold", 30), fill=(255, 255, 255)); d.text((PSW / 2, 110), "NUIT EXPRESS", font=E.fI("Bold", 40), fill=(255, 255, 255), anchor="mm")
    return sc, d


def _banner(sc, u, title, body):
    if u <= 0: return
    b = Image.new("RGBA", (PSW - 30, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(b); bd.rounded_rectangle((0, 0, b.width - 1, 149), 30, fill=(28, 28, 36, 246))
    bd.ellipse((20, 30, 110, 120), fill=(230, 120, 150, 255)); bd.text((65, 75), "M", font=E.fI("Bold", 50), fill=(255, 255, 255), anchor="mm")
    bd.text((130, 46), title, font=E.fI("Bold", 30), fill=(255, 255, 255), anchor="lm"); f = E.fI("Regular", 27)
    for k, ln in enumerate(body): bd.text((130, 86 + k * 34), ln, font=f, fill=(225, 228, 236), anchor="lm")
    sc.alpha_composite(b, (15, int(-160 + 190 * (1 - (1 - u) ** 3))))


def lock_screen(t):
    """Frame 0: his phone, locked, in the dark. 02:14. Then the notification drops in."""
    sc = Image.new("RGBA", (PSW, PSH), (14, 12, 34, 255)); d = ImageDraw.Draw(sc)
    g = Image.new("RGBA", (PSW, PSH), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((-100, 300, PSW + 100, PSH + 300), fill=(70, 46, 160, 150)); sc.alpha_composite(g.filter(ImageFilter.GaussianBlur(90))); d = ImageDraw.Draw(sc)
    d.text((PSW / 2, 150), "mardi 17 novembre", font=E.fI("SemiBold", 30), fill=(225, 225, 240), anchor="mm"); d.text((PSW / 2, 270), "2:14", font=E.fI("Bold", 170), fill=(255, 255, 255), anchor="mm")
    u = cl((t - 0.05) / 0.25); u = 1 - (1 - u) ** 3                  # the notification is there from the first frame: who is the client?
    if u > 0:
        b = Image.new("RGBA", (PSW - 40, 170), (0, 0, 0, 0)); bd = ImageDraw.Draw(b); bd.rounded_rectangle((0, 0, b.width - 1, 169), 30, fill=(40, 38, 58, 240))
        bd.rounded_rectangle((22, 30, 108, 116), 20, fill=PURPLE); bd.ellipse((44, 50, 86, 92), fill=(246, 244, 255)); bd.ellipse((56, 44, 98, 86), fill=PURPLE)
        bd.text((130, 46), "NUIT EXPRESS · maintenant", font=E.fI("SemiBold", 25), fill=(190, 190, 210), anchor="lm"); bd.text((130, 90), "Nouvelle commande · 2:14", font=E.fI("Bold", 32), fill=(255, 255, 255), anchor="lm")
        bd.text((130, 132), "Client : ???", font=E.fI("Regular", 30), fill=(225, 225, 240), anchor="lm")
        sc.alpha_composite(b, (20, int(380 + 60 * (1 - u))))
    return sc


def order_screen(t):
    """The order: the customer has your name and your face, the tip is exactly what you are short of, and one line says
    it must be handed over in person. Then his mother's message slides down."""
    sc, d = _app("02:14"); card = Image.new("RGBA", (PSW - 50, 640), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    acc = t >= T_OK; cd.rounded_rectangle((0, 0, card.width - 1, 639), 30, fill=(255, 255, 255, 255), outline=(200, 25, 25, 255) if not acc else PURPLE + (255,), width=5)
    cd.text((34, 30), "NOUVELLE COMMANDE", font=E.fI("Bold", 32), fill=(200, 25, 25)); cd.text((card.width - 34, 34), "#0013", font=ImageFont.truetype(E.MONO, 28), fill=(120, 120, 130), anchor="ra")
    hl = cl((t - T_TOI0) / 0.12); ph = cl((t - T_PHOTO) / 0.15)
    cd.text((34, 130), "Client", font=E.fI("Regular", 28), fill=(120, 120, 130), anchor="lm")
    if hl > 0: cd.text((card.width - 150, 130), "TOI", font=E.fI("Bold", int(52 * (1 + 0.5 * (1 - hl)))), fill=(200, 25, 25), anchor="rm")
    else: cd.text((card.width - 34, 130), "• • •", font=E.fI("Bold", 40), fill=(170, 170, 180), anchor="rm")
    if ph > 0:
        av = _avatar(104); card.alpha_composite(av, (card.width - 138, 78)); cd.ellipse((card.width - 142, 74, card.width - 30, 186), outline=(200, 25, 25), width=5)
    cd.text((34, 254), "Adresse", font=E.fI("Regular", 28), fill=(120, 120, 130), anchor="lm"); cd.text((card.width - 34, 254), "27 rue des Lilas · 13", font=E.fI("Bold", 30), fill=(30, 30, 36), anchor="rm")
    tp = cl((t - T_TIP) / 0.2); pul = 1 + 0.06 * np.sin(t * 9) * (1 if L_("h3") < t < L_("h4") else 0)
    cd.text((34, 316), "Pourboire", font=E.fI("Regular", 28), fill=(120, 120, 130), anchor="lm")
    if tp > 0:
        cd.rounded_rectangle((card.width - 250, 280, card.width - 28, 352), 20, fill=(255, 236, 236)); cd.text((card.width - 139, 316), "+18,50 €", font=E.fI("Bold", int(40 * pul)), fill=(200, 25, 25), anchor="mm")
    cd.rounded_rectangle((28, 392, card.width - 28, 462), 16, fill=(240, 238, 250)); cd.ellipse((44, 408, 82, 446), fill=PURPLE); cd.text((63, 427), "!", font=E.fI("Bold", 28), fill=(255, 255, 255), anchor="mm")
    cd.text((98, 427), "Remise en main propre obligatoire", font=E.fI("SemiBold", 25), fill=(60, 40, 130), anchor="lm")
    press = 0.0 < t - T_OK < 0.15
    cd.rounded_rectangle((34, 520 + (4 if press else 0), card.width - 34, 600 + (4 if press else 0)), 40, fill=PURPLE if not acc else (40, 170, 90)); cd.text((card.width / 2, 560 + (4 if press else 0)), "ACCEPTER" if not acc else "ACCEPTÉE  ✓", font=E.fI("Bold", 34), fill=(255, 255, 255), anchor="mm")
    sc.alpha_composite(card, (25, 190))
    if hl > 0 and t < L_("h3") + 1.5:                                 # the red tag, as the reference videos do on their phone screens
        tg = Image.new("RGBA", (PSW, 90), (0, 0, 0, 0)); td = ImageDraw.Draw(tg); f = E.fI("Bold", 27); w_ = td.textlength("C'EST TON NOM. ET TA PHOTO.", font=f) + 40
        td.rounded_rectangle((PSW / 2 - w_ / 2, 20, PSW / 2 + w_ / 2, 70), 12, fill=(200, 25, 25)); td.text((PSW / 2, 45), "C'EST TON NOM. ET TA PHOTO.", font=f, fill=(255, 255, 255), anchor="mm")
        sc.alpha_composite(tg, (0, 340 + int(20 * (1 - hl))))
    _banner(sc, cl((t - (L_("h4") + 0.05)) / 0.3) * cl((L_("h5") + 0.1 - t) / 0.25), "Maman", ["Rentre, il est tard.", "Je t'ai gardé une assiette."])
    return sc


def status_screen(t, kind):
    """'fail': order not handed over, tip cancelled. 'done': handed over, +18,50, the night is paid. 'new': the same address again, 50 euros."""
    sc, d = _app({"fail": "02:33", "done": "02:36", "new": "02:37"}[kind])
    if kind == "fail":
        d.rounded_rectangle((25, 200, PSW - 25, 600), 30, fill=(255, 255, 255), outline=(200, 25, 25), width=6); d.ellipse((PSW / 2 - 60, 240, PSW / 2 + 60, 360), fill=(200, 25, 25)); d.text((PSW / 2, 300), "!", font=E.fI("Bold", 84), fill=(255, 255, 255), anchor="mm")
        d.text((PSW / 2, 420), "COMMANDE NON REMISE", font=E.fI("Bold", 36), fill=(200, 25, 25), anchor="mm"); d.text((PSW / 2, 480), "Le sac n'a pas été remis", font=E.fI("Regular", 28), fill=(90, 90, 100), anchor="mm"); d.text((PSW / 2, 520), "en main propre.", font=E.fI("Regular", 28), fill=(90, 90, 100), anchor="mm")
        d.rounded_rectangle((25, 630, PSW - 25, 740), 24, fill=(255, 236, 236)); d.text((50, 685), "Pourboire", font=E.fI("Regular", 30), fill=(120, 120, 130), anchor="lm"); d.text((PSW - 50, 685), "+18,50 €", font=E.fI("Bold", 38), fill=(170, 170, 176), anchor="rm"); d.line((PSW - 230, 685, PSW - 44, 685), fill=(200, 25, 25), width=6)
    elif kind == "done":
        d.rounded_rectangle((25, 200, PSW - 25, 560), 30, fill=(255, 255, 255), outline=(40, 170, 90), width=6); d.ellipse((PSW / 2 - 60, 236, PSW / 2 + 60, 356), fill=(40, 170, 90)); d.text((PSW / 2, 296), "✓", font=E.fI("Bold", 80), fill=(255, 255, 255), anchor="mm")
        d.text((PSW / 2, 416), "COMMANDE REMISE", font=E.fI("Bold", 38), fill=(30, 130, 70), anchor="mm"); d.text((PSW / 2, 490), "+18,50 €", font=E.fI("Bold", 60), fill=(30, 30, 36), anchor="mm")
        v = 41.5 + 18.5 * ease((t - T_60) / 0.7); d.rounded_rectangle((25, 590, PSW - 25, 800), 24, fill=(240, 238, 250)); d.text((50, 640), "Ce soir", font=E.fI("Regular", 30), fill=(90, 80, 130), anchor="lm")
        d.text((PSW - 50, 640), f"{v:.2f} €".replace(".", ","), font=E.fI("Bold", 46), fill=(60, 40, 130), anchor="rm"); d.rounded_rectangle((50, 700, PSW - 50, 724), 12, fill=(214, 208, 240)); d.rounded_rectangle((50, 700, 50 + (PSW - 100) * v / 60, 724), 12, fill=PURPLE)
        if v >= 59.99: d.text((PSW / 2, 764), "Objectif atteint : 60 €", font=E.fI("SemiBold", 26), fill=(60, 40, 130), anchor="mm")
    else:
        d.rounded_rectangle((30, 180, PSW - 30, 250), 16, fill=(232, 232, 238)); d.text((54, 215), "Commande #0013 remise · 02:36", font=E.fI("Medium", 24), fill=(120, 120, 130), anchor="lm")
        u = cl((t - T_VIB) / 0.25); u = 1 - (1 - u) ** 3
        if u > 0:
            card = Image.new("RGBA", (PSW - 50, 520), (0, 0, 0, 0)); cd = ImageDraw.Draw(card); cd.rounded_rectangle((0, 0, card.width - 1, 519), 30, fill=(255, 255, 255, 255), outline=(200, 25, 25, 255), width=5)
            cd.text((34, 30), "NOUVELLE COMMANDE", font=E.fI("Bold", 32), fill=(200, 25, 25)); cd.text((card.width - 34, 34), "#0014", font=ImageFont.truetype(E.MONO, 28), fill=(120, 120, 130), anchor="ra")
            for k, (a_, b_, red) in enumerate((("Client", "TOI", True), ("Adresse", "Même adresse · 13", t >= wt("p3", "même") - 0.1), ("Pourboire", "+50,00 €", t >= T_50))):
                cd.text((34, 130 + k * 82), a_, font=E.fI("Regular", 28), fill=(120, 120, 130), anchor="lm"); cd.text((card.width - 34, 130 + k * 82), b_, font=E.fI("Bold", 36 if k != 2 else 46), fill=(200, 25, 25) if red else (30, 30, 36), anchor="rm")
            cd.rounded_rectangle((34, 400, card.width - 34, 480), 40, fill=PURPLE); cd.text((card.width / 2, 440), "ACCEPTER", font=E.fI("Bold", 34), fill=(255, 255, 255), anchor="mm")
            sc.alpha_composite(card, (25, int(290 + 220 * (1 - u))))
    return sc


def mum_screen(t):
    """02:51. Her messages. The last two were sent to someone who is already home."""
    sc = Image.new("RGBA", (PSW, PSH), (12, 13, 20, 255)); d = ImageDraw.Draw(sc)
    d.rectangle((0, 0, PSW, 150), fill=(24, 25, 36)); d.text((70, 52), "02:51", font=E.fI("SemiBold", 30), fill=(255, 255, 255)); d.ellipse((40, 86, 96, 142), fill=(230, 120, 150)); d.text((68, 114), "M", font=E.fI("Bold", 32), fill=(255, 255, 255), anchor="mm")
    d.text((116, 114), "Maman", font=E.fI("Bold", 36), fill=(255, 255, 255), anchor="lm")
    def bub(y, lines, u, hot=False):
        if u <= 0: return
        f = E.fI("Regular", 38); w = max(d.textlength(l, font=f) for l in lines) + 56; hh = 34 + 50 * len(lines); yy = y + int(30 * (1 - u))
        d.rounded_rectangle((30, yy, 30 + w, yy + hh), 28, fill=(46, 48, 62) if not hot else (70, 30, 34), outline=(205, 24, 24) if hot else None, width=4)
        for k, l in enumerate(lines): d.text((58, yy + 42 + k * 50), l, font=f, fill=(240, 240, 246), anchor="lm")
    d.text((PSW / 2, 190), "02:14", font=E.fI("Regular", 22), fill=(110, 112, 126), anchor="mm"); bub(215, ["Rentre, il est tard.", "Je t'ai gardé une assiette."], 1.0)
    u1 = cl((t - T_ENC) / 0.2); u2 = cl((t - T_NOIRQ) / 0.2)
    if u1 > 0: d.text((PSW / 2, 392), "02:51", font=E.fI("Regular", 22), fill=(110, 112, 126), anchor="mm")
    bub(420, ["Merci d'être rentré,", "mon chéri."], cl((t - T_MERCI) / 0.2)); bub(580, ["Mais pourquoi tu restes", "dans le noir ?"], u2, hot=True)
    if t >= T_NOIRQ + 1.2 and int(t * 2.5) % 2 == 0: d.text((60, 780), "Maman écrit…", font=E.fI("Regular", 26), fill=(130, 132, 150), anchor="lm")
    return sc


# ---------------------------------------------------------------- the order slip, where the rules pile up
_REC = None
ROWS = (("COMMANDE", "#0013"), ("CLIENT", "TOI"), ("REMISE", "EN MAIN PROPRE"), ("POURBOIRE", "PAYÉ EN LIGNE"), ("OBJECTIF NUIT", "60,00 €"))
RULES = (["RÈGLE 1", "Ce que tu acceptes,", "tu le livres."], ["RÈGLE 2", "Ne prends rien", "de sa main."], ["RÈGLE 3", "Quand la nuit est", "payée : rentre."])
def receipt(t, t0, stage):
    """The printed slip. Each loss circles the line that warned you and adds a rule by hand, in red."""
    global _REC
    if _REC is None:
        w, h = 760, 1260; p = E.paper_tex(w, h, (248, 246, 240), fiber=0.03, seed=51); d = ImageDraw.Draw(p); fm = ImageFont.truetype(E.MONO, 28)
        d.ellipse((335, 30, 425, 120), fill=PURPLE); d.ellipse((366, 40, 434, 108), fill=(248, 246, 240))
        d.text((380, 164), "NUIT EXPRESS", font=E.fI("Bold", 50), fill=(30, 30, 34), anchor="mm"); d.text((380, 208), "livraison 22 h - 6 h", font=fm, fill=(110, 110, 116), anchor="mm")
        for k, (a_, b_) in enumerate(ROWS):
            y = 262 + k * 50; d.text((60, y), a_, font=fm, fill=(110, 110, 116)); d.text((w - 60, y), b_, font=fm, fill=(200, 25, 25) if b_ == "TOI" else (30, 30, 34), anchor="ra")
        for x in range(60, w - 60, 22): d.line((x, 530, x + 11, 530), fill=(150, 150, 156), width=3)
        m = Image.new("L", (w, h), 255); md = ImageDraw.Draw(m)
        for x in range(0, w, 40): md.polygon([(x, h), (x + 20, h - 26), (x + 40, h)], fill=0)
        p.putalpha(m); _REC = p
    fr = _REC.copy(); d = ImageDraw.Draw(fr); f = ImageFont.truetype(E.HAND, 58); rg = np.random.default_rng(3); w = fr.width
    def circle(row, n):                                               # a hand-drawn loop around the printed line that said it
        y = 262 + row * 50 + 16; pts = [(w / 2 + (w / 2 - 34) * np.cos(a_) + rg.normal(0, 1.5), y + 30 * np.sin(a_) + rg.normal(0, 1.2)) for a_ in np.linspace(-2.6, 3.9, 60)]
        if n > 1: d.line(pts[:n], fill=(205, 24, 24), width=5, joint="curve")
    def write(lines, y, n):
        for ln in lines:
            part = ln[:max(0, n)]; n -= len(ln); x = 60
            for ch in part: d.text((x + rg.normal(0, 0.8), y + rg.normal(0, 1.2)), ch, font=f, fill=(205, 24, 24)); x += d.textlength(ch, font=f)
            y += 64
    for s in range(1, stage + 1):
        live = s == stage; circle(s + 1, int(np.clip((t - t0 - 0.15) * 90, 0, 60)) if live else 60)
        write(RULES[s - 1], 552 + (s - 1) * 216, int(np.clip((t - t0 - 0.9) * 24, 0, 99)) if live else 99)
    bg = ST["landbag"].resize((W, H)).filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.5)).convert("RGBA")
    fr = fr.resize((int(fr.width * 0.84), int(fr.height * 0.84)), Image.LANCZOS).rotate(-2.5 + np.sin(t * 8) * 0.2, expand=True, resample=Image.BICUBIC)
    E.drop_shadow(bg, fr, (int(W / 2 - fr.width / 2), int(860 - fr.height / 2)), blur=26, off=(14, 26), alpha=170)
    im = E.torch(bg, 540 + np.sin(t * 1.3) * 50, 900 + np.cos(t * 1.1) * 50, 1250, 0.5, 1.12)
    cy = 0.48 + 0.035 * (stage - 1) * ease((t - t0 - 0.6) / 0.8)       # the camera follows the hand down the slip
    return E.view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t0 + 7, 1.0, 1.06, 0.5, cy, drift=0.4)


# ---------------------------------------------------------------- overlays
def buttons(im, labels, t, t0, t1, pick=None, ab=False, title=None):
    d = ImageDraw.Draw(im); y = 400
    if title: d.text((540, 580), title, font=ImageFont.truetype(E.MONT, 58), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=(0, 0, 0))
    for n_, txt in enumerate(labels):
        x0 = 124 + n_ * 408; on = pick == txt; lab = (("A · ", "B · ")[n_] if ab else "") + txt; size = 40
        while d.textlength(lab, font=ImageFont.truetype(E.MONT, size)) > 350: size -= 2
        d.rounded_rectangle((x0, y, x0 + 388, y + 96), 48, fill=RED if on else (250, 250, 250), outline=RED, width=5); d.text((x0 + 194, y + 48), lab, font=ImageFont.truetype(E.MONT, size), fill=(255, 255, 255) if on else (30, 30, 34), anchor="mm")
    if pick is None and not ab and labels != C3: d.text((540, y + 190), "ÉCRIS TON CHOIX EN COMMENTAIRE", font=ImageFont.truetype(E.MONT, 34), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
    if pick is None and not ab:
        left = cl((t1 - t) / max(0.1, t1 - t0)); d.rounded_rectangle((124, y + 120, 920, y + 138), 9, fill=(30, 30, 34)); d.rounded_rectangle((124, y + 120, 124 + int(796 * left), y + 138), 9, fill=RED)


SEGS = None
def story(t):
    """(clock seconds, place, money): the clock is part of the story, so when the tape rewinds the clock goes back with it."""
    global SEGS
    if SEGS is None:
        s1 = 2 * 3600 + 31 * 60 + 40; c1 = s1 + (L_("w1") - L_("a1")); c2 = c1 + 60 + (L_("x1") - L_("m1")); c3 = c2 + 30 + (L_("y1") - L_("p1"))
        SEGS = [(0.0, 2 * 3600 + 14 * 60 + 7), (L_("a1"), s1), (L_("m1"), c1 + 60), (L_("p1"), c2 + 30), (L_("f1"), 2 * 3600 + 50 * 60 + 52)]
    t0, b = [s for s in SEGS if s[0] <= t][-1]; sec = b + (t - t0)
    place = ("RUE" if t < L_("a1") else "27 RUE DES LILAS" if t < L_("a2") else "HALL" if t < L_("m1") else "ESCALIER" if t < L_("m2") else "3e ÉTAGE · APPT 13" if t < L_("p3") else "ESCALIER" if t < L_("y1") else "APPT 13" if t < L_("f1") else "RUE")
    paid = (t >= T_60 and t < L_("y1")) or t >= L_("f1") or (L_("y1") <= t < t_rew3 + 0.9)
    money = 41.5 + 18.5 * ease((t - T_60) / 0.7) if L_("p2") <= t < L_("p3") else (60.0 if paid else 41.5)
    return sec, place, money


def hud(im, t):
    sec, place, money = story(t); d = ImageDraw.Draw(im); fs = ImageFont.truetype(E.MONT, 28)
    d.text((124, 232), "NUIT 1 · " + place, font=fs, fill=(235, 235, 238), stroke_width=3, stroke_fill=(0, 0, 0))
    s_ = int(sec); d.text((122, 266), f"{s_ // 3600:02d}:{s_ // 60 % 60:02d}:{s_ % 60:02d}", font=ImageFont.truetype(E.MONO, 62), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    col = (255, 60, 44) if money < 59.99 else (255, 255, 255)
    d.text((956, 232), "CE SOIR", font=fs, fill=(235, 235, 238), anchor="ra", stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((956, 272), f"{money:.2f} €".replace(".", ",") + " / 60 €", font=ImageFont.truetype(E.MONO, 38), fill=col, anchor="ra", stroke_width=4, stroke_fill=(0, 0, 0))
    d.rounded_rectangle((700, 326, 956, 338), 6, fill=(20, 20, 26)); d.rounded_rectangle((700, 326, 700 + int(256 * money / 60), 338), 6, fill=col)


def stamp(im, t, t0, txt="LIVRÉ", y=760, size=132):
    st = t - t0
    if st <= 0: return
    f = E.fI("Bold", size); wd = int(ImageDraw.Draw(im).textlength(txt, font=f)) + 110
    stp = Image.new("RGBA", (wd, 220), (0, 0, 0, 0)); sd = ImageDraw.Draw(stp)
    sd.rounded_rectangle((8, 8, wd - 8, 212), 16, outline=RED + (240,), width=14); sd.text((wd / 2, 110), txt, font=f, fill=RED + (240,), anchor="mm")
    s_ = 1.5 - 0.5 * min(1.0, st / 0.14); stp = stp.resize((int(wd * s_), int(220 * s_))).rotate(-9, expand=True, resample=Image.BICUBIC)
    im.paste(stp, (int(540 - stp.width / 2), int(y - stp.height / 2)), stp)


def smear(src, k):
    sx = {-2: 1.7, -1: 1.25}[k]; zi = src.resize((int(W * sx), H), Image.BILINEAR); o = (zi.width - W) // 2
    return zi.crop((o, 0, o + W, H))
def negative(src):
    a = np.asarray(src).astype(np.float32) / 255; l = np.clip((a @ G.LUMA) * 1.6, 0, 1)
    return Image.fromarray((np.stack([1 - l] * 3, -1) * 255).astype(np.uint8))


def rewind(i, t, t0, src):
    """A wrong choice: the tape runs backwards to the moment you chose. Black and white, tracking tears, and the clock goes back."""
    a = np.asarray(src).astype(np.float32) @ G.LUMA; rg = np.random.default_rng(i)
    for _ in range(9):
        y = int(rg.integers(0, H - 40)); hh = int(rg.integers(6, 34)); a[y:y + hh] = np.roll(a[y:y + hh], int(rg.integers(-140, 140)), axis=1) * 1.25
    a += rg.normal(0, 14, (H, W)); a[::3] *= 0.8
    im = Image.fromarray(np.clip(np.stack([a, a, a], -1), 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    d.text((124, 560), "◀◀ REW", font=ImageFont.truetype(E.MONO, 64), fill=(255, 255, 255))
    d.text((540, 1210), "TU RECOMMENCES.", font=ImageFont.truetype(E.MONT, 62), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=(0, 0, 0))
    return im


# ---------------------------------------------------------------- motion: one drawing per pose, smooth changes between poses
DEFP = dict(armL=(0.08, 0.1), armR=(0.08, 0.1), legs=(0.0, 0.0), lean=0.0, look=(0.0, 0.0), head=(0.0, 0.0), wide=1.0, brow=0.0)
@functools.lru_cache(maxsize=160)
def _char(h, items): return T2.char(h, **dict(items))
def hero(h, **kw):
    kw = {k: (tuple(round(float(x), 2) for x in v) if isinstance(v, tuple) else (round(v, 2) if isinstance(v, float) else v)) for k, v in kw.items()}
    hq = int(np.ceil(h / 250) * 250); sp = _char(hq, tuple(sorted(kw.items())))
    return sp if hq == int(h) else sp.resize((max(1, int(sp.width * h / hq)), int(h)), Image.LANCZOS)
def mixp(a, b, q):
    """Blend two poses: angles move, the rest (mouth, props) switches half-way."""
    if q <= 0: return a
    if q >= 1: return b
    out = {}
    for k in set(a) | set(b):
        va, vb = a.get(k, DEFP.get(k)), b.get(k, DEFP.get(k))
        if isinstance(va, tuple) and isinstance(vb, tuple): out[k] = tuple(round((x + (y - x) * q) * 20) / 20 for x, y in zip(va, vb))
        elif isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool) and not isinstance(vb, bool): out[k] = round((va + (vb - va) * q) * 20) / 20
        else: out[k] = vb if q >= 0.5 else va
        if out[k] is None: out.pop(k)
    return out
def walk(ph, amp=0.9):
    """A step cycle seen from the front or the back: one knee lifts while the other leg trails, the arms answer."""
    s = float(np.sin(2 * np.pi * ph)); r = lambda v: round(v * 12) / 12
    return dict(legs=(r(s * amp), r(-s * amp)), armL=(0.1, r(0.25 + 0.4 * max(0.0, -s) * amp)), armR=(0.1, r(0.25 + 0.4 * max(0.0, s) * amp)), lean=round(0.02 * s * amp, 2))
def bob(ph): return 0.5 - 0.5 * float(np.cos(4 * np.pi * ph))


def face_shot(t, t0, t1, still="street", scared=False):
    """Close on his face, lit from below by the phone. The first image of the video, and the last."""
    if scared: kw = dict(wide=1.3, brow=1.0, mouth="o", look=(0.0, 0.15), sweat=True); jx = np.sin(t * 34) * 3
    else:
        kw = mixp(dict(look=(0.0, 0.85), head=(0.0, 0.5), brow=0.2), dict(look=(0.0, 0.1), brow=0.6, wide=1.1), ease((t - T_LIV) / 0.3)); jx = 0
        kw.update(mouth="frown" if t > line_t["h1"] + dur["h1"] * 0.75 else "line", blink=blink(t))
    sp = hero(2500, **kw); bg = soft(still)
    im = put(bg, sp, SW * 0.47 + jx, SH * 1.275 + np.sin(t * 1.6) * 6, shadow=False, mul=(0.68, 0.7, 0.82), rim=((255, 190, 120), -14, 0.5))
    im = E.spill(im, SW * 0.47, SH * 0.78, 520, 330, (120, 160, 255), 0.1 + 0.02 * np.sin(t * 9))
    return E.view(im, t, t0, t1, 1.0, 1.07, 0.5, 0.47, drift=0.6)


def facade(t, t0, t1):
    """27 rue des Lilas from the street: every window dark but one. He rides in on his scooter, brakes, and looks up."""
    im = _facade_plate().copy(); y1 = int(SH * 0.86); u = cl((t - t0) / max(0.1, (t1 - t0) * 0.62)); p = 1 - (1 - u) ** 3; x = SW * (-0.16 + 0.5 * p)
    sp = T2.rider(330, spin=x / 43.0, up=ease((t - t0 - (t1 - t0) * 0.66) / 0.5)); gy = y1 + 92 + (np.sin(t * 23) * 2.5 * (1 - p)) - 6 * np.sin(np.pi * cl((u - 0.86) / 0.14)) * 0   # a little road buzz while he rolls
    dip = 5 * np.sin(np.pi * cl((u - 0.8) / 0.2))                      # the nose dips as he brakes
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((x - 150, gy - 14, x + 170, gy + 12), fill=(0, 0, 0, 150))
    lay.paste(sp.rotate(-dip * 0.5, resample=Image.BICUBIC), (int(x - sp.width * 0.47), int(gy - sp.height * 0.97)))
    im = Image.alpha_composite(Image.alpha_composite(im.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(8))), lay).convert("RGB")
    im = E.spill(im, x + 330, gy - 70, 240, 60, (255, 235, 190), 0.3 * (1 - 0.5 * p), poly=[(x + 150, gy - 150), (x + 560, gy - 230), (x + 560, gy + 10), (x + 150, gy - 120)])
    return E.view(im, t, t0, t1, 1.0, 1.1, 0.5, 0.58 - 0.12 * ease((t - t0) / (t1 - t0)), drift=0.5)


def entry_shot(t, t0, t1, mode):
    """In front of the door. mode: 'ring' (his back, finger on the button, the voice answers), 'ask' (he turns to us),
    'leave' (the bag stays on the step, he walks off), 'dark' (the hall locks, the light dies, something is behind him)."""
    base = ST["entry"]; px, py = PI["x"] * SW, PI["y"] * SH
    if mode == "ring":
        kw = mixp(dict(armR=(1.0, 1.5), armL=(0.1, 0.3), lean=0.06), dict(armR=(0.2, 0.4), armL=(0.1, 0.3), lean=-0.06), ease((t - (L_("iv") - 0.25)) / 0.35))
        sp = hero(1280, back=True, bag="L", **kw)
        im = put(base, sp, SW * 0.56, SH * 0.985 + np.sin(t * 1.7) * 3, mul=(0.8, 0.8, 0.9), rim=((255, 200, 140), 10, 0.6))
        a_ = max(amp("iv", t, 9), 0.25 * abs(np.sin(t * 7)) if T_SONNE < t < line_t["iv"] else 0.0); im = im.convert("RGBA")
        l = E.aa_layer(SW, SH); d = E.SD(l)
        for q in range(9):
            hh = 5 + 24 * min(1.0, a_) * abs(np.sin(q * 1.7 + t * 14)); d.rounded_rectangle((px - 44 + q * 11, py - hh, px - 38 + q * 11, py + hh), 3, fill=(20, 30, 40, 255))
        im.alpha_composite(E.aa_down(l)); im = E.spill(im, px, py, 300, 300, (120, 200, 255), 0.1 + 0.3 * min(1.0, a_))
        return E.view(im, t, t0, t1, 1.0, 1.1, 0.56, 0.5, drift=0.6)
    if mode == "ask":
        kw = mixp(dict(look=(0.8, 0.0), brow=0.6, armL=(0.1, 0.25), armR=(0.2, 0.4), lean=-0.04), dict(look=(0.0, 0.0), wide=1.25, brow=1.0, armL=(0.1, 0.25), armR=(0.3, 1.9), lean=-0.08), ease((t - t0) / 0.4))
        sp = hero(1280, mouth="wavy", bag="L", sweat=t > t0 + 0.3, blink=blink(t, 1.0), **kw)
        im = put(base, sp, SW * 0.5 + np.sin(t * 30) * 1.5, SH * 0.985, mul=(0.86, 0.86, 0.95), rim=((255, 200, 140), -10, 0.8))
        return E.view(im, t, t0, t1, 1.02, 1.12, 0.5, 0.52, drift=0.6)
    bagsp = _bag(250)
    if mode == "leave":
        im = put(base, bagsp, SW * 0.33, SH * 0.79, mul=(0.85, 0.82, 0.8))
        ph = (t - t0) / 0.9; p = cl((t - t0) / (t1 - t0)); g = 0.9 + 0.22 * p; kw = walk(ph); kw.update(armR=(0.3, 2.0))
        sp = hero(1300 * g, phone="R", look=(0.3, 0.6), mouth="smile" if t < we("w1") else "line", brow=-0.1, blink=blink(t), **kw)
        im = put(im, sp, SW * (0.5 + 0.1 * p), SH * (0.93 + 0.1 * p) - bob(ph) * 16 * g, mul=(0.84, 0.84, 0.95), rim=((255, 200, 140), -10, 0.7))
        return E.view(im, t, t0, t1, 1.0, 1.06, 0.5, 0.52, drift=0.5)
    q = ease((t - T_NOIR1) / 0.18); eyes = ease((t - (L_("w4") - 0.2)) / 0.35)                                       # dark: the lock, then the light
    im = put(base, bagsp, SW * 0.33, SH * 0.79, mul=(0.85, 0.82, 0.8))
    if eyes > 0:                                                    # behind him, in the dark hall: the other one rises into view
        dbl = T2.char(1500, dark=True); im = put(im, dbl, SW * 0.3, SH * (1.03 + 0.12 * (1 - eyes)), shadow=False)
    kw = mixp(dict(look=(0.3, 0.6), brow=0.2, armR=(0.3, 2.0), armL=(0.1, 0.2)), dict(look=(-0.9, 0.0), wide=1.3, brow=1.0, armR=(0.2, 0.6), armL=(0.1, 0.2), lean=0.08), ease((t - T_VERR) / 0.22))
    turned = t >= T_VERR + 0.1
    sp = hero(1320, mouth="o" if turned else "line", phone="R", sweat=turned, **kw)
    im = xf(im, Image.eval(im, lambda v: int(v * 0.16)), q)
    im = put(im, sp, SW * 0.62 + (np.sin(t * 31) * 2 if turned else 0), SH * 1.01, mul=tuple(np.array((0.84, 0.84, 0.95)) * (1 - 0.72 * q)), rim=((150, 190, 255), 12, 0.5 * q) if q > 0 else ((255, 200, 140), -10, 0.7))
    if q > 0: im = E.spill(im, px, py, 200, 200, (120, 200, 255), 0.25)
    return E.view(im, t, t0, t1, 1.0, 1.12, 0.5, 0.52, drift=0.6)


def stairs_shot(t, t0, t1, down=False):
    """The staircase. Going up: his back, a bag in his hand, and every landing going dark behind him."""
    base = ST["stairs"]; p = cl((t - t0) / (t1 - t0)); ph = (t - t0) / 0.92
    if not down:
        # Two wall lamps on the way up. Each one clicks off just after he has passed it, in time with the count of
        # the floors, and on "s'éteint" everything below him is black: only the light at the top is left.
        g = 1.0 - 0.45 * p; kw = walk(ph); kw.update(armR=(0.1, 0.25)); feet = SH * (1.0 - 0.3 * p)
        off = [ease((t - T_L1) / 0.08), ease((t - T_L2) / 0.08), ease((t - T_L3) / 0.1)]
        im = base
        for (lx_, ly_), o in zip(LAMPS, off[:2]):
            if o < 1:
                im = E.spill(im, lx_, ly_, 260, 330, (255, 190, 110), 0.5 * (1 - o)); d = ImageDraw.Draw(im); d.rounded_rectangle((lx_ - 16, ly_ - 34, lx_ + 16, ly_ + 34), 8, fill=tuple(int(40 + 215 * (1 - o) * c) for c in (1.0, 0.86, 0.6)))
            else: d = ImageDraw.Draw(im); d.rounded_rectangle((lx_ - 16, ly_ - 34, lx_ + 16, ly_ + 34), 8, fill=(26, 26, 30))
        m = np.linspace(0, 1, SH)[:, None]                             # darkness climbs behind him: 0 at the top of the frame, 1 at the bottom
        dark = 0.5 * off[0] * np.clip((m - 0.62) / 0.1, 0, 1) + 0.45 * off[1] * np.clip((m - 0.5) / 0.1, 0, 1) + 0.5 * off[2] * np.clip((m - 0.42) / 0.12, 0, 1)
        arr = np.asarray(im).astype(np.float32) * (1 - np.clip(dark, 0, 0.93))[..., None]; im = Image.fromarray(arr.astype(np.uint8))
        lit = 1 - 0.3 * off[0] - 0.3 * off[1] - 0.25 * off[2]
        sp = hero(1150 * g, back=True, bag="R", **kw)
        im = put(im, sp, SW * (0.5 + 0.012 * np.sin(2 * np.pi * ph)), feet - bob(ph) * 18 * g, mul=tuple(np.array((0.62, 0.62, 0.72)) * lit), rim=((235, 240, 255), 0, 0.0))
        return E.view(im, t, t0, t1, 1.0, 1.14, 0.5, 0.52 - 0.06 * p, drift=0.6)
    g = 0.72 + 0.3 * p; stop = ease((t - T_VIB) / 0.3)
    kw = mixp(dict(walk(ph), look=(0.0, 0.2), brow=-0.1), dict(armL=(0.1, 0.3), armR=(0.3, 2.0), look=(0.3, 0.7), brow=0.5), stop)
    sp = hero(1200 * g, phone="R" if stop > 0.5 else None, mouth="line" if stop > 0.5 else "smile", blink=blink(t), **kw)
    im = put(base, sp, SW * 0.5, SH * (0.72 + 0.26 * p) - bob(ph) * 16 * g * (1 - stop), mul=(0.6, 0.6, 0.7))
    if stop > 0: im = E.spill(im, SW * 0.56, SH * (0.72 + 0.26 * p) - 620 * g, 240, 240, (120, 160, 255), 0.25 * stop)
    return E.view(im, t, t0, t1, 1.0, 1.1, 0.5, 0.56, drift=0.6)


def door_mix(open_im, closed_im, q):
    """q = 0 open, 1 closed. The leaf swings shut from the hinge on the right, so the lit gap narrows towards the left
    jamb, and the light the room throws on the landing fades with the width of the gap."""
    if q <= 0: return open_im
    if q >= 1: return closed_im
    im = Image.blend(open_im, closed_im, float(q)); x0, y0, x1, y1 = DOOR; gap = int((x1 - x0) * (1 - q))
    im.paste(closed_im.crop((x0 + gap, y0, x1, y1)), (x0 + gap, y0))
    if gap > 0: im.paste(open_im.crop((x0, y0, x0 + gap, y1)), (x0, y0))
    return im


def landing_shot(t, t0, t1, mode):
    """The third floor. 'arrive': over his shoulder, a door ajar, his own shoes on the mat. 'put': the bag is down, he backs away, the door closes."""
    if mode == "arrive":
        base = shoes(ST["land"].copy()); q = ease((t - T_SHOES) / 0.5)
        sp = hero(1850, back=True, bag="R", armR=(0.1, 0.2), armL=(0.1, 0.3), lean=round(-0.05 * q, 2))
        im = put(base, sp, SW * 0.2, SH * 1.16 + np.sin(t * 1.5) * 5, shadow=False, mul=(0.42, 0.43, 0.52), rim=((255, 215, 170), 10, 0.5))
        return E.view(im, t, t0, t1, 1.0 + 0.5 * q, 1.08 + 0.52 * q, 0.5 - 0.02 * q, 0.5 + 0.12 * q, drift=0.5)
    q = ease((t - T_REF) / 0.5); base = door_mix(ST["landbag"], ST["closedbag"], q)
    p = cl((t - t0) / (t1 - t0)); g = 1.0 + 0.12 * p; ph = (t - t0) / 1.1
    kw = mixp(dict(armL=(0.5, 0.6), armR=(0.5, 0.6)), dict(walk(ph, 0.5)), ease((t - t0 - 0.5) / 0.5))                 # he lets go of the bag, then backs away step by step
    sp = hero(1700 * g, back=True, **kw)
    im = put(base, sp, SW * 0.22, SH * (1.12 + 0.06 * p) - bob(ph) * 8, shadow=False, mul=tuple(np.array((0.42, 0.43, 0.52)) * (1 - 0.3 * q)), rim=((255, 215, 170), 10, 0.5 * (1 - q)))
    return E.view(im, t, t0, t1, 1.12, 1.0, 0.5, 0.52, drift=0.5)


def lit_door(im, cx=560, cy=900, lo=0.3):
    """The landing timer is out: the only light left is what comes through the door."""
    return E.torch(im, cx, cy, 620, lo, 1.0)


def swap_shot(t, t0, t1):
    """After the flash you are the one inside. He walks away down the landing with your bag, wearing your colours, and the door closes on you."""
    close = ease((t - T_RESTES) / 1.4)
    me = hero(430, wide=1.3, brow=1.0, mouth="o", armL=(0.6, 2.0), armR=(0.6, 2.0 + 0.2 * float(np.sin(t * 9))), pack=False, cap=False)
    base = door_mix(put(ST["land"], me, SW * 0.5, SH * 0.668, shadow=False, mul=(0.55, 0.5, 0.48)), ST["closed"], close)
    ph = (t - t0) / 1.0; p = cl((t - t0) / (t1 - t0)); kw = walk(ph, 0.8); kw.update(armR=(0.15, 0.3))
    him = hero(1750 * (1 + 0.1 * p), bag="R", mouth="smile", look=(0.0, 0.2), brow=-0.3, wide=0.95, **kw)
    im = put(base, him, SW * (0.3 - 0.05 * p), SH * (1.2 + 0.1 * p) - bob(ph) * 14, shadow=False, mul=tuple(np.array((0.3, 0.3, 0.4)) * (1 - 0.35 * close)), rim=((255, 215, 170), 12, 0.7 * (1 - close)))
    return E.view(im, t, t0, t1, 1.0, 1.1, 0.5, 0.52, drift=0.5)


def walk_shot(t, t0, t1):
    """Walking home. The place where the scooter stood is empty."""
    base = ST["street2"]; ph = (t - t0) / 1.0; p = cl((t - t0) / (t1 - t0)); g = 0.92 + 0.12 * p
    sp = hero(1380 * g, look=(0.5, 0.2), mouth="line", brow=0.4, blink=blink(t), **walk(ph))
    im = put(base, sp, SW * 0.4, SH * (0.95 + 0.06 * p) - bob(ph) * 16, mul=(0.8, 0.82, 0.95), rim=((255, 200, 140), -10, 0.6))
    return E.view(im, t, t0, t1, 1.0, 1.08, 0.5, 0.52, drift=0.5)


GRADE = E.night_grade if os.environ.get("EI_SLOWGRADE") else fast_grade
C1 = ("MONTER", "LAISSER LE SAC"); C2 = ("PRENDRE", "POSER LE SAC"); C3 = ("ACCEPTER", "RENTRER"); C4 = ("L'APPELER", "COURIR")
CUTS = [T_NOTIF + 0.3] + [L_(k) for k in ("a1", "a2", "w3", "r1", "m1", "m2", "x3", "r2", "p1", "p2", "p3", "y1", "y2", "r3", "f1", "f2", "f4")] + [T_SONNE + 0.25, L_("c1") - 0.1, T_MAIN - 0.35, T_VIB + 0.9]
def raw(i, t):
    """The picture at time t before HUD, buttons and captions: (image, grade, cap_y, show_hud, buttons)."""
    g = ("night", 0.4); cap = 1500; hd = True; btn = None
    if t < T_NOTIF + 0.3: im = _phone(lock_screen(t), t, 0.0, vib_at=0.0); g = None
    elif t < L_("a1"): im = _phone(order_screen(t), t, 0.0); g = None
    elif t < L_("a2"): im = facade(t, L_("a1"), L_("a2")); g = ("night", 0.5)
    elif t < T_SONNE + 0.25: im = intercom_ins(t, L_("a2")); g = ("night", 0.45)
    elif t < L_("c1") - 0.1: im = entry_shot(t, T_SONNE, L_("c1"), "ring"); g = ("night", 0.35)
    elif t < L_("w1"):
        im = entry_shot(t, L_("c1") - 0.1, L_("w1"), "ask"); g = ("night", 0.35); btn = (C1, L_("c1"), L_("w1"), None)
    elif t < L_("w3"):
        im = entry_shot(t, L_("w1"), L_("w3"), "leave"); g = ("night", 0.35)
        if t < L_("w1") + 1.1: btn = (C1, 0, 1, "LAISSER LE SAC")
    elif t < L_("r1"): im = entry_shot(t, L_("w3"), L_("r1"), "dark"); g = ("night", 0.35)
    elif t < t_rew1: im = receipt(t, L_("r1"), 1); g = ("paper", 0.4); hd = False
    elif t < L_("m1"): return None
    elif t < L_("m2"):
        im = stairs_shot(t, L_("m1"), L_("m2")); g = ("night", 0.5)
        if t < L_("m1") + 1.1: btn = (C1, 0, 1, "MONTER")
    elif t < T_CLAC: im = landing_shot(t, L_("m2"), T_CLAC, "arrive"); g = ("night", 0.45)
    elif t < T_MAIN - 0.35:                                         # the timer clacks: nothing but the clock and what you hear
        im = Image.new("RGB", (W, H), (2, 2, 4)); g = None; q = cl((t - T_PRES) / 0.6)
        if q > 0: im = E.spill(im, 700, 1000, 60 + 40 * q, 520, (255, 190, 120), 0.5 * q)
    elif t < L_("x1"):
        im = hand_shot(t, T_MAIN - 0.35, L_("x1")); g = ("night", 0.4)
        if t >= L_("c2") - 0.05: btn = (C2, L_("c2"), L_("x1"), None)
    elif t < T_ECH:
        im = take_shot(t); g = ("night", 0.4)
        if t < L_("x1") + 1.1: btn = (C2, 0, 1, "PRENDRE")
    elif t < L_("r2"): im = swap_shot(t, T_ECH, L_("r2")); g = ("night", 0.45)
    elif t < t_rew2: im = receipt(t, L_("r2"), 2); g = ("paper", 0.4); hd = False
    elif t < L_("p1"): return None
    elif t < L_("p2"):
        im = landing_shot(t, L_("p1"), L_("p2"), "put"); g = ("night", 0.45)
        if t < L_("p1") + 1.1: btn = (C2, 0, 1, "POSER LE SAC")
    elif t < L_("p3"): im = _phone(status_screen(t, "done"), t, L_("p2")); g = None
    elif t < T_VIB + 0.9: im = stairs_shot(t, L_("p3"), T_VIB + 0.9, down=True); g = ("night", 0.5)
    elif t < L_("y1"):
        im = _phone(status_screen(t, "new"), t, T_VIB + 0.9, vib_until=0.5); g = None
        if t >= L_("c3") - 0.05: btn = (C3, L_("c3"), L_("y1"), None)
    elif t < L_("y2"):
        im = E.view(ST["wide"], t, L_("y1"), L_("y2"), 1.0, 1.9, 0.5, 0.52, drift=0.5); g = ("night", 0.5)
        if t < L_("y1") + 1.1: btn = (C3, 0, 1, "ACCEPTER")
    elif t < L_("r3"): im = appt_shot(t, L_("y2"), L_("r3")); g = ("night", 0.3)
    elif t < t_rew3: im = receipt(t, L_("r3"), 3); g = ("paper", 0.4); hd = False
    elif t < L_("f1"): return None
    elif t < L_("f2"):
        im = walk_shot(t, L_("f1"), L_("f2")); g = ("night", 0.5)
        if t < L_("f1") + 1.1: btn = (C3, 0, 1, "RENTRER")
    elif t < L_("f4"): im = _phone(mum_screen(t), t, L_("f2"), vib_until=0.0); g = None; im_v = t - T_ENC; im = im if not 0 <= im_v < 0.4 else _phone(mum_screen(t), t, T_ENC, vib_until=0.4)
    else:
        im = face_shot(t, L_("f4"), D, still="street2", scared=True); g = ("night", 0.45)
        if t >= L_("c4") - 0.05: btn = (C4, 0, 1, None, True)
    return im, g, cap, hd, btn


_CH = {}
def choice_img(key, tc):
    if key not in _CH: _CH[key] = finish(0, tc, raw(0, tc), captions=False)
    return _CH[key]


def finish(i, t, r, captions=True):
    im, g, cap, hd, btn = r
    if g: im = GRADE(im, i, exp=g[1], warm=True, glow=g[0] != "paper")
    if T_E1 <= t < L_("m2"): pass
    if L_("a1") + 0.2 <= t < L_("a2") and t >= T_FEN:
        im = E.callout(im, t, T_FEN, L_("a2") - 0.1, E.view_xy((SW, SH), t, L_("a1"), L_("a2"), 1.0, 1.1, 0.5, 0.58 - 0.12 * ease((t - L_("a1")) / (L_("a2") - L_("a1"))), _FACW[0], _FACW[1], drift=0.5), (-200, 330), "3e ÉTAGE · APPT 13", "la seule lumière", RED)
    if T_SHOES + 0.5 <= t < T_CLAC: im = E.callout(im, t, T_SHOES + 0.5, T_CLAC, (540, 1125), (150, -330), "SUR LE PAILLASSON", "tes chaussures", RED)
    if T_BRAC <= t < L_("dv") - 0.1: im = E.callout(im, t, T_BRAC, L_("dv") - 0.1, (HX0 + 345, 1055), (60, 300), "SON POIGNET", "ton bracelet", RED)
    if hd: hud(im, t)
    if L_("w5") + 0.25 <= t < L_("r1"): stamp(im, t, L_("w5") + 0.35, "FIN DE SERVICE", y=820, size=92)
    if T_CMD <= t < L_("r2"): stamp(im, t, T_CMD + 0.1, "LIVRÉ", y=820)
    if T_FIN3 <= t < L_("r3"): stamp(im, t, T_FIN3 + 0.1, "FIN DE SERVICE", y=1080, size=92)
    if T_E1 <= t < L_("m2"):
        n = 1 if t < T_E2 else 2; d = ImageDraw.Draw(im); d.text((540, 470), f"ÉTAGE {n}", font=ImageFont.truetype(E.MONO, 54), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
    if btn: buttons(im, btn[0], t, btn[1], btn[2], btn[3], ab=len(btn) > 4, title="TOI, TU FAIS QUOI ?" if len(btn) > 4 and t >= wt("c4", "toi") - 0.1 else None)
    if captions: G.karaoke(im, words, t, "present", hl=RED, box=False, y0=cap if g else 1575, size0=70, stroke=7)
    return im


def render(i, t):
    r = raw(i, t)
    if r is None:                                                   # the three rewinds
        for t0, key, tc in ((t_rew1, "c1", L_("w1") - 0.3), (t_rew2, "c2", L_("x1") - 0.3), (t_rew3, "c3", L_("y1") - 0.3)):
            if t0 <= t < t0 + 0.9: return rewind(i, t, t0, choice_img(key, tc))
    k = int(round((t - T_ECH) / F))                                 # the one shock of the episode: the swap
    if -2 <= k < 0: return smear(finish(i, T_ECH - 3 * F, raw(i, T_ECH - 3 * F), captions=False), k)
    if k == 0: return negative(finish(i, t, r, captions=False))
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
    STEP = os.environ.get("EI_STEP")
    RANGE = os.environ.get("EI_RANGE"); sig = json.dumps(sorted(line_t.items()))
    if not os.environ.get("EI_AUDIO_ONLY"):
        todo = [i for i in range(N) if not STEP or i % int(STEP) == 0]
        if RANGE:                                                   # EI_RANGE=12.5-18,40-44: redo only those seconds, keep every other frame
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
    def step(): n = int(0.09 * VSR); return np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same") * np.exp(-np.arange(n) / VSR * 45) * 6
    def sweep(): x = np.arange(int(0.9 * VSR)) / VSR; return np.sin(2 * np.pi * np.cumsum(1800 - 1500 * x / 0.9) / VSR) * 0.25 + rng.standard_normal(len(x)) * 0.12
    def thud(at_, g=1.0): add(np.convolve(rng.standard_normal(int(0.12 * VSR)), np.ones(40) / 40, "same") * 10, at_, 0.8 * g); add(thump(), at_, 1.3 * g)
    def buzz(d_=0.5): x = np.arange(int(d_ * VSR)) / VSR; return np.sin(2 * np.pi * 150 * x) * (np.sin(2 * np.pi * 6 * x) > 0) * 0.5
    def clack(at_, g=1.0): add(click() * 3, at_, g); add(tone(900, 0.05, 80), at_, 0.5 * g); add(thump(), at_ + 0.01, 0.6 * g)
    def breath(at_, d_=1.1, g=1.0): n = int(d_ * VSR); x = np.arange(n) / VSR; s_ = sosfiltfilt(butter(2, [500, 2400], btype="band", fs=VSR, output="sos"), rng.standard_normal(n)); add(s_ * np.sin(np.pi * x / d_) ** 2 * 2.5, at_, g)
    def heart(a_, b_, per=0.55, g=0.9):
        for q in np.arange(a_, b_, per): add(thump(), q, g); add(thump(), q + 0.19, g * 0.65)
    outside = (ts < L_("a2")) | ((ts >= T_SONNE) & (ts < L_("r1"))) | (ts >= L_("f1"))
    for a_, b_ in ((0.0, L_("a1")), (L_("f2"), L_("f4"))): outside &= ~((ts >= a_) & (ts < b_)) | True
    wind = np.convolve(rng.standard_normal(NS), np.ones(400) / 400, "same") * 0.5 * (1 + 0.5 * np.sin(ts * 0.9)); mix += wind * outside
    mix += (np.sin(2 * np.pi * 41 * ts) + 0.6 * np.sin(2 * np.pi * 61.7 * ts)) * 0.05 * ~outside
    add(boom(), 0.0, 0.5); add(buzz(0.35), 0.02, 0.5)                                                             # frame 0: the phone buzzes in his hand
    add(tone(1318, 0.4, 7) + tone(1760, 0.4, 8) * 0.6, T_NOTIF, 0.35); add(boom(), T_TOI0, 0.8); add(buzz(0.3), L_("h4") + 0.05, 0.4); add(tone(880, 0.3, 9) + tone(1318, 0.3, 9) * 0.5, L_("h4") + 0.08, 0.25)
    add(click() * 3, T_OK, 0.8); add(tone(1046, 0.3, 9) + tone(1568, 0.3, 9) * 0.7, T_OK + 0.05, 0.3)
    x = np.arange(int(1.6 * VSR)) / VSR; add(sosfiltfilt(butter(2, [90, 400], btype="band", fs=VSR, output="sos"), rng.standard_normal(len(x))) * np.sin(np.pi * x / 1.6) ** 2 * 5, L_("a1"), 0.5)     # the scooter rolling up
    x = np.arange(int(0.45 * VSR)) / VSR; add(np.sign(np.sin(2 * np.pi * 420 * x)) * 0.5 * np.exp(-x * 2), T_SONNE, 0.5)                                                              # the intercom buzzer
    for key in ("iv",): mix += rng.standard_normal(NS) * 0.02 * ((ts > line_t[key] - 0.15) & (ts < line_t[key] + dur[key] + 0.15))
    for a_, b_, n_ in ((we("c1") + 0.1, 3, 0), (we("c2") + 0.1, 3, 0), (we("c3") + 0.1, 3, 0)):
        for k in range(b_): add(tone(1200, 0.05, 60), a_ + k * 0.26, 0.45)                                         # choice timers
    heart(L_("a2"), L_("w1")); heart(L_("w3"), L_("w5"), 0.45); heart(T_CLAC, L_("x1"), 0.5); heart(L_("x1"), line_t["x1"] + dur["x1"], 0.4); heart(L_("p3") + 2, L_("y1")); heart(L_("y1"), T_FIN3, 0.5); heart(T_NOIRQ, D - 0.5, 0.48)
    for k in range(int((L_("w3") - L_("w1")) / 0.42)): add(step(), L_("w1") + 0.1 + k * 0.42, 0.45)
    add(buzz(0.4), L_("w1") + dur["w1"] + 0.1, 0.4)
    clack(T_VERR, 1.2); thud(T_VERR + 0.08, 0.6); clack(T_NOIR1, 0.9); add(boom(), T_NOIR1, 0.6); add(boom(), L_("w4") - 0.1, 0.7); thud(L_("w5") + 0.35)
    for t0_ in (L_("r1"), L_("r2"), L_("r3")):
        for k in range(46): add(click() * 0.5, t0_ + 0.2 + k * 0.05, 0.5)                                          # the pen on the slip
    for t0_ in (t_rew1, t_rew2, t_rew3): add(sweep(), t0_, 0.8)
    for k in range(int((L_("m2") - L_("m1")) / 0.46)): add(step(), L_("m1") + 0.1 + k * 0.46, 0.5)
    clack(T_L1, 0.9); clack(T_L2, 0.9); clack(T_L3, 1.1); add(boom(), T_L3, 0.4)
    clack(T_CLAC, 1.3); breath(T_RESP, 1.0, 0.8); breath(T_RESP + 1.3, 1.1, 1.0); breath(T_PRES + 0.2, 1.1, 1.2)
    xx = np.arange(int(0.6 * VSR)) / VSR; add(np.sin(2 * np.pi * np.cumsum(170 + 200 * xx) / VSR) * np.exp(-xx * 3) * 0.3, T_MAIN - 0.3, 0.6)             # the door creaks
    add(np.convolve(rng.standard_normal(int(0.2 * VSR)), np.ones(12) / 12, "same") * 3 * np.exp(-np.arange(int(0.2 * VSR)) / VSR * 14), L_("dv") - 0.1, 0.35)   # the note, unfolded
    thud(T_DOIGTS, 1.0)
    add(np.convolve(rng.standard_normal(int(0.14 * VSR)), np.ones(25) / 25, "same") * 9, T_ECH - 0.1, 0.5); add(boom(), T_ECH, 1.2)
    for k in range(int((L_("x4") - L_("x3")) / 0.5)): add(step(), L_("x3") + 0.2 + k * 0.5, 0.4)
    clack(T_RESTES + 1.3, 1.0); thud(T_CMD + 0.1)
    add(np.convolve(rng.standard_normal(int(0.2 * VSR)), np.ones(40) / 40, "same") * 6, wt("p1", "poses") + 0.3, 0.5); clack(T_REF + 0.48, 1.0)
    add(tone(1318, 0.5, 6) + tone(1760, 0.5, 7) * 0.6, L_("p2") + 0.1, 0.3)
    for k in range(8): add(tone(1568 + 60 * k, 0.08, 40), T_60 + k * 0.08, 0.25)                                    # the counter climbs to 60
    add(tone(2093, 0.7, 5) + tone(2637, 0.7, 6) * 0.6, T_60 + 0.7, 0.3)
    for k in range(int((T_VIB - L_("p3")) / 0.46)): add(step(), L_("p3") + 0.1 + k * 0.46, 0.45)
    add(buzz(0.5), T_VIB, 0.5); add(buzz(0.4), T_VIB + 0.9, 0.4)
    for k in range(4): add(step(), L_("y1") + 0.2 + k * 0.5, 0.45)
    add(boom(), T_13, 0.7); add(boom(), T_AUCUN, 0.9); thud(T_FIN3 + 0.1)
    for k in range(int((L_("f2") - L_("f1")) / 0.5)): add(step(), L_("f1") + 0.1 + k * 0.5, 0.45)
    add(buzz(0.4), T_ENC, 0.5); add(tone(880, 0.3, 9) + tone(1318, 0.3, 9) * 0.5, T_ENC + 0.05, 0.25); add(tone(880, 0.3, 9) + tone(1318, 0.3, 9) * 0.5, T_NOIRQ, 0.25); add(boom(), T_NOIRQ + 0.2, 0.8)
    add(boom(), L_("f4"), 0.6)
    mute = (ts >= we("x1") + 0.05) & (ts < T_ECH - 0.12)                                                            # one second of silence before the shock
    vox = np.zeros(NS)
    for k, t0 in line_t.items():
        v = VO_A[k]
        if k == "iv": v = sosfiltfilt(butter(3, [420, 3000], btype="band", fs=VSR, output="sos"), v) * 1.6           # through the intercom
        i0 = int(t0 * VSR); j0 = min(NS, i0 + len(v)); vox[i0:j0] += v[: j0 - i0]
    act = np.convolve((np.convolve(np.abs(vox), np.ones(2205) / 2205, "same") > 0.01).astype(float), np.ones(13230) / 13230, "same")
    mix = mix / np.abs(mix).max() * 0.55 * (1 - 0.6 * np.clip(act, 0, 1)) * (1 - np.convolve(mute.astype(float), np.ones(2205) / 2205, "same")) + vox / (np.abs(vox).max() + 1e-9) * 0.9
    mix = mix[: int(D * VSR)]; mix *= np.clip((D - ts[: len(mix)]) / 0.3, 0, 1); sf.write(TMP + "mix.wav", mix / np.abs(mix).max() * 0.9, VSR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", TMP + "f%05d.jpg", "-i", TMP + "mix.wav",
                    "-c:v", "libx264", "-crf", "24", "-maxrate", "3200k", "-bufsize", "6400k", "-preset", "slow", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-g", "60",
                    "-af", "loudnorm=I=-13:TP=-1.0:LRA=9,volume=1.3,alimiter=limit=0.89", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", _out], check=True)
    print("ok", _out, D)
