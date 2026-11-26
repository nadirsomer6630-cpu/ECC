"""CAISSIER DE NUIT: two stand-alone videos from one production (script v3, /home/user/caissier_de_nuit_script_v3_independant.md).
  A "Le ticket dit un mot" (noon): the premise, the rules, the ticket riddle, the woman without a shadow, the A/B choice.
  B "Elle n'a pas d'ombre" (evening): its own premise, the riddle replayed and solved, both outcomes, RÈGLE N°10, the loop.
No night or part number anywhere. Our characters (toon5 heads on the rig5 cut-out bodies) stand in the caisse 3 set
(caisse_set.py) between the set and its foreground mask; inserts are flat 2D.

usage: HF_HOME=$B/hfcache python3 caisse.py A|B out.mp4
env: EI_STEP=n (every n-th frame, no encode) · EI_RANGE=a-b,... (re-render seconds after a full render, same timeline)
     EI_AUDIO_ONLY=1 (remix + encode from frames) · CA_PROBE="t,t,..." (contact sheet of those times -> <tmp>/probe.jpg)"""
import os, sys, json, glob, re, math, subprocess, difflib, functools
VID = sys.argv[1]; OUTP = sys.argv[2] if len(sys.argv) > 2 else "/tmp/x.mp4"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, soundfile as sf, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import grade as G, toon5, rig5, scene5
from rig5 import Figure, CX

W, H, FPS, VSR = 1080, 1920, 30, 44100; F = 1 / FPS
NEW = G.NEW; SET = HERE + "/s2c/"; VO = NEW + "elv13/fin/"
TMP = NEW + f"ca{VID}tmp/"; os.makedirs(TMP, exist_ok=True)
INTER = "/usr/share/fonts/opentype/inter/"; ANTON = NEW + "fonts/dl2/Anton.ttf"; HAND = NEW + "fonts/caveat.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
ORANGE = (255, 168, 38); RED = (226, 32, 40); YEL = (255, 214, 10); INK = (14, 12, 18)
PURPLE, GREEN, PINK = (112, 72, 214), (40, 150, 90), (214, 110, 146)
MUM_C = (-1.0, -0.95)                                            # where she stands, across the belt from you


@functools.lru_cache(None)
def font(name, size):
    p = {"anton": ANTON, "hand": HAND, "mono": MONO}.get(name, INTER + f"Inter-{name}.otf")
    return ImageFont.truetype(p, int(size))


# ---------------------------------------------------------------- voices -> timeline
def norm(x): return re.sub(r"[^\w]", "", x.lower())


def align(ws, script):
    """Script spelling, whisper timing: match letters, so '2 h 14' heard for 'deux heures quatorze' still lands."""
    sw = script.split(); wc, wtm = [], []
    for x in ws:
        n = norm(x["w"])
        for i, ch in enumerate(n): wc.append(ch); wtm.append((x["s"] + (x["e"] - x["s"]) * i / max(1, len(n)), x["s"] + (x["e"] - x["s"]) * (i + 1) / max(1, len(n))))
    sc_, owner = [], []
    for j, w in enumerate(sw):
        for ch in norm(w): sc_.append(ch); owner.append(j)
    mp = {}
    for a1, b1, n1 in difflib.SequenceMatcher(None, sc_, wc, autojunk=False).get_matching_blocks():
        for q in range(n1): mp[a1 + q] = b1 + q
    out = []
    for j, w in enumerate(sw):
        idx = [i for i, o in enumerate(owner) if o == j and i in mp]
        out.append({"w": w, "s": wtm[mp[idx[0]]][0] if idx else None, "e": wtm[mp[idx[-1]]][1] if idx else None})
    for j, x in enumerate(out):
        if x["s"] is None:
            prev = next((out[q]["e"] for q in range(j - 1, -1, -1) if out[q]["e"] is not None), 0.0)
            nxt = next((out[q]["s"] for q in range(j + 1, len(out)) if out[q]["s"] is not None), prev + 0.4)
            x["s"], x["e"] = prev, max(prev + 0.05, nxt)
    return out


LINES = {k: re.sub(r"\[[^\]]*\]\s*", "", t).strip() for k, w_, t in json.load(open(NEW + "elv13/lines.json"))}
ORDER = {"A": ["n1", "n2", "n3", "n4", "n5", "s1", "n6", "n7", "n8", "n9", "n10", "s2", "m1", "n11", "n12", "n12b", "n13"],
         "B": ["p1v3", "n3", "n4", "n8", "p2", "n13", "a1", "a2", "a3", "r10", "b1", "m2", "n14", "s3", "n15", "t1", "t2"]}[VID]
VO_A = {k: G.voice(VO + f"{k}.wav", lp=None) for k in ORDER}
_cache = TMP + "rel.json"; _sig = {k: [LINES[k], len(VO_A[k])] for k in ORDER}
if os.path.exists(_cache) and json.load(open(_cache))["sig"] == _sig: REL = json.load(open(_cache))["rel"]
else:
    REL = {}
    for k in ORDER:
        p = TMP + f"{k}_pre.wav"; sf.write(p, VO_A[k], VSR); REL[k] = align(G.word_times(p, 0, None), LINES[k])
    json.dump({"sig": _sig, "rel": REL}, open(_cache, "w"))
dur = {k: len(v) / VSR for k, v in VO_A.items()}
T = 0.08; line_t = {}
def at(k, gap):
    global T
    line_t[k] = T; T += dur[k] + gap
if VID == "A":
    at("n1", 0.3); at("n2", 0.3); at("n3", 0.25); at("n4", 0.4); at("n5", 0.4)          # hook, context, the rules, the promise
    at("s1", 0.35); at("n6", 0.3); at("n7", 0.3); at("n8", 0.45); at("n9", 1.05)         # sign 1 (the bip), sign 2 (the ticket), one second of silence
    at("n10", 0.35); at("s2", 0.35); at("m1", 0.35); at("n11", 0.3)                      # the shock: no shadow; sign 3 (Samir); she is here
    at("n12", 0.35); at("n12b", 0.4); at("n13", 0.2)
    T_HOLD = T; T += 1.4                                                                  # the buttons stay, the bar runs out
    T_END = T; T += 3.8
else:
    at("p1v3", 0.4); at("n3", 0.25); at("n4", 0.35); at("n8", 0.35); at("p2", 0.45); at("n13", 0.2)
    T_HOLD = T; T += 1.2
    at("a1", 1.95)                                                                        # one second of silence, then the shock
    at("a2", 0.3); at("a3", 0.35); at("r10", 0.45)
    t_rew = T; T += 0.9
    at("b1", 0.35); at("m2", 0.7); at("n14", 0.35); at("s3", 0.35); at("n15", 0.35); at("t1", 0.25); at("t2", 0.55)
    T_END = T; T += 3.0
D = round(T, 2); N = int(D * FPS)
def L_(k): return line_t[k] - 0.1
def wt(k, frag, n=0):
    m = [w["s"] for w in REL[k] if frag in norm(w["w"])]
    return line_t[k] + (m[n] if len(m) > n else 0.0)
def we(k): return line_t[k] + dur[k]
if VID == "A": T_SHOCK = L_("n10") - 0.05
else: T_SHOCK = we("a1") + 1.0
words = []
for k, t0 in line_t.items(): words += [dict(w, s=w["s"] + t0, e=w["e"] + t0, line=k) for w in REL[k]]


def amp(key, t, gain=7):
    if key not in line_t: return 0.0
    a = VO_A[key]; i0 = int((t - line_t[key]) * VSR)
    return float(np.abs(a[max(0, i0):max(0, i0) + 1470]).mean() * gain) if 0 <= i0 < len(a) else 0.0
def tw(t): return math.floor(t * 15) / 15                       # animation on twos: 15 drawings a second
def cl(x): return float(min(1.0, max(0.0, x)))
def ease(u): u = cl(u); return u * u * (3 - 2 * u)
def settle(dt, w=15.0, z=0.42):
    """A move that arrives with a small overshoot and settles (the springs of rig5, in closed form so any frame can
    be drawn alone)."""
    if dt <= 0: return 0.0
    return 1 - math.exp(-z * w * dt) * math.cos(w * math.sqrt(1 - z * z) * dt)
def wob(t, seed, f=1.0): return math.sin(t * f * 1.3 + seed) * 0.6 + math.sin(t * f * 2.9 + seed * 2.1) * 0.3 + math.sin(t * f * 5.3 + seed * 3.7) * 0.1
def lid_at(t, seed=0.0, extra=()):
    bl = [0.7 + seed + k * 3.3 + 0.5 * math.sin(k * 1.7 + seed) for k in range(40)] + list(extra)
    return min(rig5.blink_lid(t, b) for b in bl)


# ---------------------------------------------------------------- the set
def _still(p, size=(1296, 2304)):
    im = Image.open(p).convert("RGB")
    return im if im.size == size else im.resize(size, Image.LANCZOS)
ST = {"front": _still(SET + "front.png"), "comptoir": _still(SET + "comptoir.png"), "cctv3": _still(SET + "cctv3.png"), "aisle": _still(HERE + "/s2/aisle.png")}
SW, SH = ST["front"].size
FG = {}
for k in ("front", "comptoir", "cctv3"):
    a = Image.open(SET + f"{k}_fg.png").convert("RGBA").resize((SW, SH), Image.LANCZOS).getchannel("A").filter(ImageFilter.MedianFilter(3))
    FG[k] = ST[k].convert("RGBA"); FG[k].putalpha(a)
CAL = {k: rig5.calib(SET + f"{k}_cal.json") for k in ("front", "comptoir", "cctv3")}
_pa = rig5.calib(HERE + "/s2/aisle_cal.json"); CAL["aisle"] = lambda x, y: tuple(v * 1.2 for v in _pa(x, y))
PTS = {k: json.load(open(SET + f"{k}_pts.json")) for k in ("front", "comptoir", "cctv3")}
_BLUR = {}
def blurred(name, r=16, k=0.55):
    if (name, r, k) not in _BLUR: _BLUR[(name, r, k)] = ST[name].filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(v * k))
    return _BLUR[(name, r, k)]


def view(im, z, cx, cy, t=0.0, shake=1.0, seed=0):
    """Frame a still: zoom z (1 = the whole still), centre (cx, cy) in still pixels, a slow handheld drift."""
    sw_, sh_ = im.size; cw, ch = sw_ / z, sh_ / z
    cx += shake * 6 * wob(t, seed, 0.7); cy += shake * 5 * wob(t, seed + 3, 0.6)
    cx = min(max(cx, cw / 2), sw_ - cw / 2); cy = min(max(cy, ch / 2), sh_ - ch / 2)
    return im.convert("RGB").resize((W, H), Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))


# ---------------------------------------------------------------- characters
_FIG = {}
def fig(who, h):
    key = (who, int(round(h / 8)) * 8)
    if key not in _FIG: _FIG[key] = Figure(who, key[1])
    return _FIG[key]


def body(f, hands, ex, torso=0.0, head=0.0, bob=0.0, phone=False):
    ex = {k: (tuple(round(v, 2) for v in x) if isinstance(x, tuple) else (round(x, 2) if isinstance(x, float) else x)) for k, x in ex.items()}
    k = f.face(repr(sorted(ex.items())), ex)
    return f.frame({"torso": torso, "head": head, "bob": bob, "legs": 0.0, "hands": hands, "face": k, "phone": phone})


