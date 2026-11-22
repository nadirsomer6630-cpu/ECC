"""EMPLOI INSTABLE episode 2 (the public chose B: leave at 18:00).
Series signature: the exact time opens the episode, the hero never speaks (his unsaid thoughts are handwritten),
red = stolen time, the past on B&W tape, one smear shock after 1 s of silence, last frame loops to the first.
usage: HF_HOME=... ei2.py <out.mp4>   (EI_STEP=n renders every n-th frame as a test)"""
import glob, json, os, random, re, subprocess, sys, difflib
import numpy as np, soundfile as sf, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade as G

NEW = "/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/"
HD1, HD2, VO, TMP = NEW + "ei1hd/", NEW + "ei2hd/", NEW + "elv2/fin4/", NEW + "ei2tmp/"
SPR1, SPR2, POSE = NEW + "ei1spr/", NEW + "ei2spr/", NEW + "ei1pose/"
RHUBARB = NEW + "rhubarb/x/Rhubarb-Lip-Sync-1.14.0-Linux/rhubarb"
OUT = sys.argv[1]
W, H, FPS, VSR = 1080, 1920, 30, 44100
F = 1 / FPS
os.makedirs(TMP, exist_ok=True)
AUDIO_ONLY = os.environ.get("EI_AUDIO_ONLY") == "1"
SHOT = os.environ.get("EI_SHOT")          # partial render: EI_SHOT=portique,vote re-renders only those shots (EI_SHOT=list prints them)
MONT, MONO = G.MONT, G.MONO
RED = (200, 25, 25)
IN = "/usr/share/fonts/opentype/inter/Inter-"
def fI(w, sz): return ImageFont.truetype(IN + w + ".otf", sz)
HAND = NEW + "fonts/caveat.ttf"

# ---------------- voices & timeline ----------------
LINES = json.load(open(NEW + "elv2/lines.json")); SCRIPT = {n: t for n, w, t in LINES}
VO_A = {k: G.voice(VO + f"{k}.wav", lp=None) for k in SCRIPT}
VO_A["k01"] = np.concatenate([VO_A["k01"], np.zeros(max(0, 99224 - len(VO_A["k01"])))])   # keep the picture timeline locked


def norm(x): return re.sub(r"[^\w]", "", x.lower())