def tinted(img, k):
    a = np.asarray(img).astype(np.float32); a[..., :3] *= np.array(k, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


@functools.lru_cache(maxsize=96)
def _bust(who, look, brow, mouth_, wide, lid, light, fiend, size):
    return toon5.bust5(who, look=look, brow=brow, mouth_=mouth_, wide=wide, lid=lid, light=light, fiend=fiend, size=size, blink=lid < 0.12)


def bust(who, size=1000, look=(0.0, 0.0), brow=0.0, mouth_="line", wide=1.0, lid=1.0, light=1.0, fiend=False):
    lid = 1.0 if lid > 0.8 else (0.55 if lid > 0.3 else 0.1)
    return _bust(who, tuple(round(v, 1) for v in look), round(brow, 1), mouth_, round(wide, 2), lid, round(light, 1), fiend, size)


def talk_mouth(key, t, idle="line", open_="o", thr=0.35):
    return open_ if amp(key, tw(t)) > thr else idle


def close_up(bg, sp, t, z0=1.0, z1=1.06, t0=0.0, t1=1.0, y=560, size=1240, tint=(0.95, 0.95, 1.0), seed=1, shake=1.0):
    """A bust in front of a blurred set: the reference creators' close shot. The bust breathes, the camera drifts."""
    im = bg.copy().convert("RGBA"); s = size * (z0 + (z1 - z0) * ease((t - t0) / max(0.1, t1 - t0)))
    b = tinted(sp, tint).resize((int(s), int(s)), Image.LANCZOS)
    br = 4 * math.sin(t * 2 * math.pi / 3.4)
    im.alpha_composite(b, (int(540 - s / 2 + shake * 5 * wob(t, seed, 0.6)), int(y + 1920 - 1920 + br + (1240 - s) * 0.35)))
    return im.convert("RGB")


# ---------------------------------------------------------------- lighting helpers
def glow(im, x, y, r, col, a):
    if a <= 0.01: return im
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((x - r, y - r, x + r, y + r), fill=col + (int(255 * min(1, a)),))
    im = im.convert("RGBA"); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.45))); return im


def dim(im, k, tint=(0.75, 0.85, 1.25)):
    a = np.asarray(im.convert("RGB")).astype(np.float32) * k * np.array(tint, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- the CCTV picture of aisle 7
_CC = {}
def basket(im, x, y, s, shadow=True, sdir=-1):
    """A red shopping basket on the floor with its shadow under the warm lamp: the fair clue next to her feet."""
    d = ImageDraw.Draw(im, "RGBA")
    if shadow: d.polygon([(x - 60 * s, y + 6 * s), (x + 50 * s, y + 6 * s), (x + 50 * s + sdir * 40 * s, y + 40 * s), (x - 60 * s + sdir * 70 * s, y + 40 * s)], fill=(0, 0, 0, 150))
    d.polygon([(x - 58 * s, y - 50 * s), (x + 58 * s, y - 50 * s), (x + 46 * s, y + 6 * s), (x - 46 * s, y + 6 * s)], fill=(190, 40, 44, 255), outline=INK + (255,), width=max(2, int(5 * s)))
    for k in range(4): d.line((x - 40 * s + k * 27 * s, y - 40 * s, x - 34 * s + k * 23 * s, y), fill=(120, 20, 28, 255), width=max(1, int(4 * s)))
    d.arc((x - 40 * s, y - 92 * s, x + 40 * s, y - 20 * s), 190, 350, fill=INK + (255,), width=max(2, int(5 * s)))


def mum_far(im, proj, xw, yw, t, look=(0.0, -0.3), warm=1.0, fiend=False, hand_out=False):
    fx, fy, hh = proj(xw, yw); f = fig("maman", hh)
    hands = {-1: (CX - 236, 1290), 1: (CX + 236, 1290)} if not hand_out else {-1: (CX - 236, 1290), 1: (CX + 330, 900)}
    img = body(f, hands, dict(look=look, lid=lid_at(t, 1.3), mouth_="line", fiend=False) if not fiend else dict(look=look, mouth_="line"),
               torso=0.6 * math.sin(t * 2 * math.pi / 3.6), bob=3 * math.sin(t * 2 * math.pi / 3.6))
    rig5.stand_in(im, img, fx, fy, tint=(0.62 + 0.38 * warm, 0.55 + 0.33 * warm, 0.62 + 0.0 * warm), shadow=False)   # no shadow: the clue
    return fx, fy, hh


def cctv(t, look_cam=False, z=1.55, label="CAM 07 · ALLÉE 7", replay=False, callout=0.0):
    """The shop's camera on aisle 7: green-grey, scanlines, the time; she stands in the only warm pool, no shadow,
    next to a basket that has one."""
    key = ("base", look_cam)
    if key not in _CC:
        im = ST["aisle"].copy().convert("RGBA"); P = CAL["aisle"]
        bx, by, bh = P(-0.25, -9.6); basket(im, bx, by, bh / 900)
        _CC[key] = im
    im = _CC[key].copy()
    fx, fy, hh = mum_far(im, CAL["aisle"], 0.4, -9.5, tw(t), look=(0.0, -0.9) if look_cam else (0.3, -0.2))
    fr = view(im, z, fx, fy - hh * 0.45, t, shake=0.0)
    out = cctv_look(fr, t, label, replay)
    d = ImageDraw.Draw(out)
    if callout > 0:                                                    # a hand-drawn circle at her feet, the fair clue named
        cxs = W / 2; cys = H / 2 + hh * 0.45 * W / (SW / z)
        u = ease(callout / 0.35); r = 150
        d.arc((cxs - r, cys - r * 0.55, cxs + r, cys + r * 0.55), -90, -90 + 360 * u, fill=RED, width=10)
        if callout > 0.3: d.text((cxs, cys + 120), "SON OMBRE ?", font=font("hand", 84), fill=RED, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    return out


def cctv_look(fr, t, label, replay=False):
    a = np.asarray(fr).astype(np.float32) @ np.array([0.30, 0.59, 0.11], np.float32)
    rg = np.random.default_rng(int(t * 30)); a = a * 1.15 + rg.normal(0, 7, a.shape); a[::4] *= 0.82
    rgb = np.stack([a * 0.86, a * 1.0, a * 0.84], -1); out = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    if (t * 2) % 2 < 1.3: d.ellipse((80, 470, 112, 502), fill=(230, 40, 40))
    d.text((126, 486), "REC", font=font("mono", 40), fill=(235, 235, 235), anchor="lm")
    d.text((80, 540), label, font=font("mono", 40), fill=(235, 235, 235))
    s_ = int(2 * 3600 + 15 * 60 + 4 + t); d.text((80, 596), f"{s_ // 3600:02d}:{s_ // 60 % 60:02d}:{s_ % 60:02d}", font=font("mono", 40), fill=(235, 235, 235))
    if replay: d.text((1000, 486), "TOUT À L'HEURE", font=font("mono", 40), fill=(255, 220, 90), anchor="rm")
    return out


def cctv_till(t, look_up=True, callout=0.0, z=1.0, cx=None, cy=None):
    """CAM 03 above the lane: you behind the till, her in front of it, staring up at the lens. Her feet are in the
    light; the basket next to her has a shadow, she has none."""
    im = ST["cctv3"].copy().convert("RGBA"); P = CAL["cctv3"]
    bx, by, bh = P(-1.75, -1.45); basket(im, bx, by, bh / 900, sdir=-1)
    fx, fy, hh = P(0.0, 1.0); f = fig("toi", hh)
    img = body(f, {-1: (CX - 170, 940), 1: (CX + 170, 940)}, dict(look=(-0.3, 0.2), brow=0.8, wide=1.15, lid=lid_at(t)), torso=0.8 * math.sin(t * 2), bob=2 * math.sin(t * 2))
    rig5.stand_in(im, img, fx, fy, tint=(0.82, 0.86, 1.0), shadow=False)
    im.alpha_composite(FG["cctv3"])
    mx, my, mh = mum_far(im, P, MUM_C[0], MUM_C[1], tw(t), look=(0.0, -0.95) if look_up else (0.4, -0.2), warm=0.4, hand_out=True)
    cx = cx if cx is not None else SW / 2; cy = cy if cy is not None else SH * 0.5
    fr = view(im, z, cx, cy, t, shake=0.0)
    out = cctv_look(fr, t, "CAM 03 · CAISSE 3")
    if callout > 0:
        d = ImageDraw.Draw(out); k_ = W / (SW / z); x_, y_ = W / 2 + (mx - cx) * k_, H / 2 + (my - cy) * k_
        u = ease(callout / 0.35); r = 130
        d.arc((x_ - r, y_ - r * 0.5, x_ + r, y_ + r * 0.5), -90, -90 + 360 * u, fill=RED, width=10)
        if callout > 0.3: d.text((x_, y_ + 110), "SON OMBRE ?", font=font("hand", 80), fill=RED, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    return out


def monitor_into(im, name, t):
    """The CCTV picture in the monitor above the till (front view), warped onto its screen."""
    p = PTS[name]; src = np.asarray(cctv(t, z=1.4).resize((540, 960)))
    sh_ = src.shape; srcq = np.float32([[0, sh_[0] * 0.3], [sh_[1], sh_[0] * 0.3], [0, sh_[0] * 0.75], [sh_[1], sh_[0] * 0.75]])
    dst = np.float32([p["mon_tl"][:2], p["mon_tr"][:2], p["mon_bl"][:2], p["mon_br"][:2]])
    M = cv2.getPerspectiveTransform(srcq, dst); base = np.asarray(im.convert("RGB")).copy()
    warped = cv2.warpPerspective(src, M, (base.shape[1], base.shape[0]))
    mask = cv2.warpPerspective(np.full(src.shape[:2], 255, np.uint8), M, (base.shape[1], base.shape[0]), flags=cv2.INTER_LINEAR)
    m = (mask.astype(np.float32) / 255)[..., None] * 0.92
    out = Image.fromarray((base * (1 - m) + warped * m).astype(np.uint8))
    cx_ = (dst[:, 0].mean()); cy_ = dst[:, 1].mean()
    return glow(out, cx_, cy_, 120, (150, 200, 160), 0.18).convert("RGB")


# ---------------------------------------------------------------- the two views with people in them
def front_scene(t, pose="idle", lights=1.0, scan=0.0, monitor=True):
    """The customer's side: you behind caisse 3, the wall of cigarettes, the door to the night, the monitor."""
    im = ST["front"].copy().convert("RGBA")
    fx, fy, hh = CAL["front"](0.0, 1.0); f = fig("toi", hh)
    br = math.sin(t * 2 * math.pi / 3.2); lid = lid_at(t)
    on_counter = {-1: (CX - 170, 940), 1: (CX + 170, 940)}
    ex = dict(look=(0.0, 0.1), lid=lid, brow=0.3)
    torso, head, bob = 0.8 * br, 0.0, 3 * br
    hands = on_counter; phone = False
    if pose == "phone":                                                # reading the phone, lit by it
        hands = {-1: (CX - 60, 900), 1: (CX + 80, 820)}; phone = True; ex = dict(look=(0.1, 0.75), lid=min(lid, 0.82), brow=0.7, mouth_="line")
        head = -4
    elif pose == "startle":                                            # the bip: anticipation, a jolt, the head snaps to the scanner
        t0 = wt("n6", "bip") - 0.05; dt = t - t0
        jolt = settle(dt, 18, 0.35) if dt > 0 else -0.15 * ease((dt + 0.12) / 0.12)
        bob = 3 * br - 22 * jolt; head = 9 * settle(dt - 0.08, 14, 0.4)
        ex = dict(look=(0.55, 0.45), wide=1.0 + 0.3 * cl(dt / 0.1), brow=0.9 * cl(dt / 0.1), lid=1.0 if dt < 0.5 else lid, mouth_="o" if 0 < dt < 0.6 else "line")
        hands = {-1: (CX - 170, 940 - 40 * jolt), 1: (CX + 120, 900 - 60 * jolt)}
    elif pose == "fear":                                               # shoulders up, a tremor, the hand to the chest
        tr = 2.5 * math.sin(t * 2 * math.pi * 9) + 1.5 * math.sin(t * 2 * math.pi * 11.3)
        hands = {-1: (CX - 40 + tr, 900), 1: (CX + 170, 940)}; bob = -12 + 2 * br; ex = dict(look=(-0.35, 0.1), wide=1.25, brow=1.0, mouth_="fear", lid=lid)
        head = 2 + 0.6 * tr
    elif pose == "alone":
        ex = dict(look=(-0.4 * ease((t % 6) / 1.0) + 0.4 * ease((t % 6 - 3) / 1.0), 0.15), lid=lid, brow=0.2)
    img = body(f, hands, ex, torso=torso, head=head, bob=bob, phone=phone)
    rig5.stand_in(im, img, fx, fy, tint=(0.88, 0.9, 1.0), shadow=False)
    im.alpha_composite(FG["front"])
    if phone:
        hx = fx + (CX + 80 - CX) * hh / rig5.STATURE; hy = fy - (rig5.FOOT - 820) * hh / rig5.STATURE
        im = glow(im, hx, hy - 40, 260, (150, 190, 255), 0.22)
    if scan > 0:
        p = PTS["front"]["scanner"]; im = glow(im, p[0], p[1], 170, (255, 30, 20), 0.7 * scan)
    out = im.convert("RGB")
    if monitor: out = monitor_into(out, "front", t)
    if lights < 1: out = dim(out, lights)
    return out


def comptoir_scene(t, mum=True, lights=1.0, hand_out=False, scan=0.0, mum_look=(0.6, -0.1)):
    """Over your till, looking out: the belt, the scanner, aisles 5 to 8, and her, past the end of the counter."""
    im = ST["comptoir"].copy().convert("RGBA"); P = CAL["comptoir"]
    if mum: mum_far(im, P, MUM_C[0], MUM_C[1], t, look=mum_look, warm=0.45, hand_out=hand_out)
    im.alpha_composite(FG["comptoir"])
    if scan > 0:
        p = PTS["comptoir"]["scanner"]; im = glow(im, p[0], p[1], 200, (255, 30, 20), 0.7 * scan)
    out = im.convert("RGB")
    if lights < 1: out = dim(out, lights)
    return out


def comptoir_xy():
    fx, fy, hh = CAL["comptoir"](*MUM_C); return fx, fy, hh


def aisle_shoulder(t, t0, t1):
    """Over your shoulder, down aisle 7: she waits in the only warm pool. The camera creeps in."""
    im = ST["aisle"].copy().convert("RGBA"); P = CAL["aisle"]
    bx, by, bh = P(-0.25, -9.6); basket(im, bx, by, bh / 900)
    fx, fy, hh = mum_far(im, P, 0.4, -9.5, tw(t), look=(0.0, 0.1))
    d = ImageDraw.Draw(im)                                             # the hanging sign
    sx, sy = SW * 0.5, 300
    d.line((sx - 150, 0, sx - 150, sy), fill=(60, 60, 70), width=6); d.line((sx + 150, 0, sx + 150, sy), fill=(60, 60, 70), width=6)
    d.rounded_rectangle((sx - 230, sy, sx + 230, sy + 170), 14, fill=(214, 216, 222), outline=INK, width=8)
    d.text((sx, sy + 85), "ALLÉE 7", font=font("Black", 92), fill=INK, anchor="mm")
    back = tinted(scene5.back5("toi"), (0.62, 0.66, 0.8)).resize((1560, 1560), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3))
    u = ease((t - t0) / max(0.1, t1 - t0))
    fr = view(im, 1.05 + 0.6 * u, fx, fy - hh * 0.6 + 200 * (1 - u), t, shake=1.0, seed=4).convert("RGBA")
    fr.alpha_composite(back, (int(-760 + 6 * wob(t, 9)), int(1060 + 30 * u)))
    return fr.convert("RGB")


# ---------------------------------------------------------------- phone: Samir's video call
PW, PH = 640, 1240
_ROOM = {}
def room(kind):
    """Your living room at night, flat 2D, as Samir films it: the couch, the floor lamp, the window. kind: 'mum'
    (she is asleep under the blanket), 'empty' (the blanket on the floor)."""
    if kind in _ROOM: return _ROOM[kind]
    im = Image.new("RGBA", (PW, PH), (28, 26, 44, 255)); d = ImageDraw.Draw(im)
    d.rectangle((0, 820, PW, PH), fill=(46, 36, 44)); d.line((0, 820, PW, 820), fill=INK, width=6)
    d.rounded_rectangle((60, 150, 300, 470), 10, fill=(24, 40, 78), outline=INK, width=8); d.line((180, 150, 180, 470), fill=INK, width=6)
    d.ellipse((210, 200, 262, 252), fill=(236, 232, 210))
    gl = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((380, 160, 660, 440), fill=(255, 190, 110, 120)); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(im); d.line((540, 300, 540, 820), fill=INK, width=8); d.polygon([(480, 300), (600, 300), (570, 220), (510, 220)], fill=(250, 210, 140), outline=INK, width=6)
    d.rounded_rectangle((30, 640, 610, 900), 40, fill=(52, 88, 104), outline=INK, width=8)                       # the couch
    d.rounded_rectangle((20, 600, 120, 900), 40, fill=(44, 76, 92), outline=INK, width=8); d.rounded_rectangle((520, 600, 620, 900), 40, fill=(44, 76, 92), outline=INK, width=8)
    d.rounded_rectangle((60, 540, 580, 690), 40, fill=(60, 100, 118), outline=INK, width=8)
    if kind == "mum":
        hd = toon5.bust5("maman", blink=True, mouth_="line", size=400).crop((40, 20, 360, 330)).rotate(90, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(hd, (70, 450))                                      # her head on the armrest, asleep
        d = ImageDraw.Draw(im)
        d.polygon([(330, 600), (600, 590), (612, 760), (560, 800), (330, 800), (300, 700)], fill=(150, 96, 170), outline=INK, width=8)       # the blanket
        for k in range(4): d.line((250 + k * 90, 650, 230 + k * 95, 790), fill=(120, 72, 140), width=5)
    else:
        d.polygon([(300, 880), (560, 860), (600, 950), (330, 990)], fill=(150, 96, 170), outline=INK, width=8)
    _ROOM[kind] = im; return im


def call_screen(t, key, mood="laugh", rear=None):
    """The video call: Samir's face (front camera) or what he films (rear camera), the call UI, your face in the box."""
    if rear:
        sc = room(rear).copy(); d = ImageDraw.Draw(sc)
        if rear == "mum":                                              # she snores
            for k in range(3):
                u = ((t * 0.6 + k / 3) % 1); d.text((150 + 40 * u, 560 - 160 * u), "z", font=font("hand", int(50 + 40 * u)), fill=(240, 240, 255, int(255 * (1 - u))))
        d.rounded_rectangle((24, 190, 300, 240), 25, fill=(0, 0, 0, 170)); d.text((44, 215), "caméra arrière", font=font("SemiBold", 26), fill=(255, 255, 255), anchor="lm")
    else:
        sc = room("mum").filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.8)).convert("RGBA")
        a = amp(key, tw(t))
        ex = {"laugh": dict(brow=-0.2, mouth_="smile" if a > 0.3 else "line"), "whisper": dict(brow=0.9, wide=1.15, mouth_="o" if a > 0.25 else "line"),
              "panic": dict(brow=1.0, wide=1.25, mouth_="o" if a > 0.3 else "fear")}[mood]
        sp = bust("samir", 900, look=(0.0, 0.0), lid=lid_at(t, 0.4), **ex)
        sc.alpha_composite(sp, (int(PW / 2 - 450 + 8 * wob(t, 2)), int(300 + 10 * abs(wob(t, 5, 1.5)))))
    d = ImageDraw.Draw(sc)
    sv = bust("toi", 260, look=(0.0, 0.3), brow=0.6, lid=lid_at(t)).crop((30, 0, 230, 230))
    box_ = Image.new("RGBA", (200, 230), (40, 40, 60, 255)); box_.alpha_composite(sv)
    m = Image.new("L", box_.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 199, 229), 22, fill=255)
    sc.paste(box_, (PW - 230, 290), m); d.rounded_rectangle((PW - 230, 290, PW - 30, 520), 22, outline=(255, 255, 255), width=4)
    d.rounded_rectangle((24, 120, 230, 172), 26, fill=GREEN); d.ellipse((44, 136, 64, 156), fill=(170, 255, 200)); d.text((76, 146), "SAMIR", font=font("Black", 30), fill=(255, 255, 255), anchor="lm")
    s_ = int(t) + 47; d.text((250, 146), f"{s_ // 60:02d}:{s_ % 60:02d}", font=font("SemiBold", 28), fill=(255, 255, 255), anchor="lm")
    for x, col in ((PW * 0.3, (225, 50, 50)), (PW * 0.7, (70, 72, 90))): d.ellipse((x - 46, PH - 150, x + 46, PH - 58), fill=col)
    return sc


def notif(im, t, t0, who, body_, y=360, now=False):
    """A text arriving at the top of the screen (frame 0 can show it already: now=True)."""
    if t < t0 and not now: return im
    u = 1.0 if now else ease((t - t0) / 0.25); yy = y - 160 * (1 - u)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((60, yy, 1020, yy + 150), 34, fill=(28, 28, 36, 235), outline=(255, 255, 255, 60), width=2)
    d.ellipse((90, yy + 33, 174, yy + 117), fill=PINK); d.text((132, yy + 75), "M", font=font("Black", 44), fill=(255, 255, 255), anchor="mm")
    d.text((198, yy + 48), who, font=font("Bold", 36), fill=(255, 255, 255), anchor="lm"); d.text((990, yy + 48), "maintenant", font=font("Regular", 26), fill=(190, 190, 200), anchor="rm")
    d.text((198, yy + 100), body_, font=font("Regular", 36), fill=(236, 236, 240), anchor="lm")
    im = im.convert("RGBA"); im.alpha_composite(lay); return im.convert("RGB")