def align(ws, script):
    """Script spelling, whisper timing (letter-level match); words whisper wrote differently ("18h") are spread evenly."""
    sw = script.split(); wc, wt = [], []
    for x in ws:
        n = norm(x["w"])
        for i, ch in enumerate(n): wc.append(ch); wt.append((x["s"] + (x["e"] - x["s"]) * i / max(1, len(n)), x["s"] + (x["e"] - x["s"]) * (i + 1) / max(1, len(n))))
    sc, owner = [], []
    for j, w in enumerate(sw):
        for ch in norm(w): sc.append(ch); owner.append(j)
    mp = {}
    for a1, b1, n1 in difflib.SequenceMatcher(None, sc, wc, autojunk=False).get_matching_blocks():
        for q in range(n1): mp[a1 + q] = b1 + q
    out = []
    for j, w in enumerate(sw):
        idx = [i for i, o in enumerate(owner) if o == j and i in mp]
        ok = len(idx) >= max(1, len(norm(w)) // 2)
        out.append({"w": w, "s": wt[mp[idx[0]]][0] if ok else None, "e": wt[mp[idx[-1]]][1] if ok else None})
    j = 0
    while j < len(out):
        if out[j]["s"] is None:
            k = j
            while k < len(out) and out[k]["s"] is None: k += 1
            prev = out[j - 1]["e"] if j > 0 else (ws[0]["s"] if ws else 0.0)
            nxt = out[k]["s"] if k < len(out) else (ws[-1]["e"] if ws else prev + 0.4 * (k - j))
            step = (nxt - prev) / (k - j)
            for q in range(j, k): out[q]["s"], out[q]["e"] = prev + (q - j) * step, prev + (q - j + 1) * step
            j = k
        else: j += 1
    return out


REL = {}
for k in VO_A:
    p = TMP + f"{k}_pre.wav"; sf.write(p, VO_A[k], VSR)
    REL[k] = align(G.word_times(p, 0, None), SCRIPT[k])
dur = {k: len(v) / VSR for k, v in VO_A.items()}

T = 0.15; line_t = {}
def at(k, gap=0.25):
    global T
    line_t[k] = T; T += dur[k] + gap + 0.22
def wt(k, word, n=0):
    hits = [w["s"] for w in REL[k] if norm(w["w"]) == norm(word)] or [w["s"] for w in REL[k] if norm(w["w"]).startswith(norm(word))]
    return line_t[k] + hits[min(n, len(hits) - 1)]
at("n01", 0.45); at("k02", 0.85); at("m01", 1.1); at("n02", 0.85); at("k01", 1.9); at("n03", 0.25)
at("n04", 0.15); at("n10", 0.8); t_pause = T                       # the drawing: silence and a music box
at("n05", 0.25); at("n06", 0.25); at("n07", 0.3)
t_sil = T; T += 1.0                                          # 1 s of silence before the shock
t_hit = T; T += 0.5
at("s01", 0.4); at("s02", 0.5); t_vote = T - 0.2; at("n08", 0.4); t_suivre = T; T += 1.25
D = round(T, 2); print("duration", D)

T_PILE = wt("n01", "pile"); T_POUR = wt("n01", "Pour") - 0.12; T_NON = wt("n01", "non")
T_ROUGE = wt("n02", "rouge"); T_LE = wt("n03", "Le") - 0.12; T_OUVRE = wt("n05", "ouvre"); T_MOINS = wt("n05", "Moins") - 0.1
T_DES = wt("n06", "Des", 1) - 0.12; T_SPLIT = wt("n08", "ou") - 0.05; T_BRAC = wt("s02", "elle") - 0.1; T_RULE = wt("k01", "sa") - 0.1
CAP_LAG = 0.12
words = []
for k, t0 in line_t.items():
    words += [dict(w, s=w["s"] + t0 + CAP_LAG, e=w["e"] + t0 + CAP_LAG, line=k) for w in REL[k]]


def L_(k): return line_t[k] - 0.15


def mouth_cues(key):
    p = TMP + f"{key}_rh.wav"; a = VO_A[key] / (np.abs(VO_A[key]).max() + 1e-9); sf.write(p, a, VSR, subtype="PCM_16")
    out = subprocess.run([RHUBARB, "-r", "phonetic", "-f", "json", "--extendedShapes", "GHX", "-q", p], capture_output=True, text=True)
    return [(line_t[key] + c["start"], c["value"]) for c in json.loads(out.stdout)["mouthCues"]]


CUES = mouth_cues("k02") + mouth_cues("s01") + mouth_cues("s02")
def mouth_at(t):
    m = "X"
    for t0, v in CUES:
        if t0 <= t: m = v
        else: break
    return m


# ---------------- pictures ----------------
def still(path, over=1.2):
    return Image.open(path).convert("RGB").resize((int(W * over), int(H * over)), Image.LANCZOS)


ST = {}
for k in ("open", "gate", "stairs", "stairdoor", "basement"): ST[k] = still(HD2 + f"{k}_0001.png")
SPOTS = json.load(open(HD2 + "basement_spots.json"))


def view(im, t, t0, t1, z0=1.0, z1=1.08, cx=0.5, cy=0.5, drift=1.0):
    p = np.clip((t - t0) / max(1e-3, t1 - t0), 0, 1); p = p * p * (3 - 2 * p); z = z0 + (z1 - z0) * p
    cw, ch = im.width / 1.2 / z, im.height / 1.2 / z
    jx, jy = (np.sin(t * 0.9) * 2.5 + np.sin(t * 2.3) * 0.8) * drift, np.cos(t * 0.7) * 2.5 * drift
    x0 = np.clip(cx * im.width - cw / 2 + jx, 0, im.width - cw); y0 = np.clip(cy * im.height - ch / 2 + jy, 0, im.height - ch)
    return im.transform((W, H), Image.EXTENT, (float(x0), float(y0), float(x0 + cw), float(y0 + ch)), Image.BICUBIC)


def view_xy(size, t, t0, t1, z0, z1, cx, cy, px, py, drift=1.0):
    """Where a point of the still (px, py as fractions) lands on screen after the same camera move as view()."""
    w_, h_ = size; p = np.clip((t - t0) / max(1e-3, t1 - t0), 0, 1); p = p * p * (3 - 2 * p); z = z0 + (z1 - z0) * p
    cw, ch = w_ / 1.2 / z, h_ / 1.2 / z
    jx, jy = (np.sin(t * 0.9) * 2.5 + np.sin(t * 2.3) * 0.8) * drift, np.cos(t * 0.7) * 2.5 * drift
    x0 = np.clip(cx * w_ - cw / 2 + jx, 0, w_ - cw); y0 = np.clip(cy * h_ - ch / 2 + jy, 0, h_ - ch)
    return (px * w_ - x0) / cw * W, (py * h_ - y0) / ch * H


class SD:
    """ImageDraw proxy that scales coordinates: shapes are drawn at 2x and downsampled, so every edge is anti-aliased."""
    def __init__(s, im, k=2): s.d = ImageDraw.Draw(im); s.k = k
    def _c(s, xy): return [(x * s.k, y * s.k) for x, y in xy] if isinstance(xy[0], (tuple, list)) else tuple(v * s.k for v in xy)
    def ellipse(s, xy, fill=None, outline=None, width=1): s.d.ellipse(s._c(xy), fill=fill, outline=outline, width=int(width * s.k))
    def line(s, xy, fill=None, width=1): s.d.line(s._c(xy), fill=fill, width=int(width * s.k))
    def rectangle(s, xy, fill=None, outline=None, width=1): s.d.rectangle(s._c(xy), fill=fill, outline=outline, width=int(width * s.k))
    def rounded_rectangle(s, xy, radius=0, fill=None, outline=None, width=1): s.d.rounded_rectangle(s._c(xy), radius * s.k, fill=fill, outline=outline, width=int(width * s.k))
    def polygon(s, xy, fill=None): s.d.polygon(s._c(xy), fill=fill)
    def text(s, xy, txt, font=None, fill=None, anchor=None): s.d.text((xy[0] * s.k, xy[1] * s.k), txt, font=font.font_variant(size=int(font.size * s.k)), fill=fill, anchor=anchor)


def aa_layer(w=None, h=None): return Image.new("RGBA", ((w or W) * 2, (h or H) * 2), (0, 0, 0, 0))
def aa_down(l): return l.resize((l.width // 2, l.height // 2), Image.LANCZOS)


def spill(im, x, y, rx, ry, color, alpha, poly=None):
    """Additive coloured light spilling on whatever is around a source (computed at 1/4 size, then upscaled: soft and cheap)."""
    if alpha <= 0.01: return im.convert("RGB")
    q = 4; lay = Image.new("RGB", (im.width // q, im.height // q), (0, 0, 0)); d = ImageDraw.Draw(lay); col = tuple(int(c * alpha) for c in color)
    if poly: d.polygon([(a_ / q, b_ / q) for a_, b_ in poly], fill=col)
    else: d.ellipse(((x - rx) / q, (y - ry) / q, (x + rx) / q, (y + ry) / q), fill=col)
    lay = lay.filter(ImageFilter.GaussianBlur(max(2, min(rx, ry) / q * 0.45))).resize(im.size, Image.BILINEAR)
    return ImageChops.add(im.convert("RGB"), lay)


def torch(im, x, y, R, lo=0.3, hi=1.15):
    """A hand-held light: bright where it points, falling off around; it moves with the hand."""
    q = 4; yy_, xx_ = np.mgrid[0:im.height // q, 0:im.width // q].astype(np.float32) * q
    m = np.clip(hi - ((xx_ - x) ** 2 + (yy_ - y) ** 2) / (R * R), lo, hi); m = cv2.resize(m, im.size, interpolation=cv2.INTER_LINEAR)[..., None]
    a = np.asarray(im.convert("RGB")).astype(np.float32) * m
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def rim_light(sp, color, dx, strength=1.0, blur=5):
    """A light behind or beside the character: a thin coloured edge on one side of the silhouette."""
    if strength <= 0.02: return sp
    a = np.asarray(sp.getchannel("A")).astype(np.float32) / 255; sh = np.roll(a, dx, axis=1)
    if dx > 0: sh[:, :dx] = 0
    else: sh[:, dx:] = 0
    rim = cv2.GaussianBlur(np.clip(a - sh, 0, 1), (0, 0), blur) * a * strength
    arr = np.asarray(sp).astype(np.float32); arr[..., :3] = np.clip(arr[..., :3] + rim[..., None] * np.array(color, np.float32), 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


_SP = {}
def sprite(who, m, blink, h, pose=None):
    key = (who, m, blink, h, pose)
    if key not in _SP:
        if pose: f = POSE + f"{who}_{pose}_{m}_{int(blink)}.png"
        elif who.startswith("kessler"): f = SPR1 + f"{who}_{m}_{int(blink)}.png"
        elif who == "samir_tired": f = SPR2 + f"{who}_{m}_{int(blink)}.png"
        elif who.startswith("w"): f = SPR2 + f"{who}_X_1.png"
        else: f = SPR1 + f"{who}_X_{int(blink)}.png"
        im = Image.open(f).convert("RGBA"); _SP[key] = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    return _SP[key]


def tint(sp, mul, add=(0, 0, 0)):
    a = np.asarray(sp).astype(np.float32); a[..., :3] = np.clip(a[..., :3] * np.array(mul) + np.array(add), 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def place(base, sp, cx, foot, shadow=True, h=None):
    im = base.convert("RGBA"); h = h or sp.height; sole = foot - sp.height * (44 / 900)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); d_ = ImageDraw.Draw(sh)
        d_.ellipse((cx - sp.width * 0.42, sole - h * 0.025, cx + sp.width * 0.42, sole + h * 0.03), fill=(0, 0, 0, 70))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(h * 0.025)))
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); d_ = ImageDraw.Draw(sh)
        d_.ellipse((cx - sp.width * 0.2, sole - h * 0.012, cx + sp.width * 0.2, sole + h * 0.012), fill=(0, 0, 0, 150))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(h * 0.006)))
    im.alpha_composite(sp, (int(cx - sp.width / 2), int(foot - sp.height)))
    return im.convert("RGB")


def kessler_shot(t, t0, t1):
    """She hears 'no': the welcoming smile freezes, then turns cold (crossfade on the word)."""
    if "open_dof" not in ST: ST["open_dof"] = ST["open"].filter(ImageFilter.GaussianBlur(3.2))       # shallow depth of field: she is sharp, the office is not
    base = ST["open_dof"]; ox = 0.5 * base.width - W / 2; oy = 0.5 * base.height - H / 2
    blink = ((t + 0.4) % 3.1) < 0.1; h = 1700
    g = float(np.clip((t - T_NON - 0.1) / 0.45, 0, 1))
    m = mouth_at(t) if line_t["k02"] <= t < line_t["k02"] + dur["k02"] + 0.1 else "X"
    a = sprite("kessler_smile", "X", blink, h); b = sprite("kessler_cold", m, blink, h)
    sp = a if g <= 0 else b if g >= 1 else Image.blend(a, b, g)
    gp = float(np.clip((t - T_NON - 0.6) / 0.8, 0, 1)); gp = gp * gp * (3 - 2 * gp) * 8
    if gp > 0:                                                    # hands on hips, chin up: she takes it as a challenge
        k0 = int(gp); f_ = gp - k0; p0 = sprite("kessler_cold", m, blink, h, f"hips{k0}")
        sp = p0 if f_ < 0.08 or k0 >= 8 else Image.blend(p0, sprite("kessler_cold", m, blink, h, f"hips{k0 + 1}"), f_)
    br = 1 + 0.008 * np.sin(t * 2 * np.pi / 3.6); sp = sp.resize((sp.width, int(sp.height * br)), Image.BICUBIC)
    lw = np.linspace(1.04, 0.84, sp.width)[None, :, None]; arr = np.asarray(sp).astype(np.float32); arr[..., :3] *= lw; sp = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    sp = rim_light(sp, (70, 95, 130), 16, strength=float(np.clip((t - T_NON - 0.3) * 0.9, 0, 1)))      # neons out: only the cold window light on her
    im = place(base, sp, 560 + ox, 2080 + oy, h=h)
    if t > T_NON + 0.3:                                             # 18:00: the office neons go out one row at a time behind her
        dk = min(0.42, (t - T_NON - 0.3) * 0.22); arr = np.asarray(im).astype(np.float32); yy_ = np.linspace(1, 0, arr.shape[0])[:, None, None]
        im = Image.fromarray(np.clip(arr * (1 - dk * (0.5 + 0.5 * yy_)) * np.array([0.97, 0.99, 1.03]), 0, 255).astype(np.uint8))
    z1 = 1.06 if t < T_NON else 1.06 + 0.1 * min(1, (t - T_NON) / 1.5)          # after "no" the camera creeps onto her face
    return view(im, t, t0, t1, 1.0, z1, 0.5, 0.45 if t > T_NON else 0.5)


def bloom(a, thr=0.72, k=0.55):
    """Halation: bright lights (screens, neons, LEDs) glow softly into the air around them."""
    hl = np.clip(a - thr, 0, None); sm = cv2.resize(hl, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    sm = cv2.GaussianBlur(sm, (0, 0), 6) + cv2.GaussianBlur(sm, (0, 0), 18) * 0.6
    return a + cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR) * k


def white_grade(im, i, exp=0.18):
    a = bloom(np.asarray(im).astype(np.float32) / 255 * (2 ** exp), 0.85, 0.3)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = np.clip(((r - np.maximum(g, b)) / np.maximum(r, 1e-3) - 0.45) * 4, 0, 1)[..., None]
    lum = a @ G.LUMA; out = a * 0.75 + lum[..., None] * 0.25
    out = out * (1 - red) + a * red
    out = G.filmic(np.clip(out, 0, 1), 1.18) * np.array([0.97, 1.0, 1.04])
    out = out * np.clip(1.08 - G.RR * 0.22, 0.6, 1)[..., None]
    out += np.random.default_rng(i).normal(0, 0.011, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def night_grade(im, i, exp=0.35, warm=False, glow=True):
    """After 18:00: cold shadows, warm-orange lights (teal/orange split), reds kept, halation, vignette, grain."""
    a = np.asarray(im).astype(np.float32) / 255 * (2 ** exp)
    if glow: a = bloom(a)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = np.clip(((r - np.maximum(g, b)) / np.maximum(r, 1e-3) - 0.45) * 4, 0, 1)[..., None]
    lum = a @ G.LUMA; out = a * 0.6 + lum[..., None] * 0.4
    out = out * (1 - red) + a * red
    out = G.filmic(np.clip(out, 0, 1), 1.25)
    l_ = (out @ G.LUMA)[..., None]                                     # split toning: teal shadows, warm highlights
    out = out + (1 - l_) * np.array([-0.025, 0.006, 0.03]) + l_ * (np.array([0.05, 0.015, -0.03]) if warm else np.array([0.02, 0.01, -0.01]))
    out = out * (np.array([1.04, 0.98, 0.9]) if warm else np.array([0.92, 0.99, 1.06]))
    out = out * np.clip(1.12 - G.RR * 0.5, 0.35, 1)[..., None]
    out += np.random.default_rng(i).normal(0, 0.015, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


# ---------------- inserts ----------------
def paper_tex(w, h, base, fiber=0.05, seed=0):
    rg = np.random.default_rng(seed)
    n = cv2.GaussianBlur(rg.standard_normal((h, w)).astype(np.float32), (0, 0), 0.8) * 0.018
    fb = cv2.GaussianBlur(rg.standard_normal((h // 4, w // 4)).astype(np.float32), (0, 0), 3); fb = cv2.resize(fb, (w, h)) * fiber
    yy_, xx_ = np.mgrid[0:h, 0:w]; edge = 1 - 0.06 * ((np.abs(xx_ / w - 0.5) * 2) ** 4 + (np.abs(yy_ / h - 0.5) * 2) ** 4)
    a = np.array(base, np.float32)[None, None] / 255 * (1 + n + fb)[..., None] * edge[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")


def drop_shadow(canvas, layer, pos, blur=30, off=(18, 28), alpha=120):
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); m = layer.getchannel("A").point(lambda v: int(v * alpha / 255))
    sh.paste(Image.new("RGBA", layer.size, (0, 0, 0, 255)), (pos[0] + off[0], pos[1] + off[1]), m)
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur))); canvas.alpha_composite(layer, pos)


_KSH = None
_WALLBG = None
def ins_clock(t):
    """17:59:58 -> 18:00:00 on the teal office wall, drawn at 2x for clean edges. On 'pile' the frame flashes red and Kessler's shadow slides over the wall."""
    global _KSH, _WALLBG
    if _WALLBG is None:
        yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
        wall = np.array([26, 74, 82], np.float32)[None, None] * np.clip(1.25 - ((xx_ - 380) ** 2 + (yy_ - 700) ** 2) / 2.2e6, 0.35, 1.25)[..., None]
        for k in range(5):                                           # daylight through the blinds: soft slanted bands
            band = np.exp(-((yy_ - (300 + k * 190) - (xx_ - 540) * 0.22) / 38) ** 2) * np.clip(1 - xx_ / 1400, 0, 1)
            wall += band[..., None] * np.array([16, 26, 24], np.float32)
        wall += np.random.default_rng(2).normal(0, 1.6, (H, W, 1))
        b_ = Image.fromarray(np.clip(wall, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(b_)
        d.rectangle((0, 1560, W, 1572), fill=(200, 25, 25)); d.rectangle((0, 1700, W, H), fill=(14, 40, 46)); d.rectangle((0, 1690, W, 1700), fill=(160, 120, 80))
        d.text((120, 1500), "VALMONT · HORAIRES : 08:00 - 18:00", font=fI("SemiBold", 26), fill=(150, 190, 196))
        cx, cy, r = 540, 860, 330
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((cx - r + 10, cy - r + 30, cx + r + 70, cy + r + 90), fill=(0, 0, 0, 130)); b_.alpha_composite(sh.filter(ImageFilter.GaussianBlur(28)))
        _WALLBG = b_
    im = _WALLBG.copy(); hit = t >= T_PILE; cx, cy, r = 540, 860, 330
    ov = aa_layer(); d = SD(ov)
    d.ellipse((cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22), fill=RED + (255,) if hit and t < T_PILE + 0.12 else (24, 24, 28, 255))
    d.ellipse((cx - r - 12, cy - r - 12, cx + r + 12, cy + r + 12), outline=(90, 92, 100, 255), width=3)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(246, 246, 242, 255))
    for k in range(60):
        a = k / 60 * 2 * np.pi; L = 40 if k % 5 == 0 else 16
        d.line((cx + np.sin(a) * (r - 10), cy - np.cos(a) * (r - 10), cx + np.sin(a) * (r - 10 - L), cy - np.cos(a) * (r - 10 - L)), fill=(30, 30, 34, 255), width=8 if k % 5 == 0 else 3)
    for k, n_ in enumerate(("12", "3", "6", "9")):
        a = k / 4 * 2 * np.pi; d.text((cx + np.sin(a) * (r - 92), cy - np.cos(a) * (r - 92)), n_, font=fI("Bold", 54), fill=RED + (255,) if n_ == "6" else (30, 30, 34, 255), anchor="mm")
    d.text((cx, cy + 130), "VALMONT", font=fI("SemiBold", 22), fill=(150, 150, 156, 255), anchor="mm")
    sec = 60 if hit else min(59, 58 + int(t / max(0.3, T_PILE / 2)))
    def hand(frac, L, w_, col, sh_=True):
        a = frac * 2 * np.pi
        if sh_: d.line((cx + 6, cy + 9, cx + 6 + np.sin(a) * L, cy + 9 - np.cos(a) * L), fill=(0, 0, 0, 50), width=w_)       # the hands float above the dial
        d.line((cx, cy, cx + np.sin(a) * L, cy - np.cos(a) * L), fill=col, width=w_)
    hand((18 if hit else 17 + 59 / 60) / 12, 170, 18, (30, 30, 34, 255)); hand(0 if hit else 59.9 / 60, 250, 12, (30, 30, 34, 255))
    hand((sec % 60) / 60, 290, 4, RED + (255,)); d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=RED + (255,))
    d.rounded_rectangle((330, 1270, 750, 1390), 16, fill=(10, 12, 14, 255), outline=(60, 62, 70, 255), width=3)
    im.alpha_composite(aa_down(ov))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).pieslice((cx - r, cy - r, cx + r, cy + r), 200, 300, fill=(255, 255, 255, 26)); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).text((540, 1330), "18:00:00" if hit else f"17:59:{sec:02d}", font=ImageFont.truetype(MONO, 78), fill=(255, 40, 30) if hit else (255, 150, 60), anchor="mm")
    g = float(np.clip((t - T_PILE + 0.5) / 0.9, 0, 1))
    if g > 0:
        if _KSH is None:
            a_ = sprite("kessler_cold", "X", 0, 2500).getchannel("A"); k_ = Image.new("RGBA", a_.size, (0, 0, 0, 255)); k_.putalpha(a_.point(lambda v: int(v * 0.5))); _KSH = k_.filter(ImageFilter.GaussianBlur(22))
        im.alpha_composite(_KSH, (int(W + 100 - (1 - (1 - g) ** 3) * 620), 420))
    im = im.convert("RGB")
    if hit: im = spill(im, 540, 1330, 520, 300, (255, 30, 20), 0.35 * np.exp(-(t - T_PILE) * 1.5) + 0.12)      # the red display lights the wall
    z = 1.0 + 0.04 * t + (0.05 * np.exp(-(t - T_PILE) * 8) if hit else 0)
    cw, ch = W / z, H / z
    return im.transform((W, H), Image.EXTENT, (540 - cw / 2, 960 - ch / 2, 540 + cw / 2, 960 + ch / 2), Image.BICUBIC)


def wall_night():
    w = np.zeros((H, W, 3), np.float32); yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
    w += np.array([0.04, 0.05, 0.1]); w += np.exp(-(((xx_ - 700) / 500) ** 2 + ((yy_ - 1300) / 600) ** 2))[..., None] * np.array([0.35, 0.12, 0.15])
    w += np.exp(-(((xx_ - 300) / 450) ** 2 + ((yy_ - 400) / 500) ** 2))[..., None] * np.array([0.08, 0.14, 0.3])
    return Image.fromarray((np.clip(w, 0, 1) * 255).astype(np.uint8))


WALLN = wall_night()
PX0, PY0, PX1, PY1 = 250, 230, 830, 1110


def phone(screen, shake=0):
    bg = Image.new("RGB", (W, H), (14, 15, 19)).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((150, 200, 930, 1300), fill=(70, 80, 110, 160))
    bg.alpha_composite(g.filter(ImageFilter.GaussianBlur(160)))
    body = Image.new("RGBA", (PX1 - PX0 + 40, PY1 - PY0 + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(body)
    d.rounded_rectangle((0, 0, body.width - 1, body.height - 1), 84, fill=(58, 60, 66), outline=(150, 152, 160), width=3)
    d.rounded_rectangle((12, 12, body.width - 13, body.height - 13), 74, fill=(8, 8, 10))
    for y_, h_ in ((230, 90), (340, 90)): d.rounded_rectangle((-4, y_, 4, y_ + h_), 3, fill=(120, 122, 130))
    m = Image.new("L", screen.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, screen.width - 1, screen.height - 1), 62, fill=255)
    body.paste(screen, (20, 20), m)
    d.rounded_rectangle((body.width / 2 - 80, 40, body.width / 2 + 80, 82), 21, fill=(0, 0, 0))
    gl = Image.new("RGBA", body.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).polygon([(0, 0), (body.width * 0.55, 0), (0, body.height * 0.55)], fill=(255, 255, 255, 22))
    body.alpha_composite(gl)
    drop_shadow(bg, body, (PX0 - 20 + shake, PY0 - 20), blur=40, off=(0, 40), alpha=200)
    return bg.convert("RGB")


AMP_M = None
def ins_voicemsg(t, t0, t1):
    """Mum's voice message playing: avatar, waveform that fills as she speaks, 'Je t'ai gardé une assiette'."""
    global AMP_M
    if AMP_M is None:
        a = np.abs(VO_A["m01"]); n = 46; AMP_M = np.array([a[int(k * len(a) / n):int((k + 1) * len(a) / n)].mean() for k in range(n)]); AMP_M = AMP_M / AMP_M.max()
    sw, sh = PX1 - PX0, PY1 - PY0
    sc = WALLN.resize((sw, sh)).convert("RGBA"); d = ImageDraw.Draw(sc)
    d.text((70, 52), "18:01", font=fI("SemiBold", 30), fill=(255, 255, 255))
    d.rounded_rectangle((sw - 150, 56, sw - 90, 82), 7, outline=(255, 255, 255), width=3); d.rectangle((sw - 145, 61, sw - 140, 77), fill=(230, 50, 40))
    d.text((sw / 2, 150), "Mercredi 6 novembre", font=fI("Medium", 30), fill=(235, 235, 245), anchor="mm")
    d.text((sw / 2, 250), "18:01", font=fI("Bold", 150), fill=(245, 245, 250), anchor="mm")
    p = min(1.0, (t - t0 + 0.4) / 0.2); by = int(380 - 60 * (1 - p))
    card = Image.new("RGBA", (sw - 50, 300), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, card.width - 1, 299), 36, fill=(250, 250, 252, 240))
    cd.ellipse((26, 26, 96, 96), fill=(232, 120, 140)); cd.text((61, 61), "M", font=fI("Bold", 38), fill=(255, 255, 255), anchor="mm")
    cd.text((114, 30), "Maman ❤", font=fI("Bold", 34), fill=(25, 25, 30)); cd.text((card.width - 30, 36), "maintenant", font=fI("Regular", 22), fill=(130, 130, 136), anchor="ra")
    cd.text((114, 72), "Message vocal · 0:05", font=fI("Regular", 24), fill=(110, 110, 118))
    prog = np.clip((t - line_t["m01"]) / dur["m01"], 0, 1)
    cd.ellipse((26, 150, 96, 220), fill=(30, 140, 230));
    if 0 < prog < 1: cd.rectangle((49, 168, 57, 202), fill=(255, 255, 255)); cd.rectangle((65, 168, 73, 202), fill=(255, 255, 255))
    else: cd.polygon([(52, 166), (52, 204), (82, 185)], fill=(255, 255, 255))
    for k, v in enumerate(AMP_M):
        x = 120 + k * 9; hh = 6 + v * 46; col = (30, 140, 230) if k / len(AMP_M) < prog else (190, 190, 198)
        cd.rounded_rectangle((x, 185 - hh / 2, x + 5, 185 + hh / 2), 2, fill=col)
    cd.text((card.width - 30, 250), f"0:0{int(prog * 5)}", font=fI("Medium", 22), fill=(130, 130, 136), anchor="ra")
    sc.alpha_composite(card, (25, by))
    t2 = line_t["m01"] + dur["m01"] * 0.55
    if t > t2:                                                    # Valmont's reply to mum, cold and automatic
        p2 = min(1.0, (t - t2) / 0.2); c2 = Image.new("RGBA", (sw - 50, 150), (0, 0, 0, 0)); c2d = ImageDraw.Draw(c2)
        c2d.rounded_rectangle((0, 0, c2.width - 1, 149), 30, fill=(250, 250, 252, int(235 * p2)))
        c2d.rounded_rectangle((22, 22, 78, 78), 12, fill=(25, 25, 30)); c2d.text((50, 50), "V", font=fI("Bold", 34), fill=(255, 255, 255), anchor="mm")
        c2d.text((96, 22), "VALMONT · RH", font=fI("SemiBold", 22), fill=(110, 110, 118)); c2d.text((c2.width - 26, 24), "maintenant", font=fI("Regular", 20), fill=(130, 130, 136), anchor="ra")
        c2d.text((96, 56), "Présence requise après 18:00.", font=fI("Bold", 28), fill=(200, 25, 25)); c2d.text((96, 98), "Merci pour votre engagement.", font=fI("Regular", 24), fill=(60, 60, 66))
        sc.alpha_composite(c2, (25, by + 320 + int(30 * (1 - p2))))
    d.rounded_rectangle((sw / 2 - 110, sh - 30, sw / 2 + 110, sh - 22), 4, fill=(255, 255, 255))
    vib = int(np.sin(t * 90) * 6) if (t - t0 < 0.5 or 0 < t - t2 < 0.4) else 0
    im = phone(sc.convert("RGB"), vib)
    z = 1.3 + 0.06 * (t - t0) / max(0.1, t1 - t0); cw, ch = W / z, H / z; cx_, cy_ = 540, PY0 + 580
    return im.transform((W, H), Image.EXTENT, (cx_ - cw / 2, cy_ - ch / 2, cx_ + cw / 2, cy_ + ch / 2), Image.BICUBIC)


_lg = json.load(open(HD2 + "gate_led.json")); LED_GATE = (_lg["x"], _lg["y"])      # the red reader in the gate still (fraction of the frame)
def gate_shot(t, t0, t1, i):
    base = ST["gate"].copy(); lay = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    lx, ly = LED_GATE[0] * base.width, LED_GATE[1] * base.height
    on = t < T_ROUGE or int((t - T_ROUGE) * 6) % 2 == 0
    if on: d.ellipse((lx - 120, ly - 70, lx + 120, ly + 70), fill=(255, 20, 10, 110))
    im = Image.alpha_composite(base.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(40)))
    hb = HERO_BADGE_S; tgt = (lx - hb.width * 0.5, ly - hb.height * 0.25)
    u = np.clip((t - t0 - 0.2) / max(0.3, T_ROUGE - t0 - 0.2), 0, 1); u = 1 - (1 - u) ** 3
    st_ = (base.width * 0.95, base.height * 0.98); bx = st_[0] + (tgt[0] - st_[0]) * u; by_ = st_[1] + (tgt[1] - st_[1]) * u
    if t > T_ROUGE: bx += np.sin((t - T_ROUGE) * 40) * 18 * np.exp(-(t - T_ROUGE) * 4); by_ += max(0, t - T_ROUGE - 0.6) * 260   # refused: it shakes, then falls away
    im.alpha_composite(hb.rotate(8 - 8 * u, expand=True, resample=Image.BICUBIC), (int(bx), int(by_)))
    im = spill(im, lx, ly + 60, 460, 330, (255, 36, 20), (0.22 if on else 0.05) * (0.4 + 0.6 * u)).convert("RGBA")     # the red LED lights the hand, the badge, the counter
    if t > T_ROUGE:          # floating reader message
        p = min(1, (t - T_ROUGE) / 0.15); s_ = 1.15 - 0.15 * p
        lab = Image.new("RGBA", (520, 120), (0, 0, 0, 0)); ld = ImageDraw.Draw(lab)
        ld.rounded_rectangle((0, 0, 519, 119), 22, fill=(200, 25, 25, 235)); ld.text((260, 60), "×  ACCÈS REFUSÉ", font=fI("Bold", 44), fill=(255, 255, 255), anchor="mm")
        lab = lab.resize((int(520 * s_), int(120 * s_)))
        im.alpha_composite(lab, (int(lx - lab.width / 2), int(ly - 330 - lab.height / 2)))
    return view(im.convert("RGB"), t, t0, t1, 1.0, 1.12, 0.6, 0.55)


_SPKBG = None
def ins_speaker(t, t0, t1):
    """Ceiling loudspeaker (drawn at 2x), grille trembling with Kessler's voice, red light pulsing on the ceiling with each word."""
    global _SPKBG
    a = VO_A["k01"]; i0 = int((t - line_t["k01"]) * VSR)
    amp = float(np.abs(a[max(0, i0):max(0, i0) + 1470]).mean() * 6) if 0 <= i0 < len(a) else 0.0
    if _SPKBG is None:
        b_ = Image.new("RGBA", (W, H), (218, 220, 224, 255)); ov = aa_layer(); d = SD(ov)
        for x in range(-200, W + 200, 300): d.line((x + 40, 0, x - 160, H), fill=(196, 198, 204, 255), width=4)
        for y in range(0, H, 330): d.line((0, y, W, y + 60), fill=(196, 198, 204, 255), width=4)
        d.rounded_rectangle((90, 250, 420, 330), 10, fill=(250, 250, 252, 255), outline=(190, 192, 198, 255), width=3)                 # a neon tube and a smoke detector
        d.ellipse((800, 1500, 900, 1600), fill=(236, 236, 238, 255), outline=(180, 182, 188, 255), width=4); d.ellipse((840, 1540, 860, 1560), fill=(60, 200, 90, 255))
        b_.alpha_composite(aa_down(ov))
        tex = np.random.default_rng(3).normal(0, 5, (H, W, 1)); yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
        lit = np.clip(1.12 - ((xx_ - 250) ** 2 + (yy_ - 290) ** 2) / 3.5e6, 0.72, 1.12)[..., None]
        _SPKBG = Image.fromarray(np.clip((np.asarray(b_.convert("RGB")) + tex) * lit, 0, 255).astype(np.uint8))
    im = _SPKBG.convert("RGBA"); cx, cy, r = 540, 900, 300 * (1 + amp * 0.03)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((cx - r - 30, cy - r - 10, cx + r + 50, cy + r + 50), fill=(0, 0, 0, 90)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
    ov = aa_layer(); d = SD(ov)
    d.ellipse((cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18), fill=(238, 238, 240, 255), outline=(170, 172, 178, 255), width=6)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(60, 62, 68, 255))
    for yy in range(int(cy - 300 + 20), int(cy + 300 - 10), 26):
        for xx in range(int(cx - 300 + 20), int(cx + 300 - 10), 26):
            if (xx - cx) ** 2 + (yy - cy) ** 2 < (300 - 24) ** 2:
                k_ = r / 300; X, Y = cx + (xx - cx) * k_, cy + (yy - cy) * k_
                d.ellipse((X - 7, Y - 7, X + 7, Y + 7), fill=(22, 22, 26, 255)); d.ellipse((X - 7, Y - 8, X + 7, Y - 5), fill=(96, 98, 106, 255))            # rim highlight on each hole
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)): d.ellipse((cx + sx * (r + 2) * 0.72 - 9, cy + sy * (r + 2) * 0.72 - 9, cx + sx * (r + 2) * 0.72 + 9, cy + sy * (r + 2) * 0.72 + 9), fill=(150, 152, 158, 255))   # screws
    live = 0 <= i0 < len(a)
    d.ellipse((cx + r - 10, cy - r - 30, cx + r + 22, cy - r + 2), fill=(230, 30, 25, 255) if live and int(t * 4) % 2 == 0 else (90, 30, 30, 255))
    if live:
        for q in range(3):
            ph = ((t * 1.6) + q / 3) % 1; rr = r + 30 + ph * 260
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(200, 25, 25, int(140 * (1 - ph) * min(1, amp * 3))), width=6)
    im.alpha_composite(aa_down(ov))
    ImageDraw.Draw(im).text((cx, cy + r + 80), "VALMONT · ANNONCE", font=fI("SemiBold", 30), fill=(150, 152, 158), anchor="mm")
    im = im.convert("RGB")
    if live: im = spill(im, cx, cy, 760, 760, (255, 30, 25), min(0.3, amp * 0.5))
    fl = 0.75 if (int(t * 13) % 7 == 0) else 1.0
    im = Image.fromarray((np.asarray(im).astype(np.float32) * fl).astype(np.uint8))
    return view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t1, 1.0, 1.1, 0.5, 0.48)


CONC = Image.open(NEW + "tex/concrete_wall_008_diff.jpg").convert("RGB")
SAMIR_HEAD = Image.open(SPR1 + "samir_X_0.png").convert("RGBA").crop((170, 40, 630, 560))
HERO_HEAD = Image.open(SPR1 + "interim_X_0.png").convert("RGBA").crop((170, 40, 630, 560))


def badge_card(w=560, h=860, who="SAMIR L.", num="V-0451", head=SAMIR_HEAD, role="Analyste"):
    c = paper_tex(w, h, (246, 246, 244), seed=21); d = ImageDraw.Draw(c)
    d.rectangle((0, 0, w, 150), fill=(25, 25, 30)); d.text((40, 75), "VALMONT", font=fI("Bold", 54), fill=(255, 255, 255), anchor="lm")
    d.rectangle((0, 150, w, 166), fill=RED)
    d.rounded_rectangle((w / 2 - 70, 30, w / 2 + 70, 52), 11, fill=(70, 70, 76))          # lanyard slot
    ph = Image.new("RGBA", (300, 340), (205, 208, 214, 255)); ph.alpha_composite(head.resize((300, 340))); c.alpha_composite(ph, (int(w / 2 - 150), 210))
    d.text((w / 2, 610), who, font=fI("Bold", 58), fill=(25, 25, 28), anchor="mm"); d.text((w / 2, 670), role, font=fI("Medium", 34), fill=(110, 110, 116), anchor="mm")
    d.text((w / 2, 760), num, font=ImageFont.truetype(MONO, 46), fill=(25, 25, 28), anchor="mm")
    m = Image.new("L", c.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=255); c.putalpha(m)
    return c