def pov_phone(t, screen, bg="front", tilt=-2.0, z0=1.0):
    """Your hands hold the phone in front of the till; the screen lights them."""
    im = blurred("comptoir" if bg == "comptoir" else "front", 18, 0.5).resize((W, H), Image.BICUBIC).convert("RGBA")
    ph = Image.new("RGBA", (PW + 40, PH + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(ph)
    d.rounded_rectangle((0, 0, PW + 39, PH + 39), 70, fill=(16, 16, 22, 255), outline=INK + (255,), width=6)
    m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW - 1, PH - 1), 54, fill=255)
    ph.paste(screen.convert("RGB"), (20, 20), m); ImageDraw.Draw(ph).rounded_rectangle((PW / 2 - 70, 34, PW / 2 + 90, 70), 18, fill=(8, 8, 10))
    ph = ph.rotate(tilt + 1.2 * wob(t, 3, 0.5), expand=True, resample=Image.BICUBIC)
    s = z0; ph = ph.resize((int(ph.width * s), int(ph.height * s)), Image.LANCZOS)
    x = int(540 - ph.width / 2 + 8 * wob(t, 1, 0.6)); y = int(300 + 10 * wob(t, 6, 0.5))
    im = glow(im, 540, 980, 520, (150, 180, 255), 0.25)
    im.alpha_composite(ph, (x, y))
    d = ImageDraw.Draw(im)                                             # your thumbs and sleeves, flat, outlined
    for s_ in (-1, 1):
        hx = 540 + s_ * (PW / 2 + 10); hy = 1500 + 10 * wob(t, 2 + s_, 0.5)
        d.polygon([(hx - s_ * 40, hy - 40), (hx + s_ * 150, hy + 10), (hx + s_ * 230, H), (hx - s_ * 120, H)], fill=PURPLE, outline=INK, width=8)
        d.line((hx + s_ * 40, hy + 40, hx + s_ * 120, H), fill=(240, 240, 248), width=12)
        d.ellipse((hx - 70, hy - 110, hx + 70, hy + 40), fill=(236, 196, 162), outline=INK, width=8)
    return im.convert("RGB")


# ---------------------------------------------------------------- inserts (flat 2D, like the references' story objects)
def paper(w, h, seed, col=(244, 240, 228)):
    rg = np.random.default_rng(seed); a = np.ones((h, w, 3), np.float32) * np.array(col, np.float32)
    n = cv2.GaussianBlur(rg.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 3) * 4 + rg.normal(0, 2.2, (h, w))
    a += n[..., None]; return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def on_dark(layer, t, bgname="comptoir", y=960, rot=-2.0, z0=1.0, z1=1.08, t0=0.0, t1=3.0, red=0.0):
    """Lay a flat object on the blurred, darkened set; a slow push-in."""
    bg = blurred(bgname, 22, 0.42).resize((W, H), Image.BICUBIC).convert("RGBA")
    if red: bg = glow(bg, 540, 1500, 700, (255, 30, 20), 0.25 * red).convert("RGBA")
    s = z0 + (z1 - z0) * ease((t - t0) / max(0.1, t1 - t0))
    ob = layer.resize((int(layer.width * s), int(layer.height * s)), Image.LANCZOS).rotate(rot + 0.4 * wob(t, 7, 0.5), expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", ob.size, (0, 0, 0, 0)); sh.putalpha(ob.getchannel("A").point(lambda v: int(v * 0.6)))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)), (int(540 - ob.width / 2 + 16), int(y - ob.height / 2 + 26)))
    bg.alpha_composite(ob, (int(540 - ob.width / 2 + 4 * wob(t, 8, 0.4)), int(y - ob.height / 2)))
    return bg.convert("RGB")


RULES = ["1. Ne quitte jamais ta caisse avant 6 h.", "2. Chaque client paie. Personne ne", "    repart sans ticket.", "3. Si un ticket sort tout seul,", "    lis-le. En silence."]
RULE_ROWS = {1: [0], 2: [1, 2], 3: [3, 4]}
_RS = {}
def rules_sheet(t, hi, conflict=0.0):
    """The sheet taped under the till: three rules in the manager's hand; each lights up as it is said (hi: {rule: t0})."""
    if "p" not in _RS:
        p = paper(900, 860, 5); d = ImageDraw.Draw(p)
        d.text((450, 90), "CAISSE 3 · LA NUIT", font=font("hand", 74), fill=(30, 30, 40), anchor="mm"); d.line((120, 140, 740, 140), fill=(30, 30, 40), width=4)
        for k, r in enumerate(RULES): d.text((60, 200 + k * 112), r, font=font("hand", 54), fill=(26, 34, 70))
        d.text((620, 790), "— la direction", font=font("hand", 44), fill=(26, 34, 70))
        for x0, a in ((40, -14), (680, 12)):                            # the tape
            tp = Image.new("RGBA", (200, 70), (236, 228, 190, 170)).rotate(a, expand=True); p.alpha_composite(tp, (x0, -10))
        _RS["p"] = p
    p = _RS["p"].copy(); lay = Image.new("RGBA", p.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for r, t0 in hi.items():
        u = ease((t - t0) / 0.45)
        if u <= 0: continue
        for row in RULE_ROWS[r]:
            wd = d.textlength(RULES[row].rstrip(), font=font("hand", 54)) + 20; x0 = 50
            d.rounded_rectangle((x0, 200 + row * 112 + 6, x0 + wd * u, 200 + row * 112 + 76), 10, fill=(255, 226, 40, 120) if not conflict else (255, 60, 60, 110))
    p.alpha_composite(lay)
    if conflict > 0:
        d = ImageDraw.Draw(p); u = ease(conflict / 0.4)
        d.text((820, 430), "?!", font=font("hand", int(140 * (0.6 + 0.4 * u))), fill=RED, anchor="mm")
    return p


ITEMS = [("FARINE", "1,09"), ("EAU", "0,45"), ("RIZ", "1,89"), ("MIEL", "4,90"), ("EPINARDS", "2,30")]
_TK = {}
def ticket_img(n_items, letters=0.0, word=0.0, hidden_total=False):
    """The receipt that prints itself: five items. letters: 0..5, the first letters circled one by one; word: FERME written under."""
    key = (n_items, round(letters, 1), round(word, 1))
    if key in _TK: return _TK[key]
    w, h = 600, 1120; p = paper(w, h, 21, (246, 246, 240)); d = ImageDraw.Draw(p)
    f = font("mono", 40); fs = font("mono", 30)
    d.text((w / 2, 70), "SUPER NUIT 24/24", font=font("mono", 46), fill=(30, 30, 34), anchor="mm")
    d.text((w / 2, 124), "CAISSE 3       02:15", font=fs, fill=(30, 30, 34), anchor="mm"); d.text((w / 2, 166), "CLIENT : ---", font=fs, fill=(30, 30, 34), anchor="mm")
    d.text((40, 200), "-" * 26, font=f, fill=(30, 30, 34))
    for k, (it, pr) in enumerate(ITEMS[:n_items]):
        y = 270 + k * 84; d.text((50, y), it, font=f, fill=(30, 30, 34)); d.text((w - 50, y), pr + " €", font=f, fill=(30, 30, 34), anchor="ra")
        u = cl(letters - k)
        if u > 0:
            d.arc((36, y - 12, 92, y + 56), -90, -90 + 360 * ease(u), fill=RED, width=6)
    if n_items >= 5 and word <= 0:
        d.text((40, 690), "-" * 26, font=f, fill=(30, 30, 34)); d.text((50, 750), "TOTAL", font=f, fill=(30, 30, 34)); d.text((w - 50, 750), "10,63 €", font=f, fill=(30, 30, 34), anchor="ra")
        d.text((w / 2, 850), "MERCI. A DEMAIN.", font=fs, fill=(30, 30, 34), anchor="mm")
    if word > 0:
        txt = "FERME"[: max(1, int(round(5 * cl(word / 0.6))))]
        d.text((w / 2, 760), txt, font=font("hand", 170), fill=RED, anchor="mm")
    m = Image.new("L", (w, h), 255); md = ImageDraw.Draw(m)
    for x in range(0, w, 30): md.polygon([(x, h), (x + 15, h - 20), (x + 30, h)], fill=0)
    p.putalpha(m); _TK[key] = p; return p


def on_dark_t(layer, t, bgname, y=900, rot=-2.0, z0=1.0, z1=1.08, t0=0.0, t1=3.0):
    return on_dark(layer, t, bgname, y=860, rot=rot, z0=z0 * 0.86, z1=z1 * 0.86, t0=t0, t1=t1)


def printer_shot(t, t0, t1):
    """The printer wakes up on its own: the paper slides out, line after line."""
    bg = blurred("comptoir", 22, 0.42).resize((W, H), Image.BICUBIC).convert("RGBA")
    bg = glow(bg, 540, 1500, 700, (255, 30, 20), 0.18).convert("RGBA")
    u = ease((t - t0 - 0.3) / max(0.3, t1 - t0 - 0.3)); tk = ticket_img(5); out_h = int(80 + 760 * u)
    strip = tk.crop((0, 0, tk.width, out_h)).transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_TOP_BOTTOM)
    bg.alpha_composite(strip.crop((0, max(0, out_h - 900), tk.width, out_h)), (240, 700))
    d = ImageDraw.Draw(bg)                                             # the printer, drawn flat in front of the paper's root
    d.rounded_rectangle((170, 470, 910, 730), 40, fill=(42, 44, 52), outline=INK, width=10)
    d.rounded_rectangle((220, 520, 860, 600), 20, fill=(26, 26, 32), outline=INK, width=6); d.rectangle((230, 690, 850, 712), fill=(10, 10, 12))
    if (t * 4) % 1 < 0.5: d.ellipse((800, 630, 834, 664), fill=(60, 230, 110))
    d.text((300, 650), "SN-80", font=font("Bold", 34), fill=(150, 150, 160), anchor="lm")
    s = 1.0 + 0.06 * ease((t - t0) / 3); return view(bg, s, W / 2, 800, t, shake=0.8, seed=5)


def banknote(t, t0):
    """A fifty on the belt, soaking: drops run off its edge into a small puddle."""
    bg = Image.new("RGBA", (W, H), (14, 14, 18, 255)); d = ImageDraw.Draw(bg)
    for y in range(-80, H + 80, 46):
        yy = y + (t * 8) % 46; d.line((0, yy, W, yy), fill=(30, 30, 36), width=6)
    note = Image.new("RGBA", (720, 380), (0, 0, 0, 0)); nd = ImageDraw.Draw(note)
    nd.rounded_rectangle((0, 0, 719, 379), 18, fill=(196, 128, 76), outline=INK, width=8); nd.rounded_rectangle((30, 30, 690, 350), 10, outline=(150, 90, 52), width=4)
    nd.text((80, 90), "50", font=font("anton", 120), fill=(120, 66, 34), anchor="mm"); nd.text((640, 290), "50", font=font("anton", 120), fill=(120, 66, 34), anchor="mm")
    nd.ellipse((280, 110, 440, 270), fill=(214, 156, 104), outline=(150, 90, 52), width=6); nd.ellipse((320, 150, 400, 230), fill=(150, 90, 52)); nd.ellipse((342, 140, 416, 214), fill=(214, 156, 104))
    nd.text((540, 90), "EURO", font=font("Black", 46), fill=(120, 66, 34), anchor="mm")
    rg = np.random.default_rng(4)
    for k in range(12):                                                # wet stains
        x, y, r = rg.uniform(40, 680), rg.uniform(40, 340), rg.uniform(20, 60); nd.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=(176, 112, 70, 255))
    note = note.rotate(-8, expand=True, resample=Image.BICUBIC); nx, ny = 540 - note.width // 2, 820 - note.height // 2
    bg.alpha_composite(note, (nx, ny)); d = ImageDraw.Draw(bg, "RGBA")
    pu = ease((t - t0) / 2.5); d.ellipse((260 - 120 * pu, 1110, 820 + 80 * pu, 1170 + 30 * pu), fill=(120, 150, 200, 70))
    for k in range(7):
        x = 300 + k * 75 + 12 * math.sin(k); per = 0.7 + 0.13 * k; u = ((t - t0) / per + k * 0.31) % 1
        y = 1040 + 100 * u * u; d.ellipse((x - 9, y - 14, x + 9, y + 12), fill=(200, 226, 255, 220)); d.ellipse((x - 4, y - 9, x + 1, y - 4), fill=(255, 255, 255, 230))
    bg = glow(bg, 540, 820, 600, (255, 210, 160), 0.10)
    return view(bg, 1.0 + 0.08 * ease((t - t0) / 3), W / 2, 880, t, shake=0.6, seed=2)