BADGE = badge_card()
HERO_BADGE = badge_card(who="TOI", num="V-0452", head=HERO_HEAD, role="Intérimaire")
_hb = HERO_BADGE.resize((230, 353)); _hand = Image.new("RGBA", (330, 470), (0, 0, 0, 0)); _hd = ImageDraw.Draw(_hand)
_hd.rounded_rectangle((150, 300, 330, 470), 60, fill=(120, 78, 52, 255)); _hd.rounded_rectangle((176, 404, 330, 470), 26, fill=(112, 116, 126, 255)); _hd.rectangle((176, 404, 330, 418), fill=(92, 96, 106, 255)); _hand.alpha_composite(_hb, (40, 20))
_hd = ImageDraw.Draw(_hand); _hd.rounded_rectangle((185, 250, 255, 380), 32, fill=(138, 90, 60, 255)); _hd.ellipse((195, 258, 245, 300), fill=(176, 128, 100, 255))   # thumb holding the card
HERO_BADGE_S = _hand
DUST = np.random.default_rng(9).random((90, 4))
def stairs_shot(t, t0, t1):
    im = ST["stairs"].copy().convert("RGBA"); lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, s_, ph in DUST:                                      # dust drifting through the bulb light
        yy = (y * im.height * 0.7 + t * (12 + s_ * 20)) % (im.height * 0.7); xx = x * im.width + np.sin(t * 0.7 + ph * 6) * 30
        r_ = 1.5 + s_ * 3.5; d.ellipse((xx - r_, yy - r_, xx + r_, yy + r_), fill=(255, 230, 190, int(60 + 120 * s_)))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))
    fl = 1.0 if (int(t * 11) % 9) else 0.72                          # the caged bulb fails for a frame now and then
    w_, h_ = im.size
    im = spill(im, 0, 0, 300, 300, (255, 205, 150), 0.2, poly=[(0.44 * w_, 0), (0.56 * w_, 0), (0.86 * w_, 0.78 * h_), (0.14 * w_, 0.78 * h_)])    # a cone of dusty light under the bulb
    im = spill(im, 0.385 * w_, 0.632 * h_, 70, 50, (255, 240, 210), 0.35 * (0.5 + 0.5 * np.sin(t * 5)))                                             # something glints on a step
    im = Image.fromarray((np.asarray(im.convert("RGB")).astype(np.float32) * fl).astype(np.uint8))
    return view(im, t, t0, t1, 1.0, 1.14, 0.5, 0.56)


def ins_badge(t, t0, t1):
    """Samir's badge on a concrete step, under the caged bulb: a glint runs across the plastic."""
    bg = CONC.resize((int(W * 1.3), int(W * 1.3 * CONC.height / CONC.width))).crop((0, 0, W, H)) if CONC.width else None
    a = np.asarray(bg.resize((W, H))).astype(np.float32) * np.array([0.55, 0.52, 0.48])
    yy_, xx_ = np.mgrid[0:H, 0:W]; a *= np.clip(1.25 - ((xx_ - 560) ** 2 + (yy_ - 700) ** 2) / 1.1e6, 0.25, 1.2)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.rectangle((0, 1500, W, 1540), fill=(150, 120, 20)); d.rectangle((0, 1540, W, H), fill=(40, 38, 36))     # step nosing and the step below
    sc_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd_ = ImageDraw.Draw(sc_); rs = random.Random(4)                # scratched into the concrete: days counted, a warning
    for g_ in range(5):
        gx, gy = 640 + (g_ % 3) * 130, 1230 + (g_ // 3) * 120
        for q in range(4): sd_.line((gx + q * 20 + rs.uniform(-3, 3), gy, gx + q * 20 + rs.uniform(-3, 3), gy + 80), fill=(215, 208, 196, 150), width=4)
        if g_ < 4: sd_.line((gx - 12, gy + 66, gx + 76, gy + 10), fill=(215, 208, 196, 150), width=4)
    fs_ = ImageFont.truetype(HAND, 78)
    for q in range(2): sd_.text((70 + rs.uniform(-2, 2), 1290 + rs.uniform(-2, 2)), "NE RESTE PAS", font=fs_, fill=(215, 208, 196, 120))
    im.alpha_composite(sc_.filter(ImageFilter.GaussianBlur(0.8)))
    lan = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lan)
    pts = [(540 + 240 * np.sin(q * 2.2) * (1 - q * 0.3), 330 - q * 420 + 60 * np.sin(q * 6)) for q in np.linspace(0, 1, 40)]
    ld.line(pts, fill=RED + (255,), width=22, joint="curve"); im.alpha_composite(lan)
    b = BADGE.rotate(-14, expand=True, resample=Image.BICUBIC)
    g = (t - t0 - 0.5) / 0.9                                           # the glint
    if 0 < g < 1:
        gl = Image.new("L", b.size, 0); gd = ImageDraw.Draw(gl); x0 = -300 + g * (b.width + 600)
        gd.polygon([(x0, 0), (x0 + 120, 0), (x0 - 280, b.height), (x0 - 400, b.height)], fill=170)
        gl = Image.fromarray(np.minimum(np.asarray(gl.filter(ImageFilter.GaussianBlur(30))), np.asarray(b.getchannel("A"))))
        b = b.copy(); wl = Image.new("RGBA", b.size, (255, 250, 235, 255)); wl.putalpha(gl); b.alpha_composite(wl)
    drop_shadow(im, b, (190, 420), blur=24, off=(26, 34), alpha=170)
    return view(im.convert("RGB").resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, 1.0, 1.12, 0.52, 0.52)


def drawing():
    """A child's drawing: crayon sky and sun, the house, a tall dad and a small girl holding hands, 'PAPA RENTRE À 18H ♥'."""
    w, h = 900, 1180; p = paper_tex(w, h, (250, 248, 240), fiber=0.03, seed=33); d = ImageDraw.Draw(p)
    rg = np.random.default_rng(5)
    def crayon(pts, col, wd=10, passes=3):
        for _ in range(passes):
            q = [(x + rg.normal(0, 2.2), y + rg.normal(0, 2.2)) for x, y in pts]; d.line(q, fill=col + (int(rg.uniform(150, 220)),), width=wd, joint="curve")
    for y in range(40, 260, 14): crayon([(30, y + rg.normal(0, 4)), (w - 30, y + rg.normal(0, 4))], (110, 170, 230), 12, 1)          # sky scribble
    cx, cy = 760, 150
    for a in np.linspace(0, 2 * np.pi, 12, endpoint=False): crayon([(cx + np.cos(a) * 80, cy + np.sin(a) * 80), (cx + np.cos(a) * 125, cy + np.sin(a) * 125)], (250, 190, 30), 9, 1)
    crayon([(cx + np.cos(a) * 62, cy + np.sin(a) * 62) for a in np.linspace(0, 2 * np.pi, 30)], (250, 190, 30), 14, 3)
    crayon([(60, 900), (w - 60, 905)], (90, 160, 60), 16, 2)                                                                            # grass
    crayon([(90, 520), (90, 900), (380, 900), (380, 520), (90, 520)], (180, 60, 40), 10); crayon([(70, 530), (235, 360), (400, 530)], (180, 60, 40), 12)   # house
    crayon([(200, 900), (200, 760), (270, 760), (270, 900)], (120, 80, 50), 9); crayon([(120, 580), (180, 580), (180, 640), (120, 640), (120, 580)], (110, 170, 230), 8)
    def person(x, foot, hgt, col, hair, smile=True):
        hr = hgt * 0.13; hy = foot - hgt + hr
        crayon([(x + np.cos(a) * hr, hy + np.sin(a) * hr) for a in np.linspace(0, 2 * np.pi, 24)], (60, 40, 30), 7, 2)
        crayon([(x - hr * 0.9, hy - hr * 0.6), (x, hy - hr * 1.15), (x + hr * 0.9, hy - hr * 0.6)], hair, 10, 2)
        crayon([(x - hr * 0.4, hy - hr * 0.1), (x - hr * 0.38, hy)], (30, 30, 30), 6, 1); crayon([(x + hr * 0.4, hy - hr * 0.1), (x + hr * 0.38, hy)], (30, 30, 30), 6, 1)
        crayon([(x - hr * 0.45, hy + hr * 0.35), (x, hy + hr * 0.6), (x + hr * 0.45, hy + hr * 0.35)], (200, 40, 40), 5, 1)
        crayon([(x - hgt * 0.14, hy + hr), (x + hgt * 0.14, hy + hr), (x + hgt * 0.17, foot - hgt * 0.38), (x - hgt * 0.17, foot - hgt * 0.38), (x - hgt * 0.14, hy + hr)], col, 9, 3)
        crayon([(x - hgt * 0.07, foot - hgt * 0.38), (x - hgt * 0.1, foot)], (40, 40, 60), 8, 2); crayon([(x + hgt * 0.07, foot - hgt * 0.38), (x + hgt * 0.1, foot)], (40, 40, 60), 8, 2)
        return hy + hr * 1.6
    ay = person(560, 900, 430, (60, 90, 160), (30, 25, 25)); by_ = person(760, 900, 250, (230, 120, 170), (60, 35, 20))
    crayon([(560 + 430 * 0.15, ay + 40), (690, 760), (760 - 250 * 0.15, by_ + 25)], (60, 40, 30), 7, 2)                              # holding hands
    f = ImageFont.truetype(HAND, 112)
    for k, (txt, y) in enumerate((("PAPA RENTRE", 960), ("À 18H", 1065))):
        for q in range(2): d.text((w / 2 + rg.normal(0, 1.5), y + rg.normal(0, 1.5)), txt, font=f, fill=(205, 30, 30, 200), anchor="mm")
    hx, hy_ = 700, 1075
    crayon([(hx, hy_ + 30), (hx - 40, hy_ - 5), (hx - 25, hy_ - 30), (hx, hy_ - 12), (hx + 25, hy_ - 30), (hx + 40, hy_ - 5), (hx, hy_ + 30)], (220, 30, 50), 9, 3)
    crayon([(60, 1135), (300, 1132)], (60, 90, 160), 5, 1); d.text((70, 1110), "Inès, 6 ans", font=ImageFont.truetype(HAND, 52), fill=(60, 90, 160, 220))
    a = np.asarray(p).astype(np.float32)                                                                                               # fold creases
    for fx in (w // 2,):
        a[:, fx - 3:fx + 3, :3] *= 0.86; a[:, fx + 3:fx + 40, :3] *= np.linspace(0.93, 1, 37)[None, :, None]
    for fy in (h // 2,):
        a[fy - 3:fy + 3, :, :3] *= 0.88; a[fy + 3:fy + 30, :, :3] *= np.linspace(0.94, 1, 27)[:, None, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


DRAW = drawing()
def ins_drawing(t, t0, t1):
    a = np.asarray(CONC.resize((W, int(W * CONC.height / CONC.width))).resize((W, H))).astype(np.float32) * 0.32
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA").filter(ImageFilter.GaussianBlur(3))
    u = min(1.0, (t - t0) / 0.45); u = u * u * (3 - 2 * u)                         # unfolding
    dp = DRAW.resize((DRAW.width, max(2, int(DRAW.height * (0.5 + 0.5 * u)))))
    sh_ = (1 - u) * 0.35; arr = np.asarray(dp).astype(np.float32); arr[: arr.shape[0] // 2, :, :3] *= (1 - sh_); dp = Image.fromarray(arr.astype(np.uint8), "RGBA")
    tr = np.sin(t * 9) * 0.25 + np.sin(t * 13.7) * 0.15                            # a trembling hand
    dp = dp.rotate(-2.5 + tr, expand=True, resample=Image.BICUBIC)
    warm = Image.new("RGBA", (W, H), (255, 190, 120, 0)); ImageDraw.Draw(warm).ellipse((80, 300, 1000, 1500), fill=(255, 190, 120, 40)); im.alpha_composite(warm.filter(ImageFilter.GaussianBlur(120)))
    drop_shadow(im, dp, (int(W / 2 - dp.width / 2), int(860 - dp.height / 2)), blur=30, off=(18, 30), alpha=180)
    im = torch(im, 540 + np.sin(t * 1.3) * 70, 840 + np.cos(t * 1.1) * 60, 1150, 0.45, 1.12)       # your phone torch, held by a shaking hand
    return view(im.convert("RGB").resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, 1.0, 1.12, 0.5, 0.6, drift=0.4)


LED_DOOR = (0.835, 0.5)
def door_shot(t, t0, t1):
    base = ST["stairdoor"].copy(); lay = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    lx, ly = LED_DOOR[0] * base.width, LED_DOOR[1] * base.height
    col = (40, 255, 90, 150) if t >= T_OUVRE else ((255, 30, 20, 150) if int(t * 3) % 2 == 0 else (255, 30, 20, 40))
    d.ellipse((lx - 70, ly - 50, lx + 70, ly + 50), fill=col)
    im = Image.alpha_composite(base.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(22)))
    bw_, bh_ = base.size; dd_ = ImageDraw.Draw(im)
    dd_.rounded_rectangle((0.33 * bw_, 0.42 * bh_, 0.72 * bw_, 0.47 * bh_), 8, fill=(18, 18, 20, 235), outline=(110, 112, 118, 255), width=3)
    dd_.text((0.525 * bw_, 0.435 * bh_), "PERSONNEL PERMANENT", font=fI("Bold", 34), fill=(205, 205, 200), anchor="mm"); dd_.text((0.525 * bw_, 0.457 * bh_), "aucune sortie", font=fI("Medium", 24), fill=(200, 40, 40), anchor="mm")
    for q in range(8): dd_.rectangle((0.215 * bw_ + q * 0.09 * bw_, 0.8 * bh_, 0.215 * bw_ + q * 0.09 * bw_ + 0.045 * bw_, 0.825 * bh_), fill=(170, 135, 20, 150))      # worn hazard band
    rs = random.Random(11); sl = Image.new("RGBA", base.size, (0, 0, 0, 0)); sd_ = ImageDraw.Draw(sl)
    for q in range(9):                                               # fingernail scratches under the handle, from the inside out
        x_ = (0.52 + rs.uniform(0, 0.2)) * bw_; y_ = (0.6 + rs.uniform(0, 0.03)) * bh_; sd_.line((x_, y_, x_ + rs.uniform(-25, 25), y_ + rs.uniform(150, 330)), fill=(190, 190, 186, 95), width=3)
    im.alpha_composite(sl.filter(ImageFilter.GaussianBlur(0.7))); im = im.convert("RGB")
    if t >= T_OUVRE:                                                         # the door gives way by a few centimetres: a blade of cold light
        g = min(1, (t - T_OUVRE) / 0.6); dl = Image.new("RGBA", base.size, (0, 0, 0, 0))
        ImageDraw.Draw(dl).rectangle((0.205 * base.width, 0.2 * base.height, 0.205 * base.width + 10 * g, 0.84 * base.height), fill=(150, 190, 255, int(200 * g)))
        im = Image.alpha_composite(im.convert("RGBA"), dl.filter(ImageFilter.GaussianBlur(6))).convert("RGB")
    if t >= T_OUVRE:
        g = min(1, (t - T_OUVRE) / 0.6)
        im = spill(im, lx, ly, 300, 300, (40, 255, 90), 0.28 * g)                                    # green on the frame and the wall
        im = spill(im, 0.56 * bw_, 0.855 * bh_, 0.42 * bw_, 0.05 * bh_, (120, 170, 255), 0.55 * g)   # cold light leaking under the door
    else: im = spill(im, lx, ly, 220, 220, (255, 30, 20), 0.2 if int(t * 3) % 2 == 0 else 0.05)
    if t < T_MOINS: return view(im, t, t0, T_MOINS, 1.0, 1.08, 0.5, 0.5)
    return view(im, t, T_MOINS, t1, 1.08, 1.45, 0.5, 0.33)


WORKERS = None
def basement_plate():
    """Level -2 with its employees placed behind their screens: heads above the monitors, lit blue, eyes closed."""
    global WORKERS
    base = ST["basement"].convert("RGBA"); rg = random.Random(7)
    sp = sorted([s for s in SPOTS if s["d"] < 26], key=lambda s: -s["d"])
    for s in sp:
        if rg.random() < 0.18: continue                                     # some empty chairs
        hpx = (s["fy"] - s["hy"]) * base.height / (1 - 44 / 900) * 1.02
        who = rg.choice(["w1", "w2", "w3", "w4", "w5"])
        spr = sprite(who, "X", 1, max(20, int(hpx)))
        fade = np.clip(1.15 - s["d"] / 26, 0.15, 1)
        spr = tint(spr, (0.42 * fade, 0.55 * fade, 0.85 * fade), (4, 8, 22))
        cut = int((s["my"] - (s["fy"] - spr.height / base.height)) * base.height)    # hide what the monitor and desk cover
        cut = max(0, min(spr.height, cut + int(spr.height * 0.02)))
        sp_ = spr.crop((0, 0, spr.width, cut))
        base.alpha_composite(sp_, (int(s["hx"] * base.width - spr.width / 2), int(s["fy"] * base.height - spr.height)))
    WORKERS = base.convert("RGB")
    return WORKERS


WLIST = None
def basement_live(t):
    """Per-frame: every worker bobs over the keyboard at his own rhythm; screens flicker on their faces."""
    global WLIST
    if WLIST is None:
        base = ST["basement"]; rg = random.Random(7); WLIST = []
        for s in sorted([s for s in SPOTS if s["d"] < 26], key=lambda s: -s["d"]):
            if rg.random() < 0.18: continue
            hpx = (s["fy"] - s["hy"]) * base.height / (1 - 44 / 900) * 1.02
            spr = sprite(rg.choice(["w1", "w2", "w3", "w4", "w5"]), "X", 1, max(20, int(hpx)))
            fade = np.clip(1.15 - s["d"] / 26, 0.15, 1); spr = tint(spr, (0.42 * fade, 0.55 * fade, 0.85 * fade), (4, 8, 22))
            cut = max(0, min(spr.height, int((s["my"] - (s["fy"] - spr.height / base.height)) * base.height + spr.height * 0.02)))
            WLIST.append((spr.crop((0, 0, spr.width, cut)), int(s["hx"] * base.width - spr.width / 2), int(s["fy"] * base.height - spr.height), rg.uniform(1.3, 2.2), rg.uniform(0, 6.28), spr.height))
    im = ST["basement"].convert("RGBA")
    for spr, x, y, f_, ph, hh in WLIST:
        bob = np.sin(t * 2 * np.pi * f_ + ph) * hh * 0.006
        sp = spr if int(t * 7 + ph * 3) % 11 else spr.point(lambda v: v * 0.8)
        im.alpha_composite(sp, (x, int(y + bob)))
    hz = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(hz).rectangle((0, int(im.height * 0.4), im.width, int(im.height * 0.52)), fill=(70, 100, 170, 70))
    im.alpha_composite(hz.filter(ImageFilter.GaussianBlur(70)))
    bw_, bh_ = im.size; cx_, cy_ = bw_ * 0.5, bh_ * 0.405; d_ = ImageDraw.Draw(im)       # down here it is always 18:00:00
    d_.line((cx_ - 70, cy_ - 60, cx_ - 70, cy_ - 30), fill=(40, 42, 48), width=4); d_.line((cx_ + 70, cy_ - 60, cx_ + 70, cy_ - 30), fill=(40, 42, 48), width=4)
    d_.rounded_rectangle((cx_ - 130, cy_ - 34, cx_ + 130, cy_ + 34), 8, fill=(6, 6, 8), outline=(50, 52, 58), width=3)
    on_ = int(t * 2) % 9 != 0
    gl_ = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(gl_).text((cx_, cy_), "18:00:00", font=ImageFont.truetype(MONO, 48), fill=(255, 30, 20, 255 if on_ else 110), anchor="mm")
    im.alpha_composite(gl_.filter(ImageFilter.GaussianBlur(9))); im.alpha_composite(gl_)
    return im.convert("RGB")


def basement_shot(t, t0, t1):
    return view(basement_live(t), t, t0, t1, 1.12, 1.3, 0.5, 0.53, drift=0.6)


def ins_face(t, t0, t1):
    """One of them, close: eyes closed, lips still, the screen glow from below; the fingers never stop."""
    im = Image.new("RGB", (W, H), (4, 5, 9)).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((-100, 1100, 1180, 2300), fill=(90, 130, 220, 150)); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(160)))
    sp = sprite("w3", "X", 1, 2900); sp = tint(sp, (0.55, 0.66, 0.95), (6, 10, 24))
    a = np.asarray(sp).astype(np.float32); grad = np.linspace(0.55, 1.25, sp.height)[:, None, None]; a[..., :3] = np.clip(a[..., :3] * grad, 0, 255); sp = Image.fromarray(a.astype(np.uint8), "RGBA")
    bob = np.sin(t * 2 * np.pi * 1.7) * 3
    im.alpha_composite(sp, (int(W / 2 - sp.width / 2), int(1650 - sp.height * 0.36 + bob)))
    d = ImageDraw.Draw(im); d.rectangle((0, 1560, W, H), fill=(6, 6, 9)); d.rectangle((0, 1556, W, 1566), fill=(120, 160, 240))           # monitor edge, glowing
    return view(im.convert("RGB").resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, 1.0, 1.1, 0.5, 0.42, drift=0.3)


def _head(who, blink=1):
    f = SPR2 + (f"{who}_X_{blink}.png" if not who.startswith("samir") else f"{who}_X_1.png")
    hd_ = Image.open(f).convert("RGBA").crop((170, 40, 630, 560)).resize((120, 120))
    c = Image.new("RGBA", (120, 120), (40, 52, 80, 255)); c.alpha_composite(tint(hd_, (0.6, 0.7, 0.95), (6, 10, 24))); return c.convert("RGB")
PERM_HEADS = [(_head("w2"), "V-0388"), (_head("w4"), "V-0402"), (_head("samir_tired"), "V-0451"), (_head("w1"), "V-0417"), (_head("w5"), "V-0440"), (_head("w3"), "V-0396")]


def ins_screen(t, t0, t1):
    """Your employee record on a level -2 screen: your photo, V-0452 (the number after Samir), status typed in red."""
    im = Image.new("RGB", (W, H), (8, 12, 22)); d = ImageDraw.Draw(im)
    d.rectangle((80, 260, 1000, 1500), fill=(14, 22, 40)); d.rectangle((80, 260, 1000, 340), fill=(22, 34, 62))
    d.text((120, 300), "VALMONT · RESSOURCES HUMAINES · NIVEAU -2", font=ImageFont.truetype(MONO, 26), fill=(150, 175, 230), anchor="lm")
    ph = Image.new("RGBA", (300, 340), (40, 52, 80, 255)); ph.alpha_composite(HERO_HEAD.resize((300, 340))); im.paste(ph.convert("RGB"), (130, 400))
    fm = ImageFont.truetype(MONO, 40)
    rows = (("MATRICULE", "V-0452"), ("POSTE", "Intérimaire"), ("ARRIVÉE", "Aujourd'hui 08:00"), ("DÉPART", "—"))
    for k, (a_, b_) in enumerate(rows):
        d.text((470, 420 + k * 70), a_, font=ImageFont.truetype(MONO, 28), fill=(110, 130, 175)); d.text((470, 452 + k * 70), b_, font=fm, fill=(225, 232, 245))
    d.text((130, 780), "STATUT :", font=ImageFont.truetype(MONO, 48), fill=(150, 175, 230))
    full = "BIENTÔT PERMANENT"; ts = wt("n07", "Statut") + 0.35
    n = int(np.clip((t - ts) / 0.045, 0, len(full))); txt = full[:n] + ("█" if int(t * 3) % 2 == 0 else " ")
    d.text((130, 850), txt, font=ImageFont.truetype(MONO, 72), fill=(235, 40, 40))
    d.text((130, 960), "Heures supplémentaires acceptées : 0", font=ImageFont.truetype(MONO, 30), fill=(110, 130, 175))
    d.rectangle((130, 1004, 950, 1028), outline=(60, 80, 120), width=3); d.rectangle((134, 1008, 134 + int(812 * min(1, (t - t0) / 6) * 0.97), 1024), fill=(200, 30, 30))
    d.text((130, 1050), "PERMANENTS : 1 247", font=ImageFont.truetype(MONO, 28), fill=(150, 175, 230))
    for k, (hd_, lab) in enumerate(PERM_HEADS):                     # the wall of permanents, Samir among them
        x = 130 + k * 140; d.rectangle((x - 4, 1086, x + 124, 1214), outline=RED if lab == "V-0451" else (60, 80, 120), width=4 if lab == "V-0451" else 2)
        im.paste(hd_, (x, 1090)); d.text((x + 60, 1236), lab, font=ImageFont.truetype(MONO, 20), fill=(235, 60, 60) if lab == "V-0451" else (110, 130, 175), anchor="mm")
    a = np.asarray(im).astype(np.float32); a[::3] *= 0.86                       # scanlines + screen glow
    a += cv2.GaussianBlur(a, (0, 0), 18) * 0.35
    dark = 1 - 0.85 * np.clip((t - t_sil) / 1.0, 0, 1)                           # the silence: the screen dies
    im = Image.fromarray(np.clip(a * dark, 0, 255).astype(np.uint8))
    return view(im.resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, 1.0, 1.12, 0.48, 0.5)


def samir_smear(k, base):
    dx, sx, sh_, spread = {-3: (330, 2.3, -0.45, 700), -2: (180, 1.75, -0.3, 520), -1: (60, 1.2, -0.1, 300)}[k]
    cx, foot, h = 540, 2500, 2200
    sp = sprite("samir_tired", "D", 0, h); w2 = int(sp.width * sx); body = sp.resize((w2, int(h * 0.96)))
    body = body.transform(body.size, Image.AFFINE, (1, sh_, -sh_ * body.height, 0, 1, 0), resample=Image.BILINEAR)
    left = cx + dx - w2 / 2; im = base.convert("RGBA"); lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r_ = random.Random(k); top = foot - h
    for n in range(26):
        y = top + 60 + n * (h - 120) / 26 + r_.uniform(-12, 12); hh = r_.uniform(14, 34); f_ = (y - top) / h
        col = (30, 26, 26) if f_ < 0.08 else (138, 90, 60) if f_ < 0.22 else r_.choice([(51, 80, 124), (40, 60, 100), (200, 25, 25)]) if f_ < 0.5 else (40, 44, 60)
        x1 = left + w2 * r_.uniform(0.5, 0.8); x0 = x1 + r_.uniform(spread * 0.5, spread)
        d.polygon([(x1, y), (x0, y), (x0 + r_.uniform(0, 40), y + hh), (x1 - r_.uniform(10, 60), y + hh)], fill=col + (int(r_.uniform(150, 235)),))
    im = Image.alpha_composite(im, lay)
    for g in range(3):
        gh = body.copy(); gh.putalpha(gh.getchannel("A").point(lambda v, o=(0.45 - g * 0.13): int(v * o))); im.alpha_composite(gh, (int(left + 170 * (g + 1)), int(foot - body.height)))
    im.alpha_composite(body, (int(left), int(foot - body.height)))
    return im.convert("RGB")


def samir_shot(t, t0, t1, talk=True):
    base = (WORKERS if WORKERS is not None else basement_plate()).resize((int(W * 1.2), int(H * 1.2))).filter(ImageFilter.GaussianBlur(7))
    m = mouth_at(t) if talk else "X"; blink = ((t + 1.1) % 2.3) < 0.1
    sp = sprite("samir_tired", m, blink, 2300)
    sp = tint(sp, (0.62, 0.72, 1.0), (4, 6, 16))
    a = np.asarray(sp).astype(np.float32); a[..., :3] *= np.linspace(1.15, 0.45, sp.height)[:, None, None]; sp = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    ttear = line_t["s01"] + dur["s01"] * 0.55
    if t > ttear:                                                  # one tear runs down from his right eye
        sp = sp.copy(); dd = ImageDraw.Draw(sp); sx_, sy_ = sp.width / 400, sp.height / 900; p_ = min(1.0, (t - ttear) / 1.6)
        x0, y0 = 252 * sx_, 196 * sy_; y1 = y0 + p_ * 46 * sy_
        dd.line((x0, y0, x0 + 3 * sx_ * p_, y1), fill=(170, 210, 255, 150), width=int(3 * sx_)); dd.ellipse((x0 + 3 * sx_ * p_ - 4 * sx_, y1 - 4 * sx_, x0 + 3 * sx_ * p_ + 4 * sx_, y1 + 6 * sx_), fill=(210, 235, 255, 230))
    fk = 0.8 + 0.2 * np.sin(t * 9) * np.sin(t * 3.1)                                                                 # hundreds of screens flickering behind him
    sp = rim_light(rim_light(sp, (60, 110, 210), 12, fk * 0.5, blur=3), (40, 70, 150), -12, fk * 0.4, blur=3)
    br = 1 + 0.012 * np.sin(t * 2 * np.pi / 1.4); sp = sp.resize((sp.width, int(sp.height * br)), Image.BICUBIC)      # short, fast breaths
    shake = np.sin(t * 31) * 3 + np.sin(t * 17) * 2                                 # he is shaking
    ox, oy = 0.5 * base.width - W / 2, 0.5 * base.height - H / 2
    im = base.convert("RGBA"); im.alpha_composite(sp, (int(540 + ox - sp.width / 2 + shake), int(2600 + oy - sp.height)))
    return view(im.convert("RGB"), t, t0, t1, 1.0, 1.07, 0.5, 0.45)


_RULES = None
def ins_rules(t, t0, t1):
    """The framed house rules on the lobby wall. Article 4 is the one that matters: a red marker circles it as you read."""
    global _RULES
    if _RULES is None:
        w, h = 860, 1240; pp = paper_tex(w, h, (247, 246, 240), fiber=0.03, seed=41); l = aa_layer(w, h); d = SD(l)
        d.rectangle((0, 0, w, 170), fill=(25, 25, 30, 255)); d.rectangle((0, 170, w, 184), fill=RED + (255,))
        d.text((50, 70), "VALMONT", font=fI("Bold", 64), fill=(255, 255, 255, 255), anchor="lm"); d.text((52, 128), "RÈGLEMENT INTÉRIEUR · NOTE DE SERVICE 18-B", font=fI("SemiBold", 24), fill=(190, 190, 196, 255), anchor="lm")
        rules = ["Le badge se porte visible. Toujours.", "On ne parle pas des anciens collègues.", "Les heures supplémentaires ne se refusent pas.", "Après 18 h, personne ne sort.", "Valmont est votre famille."]
        for k, r_ in enumerate(rules):
            y = 260 + k * 172; hot = k == 3
            d.ellipse((50, y, 130, y + 80), fill=(RED if hot else (25, 25, 30)) + (255,)); d.text((90, y + 40), str(k + 1), font=fI("Bold", 44), fill=(255, 255, 255, 255), anchor="mm")
            d.text((160, y + 40), r_, font=fI("Bold" if hot else "SemiBold", 29 if not hot else 38), fill=(RED if hot else (40, 40, 46)) + (255,), anchor="lm")
            d.line((160, y + 112, w - 50, y + 112), fill=(222, 220, 214, 255), width=2)
        d.text((50, h - 70), "Toute infraction entraîne une affectation permanente.", font=fI("Medium", 24), fill=(120, 120, 126, 255), anchor="lm")
        d.text((w - 50, h - 70), "Dir. K.", font=ImageFont.truetype(HAND, 50), fill=(24, 30, 70, 255), anchor="rm")
        pp.alpha_composite(aa_down(l))
        fr = Image.new("RGBA", (w + 60, h + 60), (22, 22, 26, 255)); fr.paste(pp, (30, 30))
        gl = Image.new("RGBA", fr.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).polygon([(0, 0), (fr.width * 0.6, 0), (fr.width * 0.15, fr.height)], fill=(255, 255, 255, 16)); fr.alpha_composite(gl)   # glass
        _RULES = fr
    yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
    wall = np.array([226, 228, 232], np.float32)[None, None] * np.clip(1.08 - ((xx_ - 300) ** 2 + (yy_ - 500) ** 2) / 5e6, 0.7, 1.08)[..., None]
    im = Image.fromarray(np.clip(wall, 0, 255).astype(np.uint8)).convert("RGBA")
    ImageDraw.Draw(im).rectangle((0, 1640, W, 1652), fill=RED)
    fr = _RULES
    g = float(np.clip((t - t0 - 0.9) / 0.7, 0, 1))                      # the red marker circle closes around rule 4
    if g > 0:
        fr = fr.copy(); l = aa_layer(fr.width, fr.height); d = SD(l); cx_, cy_, rx_, ry_ = 470, 846, 430, 78
        pts = [(cx_ + np.cos(a) * rx_ * (1 + 0.03 * np.sin(a * 3)), cy_ + np.sin(a) * ry_ * (1 + 0.05 * np.cos(a * 2))) for a in np.linspace(-2.6, -2.6 + 6.6 * g, max(2, int(70 * g)))]
        d.line(pts, fill=RED + (235,), width=9); fr.alpha_composite(aa_down(l))
    fr = fr.resize((int(fr.width * 0.86), int(fr.height * 0.86)), Image.LANCZOS).rotate(1.2, expand=True, resample=Image.BICUBIC)
    drop_shadow(im, fr, (int(W / 2 - fr.width / 2), int(1010 - fr.height / 2)), blur=26, off=(14, 26), alpha=120)
    im = im.convert("RGB")
    pulse = 0.5 + 0.5 * np.sin(t * 5); im = spill(im, 540, 1000, 900, 900, (255, 30, 25), 0.10 + 0.08 * pulse)        # the gate's red light breathing on the wall
    return view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t1, 1.0, 1.07, 0.5, 0.5 + 0.03 * g, drift=0.5)