def hands_shot(t, t0):
    """A: your hand holds out the change; hers closes over it. Grey, too still. Then the cold spreads."""
    bg = blurred("comptoir", 22, 0.35).resize((W, H), Image.BICUBIC).convert("RGBA"); d = ImageDraw.Draw(bg)
    tc = wt("a1", "referme") - 0.1; tf = wt("a1", "froide") - 0.1
    tr = 3 * math.sin(t * 2 * math.pi * 10) * cl((t - tf) / 0.2)
    d.polygon([(560, 1920), (1080, 1500), (1080, 1920)], fill=PURPLE, outline=INK, width=10); d.line((760, 1920, 1080, 1660), fill=(240, 240, 248), width=16)
    hx, hy = 560 + tr, 1240
    d.ellipse((hx - 190, hy - 120, hx + 230, hy + 210), fill=(236, 196, 162), outline=INK, width=10)          # your open palm
    d.line((hx + 230, hy + 210, 1080, 1500), fill=INK, width=10)
    for k, (dx, dy) in enumerate(((-60, 10), (30, -20), (100, 40), (-10, 70))):                                # the coins
        col = (214, 176, 84) if k % 2 == 0 else (196, 200, 210)
        d.ellipse((hx + dx - 48, hy + dy - 48, hx + dx + 48, hy + dy + 48), fill=col, outline=INK, width=6); d.ellipse((hx + dx - 28, hy + dy - 28, hx + dx + 28, hy + dy + 28), outline=tuple(int(v * 0.8) for v in col), width=4)
    u = settle(t - tc, 9, 0.6) if t > tc else 0.25 * ease((t - t0) / max(0.1, tc - t0))
    my = -500 + 1640 * u                                               # her hand comes down from the top and closes
    d.polygon([(380, my - 900), (760, my - 900), (720, my - 220), (420, my - 220)], fill=PINK, outline=INK, width=10)
    sk = (176, 180, 186)
    d.rounded_rectangle((400, my - 260, 740, my + 40), 80, fill=sk, outline=INK, width=10)
    for k in range(4):
        fx_ = 430 + k * 80; d.rounded_rectangle((fx_, my - 20, fx_ + 66, my + 170 + 20 * math.sin(k * 1.3)), 33, fill=sk, outline=INK, width=9)
        d.line((fx_ + 14, my + 130, fx_ + 52, my + 130), fill=(120, 124, 134), width=4)
    if t > tf:                                                         # the frost
        f_ = ease((t - tf) / 0.8); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); rg = np.random.default_rng(3)
        for k in range(40):
            a0 = rg.uniform(0, 2 * math.pi); r = rg.uniform(60, 420) * f_; x0, y0 = 580, 1220
            ld.line((x0, y0, x0 + r * math.cos(a0), y0 + r * math.sin(a0) * 0.7), fill=(220, 240, 255, 180), width=3)
        bg.alpha_composite(lay); bg = Image.blend(bg.convert("RGB"), Image.new("RGB", (W, H), (120, 170, 255)), 0.18 * f_).convert("RGBA")
    return view(bg, 1.0 + 0.05 * ease((t - t0) / 4), W / 2, 1000, t, shake=0.7, seed=3)


def terminal(t, t0):
    """The till's card reader: someone has paid. The card holder is you."""
    bg = blurred("front", 20, 0.4).resize((W, H), Image.BICUBIC).convert("RGBA"); d = ImageDraw.Draw(bg)
    d.rounded_rectangle((240, 420, 840, 1460), 70, fill=(34, 36, 44), outline=INK, width=12)
    d.rounded_rectangle((300, 490, 780, 980), 26, fill=(20, 56, 64), outline=INK, width=8)
    d.text((540, 550), "CAISSE 3 · 02:14", font=font("mono", 34), fill=(170, 230, 230), anchor="mm")
    d.text((540, 640), "SANS CONTACT", font=font("Black", 50), fill=(230, 250, 250), anchor="mm")
    if t > t0 + 0.4: d.text((540, 730), "✓ PAYÉ  10,63 €", font=font("mono", 44), fill=(120, 240, 150), anchor="mm")
    if t > wt("t2", "carte") - 0.1:
        d.text((540, 820), "CARTE •••• 4271", font=font("mono", 40), fill=(230, 250, 250), anchor="mm")
        d.text((540, 905), "TITULAIRE : TOI", font=font("mono", 46), fill=(255, 80, 80), anchor="mm")
    for r in range(3):
        for c in range(3): d.rounded_rectangle((330 + c * 150, 1030 + r * 130, 450 + c * 150, 1130 + r * 130), 20, fill=(60, 62, 72), outline=INK, width=6)
    bg = glow(bg, 540, 735, 380, (90, 220, 220), 0.18)
    return view(bg, 1.0 + 0.1 * ease((t - t0) / 2.5), W / 2, 820, t, shake=0.7, seed=6)


def rule_card(t, t0):
    """RÈGLE N°10, in red, on the back of the ticket: the outline first, then it fills; the rule is written as it is said."""
    p = paper(800, 1100, 33, (240, 236, 222)); d = ImageDraw.Draw(p)
    u = cl((t - t0 - 0.1) / 0.5); f = font("hand", 150)
    if u < 0.5: d.text((400, 230), "RÈGLE N°10", font=f, fill=(0, 0, 0, 0), anchor="mm", stroke_width=4, stroke_fill=RED)
    else: d.text((400, 230), "RÈGLE N°10", font=f, fill=RED, anchor="mm")
    txt = ["Ne rends jamais", "la monnaie à", "quelqu'un sans", "ombre."]; n = int(max(0, (t - wt("r10", "rends") + 0.3) * 26)); y = 430
    for ln in txt:
        d.text((90, y), ln[:max(0, n)], font=font("hand", 96), fill=RED); n -= len(ln); y += 130
    im = on_dark(p, t, "front", y=900, rot=-2.5, z0=0.96, z1=1.04, t0=t0, t1=t0 + 4)
    st = t - t0 - 0.6
    if st > 0:                                                         # the stamp
        f2 = font("Black", 120); wd = 560; stp = Image.new("RGBA", (wd, 200), (0, 0, 0, 0)); sd = ImageDraw.Draw(stp)
        sd.rounded_rectangle((8, 8, wd - 8, 192), 18, outline=RED + (240,), width=14); sd.text((wd / 2, 100), "PERDU", font=f2, fill=RED + (240,), anchor="mm")
        s_ = 1.5 - 0.5 * cl(st / 0.14); stp = stp.resize((int(wd * s_), int(200 * s_))).rotate(-10, expand=True, resample=Image.BICUBIC)
        im = im.convert("RGBA"); im.alpha_composite(stp, (int(540 - stp.width / 2), int(1450 - stp.height / 2))); im = im.convert("RGB")
    return im