def ins_bracelet(t, t0, t1):
    """His wrist, close: the bead bracelet his daughter made (P A P A and a heart), a shaking thumb, a tear landing on it."""
    im = (WORKERS if WORKERS is not None else basement_plate()).resize((W, H)).filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.55)).convert("RGBA")
    c = Image.new("RGBA", (1500, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((-200, 300, 560, 640), 60, fill=(51, 80, 124, 255)); d.rounded_rectangle((470, 290, 600, 650), 30, fill=(74, 106, 156, 255))        # sleeve and cuff
    for q in range(3): d.line((60 + q * 150, 330, 20 + q * 150, 610), fill=(38, 62, 100, 255), width=7)
    d.ellipse((540, 474, 566, 500), fill=(232, 232, 226, 255))                                                                                              # cuff button
    d.rounded_rectangle((560, 330, 1060, 610), 120, fill=(138, 90, 60, 255))                                                                                # wrist
    d.rounded_rectangle((960, 300, 1420, 640), 150, fill=(138, 90, 60, 255))                                                                                # hand
    for q in range(4): d.rounded_rectangle((1250, 318 + q * 78, 1480, 388 + q * 78), 34, fill=(128, 82, 54, 255), outline=(100, 62, 40, 255), width=4)      # curled fingers
    d.rounded_rectangle((1010, 250, 1250, 350), 48, fill=(146, 98, 66, 255), outline=(100, 62, 40, 255), width=4)                                           # thumb
    d.ellipse((1180, 262, 1238, 316), fill=(196, 150, 120, 255))
    d.line((700, 338, 700, 604), fill=(250, 250, 250, 255), width=6)                                                                                        # elastic
    beads = [("#5fc27a", ""), ("#e94b5a", "h"), ("#ffffff", "A"), ("#ffffff", "P"), ("#ffffff", "A"), ("#ffffff", "P"), ("#f6c443", ""), ("#4aa3e8", ""), ("#e94b5a", "")]
    fb = fI("Bold", 40)
    for k, (col, ch) in enumerate(beads):
        y = 320 + k * 33; x = 700 + np.sin(k * 0.7) * 5
        d.rounded_rectangle((x - 24, y - 3, x + 24, y + 29), 9 if ch and ch != "h" else 15, fill=col, outline=(0, 0, 0, 90), width=2)
        if ch == "h": d.text((x, y + 12), "♥", font=ImageFont.truetype(MONO, 30), fill=(255, 255, 255, 255), anchor="mm")
        elif ch:
            tl = Image.new("RGBA", (50, 50), (0, 0, 0, 0)); ImageDraw.Draw(tl).text((25, 25), ch, font=fb, fill=(40, 40, 46, 255), anchor="mm"); tl = tl.rotate(90).resize((34, 34)); c.alpha_composite(tl, (int(x - 17), int(y - 4)))
    a = np.asarray(c).astype(np.float32); a[..., :3] *= np.linspace(0.6, 1.1, c.height)[:, None, None] * np.array([0.78, 0.86, 1.08]); c = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    c = c.rotate(-76 + np.sin(t * 23) * 0.5 + np.sin(t * 14) * 0.4, expand=True, resample=Image.BICUBIC)
    sh = np.sin(t * 29) * 4
    drop_shadow(im, c, (int(W / 2 - c.width / 2 + 60 + sh), int(1000 - c.height / 2)), blur=40, off=(30, 40), alpha=160)
    tp = (t - t0 - 0.8) / 0.45                                       # a tear falls and breaks on the beads
    if tp > 0:
        dd = ImageDraw.Draw(im); ty = 560 + min(1.0, tp) ** 2 * 380
        if tp < 1: dd.ellipse((566, ty - 16, 588, ty + 18), fill=(200, 228, 255, 235))
        else:
            r_ = 30 + (tp - 1) * 40; sp_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sp_).ellipse((577 - r_, 950 - r_ * 0.4, 577 + r_, 950 + r_ * 0.4), outline=(200, 228, 255, int(max(0, 200 - (tp - 1) * 150))), width=5); im.alpha_composite(sp_)
    return view(im.convert("RGB").resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, 1.3, 1.5, 0.535, 0.5, drift=0.4)


# ---------------- on-screen text ----------------
def hud(im, dark=False, light_text=False):
    if dark: return
    d = ImageDraw.Draw(im); fs = ImageFont.truetype(MONT, 30)
    d.text((124, 236), "EMPLOI INSTABLE", font=fs, fill=(235, 235, 238) if light_text else (25, 25, 28)); d.text((124, 276), "ÉPISODE 2", font=fs, fill=RED)


_TAGS = {}
def tag(im, text):
    if text not in _TAGS:
        f = ImageFont.truetype(MONT, 34); w_ = int(ImageDraw.Draw(im).textlength(text, font=f)) + 34
        l = aa_layer(w_ + 8, 60); d = SD(l); d.rounded_rectangle((0, 2, w_, 54), 9, fill=RED + (255,)); d.rectangle((0, 2, 10, 54), fill=(120, 10, 10, 255)); d.text((20, 28), text, font=f, fill=(255, 255, 255, 255), anchor="lm")
        _TAGS[text] = aa_down(l)
    im.paste(_TAGS[text], (124, 358), _TAGS[text])


def hud_chip(im, text, t, t0):
    """Location line under the title: a blinking red dot and the place, typed in."""
    n = int(np.clip((t - t0) * 30, 0, len(text)))
    if n <= 0: return
    f = ImageFont.truetype(MONO, 27); w_ = int(ImageDraw.Draw(im).textlength(text[:n], font=f)) + 62
    l = aa_layer(w_ + 8, 56); d = SD(l)
    d.rounded_rectangle((0, 2, w_, 50), 24, fill=(10, 12, 16, 170), outline=(255, 255, 255, 70), width=2)
    d.ellipse((16, 17, 34, 35), fill=RED + (255 if int(t * 2) % 2 == 0 else 110,)); d.text((46, 26), text[:n], font=f, fill=(240, 240, 240, 255), anchor="lm")
    l = aa_down(l); im.paste(l, (124, 360), l)


def callout(im, t, t0, t1, pt, off, title, sub, color=RED):
    """Object marker: a pulsing ring on the object, an elbow line drawn out to a small label."""
    p = float(np.clip((t - t0) / 0.3, 0, 1)); fade = float(np.clip((t1 - t) / 0.2, 0, 1)); x, y = pt
    lx = float(np.clip(x + off[0], 150, 930)); ly = float(np.clip(y + off[1], 460, 1500)); A = lambda v: int(v * fade)
    ov = aa_layer(); d = SD(ov); pr = 26 + 6 * np.sin(t * 6)
    d.ellipse((x - pr, y - pr, x + pr, y + pr), outline=color + (A(255),), width=4); d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 255, 255, A(255)))
    for a_ in (0, 90, 180, 270):
        ca, sa = np.cos(np.radians(a_)), np.sin(np.radians(a_)); d.line((x + ca * (pr + 6), y + sa * (pr + 6), x + ca * (pr + 20), y + sa * (pr + 20)), fill=(255, 255, 255, A(220)), width=3)
    ex, ey = x + (lx - x) * p, y + (ly - y) * p; dn = max(1.0, float(np.hypot(lx - x, ly - y)))
    d.line((x + (lx - x) / dn * pr, y + (ly - y) / dn * pr, ex, ey), fill=(255, 255, 255, A(230)), width=3)
    if p >= 1:
        ft, fs_ = fI("Bold", 30), ImageFont.truetype(MONO, 23); n = int(np.clip((t - t0 - 0.3) * 34, 0, len(sub)))
        w_ = max(ImageDraw.Draw(im).textlength(title, font=ft), ImageDraw.Draw(im).textlength(sub, font=fs_)) + 40; right = off[0] >= 0
        bx0 = lx if right else lx - w_; bx0 = float(np.clip(bx0, 110, 970 - w_))
        d.rounded_rectangle((bx0, ly - 46, bx0 + w_, ly + 46), 10, fill=(10, 12, 16, A(205)), outline=color + (A(255),), width=3)
        d.rectangle((bx0, ly - 46, bx0 + 8, ly + 46), fill=color + (A(255),))
        d.text((bx0 + 24, ly - 20), title, font=ft, fill=(255, 255, 255, A(255)), anchor="lm"); d.text((bx0 + 24, ly + 20), sub[:n], font=fs_, fill=(215, 220, 228, A(255)), anchor="lm")
    out = im.convert("RGBA"); out.alpha_composite(aa_down(ov)); return out.convert("RGB")


THOUGHTS = []          # (start, end, text, x, y, ink): the hero's unsaid words, handwritten, shaky
def thought(im, t):
    for t0, t1, txt, x, y, ink in THOUGHTS:
        if not (t0 <= t < t1): continue
        n = int(np.clip((t - t0) * 22, 0, len(txt))); a_ = min(1.0, (t1 - t) / 0.25)
        lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = ImageFont.truetype(HAND, 108)
        rg = np.random.default_rng(int(t * 12)); xx = 20
        for k, ch in enumerate(txt[:n]):
            jx, jy = rg.normal(0, 1.3), rg.normal(0, 1.6)
            if ink == "light": d.text((xx + jx + 3, 120 + jy + 4), ch, font=f, fill=(0, 0, 0, int(160 * a_)))
            d.text((xx + jx, 120 + jy), ch, font=f, fill=((246, 244, 236) if ink == "light" else (24, 30, 70)) + (int(255 * a_),))
            xx += d.textlength(ch, font=f)
        lay = lay.rotate(-3, resample=Image.BICUBIC)
        im.paste(lay, (x, y), lay)


_KDARK = {}
def kessler_far(im, t):
    """B: she is already down here. A black figure at the end of the aisle, two pale eyes, a red pocket square; she comes closer."""
    u = float(np.clip((t - T_SPLIT) / max(0.5, D - T_SPLIT), 0, 1)); h = int(380 + 420 * u * u)
    x, y = view_xy(ST["basement"].size, t, T_SPLIT, D, 1.12, 1.3, 0.5, 0.53, 0.5, 0.5, drift=0.6)
    h = h // 6 * 6
    if h not in _KDARK:
        sp = sprite("kessler_cold", "X", 0, h); a = np.asarray(sp).astype(np.float32); a[..., :3] = a[..., :3] * 0.07 + np.array([6, 9, 18]); _KDARK[h] = Image.fromarray(a.astype(np.uint8), "RGBA")
    sp = _KDARK[h]; out = im.convert("RGBA"); px, py = int(x - sp.width / 2), int(y - sp.height * 0.2)
    out.alpha_composite(sp, (px, py))
    l = Image.new("RGBA", out.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l); k = sp.height / 900; ex, ey = px + sp.width / 2, py + 178 * k
    for sx in (-1, 1): d.ellipse((ex + sx * 37 * k - 9 * k, ey - 6 * k, ex + sx * 37 * k + 9 * k, ey + 6 * k), fill=(235, 240, 255, int(255 * min(1, u * 3 + 0.3))))
    d.rectangle((ex + 30 * k, ey + 150 * k, ex + 52 * k, ey + 168 * k), fill=(230, 30, 30, 255))
    out.alpha_composite(l.filter(ImageFilter.GaussianBlur(max(2, 9 * k)))); out.alpha_composite(l)
    return out.convert("RGB"), (ex, ey)


VOTE_PT = [None]
def cards(im, t):
    on_a = t < T_SPLIT; both = t > line_t["n08"] + dur["n08"]; tgt = (745, 1010) if on_a else VOTE_PT[0]
    if tgt and not both:                                           # the active choice points at what it means, inside the scene
        l = aa_layer(); d_ = SD(l); y0 = 430 + (0 if on_a else 110); p = float(np.clip((t - (t_vote if on_a else T_SPLIT)) / 0.35, 0, 1))
        sx_, sy_ = 880, y0 + 92; ex_, ey_ = sx_ + (tgt[0] - sx_) * p, sy_ + (tgt[1] - sy_) * p
        d_.line((sx_, sy_, ex_, ey_), fill=(255, 255, 255, 235), width=4)
        if p >= 1:
            pr = 30 + 6 * np.sin(t * 6); d_.ellipse((tgt[0] - pr, tgt[1] - pr, tgt[0] + pr, tgt[1] + pr), outline=RED + (255,), width=5); d_.ellipse((tgt[0] - 7, tgt[1] - 7, tgt[0] + 7, tgt[1] + 7), fill=(255, 255, 255, 255))
        l = aa_down(l); im.paste(l, (0, 0), l)
    d = ImageDraw.Draw(im); fl = ImageFont.truetype(MONT, 54); ft = ImageFont.truetype(MONT, 34)
    for n_, (lab, txt) in enumerate((("A", "Je ramène Samir à sa fille"), ("B", "Je découvre la vérité"))):
        y0 = 430 + n_ * 110; on = (n_ == 0) == (t < T_SPLIT) or t > line_t["n08"] + dur["n08"]
        d.rounded_rectangle((124, y0, 920, y0 + 92), 16, fill=RED if on else (250, 250, 250), outline=RED, width=4)
        d.text((168, y0 + 46), lab, font=fl, fill=(255, 255, 255) if on else RED, anchor="mm")
        d.text((215, y0 + 46), txt, font=ft, fill=(255, 255, 255) if on else (40, 40, 44), anchor="lm")
    if t > t_suivre:
        d.text((540, 1430), "À SUIVRE", font=ImageFont.truetype(MONT, 42), fill=(240, 240, 240), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))


# ---------------- frames ----------------
THOUGHTS += [(line_t["k02"] + dur["k02"] + 0.15, L_("m01") - 0.05, "ne te retourne pas…", 150, 1330, "light"),
             (line_t["m01"] + dur["m01"] + 0.55, L_("n02") + 0.02, "j'arrive, maman.", 170, 1390, "light"),
             (T_ROUGE + 0.45, L_("k01") - 0.05, "non non non", 140, 640, "dark"),
             (wt("n06", "vue") + 0.1, T_DES - 0.05, "ils dorment… ?", 180, 1380, "light"),
             (line_t["k01"] + dur["k01"] + 0.5, L_("n03") - 0.05, "règle n°4…", 600, 1480, "dark")]
CUTS = [T_POUR, L_("m01"), L_("n02"), L_("k01"), T_RULE, L_("n03"), T_LE, L_("n04"), L_("n05"), L_("n06"), T_DES, L_("n07"), T_BRAC, t_vote, T_SPLIT]


def render(i, t):
    tg = None; kind = "white"; light_hud = False; cap_y = None; chip = None; co = None
    if t < T_POUR: im = ins_clock(t); kind = "wall"; light_hud = True; chip = ("VALMONT · OPEN SPACE · 3e", 0.25)
    elif t < L_("m01"): im = kessler_shot(t, T_POUR, L_("m01")); tg = "MME KESSLER · MANAGER"
    elif t < L_("n02"): im = ins_voicemsg(t, L_("m01"), L_("n02")); kind = "phone"; cap_y = 1470
    elif t < L_("k01"):
        im = gate_shot(t, L_("n02"), L_("k01"), i); cap_y = 1470; kind = "gate"; chip = ("HALL · SORTIE PRINCIPALE", L_("n02") + 0.2)
        co = (L_("n02") + 0.35, T_ROUGE, view_xy(ST["gate"].size, t, L_("n02"), L_("k01"), 1.0, 1.12, 0.6, 0.55, *LED_GATE), (-300, -330), "LECTEUR B-04", "analyse du badge…", RED)
    elif t < T_RULE: im = ins_speaker(t, L_("k01"), T_RULE); chip = ("ANNONCE GÉNÉRALE · DIRECTION", L_("k01") + 0.2)
    elif t < L_("n03"): im = ins_rules(t, T_RULE, L_("n03")); kind = "rules"; cap_y = 1560
    elif t < T_LE:
        im = stairs_shot(t, L_("n03"), T_LE); kind = "night_warm"; light_hud = True; chip = ("ESCALIER DE SERVICE · NIV. -1", L_("n03") + 0.2)
        co = (wt("n03", "quelque") - 0.1, T_LE, view_xy(ST["stairs"].size, t, L_("n03"), T_LE, 1.0, 1.14, 0.5, 0.56, 0.385, 0.632), (230, -250), "OBJET AU SOL", "badge Valmont", (255, 190, 60))
    elif t < L_("n04"): im = ins_badge(t, T_LE, L_("n04")); kind = "night_warm"; light_hud = True
    elif t < L_("n05"): im = ins_drawing(t, L_("n04"), L_("n05")); kind = "drawing"; light_hud = True; cap_y = 430
    elif t < L_("n06"):
        im = door_shot(t, L_("n05"), L_("n06")); kind = "night"; light_hud = True; cap_y = 1490; chip = ("NIVEAU -2 · ACCÈS RESTREINT", L_("n05") + 0.2)
        ok_ = t >= T_OUVRE
        co = (L_("n05") + 0.4 if not ok_ else T_OUVRE, T_OUVRE if not ok_ else T_MOINS, view_xy(ST["stairdoor"].size, t, L_("n05"), T_MOINS, 1.0, 1.08, 0.5, 0.5, *LED_DOOR), (-300, 190),
              "LECTEUR · NIV. -2", "V-0451 · ACCEPTÉ" if ok_ else "présentez un badge", (60, 220, 110) if ok_ else RED)
    elif t < T_DES:
        im = basement_shot(t, L_("n06"), T_DES); kind = "basement"; light_hud = True; chip = ("NIVEAU -2 · 1 247 POSTES OCCUPÉS", L_("n06") + 0.2)
        co = (L_("n06") + 0.9, T_DES, view_xy(ST["basement"].size, t, L_("n06"), T_DES, 1.12, 1.3, 0.5, 0.53, 0.612, 0.405, drift=0.6), (200, -210), "HEURE LOCALE", "18:00:00 · figée", RED)
    elif t < L_("n07"): im = ins_face(t, T_DES, L_("n07")); kind = "screen"
    elif t < t_hit - 3 * F: im = ins_screen(t, L_("n07"), t_hit); kind = "screen"; cap_y = 1440
    elif t < t_hit + 3 * F:
        k = int(round((t - t_hit) / F)); base = basement_shot(t, 0, 1).point(lambda v: int(v * 0.6))
        if k < 0: return night_grade(samir_smear(max(-3, k), base), i)
        a = np.asarray(samir_shot(t, t_hit, t_vote, talk=False)).astype(np.float32) / 255; l = a @ G.LUMA
        return Image.fromarray(((np.stack([1 - np.clip(l * 1.6, 0, 1)] * 3, -1) if k != 1 else np.zeros_like(a)) * 255).astype(np.uint8))
    elif t < T_BRAC:
        im = samir_shot(t, t_hit, T_BRAC); kind = "night"; light_hud = True; tg = "SAMIR L. · DISPARU DEPUIS HIER"
    elif t < t_vote: im = ins_bracelet(t, T_BRAC, t_vote); kind = "night"; light_hud = True
    else:
        if t < T_SPLIT: im = samir_shot(t, t_vote, T_SPLIT, talk=False)
        else: im, VOTE_PT[0] = kessler_far(basement_shot(t, T_SPLIT, D), t)
        kind = "night" if t < T_SPLIT else "basement"; light_hud = True
    hits = [T_PILE, T_ROUGE, T_OUVRE + 0.12]
    amp = sum(14 * np.exp(-(t - h_) * 9) for h_ in hits if 0 <= t - h_ < 0.6)
    if amp > 0.5:                                                  # camera jolt on the bell, the refusal, the latch
        dx, dy = np.sin(t * 61) * amp, np.cos(t * 47) * amp; z_ = 1 + amp / 400
        im = im.resize((int(W * z_), int(H * z_)), Image.BILINEAR); ox_, oy_ = (im.width - W) / 2 + dx, (im.height - H) / 2 + dy
        im = im.crop((int(ox_), int(oy_), int(ox_) + W, int(oy_) + H))
    if kind in ("white", "rules"): im = white_grade(im, i)
    elif kind == "gate": im = white_grade(im, i, exp=-0.22)
    elif kind == "night": im = night_grade(im, i)
    elif kind == "night_warm": im = night_grade(im, i, exp=0.45, warm=True)
    elif kind == "drawing": im = night_grade(im, i, exp=0.4, warm=True, glow=False)
    elif kind == "screen": im = night_grade(im, i, exp=0.2)
    elif kind == "basement": im = night_grade(im, i, exp=0.6)
    elif kind == "wall": im = night_grade(im, i, exp=0.25)
    hud(im, dark=kind in ("phone", "screen", "rules"), light_text=light_hud)
    if tg and t >= (t_hit if tg.startswith("SAMIR") else 0): tag(im, tg)
    if chip and not tg: hud_chip(im, chip[0], t, chip[1])
    if co and co[0] <= t < co[1]: im = callout(im, t, *co)
    thought(im, t)
    if t >= t_vote: cards(im, t)
    G.karaoke(im, words, t, "present", hl=RED, box=False, y0=cap_y, size0=66, stroke=7)
    if t > D - 0.45:                                       # loop: the last frame melts into the first (17:59:58)
        q = (t - (D - 0.45)) / 0.45; im = Image.blend(im, night_grade(ins_clock(0.0), i, exp=0.25), float(np.clip(q, 0, 1)))
    return im