# ---------------------------------------------------------------- titles and buttons
def banner(im, t, t0, txt, y=640, t1=None):
    if t < t0 or (t1 and t > t1): return im
    u = cl((t - t0) / 0.16); s = 1.25 - 0.25 * ease(u)
    f = font("Black", 64); tw_ = ImageDraw.Draw(im).textlength(txt, font=f)
    lay = Image.new("RGBA", (int(tw_ + 80), 120), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle((0, 0, lay.width, 120), fill=YEL + (255,)); d.text((lay.width / 2, 60), txt, font=f, fill=INK, anchor="mm")
    lay = lay.resize((int(lay.width * s), int(120 * s)), Image.LANCZOS).rotate(-2.5, expand=True, resample=Image.BICUBIC)
    im = im.convert("RGBA"); im.alpha_composite(lay, (int(540 - lay.width / 2), int(y - lay.height / 2))); return im.convert("RGB")


def plate(im, t, t0, txt, col, xy=(70, 1390)):
    if t < t0: return im
    u = ease((t - t0) / 0.2); d = ImageDraw.Draw(im); f = font("Black", 40); wd = d.textlength(txt, font=f) + 70
    x, y = xy[0] - 40 * (1 - u), xy[1]
    d.rounded_rectangle((x, y, x + wd, y + 74), 37, fill=col); d.text((x + wd / 2, y + 37), txt, font=f, fill=(255, 255, 255), anchor="mm")
    return im


def tag(im, t, t0, txt, xy, col=RED, angle=-4, size=46):
    if t < t0: return im
    f = font("Black", size); d0 = ImageDraw.Draw(im); wd = d0.textlength(txt, font=f) + 50
    lay = Image.new("RGBA", (int(wd), size + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, wd - 1, size + 39), 12, fill=col + (255,)); d.text((wd / 2, (size + 40) / 2), txt, font=f, fill=(255, 255, 255), anchor="mm")
    s = 1.2 - 0.2 * ease((t - t0) / 0.14); lay = lay.resize((int(lay.width * s), int(lay.height * s))).rotate(angle, expand=True, resample=Image.BICUBIC)
    im = im.convert("RGBA"); im.alpha_composite(lay, (int(xy[0] - lay.width / 2), int(xy[1] - lay.height / 2))); return im.convert("RGB")


CHOICE = ("TU RENDS LA MONNAIE", "TU FERMES TA CAISSE")
def choice_card(im, t, ta, tb, t_end, hint):
    """The versus slam: A from the left, B from the right, they hit and the frame shakes; the bar runs out."""
    im = dim(im, 0.5, (1.0, 1.0, 1.0)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.text((540, 560), "A OU B ?", font=font("anton", 150), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=INK)
    d.text((540, 680), "ÉCRIS-LE EN COMMENTAIRE", font=font("Black", 44), fill=YEL, anchor="mm", stroke_width=5, stroke_fill=INK)
    for k, (lab, t0, col) in enumerate(((CHOICE[0], ta, (250, 250, 250)), (CHOICE[1], tb, (250, 250, 250)))):
        if t < t0: continue
        u = settle(t - t0, 16, 0.5); x0 = 110 + (1 - u) * (-900 if k == 0 else 900); y = 800 + k * 170
        d.rounded_rectangle((x0, y, x0 + 860, y + 130), 65, fill=col, outline=ORANGE if k == 0 else PURPLE, width=10)
        d.ellipse((x0 + 18, y + 15, x0 + 118, y + 115), fill=ORANGE if k == 0 else PURPLE); d.text((x0 + 68, y + 65), "AB"[k], font=font("Black", 60), fill=(255, 255, 255), anchor="mm")
        d.text((x0 + 500, y + 65), lab, font=font("Black", 50), fill=INK, anchor="mm")
    if t > tb:
        left = cl((t_end - t) / max(0.1, t_end - tb)); d.rounded_rectangle((160, 1150, 920, 1170), 10, fill=(40, 40, 46)); d.rounded_rectangle((160, 1150, 160 + int(760 * left), 1170), 10, fill=RED)
        d.text((540, 1230), hint, font=font("hand", 64), fill=(255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=INK)
    out = im.convert("RGB"); hit = t - tb
    if 0 < hit < 0.25:
        out = out.transform((W, H), Image.AFFINE, (1, 0, 14 * math.sin(hit * 90) * (1 - hit / 0.25), 0, 1, 0))
        out = Image.blend(out, Image.new("RGB", (W, H), (255, 255, 255)), 0.35 * (1 - hit / 0.25))
    return out


def end_card(im, t, t0, prompt, costs):
    u = ease((t - t0) / 0.35); im = Image.blend(im, Image.new("RGB", (W, H), (8, 6, 12)), 0.78 * u)
    if u <= 0: return im
    d = ImageDraw.Draw(im)
    d.text((540, 470), "TU FERAIS QUOI ?", font=font("anton", 120), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=INK)
    for k, (lab, sub) in enumerate(costs):
        if t < t0 + 0.25 + k * 0.25: continue
        y = 640 + k * 250; col = ORANGE if k == 0 else PURPLE
        d.rounded_rectangle((110, y, 970, y + 120), 60, fill=col); d.text((540, y + 60), ("A · ", "B · ")[k] + lab, font=font("Black", 46), fill=(255, 255, 255), anchor="mm")
        d.text((540, y + 170), sub, font=font("SemiBold", 38), fill=(226, 226, 232), anchor="mm")
    if t > t0 + 0.9:
        for k, ln in enumerate(prompt): d.text((540, 1180 + k * 66), ln, font=font("Black", 44), fill=YEL, anchor="mm")
    return im


# ---------------------------------------------------------------- captions, HUD, grade
GROUPS = []
_cur = []
for _n, w in enumerate(words):
    _cur.append(w)
    last = _n + 1 == len(words) or words[_n + 1]["line"] != w["line"]
    if len(_cur) == 3 or w["w"].endswith((".", ",", "…", "?", ":", "!")) or last:
        GROUPS.append(_cur); _cur = []


def captions(im, t, y=1270):
    """At most three words, each appears when it is spoken, the spoken word orange, heavy white capitals."""
    g = None
    for n, gr in enumerate(GROUPS):
        nxt = GROUPS[n + 1][0]["s"] - 0.04 if n + 1 < len(GROUPS) and GROUPS[n + 1][0]["line"] == gr[-1]["line"] else gr[-1]["e"] + 0.45
        if gr[0]["s"] - 0.04 <= t < nxt: g = gr
    if not g: return im
    d = ImageDraw.Draw(im); txt = [x["w"].upper() for x in g]; size = 76
    while size > 50 and d.textlength(" ".join(txt), font=font("Black", size)) > 860: size -= 4
    f = font("Black", size); widths = [d.textlength(x + " ", font=f) for x in txt]
    x = W / 2 - (sum(widths) - d.textlength(" ", font=f)) / 2
    for wd, s_, wi in zip(g, txt, widths):
        if t >= wd["s"] - 0.04:
            now = t <= wd["e"] + 0.06; age = t - wd["s"] + 0.04; yy = y + int(12 * max(0.0, 1 - age / 0.09))
            d.text((x + 4, yy + 6), s_, font=f, fill=(0, 0, 0), anchor="ls")
            d.text((x, yy), s_, font=f, fill=ORANGE if now else (250, 250, 250), anchor="ls", stroke_width=6, stroke_fill=INK)
        x += wi
    return im


def hud(im, t):
    if VID == "A":
        t_m = L_("m1")
        if t < t_m: lab, val = "ELLE ARRIVE", int(math.ceil(60 * (1 - t / t_m)))
        elif t < L_("n12b"): lab, val = "ELLE EST LÀ", 0
        else: lab, val = "CHOIX", max(0, 50 - int(t - wt("n12b", "cinquante")))
        v = f"00:{val:02d}" if val < 60 else "01:00"
    else:
        if t < t_rew: m = 15 + int(t / 22)
        else: m = 16 + int((t - t_rew) / 9)
        lab, v = "IL EST", f"02:{m:02d}"
    scene5.hud(im, "Caissier de nuit", "Caisse 3", None, lab, v)
    return im


yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.55 * (1 - np.clip(1 - (((xx_ - W / 2) / (W * 0.8)) ** 2 + ((yy_ - H * 0.48) / (H * 0.66)) ** 2), 0, 1) ** 0.8))[..., None]
def grade(im, i, cold=1.0):
    """The night grade: shadows lean blue-violet, a little contrast, a vignette, a fine grain that changes every frame."""
    a = np.asarray(im).astype(np.float32) / 255
    a = a * VIG; sh = (1 - a) ** 4
    a = a + sh * np.array([0.012, 0.018, 0.05], np.float32) * cold
    a = np.clip((a - 0.5) * 1.06 + 0.5, 0, 1)
    rg = np.random.default_rng(i); a += rg.normal(0, 0.012, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# ---------------------------------------------------------------- the shots, per video
def shots_A(t):
    """-> (image, labels list of callables(im, t) -> im, hud?, graded?)"""
    lab = []; hd = True; gr = True
    if t < L_("n2"):                                                    # HOOK: you read her text; on the monitor she is already in aisle 7
        fx, fy, hh = CAL["front"](0.0, 1.0); m = PTS["front"]["monitor"]
        im = view(front_scene(t, "phone"), 1.3 + 0.06 * ease(t / 2.6), (fx + m[0]) / 2 + 40, 960, t, seed=1)
        im = notif(im, t, 0, "Maman", "J'arrive à ta caisse.", now=True)
        lab = [lambda im, t: banner(im, t, -1, "ELLE DORT CHEZ TOI.", y=1110)]
    elif t < L_("n3"):
        fx, fy, hh = CAL["front"](0.0, 1.0); u = ease((t - L_("n2")) / 2.5)
        im = view(front_scene(t, "alone"), 1.12 + 0.06 * u, fx, fy - hh * 0.55, t, seed=2)
        lab = [lambda im, t: plate(im, t, L_("n2") + 0.3, "TOI", PURPLE)]
    elif t < L_("n5"):
        hi = {1: wt("n4", "quitte") - 0.15, 2: wt("n4", "chacun") - 0.15, 3: wt("n4", "ticket") - 0.15}
        im = on_dark(rules_sheet(t, hi), t, "front", y=820, rot=-1.5, z0=0.9, z1=0.98, t0=L_("n3"), t1=L_("n5"), red=0.6)
    elif t < L_("s1"):
        sp = bust("toi", 1000, look=(0.3, 0.05), brow=0.8, wide=1.1, lid=lid_at(t, 0.2), mouth_="line")
        im = close_up(blurred("front", 14, 0.6).resize((W, H)), sp, t, 1.0, 1.07, L_("n5"), L_("s1"), tint=(0.86, 0.9, 1.0))
    elif t < L_("n6"):
        rear = "mum" if t > wt("s1", "filme") - 0.2 else None
        im = pov_phone(t, call_screen(t, "s1", "laugh", rear=rear))
        lab = [lambda im, t: plate(im, t, L_("s1") + 0.2, "SAMIR", GREEN, xy=(70, 1560))]
        if rear: lab.append(lambda im, t: tag(im, t, wt("s1", "filme"), "CHEZ TOI · EN DIRECT", (540, 470), RED, -3, 40))
    elif t < L_("n7"):
        fx, fy, hh = CAL["front"](0.0, 1.0); tb = wt("n6", "bip") - 0.05
        scan = (1.0 if 0 < t - tb < 0.35 or 0.55 < t - tb < 0.8 else 0.25) if t > tb else 0.0
        im = view(front_scene(t, "startle", scan=scan), 1.25, fx + 40, fy - hh * 0.6, t, seed=3)
        lab = [lambda im, t: tag(im, t, wt("n6", "personne") - 0.05, "PERSONNE.", (540, 650), RED, -4)]
    elif t < L_("n8"): im = printer_shot(t, L_("n7"), L_("n9"))
    elif t < L_("n9"):
        k = sum(1 for w_ in ("farine", "eau", "riz", "miel", "epinards") if t >= wt("n8", w_) - 0.1)
        im = on_dark_t(ticket_img(max(1, k) if k < 5 else 5), t, "comptoir", y=900, rot=-2, z0=1.0, z1=1.1, t0=L_("n8"), t1=L_("n10"))
        lab = [lambda im, t: banner(im, t, L_("n8") + 0.6, "⏸ METS PAUSE : LIS LE TICKET", y=1520)]
    elif t < T_SHOCK: im = aisle_shoulder(t, L_("n9"), T_SHOCK)
    elif t < L_("s2"):
        im = cctv(t, look_cam=True, z=1.5 + 0.25 * ease((t - T_SHOCK) / 2.5), callout=t - (wt("n10", "ombre") - 0.2))
    elif t < L_("m1"):
        rear = "mum" if t > wt("s2", "video") - 0.2 else None
        im = pov_phone(t, call_screen(t, "s2", "whisper", rear=rear), tilt=2)
        if rear: lab = [lambda im, t: tag(im, t, wt("s2", "video"), "ELLE DORT. CHEZ TOI.", (540, 470), RED, -3, 40)]
    elif t < L_("n11"):
        a = amp("m1", tw(t)); sp = bust("maman", 1000, look=(0.0, 0.0), mouth_="o" if a > 0.3 else "smile", lid=min(0.5, lid_at(t, 0.0, (L_("m1") + 1.2,))), brow=-0.3)
        im = close_up(blurred("comptoir", 14, 0.55).resize((W, H)), sp, t, 1.0, 1.05, L_("m1"), L_("n11"), tint=(1.0, 0.92, 0.86), seed=4)
        lab = [lambda im, t: plate(im, t, L_("m1") + 0.2, "TA MÈRE", PINK)]
    elif t < L_("n12"): im = banknote(t, L_("n11"))
    elif t < L_("n12b"):
        hi = {1: -99, 2: wt("n12", "deux") - 0.1, 3: wt("n12", "trois") - 0.1}; hi.pop(1)
        im = on_dark(rules_sheet(t, hi, conflict=t - wt("n12", "trois") - 0.4), t, "front", y=820, rot=1.5, z0=0.94, z1=1.0, t0=L_("n12"), t1=L_("n12b"), red=0.8)
        lab = [lambda im, t: banner(im, t, wt("n12", "trois") + 0.2, "DEUX RÈGLES. UN CHOIX.", y=1500)]
    elif t < L_("n13"):
        fx, fy, hh = CAL["front"](0.0, 1.0); im = view(front_scene(t, "fear"), 1.45, fx, fy - hh * 0.68, t, shake=1.6, seed=5)
    elif t < T_END:
        fx, fy, hh = comptoir_xy(); base = view(comptoir_scene(t, hand_out=True, mum_look=(0.7, -0.15)), 1.15, fx + 120, fy - hh * 0.5, t, seed=6)
        im = choice_card(base, t, wt("n13", "a") - 0.05, wt("n13", "b") - 0.05, T_END, "Indice : le ticket.")
    else:
        fx, fy, hh = comptoir_xy(); base = view(comptoir_scene(t, hand_out=True), 1.15, fx + 120, fy - hh * 0.5, t, seed=6)
        im = end_card(grade(base, int(t * 30)), t, T_END, ["Le mot caché du ticket,", "tu l'as trouvé ? Écris-le."],
                      [("Tu rends la monnaie", "Règle 2 : chacun paie."), ("Tu fermes ta caisse", "Tu restes seul avec elle.")])
        hd = False; gr = False
    return im, lab, hd, gr


def shots_B(t):
    lab = []; hd = True; gr = True
    if t < L_("n3"):                                                    # HOOK: a woman without a shadow holds out a wet note
        tc = wt("p1v3", "tend") - 0.1
        if t < tc:
            im = cctv_till(t, z=1.25 + 0.15 * ease(t / tc), cy=SH * 0.56, callout=t - (wt("p1v3", "ombre") - 0.2))
        else:
            fx, fy, hh = comptoir_xy(); im = view(comptoir_scene(t, hand_out=True, mum_look=(0.7, -0.15)), 1.3 + 0.1 * ease((t - tc) / 2), fx + 120, fy - hh * 0.6, t, seed=1)
        lab = [lambda im, t: banner(im, t, -1, "ELLE N'A PAS D'OMBRE.", y=1110),
               lambda im, t: plate(im, t, tc + 0.1, "TA MÈRE ?", PINK)]
    elif t < L_("n8"):
        hi = {1: wt("n4", "quitte") - 0.15, 2: wt("n4", "chacun") - 0.15, 3: wt("n4", "ticket") - 0.15}
        im = on_dark(rules_sheet(t, hi), t, "front", y=820, rot=-1.5, z0=0.9, z1=0.98, t0=L_("n3"), t1=L_("n8"), red=0.6)
        lab = [lambda im, t: tag(im, t, L_("n3") + 0.2, "SOUS TA CAISSE", (540, 330), PURPLE, -3, 40)]
    elif t < L_("p2"):
        k = sum(1 for w_ in ("farine", "eau", "riz", "miel", "epinards") if t >= wt("n8", w_) - 0.1)
        im = on_dark_t(ticket_img(max(1, k) if k < 5 else 5), t, "comptoir", y=900, rot=-2, z0=1.0, z1=1.06, t0=L_("n8"), t1=L_("p2"))
        lab = [lambda im, t: tag(im, t, L_("n8") + 0.2, "LE TICKET SORT TOUT SEUL", (540, 330), RED, -3, 40)]
    elif t < L_("n13"):
        ts = [wt("p2", "f"), wt("p2", "e", 0), wt("p2", "r"), wt("p2", "m"), wt("p2", "e", 1)]
        ts = [line_t["p2"] + 1.9 + 0.42 * k if (k > 0 and ts[k] <= ts[k - 1]) else ts[k] for k in range(5)]
        lt = sum(cl((t - x + 0.1) / 0.3) for x in ts); wd = t - (ts[-1] + 0.35)
        im = on_dark_t(ticket_img(5, letters=lt, word=wd), t, "comptoir", y=900, rot=-2, z0=1.06, z1=1.16, t0=L_("p2"), t1=L_("n13"))
    elif t < L_("a1"):
        fx, fy, hh = comptoir_xy(); base = view(comptoir_scene(t, hand_out=True, mum_look=(0.7, -0.15)), 1.15, fx + 120, fy - hh * 0.5, t, seed=6)
        im = choice_card(base, t, wt("n13", "a") - 0.05, wt("n13", "b") - 0.05, L_("a1"), "Indice : FERME.")
    elif t < T_SHOCK:
        im = hands_shot(t, L_("a1")); lab = [lambda im, t: banner(im, t, L_("a1") + 0.05, "SI TU CHOISIS A", y=420)]
        if t > we("a1") + 0.15: im = dim(im, max(0.25, 1 - (t - we("a1") - 0.15) / 0.6), (1, 1, 1))   # the light dies in the silence
    elif t < L_("a2"):
        sp = bust("maman", 1000, look=(0.0, -0.1), fiend=True, wide=1.2)
        im = close_up(blurred("comptoir", 14, 0.4).resize((W, H)), sp, t, 1.08, 1.14, T_SHOCK, L_("a2"), tint=(1.0, 0.9, 0.9), y=520, seed=7, shake=2.2)
    elif t < L_("a3"):
        im = cctv(t - 20, z=1.5, replay=True, callout=t - (wt("a2", "ombre") - 0.25))
    elif t < L_("r10"):
        im = on_dark_t(ticket_img(5, letters=5, word=9), t, "comptoir", y=900, rot=-2, z0=1.1, z1=1.16, t0=L_("a3"), t1=L_("r10"))
    elif t < t_rew: im = rule_card(t, L_("r10")); hd = False
    elif t < L_("b1"):
        src = view(comptoir_scene(L_("n13") + 0.5, hand_out=True), 1.15, comptoir_xy()[0] + 260, comptoir_xy()[1] - comptoir_xy()[2] * 0.5, L_("n13"), seed=6)
        im = rewind(int(t * 30), src); hd = False; gr = False
    elif t < L_("m2"):
        off = t > wt("b1", "eteins") + 0.1
        k = 1.0 if not off else max(0.16, 1 - (t - wt("b1", "eteins") - 0.1) / 0.12)
        fx, fy, hh = comptoir_xy(); im = view(comptoir_scene(t, mum_look=(0.7, -0.1), lights=k), 1.2, fx + 260, fy - hh * 0.5, t, seed=8)
        lab = [lambda im, t: banner(im, t, L_("b1") + 0.05, "SI TU CHOISIS B", y=420)]
        if wt("b1", "fermee") - 0.1 < t: lab.append(lambda im, t: tag(im, t, wt("b1", "fermee"), "CAISSE FERMÉE", (540, 640), RED, -3))
    elif t < L_("n14"):
        frozen = t > we("m2") - 0.05; tt = we("m2") - 0.05 if frozen else t
        a = amp("m2", tw(tt)); sp = bust("maman", 1000, look=(0.0, 0.0), mouth_="o" if a > 0.3 else "line", lid=1.0 if frozen else lid_at(tt, 0.5), light=-0.6)
        im = close_up(blurred("comptoir", 14, 0.22).resize((W, H)), sp, tt, 1.0, 1.05, L_("m2"), L_("n14"), tint=(0.55, 0.6, 0.85), seed=9, shake=0.0 if frozen else 1.0)
        if frozen:
            a_ = np.asarray(im).copy(); rg = np.random.default_rng(int(t * 30))
            for _ in range(5):
                y = int(rg.integers(300, 1700)); h_ = int(rg.integers(6, 30)); a_[y:y + h_] = np.roll(a_[y:y + h_], int(rg.integers(-60, 60)), axis=1)
            im = Image.fromarray(a_)
    elif t < L_("s3"):
        tr = wt("n14", "reviennent") - 0.1; fl = 1.0 if t > tr + 0.6 else (0.16 if t < tr else (1.0 if int((t - tr) * 20) % 3 else 0.3))
        fx, fy, hh = comptoir_xy(); im = view(comptoir_scene(t, mum=False, lights=fl), 1.2, fx + 260, fy - hh * 0.5, t, seed=8)
        if t > tr + 0.7: lab = [lambda im, t: tag(im, t, wt("n14", "plus") - 0.1, "PARTIE.", (540, 640), RED, -3)]
    elif t < L_("n15"):
        rear = "empty" if t > wt("s3", "demande") - 0.3 else None
        im = pov_phone(t, call_screen(t, "s3", "panic", rear=rear), tilt=-3)
        lab = [lambda im, t: plate(im, t, L_("s3") + 0.2, "SAMIR", GREEN, xy=(70, 1560))]
        if rear: lab.append(lambda im, t: tag(im, t, wt("s3", "demande"), "LE CANAPÉ EST VIDE", (540, 470), RED, -3, 40))
    elif t < L_("t1"):
        fx, fy, hh = CAL["front"](0.0, 1.0); im = view(front_scene(t, "phone"), 1.55, fx - 150, fy - hh * 0.68, t, seed=1)
        im = notif(im, t, wt("n15", "vibre") - 0.1, "Maman", "J'arrive à ta caisse.")
    elif t < L_("t2"):
        fx, fy, hh = CAL["front"](0.0, 1.0); im = view(front_scene(t, "alone", lights=0.85), 1.12, fx, fy - hh * 0.55, t, seed=2)
        lab = [lambda im, t: tag(im, t, L_("t1") + 0.1, "DEMAIN SOIR", (540, 640), PURPLE, -3)]
    elif t < T_END: im = terminal(t, L_("t2"))
    else:
        im = end_card(grade(terminal(t, L_("t2")), int(t * 30)), t, T_END, ["Tu lui rends la monnaie, toi ?", "Écris A ou B."],
                      [("Tu rends la monnaie", "Règle 2 : chacun paie."), ("Tu fermes ta caisse", "Elle a déjà ta carte.")])
        hd = False; gr = False
    return im, lab, hd, gr


def rewind(i, src):
    """A wrong choice: the tape runs back to the moment you chose. Black and white, tracking tears."""
    a = np.asarray(src).astype(np.float32) @ np.array([0.2126, 0.7152, 0.0722], np.float32); rg = np.random.default_rng(i)
    for _ in range(9):
        y = int(rg.integers(0, H - 40)); hh = int(rg.integers(6, 34)); a[y:y + hh] = np.roll(a[y:y + hh], int(rg.integers(-140, 140)), axis=1) * 1.25
    a += rg.normal(0, 14, (H, W)); a[::3] *= 0.8
    im = Image.fromarray(np.clip(np.stack([a, a, a], -1), 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    d.text((110, 560), "◀◀ REW", font=font("mono", 64), fill=(255, 255, 255))
    d.text((540, 1210), "TU RECOMMENCES.", font=font("Black", 66), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=(0, 0, 0))
    return im


def smear(src, k):
    sx = {-2: 1.7, -1: 1.25}[k]; zi = src.resize((int(W * sx), H), Image.BILINEAR); o = (zi.width - W) // 2
    return zi.crop((o, 0, o + W, H))
def negative(src):
    a = np.asarray(src).astype(np.float32) / 255; l = np.clip((a @ np.array([0.2126, 0.7152, 0.0722], np.float32)) * 1.6, 0, 1)
    return Image.fromarray((np.stack([1 - l] * 3, -1) * 255).astype(np.uint8))


SHOTS = shots_A if VID == "A" else shots_B


def render(i, t, captions_on=True):
    im, lab, hd, gr = SHOTS(t)
    if gr: im = grade(im, i)
    for f_ in lab: im = f_(im, t)
    if hd: im = hud(im, t)
    quiet = (L_("n13") <= t < T_HOLD + 1.3) or (VID == "B" and L_("r10") <= t < t_rew)
    if captions_on and t < T_END and not quiet: im = captions(im, t)
    return im


def frame_img(i):
    t = i * F; k = int(round((t - T_SHOCK) / F))                       # the one shock: two smeared frames, a negative flash
    if -2 <= k < 0: return smear(render(i, T_SHOCK + 0.1, False), k)
    if k == 0: return negative(render(i, T_SHOCK + 0.1, False))
    return render(i, t)


def frame(i):
    frame_img(i).save(TMP + f"f{i:05d}.jpg", quality=92)


if __name__ == "__main__":
    print("video", VID, "duration", D, "frames", N)
    if os.environ.get("CA_PROBE"):
        ts = [eval(x, globals()) for x in os.environ["CA_PROBE"].split(";")]
        ims = [frame_img(int(round(x * FPS))).resize((360, 640)) for x in ts]
        cols = min(6, len(ims)); rows = (len(ims) + cols - 1) // cols; sheet = Image.new("RGB", (cols * 360, rows * 640))
        for n, im_ in enumerate(ims): sheet.paste(im_, ((n % cols) * 360, (n // cols) * 640))
        sheet.save(TMP + "probe.jpg", quality=88); print("probe", TMP + "probe.jpg", [round(x, 2) for x in ts]); sys.exit(0)
    from multiprocessing import Pool
    from scipy.signal import butter, sosfiltfilt
    STEP = os.environ.get("EI_STEP"); RANGE = os.environ.get("EI_RANGE"); sig = json.dumps(sorted(line_t.items()))
    if not os.environ.get("EI_AUDIO_ONLY"):
        todo = [i for i in range(N) if not STEP or i % int(STEP) == 0]
        if RANGE:
            if not os.path.exists(TMP + "timeline.sig") or open(TMP + "timeline.sig").read() != sig: sys.exit("EI_RANGE needs a full render with the same timeline")
            spans = [tuple(float(v) for v in r.split("-")) for r in RANGE.split(",")]; todo = [i for i in range(N) if any(a_ - 0.2 <= i * F <= b_ + 0.2 for a_, b_ in spans)]
        elif not STEP:
            for f_ in glob.glob(TMP + "f*.jpg"): os.remove(f_)
        with Pool(4) as pool: pool.map(frame, todo, chunksize=4)
        if not STEP: open(TMP + "timeline.sig", "w").write(sig)
    if STEP: print("test ok", D); sys.exit(0)
    # ------------------------------------------------------------ sound, in numpy
    NS = int(D * VSR) + VSR; ts = np.arange(NS) / VSR; mix = np.zeros(NS); rng = np.random.default_rng(5)
    def add(s_, at_, g=1.0):
        i0 = int(at_ * VSR); j0 = min(NS, i0 + len(s_))
        if j0 > i0 and i0 >= 0: mix[i0:j0] += s_[: j0 - i0] * g
    def env(n, a=0.005, r=0.05): x = np.arange(n) / VSR; return np.minimum(1, x / a) * np.exp(-x / r)
    def tone(f, d_, decay): x = np.arange(int(d_ * VSR)) / VSR; return np.sin(2 * np.pi * f * x) * np.exp(-x * decay)
    def boom(): x = np.arange(int(1.4 * VSR)) / VSR; return np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x * 4) + 30) / VSR) * np.exp(-x * 2.6)
    def thump(): x = np.arange(int(0.25 * VSR)) / VSR; return np.sin(2 * np.pi * 52 * x) * np.exp(-x * 22)
    def click(): n = int(0.012 * VSR); return rng.standard_normal(n) * np.exp(-np.arange(n) / VSR * 500)
    def band(lo, hi, n): return sosfiltfilt(butter(2, [lo, hi], btype="band", fs=VSR, output="sos"), rng.standard_normal(n))
    def sweep(): x = np.arange(int(0.9 * VSR)) / VSR; return np.sin(2 * np.pi * np.cumsum(1800 - 1500 * x / 0.9) / VSR) * 0.25 + rng.standard_normal(len(x)) * 0.12
    def whoosh(d_=0.35): n = int(d_ * VSR); return band(400, 3000, n) * np.sin(np.linspace(0, np.pi, n)) ** 2
    def heart(a_, b_, per=0.55, g=0.9):
        for q in np.arange(a_, b_, per): add(thump(), q, g); add(thump(), q + 0.19, g * 0.65)
    def beep(at_, f=1850): x = np.arange(int(0.09 * VSR)) / VSR; add(np.sign(np.sin(2 * np.pi * f * x)) * 0.3 * np.minimum(1, (0.09 - x) / 0.01), at_, 0.5)
    def buzz(at_, n=2):
        for k in range(n): x = np.arange(int(0.32 * VSR)) / VSR; add(np.sin(2 * np.pi * 160 * x) * (np.sin(2 * np.pi * 40 * x) > 0) * 0.5, at_ + k * 0.45, 0.45)
    def printer(a_, b_):
        for q in np.arange(a_, b_, 0.034): add(click() * (0.6 + 0.4 * rng.random()), q, 0.35)
        add(band(700, 2400, int((b_ - a_) * VSR)) * 0.25, a_, 0.5)
    def ring(at_): add(tone(880, 0.25, 6) + tone(1320, 0.25, 7) * 0.6, at_, 0.25)
    def tick(at_): add(tone(3000, 0.03, 120), at_, 0.35); add(click() * 0.2, at_, 0.35)
    def clunk(at_): add(thump() * 1.6, at_, 1.0); add(tone(120, 0.6, 5), at_, 0.4); add(click() * 3, at_, 0.8)
    # room tone: the fluorescent hum and the fridges, the same under everything that happens in the shop
    hum = (np.sin(2 * np.pi * 100 * ts) * 0.5 + np.sin(2 * np.pi * 200 * ts) * 0.25 + np.sin(2 * np.pi * 300 * ts) * 0.1) * 0.05 + band(60, 400, NS) * 0.08
    mix += hum
    sil = np.zeros(NS)
    if VID == "A":
        add(boom(), 0.0, 0.5); buzz(0.02); add(whoosh(), 0.05, 0.4)
        add(whoosh(), L_("n3"), 0.3); add(click() * 2, wt("n4", "quitte") - 0.1, 0.3)
        ring(L_("s1")); add(tone(660, 0.2, 10), we("s1") + 0.1, 0.2)
        tb = wt("n6", "bip") - 0.05; beep(tb); beep(tb + 0.55); add(thump() * 0.8, tb + 0.02, 0.5)
        printer(L_("n7") + 0.3, L_("n9") - 0.4)
        heart(L_("n9"), we("n9") + 0.2, 0.62, 0.7)
        sil[int((we("n9") + 0.15) * VSR):int((T_SHOCK - 0.04) * VSR)] = 1
        add(np.convolve(rng.standard_normal(int(0.14 * VSR)), np.ones(25) / 25, "same") * 9, T_SHOCK - 0.08, 0.5); add(boom(), T_SHOCK, 1.2)
        heart(L_("s2"), L_("n12b"), 0.5, 0.8); ring(L_("s2"))
        add(boom(), L_("m1"), 0.45)
        for k in range(14): add(tone(2600, 0.02, 200), L_("n11") + 0.3 + k * 0.19 + 0.05 * math.sin(k), 0.12)       # drops
        add(boom(), wt("n12", "trois"), 0.5)
        for k in range(int((D - wt("n12b", "cinquante")))): tick(wt("n12b", "cinquante") + k)
        add(whoosh(0.3), wt("n13", "a") - 0.25, 0.6); add(whoosh(0.3), wt("n13", "b") - 0.25, 0.6); add(boom(), wt("n13", "b") - 0.03, 0.9)
        add(tone(1046, 0.5, 6) + tone(1568, 0.5, 7) * 0.6, T_END + 0.9, 0.3)
    else:
        add(boom(), 0.0, 0.5); add(whoosh(), 0.05, 0.4)
        for k in range(8): add(tone(2600, 0.02, 200), 1.0 + k * 0.4, 0.1)
        add(whoosh(), L_("n3"), 0.3); printer(L_("n8"), L_("p2") - 0.3)
        lt = [wt("p2", x) for x in ("f", "r", "m")]
        for x in lt: add(tone(1400, 0.15, 14), x, 0.25)
        add(boom(), we("p2") - 0.4, 0.6)
        add(whoosh(0.3), wt("n13", "a") - 0.25, 0.6); add(whoosh(0.3), wt("n13", "b") - 0.25, 0.6); add(boom(), wt("n13", "b") - 0.03, 0.9)
        for k in range(int(L_("a1") - wt("n13", "b"))): tick(wt("n13", "b") + 0.3 + k)
        for k in range(5): add(click() * 1.5, L_("a1") + 0.8 + k * 0.05, 0.4)                                        # coins
        add(tone(4000, 0.6, 3) * 0.3, wt("a1", "froide"), 0.4); add(band(3000, 8000, int(0.6 * VSR)) * 0.3, wt("a1", "froide"), 0.4)               # frost
        sil[int((we("a1") + 0.15) * VSR):int((T_SHOCK - 0.04) * VSR)] = 1
        add(np.convolve(rng.standard_normal(int(0.14 * VSR)), np.ones(25) / 25, "same") * 9, T_SHOCK - 0.08, 0.5); add(boom(), T_SHOCK, 1.2)
        add(boom(), wt("a3", "ferme"), 0.6)
        for k in range(40): add(click() * 0.5, L_("r10") + 0.5 + k * 0.05, 0.5)
        add(thump() * 1.2, L_("r10") + 0.62, 0.8); add(sweep(), t_rew, 0.8)
        clunk(wt("b1", "eteins")); hum_off = (ts > wt("b1", "eteins")) & (ts < wt("n14", "reviennent") - 0.1); mix -= hum * hum_off * 0.9
        heart(L_("m2"), L_("n14"), 0.5, 0.8)
        tr = wt("n14", "reviennent") - 0.1
        for k in range(6): add(click() * 2, tr + k * 0.1, 0.5); add(tone(100, 0.08, 20), tr + k * 0.1, 0.3)
        ring(L_("s3")); buzz(wt("n15", "vibre") - 0.05)
        add(tone(1800, 0.1, 30) + tone(2400, 0.1, 30), L_("t2") + 0.4, 0.3); add(boom(), wt("t2", "carte"), 0.7)
        add(tone(1046, 0.5, 6) + tone(1568, 0.5, 7) * 0.6, T_END + 0.9, 0.3)
    vox = np.zeros(NS)
    for k, t0 in line_t.items():
        v = VO_A[k]
        if k.startswith("s"): v = sosfiltfilt(butter(3, [250, 4200], btype="band", fs=VSR, output="sos"), v) * 1.4            # through the phone
        i0 = int(t0 * VSR); j0 = min(NS, i0 + len(v)); vox[i0:j0] += v[: j0 - i0]
    act = np.convolve((np.convolve(np.abs(vox), np.ones(2205) / 2205, "same") > 0.01).astype(float), np.ones(13230) / 13230, "same")
    mute = np.convolve(sil, np.ones(2205) / 2205, "same")
    mix = mix / np.abs(mix).max() * 0.55 * (1 - 0.6 * np.clip(act, 0, 1)) * (1 - mute) + vox / (np.abs(vox).max() + 1e-9) * 0.9
    mix = mix[: int(D * VSR)]; mix *= np.clip((D - ts[: len(mix)]) / 0.3, 0, 1); sf.write(TMP + "mix.wav", mix / np.abs(mix).max() * 0.9, VSR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", TMP + "f%05d.jpg", "-i", TMP + "mix.wav",
                    "-c:v", "libx264", "-crf", "24", "-maxrate", "3200k", "-bufsize", "6400k", "-preset", "slow", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-g", "60",
                    "-af", "loudnorm=I=-13:TP=-1.0:LRA=9,volume=1.3,alimiter=limit=0.89", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUTP], check=True)
    print("ok", OUTP, D)