def frame(i):
    t = i * F
    c = next((c for c in CUTS if 0 <= t - c < 0.3), None)
    if c is not None:
        a_ = render(i, t); b_ = render(i, c - F); q = (t - c) / 0.3; q = q * q * (3 - 2 * q)
        zb = 1 + 0.035 * q; bw, bh = int(W * zb), int(H * zb)
        b_ = b_.resize((bw, bh), Image.BICUBIC).crop(((bw - W) // 2, (bh - H) // 2, (bw - W) // 2 + W, (bh - H) // 2 + H))
        za = 1.035 - 0.035 * q; aw, ah = int(W * za), int(H * za)
        a_ = a_.resize((aw, ah), Image.BICUBIC).crop(((aw - W) // 2, (ah - H) // 2, (aw - W) // 2 + W, (ah - H) // 2 + H))
        im = Image.blend(b_, a_, q)
    else:
        im = render(i, t)
    im.save(TMP + f"f{i:05d}.jpg", quality=95)


N = int(D * FPS)
basement_plate(); basement_live(0.0)
if __name__ == "__main__":
    from multiprocessing import Pool
    RANGE = os.environ.get("EI_STEP")
    SHOTS = dict(horloge=(0, T_POUR), kessler=(T_POUR, L_("m01")), vocal=(L_("m01"), L_("n02")), portique=(L_("n02"), L_("k01")), hautparleur=(L_("k01"), T_RULE),
                 reglement=(T_RULE, L_("n03")), escalier=(L_("n03"), T_LE), badge=(T_LE, L_("n04")), dessin=(L_("n04"), L_("n05")), porte=(L_("n05"), L_("n06")),
                 soussol=(L_("n06"), T_DES), visage=(T_DES, L_("n07")), ecran=(L_("n07"), t_hit - 0.15), samir=(t_hit - 0.15, T_BRAC), bracelet=(T_BRAC, t_vote), vote=(t_vote, D))
    SIG = TMP + "timeline.json"; cur = {k: round(float(v), 3) for k, v in line_t.items()}; cur["D"] = D
    have = len(glob.glob(TMP + "f*.jpg"))
    if SHOT == "list":
        for k, (a, b) in SHOTS.items(): print(f"{k:12s} {a:6.2f} -> {b:6.2f} s")
        sys.exit(0)
    if SHOT:
        # only valid while the timeline is unchanged (same voices, same pauses) and every other frame is already on disk
        old = json.load(open(SIG)) if os.path.exists(SIG) else None
        if old != cur or have != N: sys.exit(f"partial render refused: timeline changed or frames missing ({have}/{N}) -> run a full render")
        bad = [n for n in SHOT.split(",") if n not in SHOTS]
        if bad: sys.exit(f"unknown shot {bad}; EI_SHOT=list shows the names")
        sel = set()
        for n in SHOT.split(","):
            a, b = SHOTS[n]; sel |= set(range(max(0, int((a - 0.4) * FPS)), min(N, int((b + 0.4) * FPS) + 1)))      # +/- the dissolve that shares frames with the neighbours
        idx = sorted(sel); print("partial render:", SHOT, len(idx), "frames of", N)
    elif RANGE: idx = [i for i in range(N) if i % int(RANGE) == 0]
    else:
        idx = range(N)
        if not AUDIO_ONLY:
            for f in glob.glob(TMP + "f*.jpg"): os.remove(f)
    if not AUDIO_ONLY:
        with Pool(4) as pool: pool.map(frame, idx, chunksize=6)
    if RANGE and not SHOT: print("test ok", D); sys.exit(0)
    if not AUDIO_ONLY and not SHOT: json.dump(cur, open(SIG, "w"))

    # ---------------- sound ----------------
    NS = int(D * VSR) + VSR; ts = np.arange(NS) / VSR; mix = np.zeros(NS); rng = np.random.default_rng(5)
    def add(s_, at_, g=1.0):
        i0 = int(at_ * VSR); j0 = min(NS, i0 + len(s_))
        if j0 > i0 and i0 >= 0: mix[i0:j0] += s_[: j0 - i0] * g
    def tone(f, d_, decay): x = np.arange(int(d_ * VSR)) / VSR; return np.sin(2 * np.pi * f * x) * np.exp(-x * decay)
    def boom(): x = np.arange(int(1.4 * VSR)) / VSR; return np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x * 4) + 30) / VSR) * np.exp(-x * 2.6)
    def thump(): x = np.arange(int(0.25 * VSR)) / VSR; return np.sin(2 * np.pi * 52 * x) * np.exp(-x * 22)
    def bell(f): return tone(f, 2.5, 1.6) + tone(f * 2.01, 2.5, 2.4) * 0.4 + tone(f * 3.02, 2.5, 3.5) * 0.2
    def click(): n = int(0.012 * VSR); return rng.standard_normal(n) * np.exp(-np.arange(n) / VSR * 500)
    office = (ts < L_("n03")) & ~((ts > L_("m01")) & (ts < L_("n02")))
    hum = (np.sin(2 * np.pi * 100 * ts) * 0.4 + np.sin(2 * np.pi * 120 * ts) * 0.2) * 0.025 + np.convolve(rng.standard_normal(NS), np.ones(40) / 40, "same") * 0.02
    mix += hum * office
    drone = (np.sin(2 * np.pi * 41 * ts) + 0.6 * np.sin(2 * np.pi * 61.7 * ts) + 0.3 * np.sin(2 * np.pi * 82.4 * ts * (1 + 0.002 * np.sin(ts)))) * 0.05
    mix += drone * (ts > L_("n03")) * np.clip((ts - L_("n03")) / 2, 0, 1)
    def tick():
        a_ = tone(3000, 0.03, 120); c_ = click() * 0.4; a_[: len(c_)] += c_[: len(a_)]; return a_
    for k in range(3): add(tick(), 0.15 + k * T_PILE / 2.2, 0.6)               # ticks
    for k in range(int(T_POUR / 0.75) + 2): add(thump(), 0.05 + k * 0.75, 0.9); add(thump(), 0.05 + k * 0.75 + 0.22, 0.6)   # heartbeat
    add(bell(392) + bell(523.25) * 0.6, T_PILE, 0.5)                                                            # 18:00
    x = np.arange(int(0.6 * VSR)) / VSR
    add(np.sin(2 * np.pi * 150 * x) * (np.sin(2 * np.pi * 6 * x) > 0) * 0.5, L_("m01") + 0.02, 0.45)            # phone buzz
    for k in range(3): add(tone(880, 0.12, 8) * (np.arange(int(0.12 * VSR)) < int(0.1 * VSR)), T_ROUGE + 0.1 + k * 0.17, 0.5)   # access denied beeps
    ch_ = np.concatenate([bell(659.25)[: int(0.4 * VSR)], bell(523.25)[: int(0.5 * VSR)]]); ch_[-int(0.25 * VSR):] *= np.linspace(1, 0, int(0.25 * VSR)); add(ch_, L_("k01") - 0.95, 0.35)                 # PA chime: ding-dong
    mix += np.convolve(rng.standard_normal(NS), np.ones(8) / 8, "same") * 0.004 * ((ts > line_t["k01"]) & (ts < line_t["k01"] + dur["k01"]))
    buzz = (np.sign(np.sin(2 * np.pi * 100 * ts)) * 0.02 + rng.standard_normal(NS) * 0.004) * ((ts > L_("n03")) & (ts < L_("n04")))
    mix += buzz * (1 + (rng.random(NS) < 0.0004) * 20)                                                         # caged bulb, crackling
    sh = np.arange(int(0.9 * VSR)) / VSR; add(sum(np.sin(2 * np.pi * f * sh) for f in (3520, 4186, 5274)) * np.exp(-sh * 5) * 0.12, T_LE + 0.45, 0.6)   # glint
    for k, f in enumerate((659.25, 523.25, 587.33, 392.0, 392.0, 587.33, 659.25, 523.25)):                    # music box over the drawing
        add(tone(f * 2, 1.6, 3) + tone(f * 4, 1.6, 6) * 0.25, L_("n04") + 0.2 + k * 0.62, 0.22)
    add(tone(1500, 0.08, 30), T_OUVRE - 0.02, 0.4); add(boom()[: int(0.3 * VSR)] * 0.8, T_OUVRE + 0.12, 0.6)
    add(np.convolve(rng.standard_normal(int(0.25 * VSR)), np.ones(30) / 30, "same") * 6 * np.exp(-np.arange(int(0.25 * VSR)) / VSR * 18), T_OUVRE + 0.1, 0.5)   # latch clack
    for tt in np.arange(L_("n06"), t_sil, 0.045):                                                               # dozens of keyboards
        if rng.random() < 0.7: add(click() * rng.uniform(0.2, 0.6), tt + rng.uniform(0, 0.04), 0.5)
    for tt in np.arange(wt("n07", "Statut") + 0.35, wt("n07", "Statut") + 0.35 + 17 * 0.045, 0.045): add(tone(2400, 0.02, 200), tt, 0.25)
    m = (ts > t_sil) & (ts < t_hit); mix[m] *= 0.03
    add(np.convolve(rng.standard_normal(int(0.14 * VSR)), np.ones(25) / 25, "same") * 9, t_hit - 3 * F - 0.04, 0.5)
    add(boom(), t_hit, 1.0)
    STG = NEW + "fxtest/stinger.wav"
    if os.path.exists(STG):
        st, sr = sf.read(STG); st = st if st.ndim == 1 else st.mean(1); g_ = G.gcd(sr, VSR); st = G.resample_poly(st, VSR // g_, sr // g_) / np.abs(st).max()
        st = st[: int(0.8 * VSR)] * np.linspace(1, 0, int(0.8 * VSR)) ** 2; add(st, t_hit, 0.45)
    for b_ in np.arange(t_vote, D - 0.5, 0.75): add(thump(), b_, 0.9); add(thump(), b_ + 0.22, 0.6)          # the heartbeat returns for the vote
    vox = np.zeros(NS)
    for k, t0 in line_t.items():
        i0 = int(t0 * VSR); j0 = min(NS, i0 + len(VO_A[k])); vox[i0:j0] += VO_A[k][: j0 - i0] * (0.8 if k in ("s01", "s02") else 1.0)
    act = np.convolve((np.convolve(np.abs(vox), np.ones(2205) / 2205, "same") > 0.01).astype(float), np.ones(13230) / 13230, "same")
    mix = mix / np.abs(mix).max() * 0.55 * (1 - 0.6 * np.clip(act, 0, 1)) + vox / (np.abs(vox).max() + 1e-9) * 0.9
    mix = mix[: int(D * VSR)]; mix *= np.clip((D - ts[: len(mix)]) / 0.4, 0, 1)
    sf.write(TMP + "mix.wav", mix / np.abs(mix).max() * 0.9, VSR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", TMP + "f%05d.jpg", "-i", TMP + "mix.wav",
                    "-c:v", "libx264", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M", "-preset", "veryslow", "-tune", "film", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-x264-params", "aq-mode=3:aq-strength=0.9:psy-rd=1.0,0.15:deblock=-1,-1", "-g", "60",
                    "-af", "loudnorm=I=-13:TP=-1.0:LRA=9,volume=1.3,alimiter=limit=0.89", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ok", OUT, D)
