"""EMPLOI INSTABLE episode 3 (the public chose A: bring Samir back to his daughter).
Reuses the episode 2 engine: the library part of ei2.py (camera, sprites, lights, HUD, inserts) is loaded as-is,
this file only defines the episode 3 voices, timeline, new shots, render and sound.
usage: HF_HOME=... ei3.py <out.mp4>   EI_STEP=n (test)  EI_RANGE=a-b[,a-b] seconds (partial)  EI_AUDIO_ONLY=1"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(_HERE, "ei2.py")).read()
def _seg(a, b): return SRC[SRC.index(a):SRC.index(b)]
exec(SRC[:SRC.index("# ---------------- voices & timeline")])                    # imports, constants, fonts
VO, TMP, HD3 = NEW + "elv5/fin/", NEW + "ei3tmp/", NEW + "ei3hd/"
os.makedirs(TMP, exist_ok=True)
exec(_seg("def norm(x)", "REL = {}"))                                            # norm, align

# ---------------- voices & timeline ----------------
LINES = json.load(open(NEW + "elv5/script.json")); SCRIPT = {n: t for n, w, t in LINES}
VO_A = {k: G.voice(VO + f"{k}.wav", lp=None) for k in SCRIPT}
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
def L_(k): return line_t[k] - 0.15
at("n01", 0.5); at("n02", 0.3); at("k00", 0.3)
at("q1", 0.0); t_hold = T; T += 0.9                         # the in-video choice: three seconds to decide, the bar runs out
at("a1", 0.2); at("a2", 0.35); at("r6", 0.35)                # outcome A, shown in full: you turned round
t_rew = T; T += 0.9                                         # the tape rewinds to the choice
at("b1", 0.0)                                               # outcome B: you ran
t_sil = T; T += 1.0                                         # 1 s of silence: every keyboard stops
t_hit = T; T += 0.45                                        # the shock: a thousand eyes open
at("n03", 0.45); at("n04", 0.35); at("s01", 0.45); at("n05", 0.45); at("n06", 0.3); at("n07", 0.45); at("n08", 0.55); at("k01", 0.4)
t_vote = T - 0.2; at("n09", 0.4); t_suivre = T; T += 1.1
D = round(T, 2); print("duration", D)
T_POUR = wt("n01", "Pour") - 0.12; T_TOMBE = wt("n04", "tombe"); T_RULE = wt("n06", "Règle") - 0.1
T_GREEN = wt("n07", "Dix-sept") - 0.1; T_SPLIT = wt("n09", "ou") - 0.05
T_ASSOIS = wt("a1", "t'assois") - 0.15; T_OU = wt("q1", "ou") - 0.05
CAP_LAG = 0.12
words = []
for k, t0 in line_t.items():
    words += [dict(w, s=w["s"] + t0 + CAP_LAG, e=w["e"] + t0 + CAP_LAG, line=k) for w in REL[k]]
exec(_seg("def mouth_cues(key):", "CUES = "))
CUES = mouth_cues("s01")
exec(_seg("def mouth_at(t):", "# ---------------- pictures"))
exec(_seg("# ---------------- pictures", "# ---------------- frames"))           # the whole engine: camera, sprites, lights, inserts, HUD
for k in ("gateopen", "exit", "stairsup"): ST[k] = still(HD3 + f"{k}_0001.png")
EXJ = json.load(open(HD3 + "exit_led.json")); GIRL = EXJ["girl"]


def hud(im, dark=False, light_text=False):
    if dark: return
    d = ImageDraw.Draw(im); fs = ImageFont.truetype(MONT, 30)
    d.text((124, 236), "EMPLOI INSTABLE", font=fs, fill=(235, 235, 238) if light_text else (25, 25, 28)); d.text((124, 276), "ÉPISODE 3", font=fs, fill=RED)


def amp_of(key, t, gain=6):
    a = VO_A[key]; i0 = int((t - line_t[key]) * VSR)
    return float(np.abs(a[max(0, i0):max(0, i0) + 1470]).mean() * gain) if 0 <= i0 < len(a) else 0.0


# ---------------- episode 3 shots ----------------
def ins_led(t):
    """Opening signature: the exact time. Down here the red clock is stuck on 18:00:00."""
    im = Image.new("RGB", (W, H), (4, 5, 9)).convert("RGBA")
    hz = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(hz).ellipse((-200, 500, 1280, 1500), fill=(40, 60, 120, 90)); im.alpha_composite(hz.filter(ImageFilter.GaussianBlur(160)))
    ov = aa_layer(); d = SD(ov)
    for x in (300, 780): d.line((x, 0, x, 690), fill=(40, 42, 50, 255), width=8)
    d.rounded_rectangle((110, 690, 970, 1010), 22, fill=(8, 8, 10, 255), outline=(58, 60, 68, 255), width=6)
    for sx, sy in ((140, 720), (940, 720), (140, 980), (940, 980)): d.ellipse((sx - 8, sy - 8, sx + 8, sy + 8), fill=(70, 72, 80, 255))
    im.alpha_composite(aa_down(ov))
    on = not (int(t * 9) % 13 == 0)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl); f = ImageFont.truetype(MONO, 150)
    gd.text((540, 850), "88:88:88", font=f, fill=(60, 8, 8, 255), anchor="mm")                                  # unlit segments
    gd.text((540, 850), "18:00:00", font=f, fill=(255, 34, 22, 255 if on else 120), anchor="mm")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); im.alpha_composite(gl)
    im = spill(im.convert("RGB"), 540, 850, 700, 380, (255, 30, 20), 0.22 if on else 0.08)
    return view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, 0, T_POUR, 1.0, 1.1, 0.5, 0.47, drift=0.6)


def samir_close(t, t0, t1, bg="basement", talk=False, badge=False, tilt=0.0, tear=True):
    if bg == "basement": base = (WORKERS if WORKERS is not None else basement_plate()).resize((int(W * 1.2), int(H * 1.2))).filter(ImageFilter.GaussianBlur(7))
    else: base = ST[bg].filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.42))
    m = mouth_at(t) if talk else "X"; blink = ((t + 1.1) % 2.3) < 0.1
    sp = sprite("samir_tired", m, blink, 2300)
    sp = tint(sp, (0.62, 0.72, 1.0), (4, 6, 16)) if bg == "basement" else tint(sp, (0.8, 0.78, 0.78), (4, 4, 8))
    a = np.asarray(sp).astype(np.float32); a[..., :3] *= np.linspace(1.15, 0.45, sp.height)[:, None, None]; sp = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    if tear:
        sp = sp.copy(); dd = ImageDraw.Draw(sp); sx_, sy_ = sp.width / 400, sp.height / 900; p_ = min(1.0, (t - t0) / 2.0)
        x0, y0 = 252 * sx_, 196 * sy_; y1 = y0 + p_ * 46 * sy_
        dd.line((x0, y0, x0 + 3 * sx_ * p_, y1), fill=(170, 210, 255, 150), width=int(3 * sx_)); dd.ellipse((x0 + 3 * sx_ * p_ - 4 * sx_, y1 - 4 * sx_, x0 + 3 * sx_ * p_ + 4 * sx_, y1 + 6 * sx_), fill=(210, 235, 255, 230))
    fk = 0.8 + 0.2 * np.sin(t * 9) * np.sin(t * 3.1)
    sp = rim_light(rim_light(sp, (60, 110, 210), 12, fk * 0.5, blur=3), (40, 70, 150), -12, fk * 0.4, blur=3) if bg == "basement" else rim_light(sp, (150, 170, 200), 14, 0.5, blur=3)
    br = 1 + 0.012 * np.sin(t * 2 * np.pi / 1.4); sp = sp.resize((sp.width, int(sp.height * br)), Image.BICUBIC)
    if tilt: sp = sp.rotate(tilt, resample=Image.BICUBIC, expand=True)
    shake = np.sin(t * 31) * 3 + np.sin(t * 17) * 2
    ox, oy = 0.5 * base.width - W / 2, 0.5 * base.height - H / 2
    im = base.convert("RGBA"); im.alpha_composite(sp, (int(540 + ox - sp.width / 2 + shake), int(2600 + oy - sp.height)))
    if badge:                                                      # the badge photo, taken "yesterday": the same man, eleven years younger
        b = BADGE.resize((330, 507), Image.LANCZOS).rotate(7 + np.sin(t * 2.1) * 0.8, expand=True, resample=Image.BICUBIC)
        u = min(1.0, (t - t0) / 0.35); u = 1 - (1 - u) ** 3
        drop_shadow(im, b, (int(ox + 90), int(oy + 1130 + 500 * (1 - u))), blur=22, off=(12, 22), alpha=170)
    return view(im.convert("RGB"), t, t0, t1, 1.0, 1.07, 0.5, 0.45)


_RUN = {}
def _runspr(who, k, h):
    key = (who, k, h)
    if key not in _RUN:
        im_ = Image.open(NEW + f"ei3pose/{who}_run{k}.png").convert("RGBA"); sp = im_.resize((int(im_.width * h / im_.height), h), Image.LANCZOS)
        sp = tint(sp, (0.6, 0.7, 0.98), (4, 6, 16)); a = np.asarray(sp).astype(np.float32); a[..., :3] *= np.linspace(1.12, 0.6, sp.height)[:, None, None]
        _RUN[key] = rim_light(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"), (60, 110, 210), 8, 0.5, blur=3)
    return _RUN[key]


def run_plate(t, t0, t1):
    """2D, like the rest of the series: you pull Samir up the aisle towards us, between the rows of sleepers; Kessler stands at the far end."""
    im = basement_live(t).convert("RGBA"); w_, h_ = im.size
    p = float(np.clip((t - t0) / max(0.1, t1 - t0), 0, 1)); pe = p ** 1.25
    ks = _KFAR.setdefault(0, tint(sprite("kessler_cold", "X", 0, 300), (0.06, 0.06, 0.07), (5, 7, 14)))
    kx, ky = int(0.5 * w_ - ks.width / 2), int(0.47 * h_); im.alpha_composite(ks, (kx, ky))
    l = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l); k_ = ks.height / 900; ex, ey = kx + ks.width / 2, ky + 178 * k_
    for sx in (-1, 1): d.ellipse((ex + sx * 37 * k_ - 4, ey - 3, ex + sx * 37 * k_ + 4, ey + 3), fill=(235, 240, 255, 255))
    im.alpha_composite(l.filter(ImageFilter.GaussianBlur(4))); im.alpha_composite(l)
    for who, x0, x1, ph, hm in (("samir_tired", 0.43, 0.31, 0.0, 1.0), ("interim", 0.57, 0.70, 0.5, 1.05)):       # you are half a stride ahead, pulling him
        h = int((620 + 520 * pe) * hm) // 10 * 10; c = ((t - t0) * 2.8 + ph) * 12; k0 = int(c) % 12; f_ = c - int(c)
        sp = _runspr(who, k0, h); sp = sp if f_ < 0.08 else Image.blend(sp, _runspr(who, (k0 + 1) % 12, h), f_)
        bob = abs(np.sin(((t - t0) * 2.8 + ph) * 2 * np.pi)) * h * 0.025
        x = (x0 + (x1 - x0) * pe) * w_; foot = (0.66 + 0.2 * pe) * h_
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((x - h * 0.16, foot - h * 0.045, x + h * 0.16, foot - h * 0.015), fill=(0, 0, 0, 150)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(h * 0.012)))
        im.alpha_composite(sp, (int(x - sp.width / 2), int(foot - sp.height - bob)))
    return im.convert("RGB")


_KFAR = {}
def run_shot(t, t0, t1):
    """You and Samir sprinting up the aisle towards us. Push-in, radial streaks, footstep jolts."""
    p = np.clip((t - t0) / max(0.1, t1 - t0), 0, 1); z = 1.0 + 0.22 * p
    bob = abs(np.sin((t - t0) * 2 * np.pi * 2.8)) * 0.012
    im = view(run_plate(t, t0, t1), t, t0, t1, 1.0, 1.12, 0.5, 0.52 - bob, drift=0.3)
    acc = np.asarray(im).astype(np.float32); n = 1.0
    for k, wgt in ((1.03, 0.22), (1.06, 0.12)):      # zoom streaks towards the edges, the centre stays sharp
        zw, zh = int(W * k), int(H * k); zi = im.resize((zw, zh), Image.BILINEAR).crop(((zw - W) // 2, (zh - H) // 2, (zw - W) // 2 + W, (zh - H) // 2 + H))
        acc += np.asarray(zi).astype(np.float32) * wgt * np.clip(G.RR * 1.5 - 0.45, 0, 1)[..., None]; n = n + wgt * np.clip(G.RR * 1.5 - 0.45, 0, 1)[..., None]
    return Image.fromarray(np.clip(acc / n, 0, 255).astype(np.uint8))


_KBIG = None
def kessler_dark(t, t0, t1, key="k00", close=False):
    """She is right behind you. Only her outline, two pale eyes that brighten when she speaks, the red pocket square."""
    global _KBIG
    base = (WORKERS if WORKERS is not None else basement_plate()).resize((int(W * 1.2), int(H * 1.2))).filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.35))
    if _KBIG is None:
        sp = sprite("kessler_cold", "X", 0, 2300); a = np.asarray(sp).astype(np.float32); a[..., :3] = a[..., :3] * 0.07 + np.array([5, 7, 14]); _KBIG = Image.fromarray(a.astype(np.uint8), "RGBA")
    sp = rim_light(_KBIG, (40, 70, 140), 14, 0.5, blur=4); ox, oy = 0.5 * base.width - W / 2, 0.5 * base.height - H / 2
    im = base.convert("RGBA"); px, py = int(540 + ox - sp.width / 2), int(2650 + oy - sp.height); im.alpha_composite(sp, (px, py))
    k = sp.height / 900; ex, ey = px + sp.width / 2, py + 178 * k; a_ = 1.0 if close else min(1.0, 0.45 + amp_of(key, t, 9))
    l = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    for sx in (-1, 1): d.ellipse((ex + sx * 37 * k - 10 * k, ey - 6 * k, ex + sx * 37 * k + 10 * k, ey + 6 * k), fill=(235, 240, 255, int(255 * a_)))
    d.rectangle((ex + 30 * k, ey + 150 * k, ex + 52 * k, ey + 168 * k), fill=(230, 30, 30, 255))
    im.alpha_composite(l.filter(ImageFilter.GaussianBlur(22))); im.alpha_composite(l)
    im = im.convert("RGB")
    if close:                                                    # you looked: the camera falls into her eyes, the room goes white-blue
        im = spill(im, ex, ey, 520, 300, (200, 220, 255), 0.5 * float(np.clip((t - t0) / max(0.2, t1 - t0), 0, 1)))
        return view(im, t, t0, t1, 1.5, 2.6, 0.5, 0.265, drift=0.2)
    return view(im, t, t0, t1, 1.0, 1.14, 0.5, 0.42, drift=0.4)


def hero_perm(t, t0, t1):
    """Outcome A: you sat down. Headset on, eyes closed, the screen light from below. You are one of them now."""
    im = Image.new("RGB", (W, H), (4, 5, 9)).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((-100, 1100, 1180, 2300), fill=(90, 130, 220, 150)); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(160)))
    src_ = Image.open(SPR1 + "interim_X_1.png").convert("RGBA"); sp = src_.resize((int(src_.width * 2900 / src_.height), 2900), Image.LANCZOS)
    l = aa_layer(sp.width, sp.height); d = SD(l); k = sp.width / 400                      # the Valmont headset, drawn onto him
    d.line([(100 * k + np.cos(a) * 0, 170 * k) for a in (0,)] + [(200 * k + np.cos(a) * 104 * k, 170 * k - np.sin(a) * 118 * k) for a in np.linspace(np.pi, 0, 30)], fill=(21, 22, 26, 255), width=12 * k)
    for x_ in (86, 284): d.rounded_rectangle((x_ * k, 150 * k, (x_ + 30) * k, 212 * k), 12 * k, fill=(21, 22, 26, 255))
    d.line([(100 * k, 205 * k), (112 * k, 250 * k), (168 * k, 254 * k)], fill=(21, 22, 26, 255), width=6 * k); d.ellipse((161 * k, 245 * k, 179 * k, 263 * k), fill=(21, 22, 26, 255)); d.ellipse((96 * k, 176 * k, 106 * k, 186 * k), fill=(226, 58, 58, 255))
    sp.alpha_composite(aa_down(l))
    sp = tint(sp, (0.55, 0.66, 0.95), (6, 10, 24)); a = np.asarray(sp).astype(np.float32); a[..., :3] = np.clip(a[..., :3] * np.linspace(0.55, 1.25, sp.height)[:, None, None], 0, 255); sp = Image.fromarray(a.astype(np.uint8), "RGBA")
    bob = np.sin(t * 2 * np.pi * 1.7) * 3
    im.alpha_composite(sp, (int(W / 2 - sp.width / 2), int(1650 - sp.height * 0.36 + bob)))
    d = ImageDraw.Draw(im); d.rectangle((0, 1560, W, H), fill=(6, 6, 9)); d.rectangle((0, 1556, W, 1566), fill=(120, 160, 240))
    st = t - line_t["a2"]
    if st > 0:                                                    # the verdict, stamped
        stp = Image.new("RGBA", (860, 220), (0, 0, 0, 0)); sd = ImageDraw.Draw(stp)
        sd.rounded_rectangle((8, 8, 852, 212), 16, outline=RED + (240,), width=14); sd.text((430, 110), "PERMANENT", font=fI("Bold", 128), fill=RED + (240,), anchor="mm")
        s_ = 1.5 - 0.5 * min(1.0, st / 0.14); stp = stp.resize((int(860 * s_), int(220 * s_))).rotate(-9, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(stp, (int(540 - stp.width / 2), int(700 - stp.height / 2)))
    return view(im.convert("RGB").resize((int(W * 1.2), int(H * 1.2))), t, t0, t1, 1.0, 1.1, 0.5, 0.42, drift=0.3)


def ins_rule6(t, t0, t1):
    """The loss teaches a rule: someone has added a sixth line to Valmont's poster, by hand, in red."""
    ins_rules(t0, t0, t1)                                          # make sure the framed poster exists
    fr = _RULES.copy(); d = ImageDraw.Draw(fr); txt = "6. Ne la regarde jamais dans les yeux."; f = ImageFont.truetype(HAND, 60)
    n = int(np.clip((t - t0 - 0.25) * 26, 0, len(txt))); rg = np.random.default_rng(6); x = 78
    for ch in txt[:n]:
        d.text((x + rg.normal(0, 0.8), 1076 + rg.normal(0, 1.2)), ch, font=f, fill=(205, 24, 24)); x += d.textlength(ch, font=f)
    if n >= len(txt): d.line((78, 1148, x, 1142), fill=(205, 24, 24), width=5)
    yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
    wall = np.array([226, 228, 232], np.float32)[None, None] * np.clip(1.08 - ((xx_ - 300) ** 2 + (yy_ - 500) ** 2) / 5e6, 0.7, 1.08)[..., None]
    im = Image.fromarray(np.clip(wall, 0, 255).astype(np.uint8)).convert("RGBA"); ImageDraw.Draw(im).rectangle((0, 1640, W, 1652), fill=RED)
    fr = fr.resize((int(fr.width * 0.86), int(fr.height * 0.86)), Image.LANCZOS).rotate(1.2, expand=True, resample=Image.BICUBIC)
    drop_shadow(im, fr, (int(W / 2 - fr.width / 2), int(1010 - fr.height / 2)), blur=26, off=(14, 26), alpha=120)
    im = spill(im.convert("RGB"), 540, 1400, 900, 600, (255, 30, 25), 0.14)
    return view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t1, 1.1, 1.2, 0.5, 0.68, drift=0.4)


def rewind_shot(i, t):
    """Wrong choice: the surveillance tape rewinds to the moment you chose. Black and white, torn lines, REW."""
    p = float(np.clip((t - t_rew) / 0.9, 0, 1)); tb = line_t["q1"] + 0.6 - p * 0.0; tsrc = L_("r6") - (L_("r6") - (L_("q1") + 0.3)) * p
    if tsrc >= L_("r6") - 0.02: src = ins_rule6(tsrc, L_("r6"), t_rew)
    elif tsrc >= T_ASSOIS: src = hero_perm(tsrc, T_ASSOIS, L_("r6"))
    elif tsrc >= L_("a1"): src = kessler_dark(tsrc, L_("a1"), T_ASSOIS, close=True)
    else: src = run_shot(tsrc, L_("n02"), L_("a1"))
    a = np.asarray(src).astype(np.float32) @ G.LUMA; rg = np.random.default_rng(i)
    for _ in range(9):                                             # tracking tears
        y = int(rg.integers(0, H - 40)); hh = int(rg.integers(6, 34)); a[y:y + hh] = np.roll(a[y:y + hh], int(rg.integers(-140, 140)), axis=1) * 1.25
    a += rg.normal(0, 14, (H, W)); a[::3] *= 0.8
    im = Image.fromarray(np.clip(np.stack([a, a, a], -1), 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    d.text((124, 420), "◀◀ REW", font=ImageFont.truetype(MONO, 64), fill=(255, 255, 255)); d.text((124, 500), "CAM 14 · NIVEAU -2", font=ImageFont.truetype(MONO, 30), fill=(230, 230, 230))
    d.text((540, 1210), "TU RECOMMENCES.", font=ImageFont.truetype(MONT, 62), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=(0, 0, 0))
    return im


def choice_cards(im, t, t0, a_txt, b_txt, t_ou, t_end, pick=None):
    """In-video choice: two cards and a red bar that runs out. After the bar, the chosen card stays lit."""
    d = ImageDraw.Draw(im); fl = ImageFont.truetype(MONT, 54); ft = ImageFont.truetype(MONT, 36); u = float(np.clip((t - t0) / 0.2, 0, 1))
    for n_, (lab, txt) in enumerate((("A", a_txt), ("B", b_txt))):
        if n_ == 1 and t < t_ou: continue
        y0 = 430 + n_ * 110 + int(30 * (1 - u)); on = (pick == lab) if pick else ((n_ == 0) == (t < t_ou))
        d.rounded_rectangle((124, y0, 920, y0 + 92), 16, fill=RED if on else (250, 250, 250), outline=RED, width=4)
        d.text((168, y0 + 46), lab, font=fl, fill=(255, 255, 255) if on else RED, anchor="mm"); d.text((215, y0 + 46), txt, font=ft, fill=(255, 255, 255) if on else (40, 40, 44), anchor="lm")
    if pick is None and t >= t_hold - 0.2:
        left = float(np.clip((t_end - t) / max(0.1, t_end - t_hold), 0, 1)); d.rounded_rectangle((124, 668, 920, 688), 10, fill=(30, 30, 34)); d.rounded_rectangle((124, 668, 124 + int(796 * left), 688), 10, fill=RED)
        d.text((540, 730), "CHOISIS.", font=ImageFont.truetype(MONT, 40), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))


def story_clock(im, t, kind):
    """The clock stays on screen for the whole episode. Under ground it is stuck; upstairs it runs; then you turn it back."""
    if kind == "phone": return
    if t < L_("n04"): txt, col, lab = "18:00:00", (255, 60, 44), "HEURE FIGÉE"
    elif t < L_("n07"): s_ = int(7 * 60 + 12 + (t - L_("n04"))); txt, col, lab = f"18:{s_ // 60:02d}:{s_ % 60:02d}", (255, 60, 44), "APRÈS 18 H"
    elif t < T_GREEN:
        u = float(np.clip((t - L_("n07") - 0.35) / max(0.4, T_GREEN - L_("n07") - 0.5), 0, 1)); u = u * u * (3 - 2 * u); s_ = int((7 - 8 * u) * 60)
        txt, col, lab = (f"18:{s_ // 60:02d}:{s_ % 60:02d}" if s_ >= 0 else f"17:59:{60 + s_:02d}"), (255, 60, 44) if s_ >= 0 else (60, 240, 110), "TU RECULES"
    else: s_ = int(2 + (t - T_GREEN)); txt, col, lab = f"17:59:{min(59, s_):02d}", (60, 240, 110), "AVANT 18 H"
    blink = t < L_("n04") and int(t * 2) % 2 == 0
    l = aa_layer(300, 110); d = SD(l)
    d.rounded_rectangle((2, 2, 286, 100), 14, fill=(8, 9, 12, 215), outline=col + (255,), width=3)
    d.text((144, 40), txt if not blink else txt.replace(":", " "), font=ImageFont.truetype(MONO, 44), fill=col + (255,), anchor="mm"); d.text((144, 80), lab, font=ImageFont.truetype(MONO, 20), fill=(215, 220, 228, 255), anchor="mm")
    l = aa_down(l); im.paste(l, (670, 226), l)


_OPEN = None
def open_plate():
    """Level -2 with every worker's eyes open, glowing, all turned to you."""
    global _OPEN
    if _OPEN is None:
        base = ST["basement"].convert("RGBA"); rg = random.Random(7); glow = Image.new("RGBA", base.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
        for s in sorted([s for s in SPOTS if s["d"] < 26], key=lambda s: -s["d"]):
            if rg.random() < 0.18: continue
            hpx = max(20, int((s["fy"] - s["hy"]) * base.height / (1 - 44 / 900) * 1.02)); who = rg.choice(["w1", "w2", "w3", "w4", "w5"])
            im_ = Image.open(SPR2 + f"{who}_X_0.png").convert("RGBA"); spr = im_.resize((int(im_.width * hpx / im_.height), hpx), Image.LANCZOS)
            fade = np.clip(1.15 - s["d"] / 26, 0.15, 1); spr = tint(spr, (0.42 * fade, 0.55 * fade, 0.85 * fade), (4, 8, 22))
            cut = max(0, min(spr.height, int((s["my"] - (s["fy"] - spr.height / base.height)) * base.height + spr.height * 0.02)))
            x, y = int(s["hx"] * base.width - spr.width / 2), int(s["fy"] * base.height - spr.height)
            base.alpha_composite(spr.crop((0, 0, spr.width, cut)), (x, y)); kx, ky = spr.width / 400, spr.height / 900
            for ex in (163, 237): gd.ellipse((x + ex * kx - 9 * kx, y + 180 * ky - 7 * ky, x + ex * kx + 9 * kx, y + 180 * ky + 7 * ky), fill=(235, 242, 255, int(255 * fade)))
        _OPEN = (base.convert("RGB"), glow)
    return _OPEN


def eyes_shot(t, t0, t1):
    plate, glow = open_plate(); pulse = 0.75 + 0.25 * np.sin(t * 5.5)
    im = plate.convert("RGBA"); g = glow.copy(); g.putalpha(g.getchannel("A").point(lambda v: int(v * pulse)))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(9))); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(2)))
    return view(im.convert("RGB"), t, t0, t1, 1.1, 1.34, 0.5, 0.53, drift=0.6)


def stairs_fall(t, t0, t1):
    """Looking up the forty steps. Samir's hand on the red rail; on 'tombe' it slips and the camera drops."""
    base = ST["stairsup"]; im = base.convert("RGBA"); w_, h_ = base.size
    drop = float(np.clip((t - T_TOMBE) / 0.35, 0, 1)); drop = drop * drop
    hx, hy = 0.335 * w_, (0.63 + 0.16 * drop) * h_
    l = aa_layer(w_, h_); d = SD(l)
    d.line((hx + 30, hy + 60, hx + 430, hy + 900), fill=(51, 80, 124, 255), width=150)                    # the sleeve
    d.line((hx + 22, hy + 40, hx + 70, hy + 150), fill=(74, 106, 156, 255), width=160)                     # cuff
    d.ellipse((hx - 70, hy - 80, hx + 90, hy + 80), fill=(138, 90, 60, 255))                               # the hand around the rail
    for q in range(4): d.rounded_rectangle((hx - 92, hy - 70 + q * 36, hx - 10, hy - 40 + q * 36), 15, fill=(128, 82, 54, 255), outline=(100, 62, 40, 255), width=3)
    lay = aa_down(l); a = np.asarray(lay).astype(np.float32); a[..., :3] *= np.array([0.5, 0.48, 0.5]); im.alpha_composite(Image.fromarray(a.astype(np.uint8), "RGBA"))
    cy = 0.5 + 0.07 * drop
    return view(im.convert("RGB"), t, t0, t1, 1.0, 1.08, 0.5, cy, drift=1.5)


def carry_shot(t, t0, t1):
    """'Tu le portes.' Step by step towards the rectangle of light."""
    step = abs(np.sin((t - t0) * 2 * np.pi * 1.5)) * 0.012
    im = view(ST["stairsup"], t, t0, t1, 1.0, 1.75, 0.5, 0.36 + step, drift=0.5)
    return spill(im, 540, 620, 420, 520, (210, 228, 255), 0.25 * np.clip((t - t0) / max(0.2, t1 - t0), 0, 1))


def gate_red(t, t0, t1):
    base = ST["gate"]; lx, ly = LED_GATE[0] * base.width, LED_GATE[1] * base.height
    im = spill(base, lx, ly + 60, 460, 330, (255, 36, 20), 0.2 if int(t * 3) % 2 == 0 else 0.07)
    return view(im, t, t0, t1, 1.0, 1.1, 0.6, 0.55)


def ins_rewind(t, t0, t1):
    """The lobby clock, close. Your hand pushes the minute hand backwards: 18:07 -> 17:59. The display turns green."""
    yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
    wall = np.array([226, 228, 232], np.float32)[None, None] * np.clip(1.08 - ((xx_ - 300) ** 2 + (yy_ - 500) ** 2) / 5e6, 0.7, 1.08)[..., None]
    im = Image.fromarray(np.clip(wall, 0, 255).astype(np.uint8)).convert("RGBA"); cx, cy, r = 540, 850, 320
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((cx - r + 10, cy - r + 30, cx + r + 70, cy + r + 90), fill=(0, 0, 0, 110)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(28)))
    u = float(np.clip((t - t0 - 0.35) / max(0.4, T_GREEN - t0 - 0.5), 0, 1)); u = u * u * (3 - 2 * u)
    minute = 7 - 8 * u                                           # 7 -> -1 (17:59)
    ok = minute < 0
    ov = aa_layer(); d = SD(ov)
    d.ellipse((cx - r - 24, cy - r - 24, cx + r + 24, cy + r + 24), fill=(120, 128, 136, 255)); d.ellipse((cx - r - 12, cy - r - 12, cx + r + 12, cy + r + 12), fill=(70, 76, 84, 255))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(246, 246, 242, 255))
    for k in range(60):
        a = k / 60 * 2 * np.pi; L = 40 if k % 5 == 0 else 16
        d.line((cx + np.sin(a) * (r - 10), cy - np.cos(a) * (r - 10), cx + np.sin(a) * (r - 10 - L), cy - np.cos(a) * (r - 10 - L)), fill=(30, 30, 34, 255), width=8 if k % 5 == 0 else 3)
    for k in range(12):
        a = (k + 1) / 12 * 2 * np.pi; d.text((cx + np.sin(a) * (r - 92), cy - np.cos(a) * (r - 92)), str(k + 1), font=fI("Bold", 46), fill=RED + (255,) if k == 5 else (30, 30, 34, 255), anchor="mm")
    def hand(frac, L, w_, col):
        a = frac * 2 * np.pi; d.line((cx + 6, cy + 9, cx + 6 + np.sin(a) * L, cy + 9 - np.cos(a) * L), fill=(0, 0, 0, 50), width=w_); d.line((cx, cy, cx + np.sin(a) * L, cy - np.cos(a) * L), fill=col, width=w_)
        return cx + np.sin(a) * L, cy - np.cos(a) * L
    hand((18 + minute / 60) / 12, 175, 18, (30, 30, 34, 255)); tx, ty = hand(minute / 60, 262, 12, (30, 30, 34, 255))
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=RED + (255,))
    if u < 1:                                                      # your arm reaching up, a finger on the minute hand
        d.line((tx + 30, ty + 40, tx + 520, ty + 900), fill=(112, 116, 126, 255), width=150); d.line((tx + 24, ty + 30, tx + 70, ty + 120), fill=(92, 96, 106, 255), width=158)
        d.ellipse((tx - 50, ty - 40, tx + 70, ty + 80), fill=(138, 90, 60, 255)); d.rounded_rectangle((tx - 16, ty - 76, tx + 20, ty + 10), 18, fill=(146, 98, 66, 255), outline=(100, 62, 40, 255), width=3)
    d.rounded_rectangle((330, 1230, 750, 1350), 16, fill=(10, 12, 14, 255), outline=(60, 62, 70, 255), width=3)
    im.alpha_composite(aa_down(ov))
    mm = int(np.ceil(minute)) if minute > 0 else (0 if minute > -0.5 else -1)
    txt = "17:59" if ok or mm < 0 else f"18:{mm:02d}"; col = (60, 240, 110) if txt == "17:59" else (255, 60, 40)
    ImageDraw.Draw(im).text((540, 1290), txt, font=ImageFont.truetype(MONO, 86), fill=col, anchor="mm")
    im = spill(im.convert("RGB"), 540, 1290, 520, 300, col, 0.16)
    return view(im.resize((int(W * 1.2), int(H * 1.2)), Image.BICUBIC), t, t0, t1, 1.0, 1.05, 0.5, 0.5, drift=0.5)


def gate_green(t, t0, t1):
    q = float(np.clip((t - t0) / 0.45, 0, 1)); base = Image.blend(ST["gate"], ST["gateopen"], q) if q < 1 else ST["gateopen"]
    lx, ly = LED_GATE[0] * base.width, LED_GATE[1] * base.height
    im = spill(base, lx, ly + 60, 460, 330, (40, 255, 100), 0.09 * q).convert("RGBA")
    p = float(np.clip((t - t0 - 0.2) / 0.15, 0, 1))
    if p > 0:
        lab = Image.new("RGBA", (560, 120), (0, 0, 0, 0)); ld = ImageDraw.Draw(lab)
        ld.rounded_rectangle((0, 0, 559, 119), 22, fill=(20, 150, 70, 235)); ld.text((280, 60), "ACCÈS AUTORISÉ", font=fI("Bold", 44), fill=(255, 255, 255), anchor="mm")
        s_ = 1.15 - 0.15 * p; lab = lab.resize((int(560 * s_), int(120 * s_))); im.alpha_composite(lab, (int(lx - lab.width / 2), int(ly - 330 - lab.height / 2)))
    return view(im.convert("RGB"), t, t0, t1, 1.0, 1.1, 0.6, 0.55)


_INES = {}
def exit_shot(t, t0, t1, z0=1.0, z1=1.55):
    """The doors are open. Outside, under the street lamp, a little girl with a drawing has been waiting since yesterday."""
    base = ST["exit"]; w_, h_ = base.size; fx, fy, hx, hy = GIRL
    hpx = int((fy - hy) * h_ * 1.12)
    if hpx not in _INES:
        im_ = Image.open(SPR2 + "ines_X_0.png").convert("RGBA"); sp = im_.resize((int(im_.width * hpx / im_.height), hpx), Image.LANCZOS)
        sp = tint(sp, (0.9, 0.8, 0.66), (4, 3, 2)); a = np.asarray(sp).astype(np.float32); a[..., :3] *= np.linspace(1.05, 0.62, sp.height)[:, None, None]
        _INES[hpx] = rim_light(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"), (255, 190, 110), 3, 0.45, blur=1.5)
    sp = _INES[hpx]; im = base.convert("RGBA"); gx, gy = fx * w_, fy * h_
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((gx - sp.width * 0.5, gy - 8, gx + sp.width * 0.5, gy + 14), fill=(0, 0, 0, 170)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    sway = np.sin(t * 1.3) * 2                                     # she shifts from one foot to the other
    im.alpha_composite(sp, (int(gx - sp.width / 2 + sway), int(gy - sp.height + sp.height * 44 / 900)))
    im = spill(im, gx, gy, 300, 60, (255, 180, 90), 0.3)                                                   # the pool of light at her feet
    im = spill(im, 0, 0, 200, 200, (255, 180, 90), 0.16, poly=[(gx - 40, gy - hpx * 3.2), (gx + 40, gy - hpx * 3.2), (gx + 300, gy + 20), (gx - 300, gy + 20)])   # the lamp cone above her                         # the lamp's pool of warm light
    return view(im, t, t0, t1, z0, z1, fx, fy - 0.05, drift=0.5)


def ins_mum(t, t0, t1):
    """B: your own way out. On the lock screen: Maman."""
    sw, sh = PX1 - PX0, PY1 - PY0
    sc = WALLN.resize((sw, sh)).convert("RGBA"); d = ImageDraw.Draw(sc)
    d.text((70, 52), "17:59", font=fI("SemiBold", 30), fill=(255, 255, 255))
    d.rounded_rectangle((sw - 150, 56, sw - 90, 82), 7, outline=(255, 255, 255), width=3); d.rectangle((sw - 145, 61, sw - 141, 77), fill=(230, 50, 40))
    d.text((sw / 2, 150), "Mercredi 6 novembre", font=fI("Medium", 30), fill=(235, 235, 245), anchor="mm")
    d.text((sw / 2, 250), "17:59", font=fI("Bold", 150), fill=(245, 245, 250), anchor="mm")
    p = min(1.0, (t - t0) / 0.2); card = Image.new("RGBA", (sw - 50, 250), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, card.width - 1, 249), 36, fill=(250, 250, 252, 240))
    cd.ellipse((26, 26, 96, 96), fill=(232, 120, 140)); cd.text((61, 61), "M", font=fI("Bold", 38), fill=(255, 255, 255), anchor="mm")
    cd.text((114, 30), "Maman ❤", font=fI("Bold", 34), fill=(25, 25, 30)); cd.text((card.width - 30, 36), "maintenant", font=fI("Regular", 22), fill=(130, 130, 136), anchor="ra")
    cd.text((30, 122), "Tu rentres bientôt ?", font=fI("SemiBold", 36), fill=(25, 25, 30)); cd.text((30, 176), "Ton assiette est au chaud.", font=fI("Regular", 32), fill=(70, 70, 78))
    sc.alpha_composite(card, (25, int(380 - 60 * (1 - p))))
    d.rounded_rectangle((sw / 2 - 110, sh - 30, sw / 2 + 110, sh - 22), 4, fill=(255, 255, 255))
    vib = int(np.sin(t * 90) * 6) if t - t0 < 0.5 else 0
    im = phone(sc.convert("RGB"), vib); z = 1.3 + 0.06 * (t - t0) / max(0.1, t1 - t0); cw, ch = W / z, H / z; cx_, cy_ = 540, PY0 + 330
    return im.transform((W, H), Image.EXTENT, (cx_ - cw / 2, cy_ - ch / 2, cx_ + cw / 2, cy_ + ch / 2), Image.BICUBIC)


VOTE_PT = [None]
def cards(im, t):
    on_a = t < T_SPLIT; both = t > line_t["n09"] + dur["n09"]; tgt = VOTE_PT[0]
    if tgt and not both:
        l = aa_layer(); d_ = SD(l); y0 = 430 + (0 if on_a else 110); p = float(np.clip((t - (t_vote if on_a else T_SPLIT)) / 0.35, 0, 1))
        sx_, sy_ = 880, y0 + 92; ex_, ey_ = sx_ + (tgt[0] - sx_) * p, sy_ + (tgt[1] - sy_) * p
        d_.line((sx_, sy_, ex_, ey_), fill=(255, 255, 255, 235), width=4)
        if p >= 1:
            pr = 34 + 6 * np.sin(t * 6); d_.ellipse((tgt[0] - pr, tgt[1] - pr, tgt[0] + pr, tgt[1] + pr), outline=RED + (255,), width=5)
        l = aa_down(l); im.paste(l, (0, 0), l)
    d = ImageDraw.Draw(im); fl = ImageFont.truetype(MONT, 54); ft = ImageFont.truetype(MONT, 36)
    for n_, (lab, txt) in enumerate((("A", "Samir sort. Je reste."), ("B", "Je sors. Samir reste."))):
        y0 = 430 + n_ * 110; on = (n_ == 0) == on_a or both
        d.rounded_rectangle((124, y0, 920, y0 + 92), 16, fill=RED if on else (250, 250, 250), outline=RED, width=4)
        d.text((168, y0 + 46), lab, font=fl, fill=(255, 255, 255) if on else RED, anchor="mm")
        d.text((215, y0 + 46), txt, font=ft, fill=(255, 255, 255) if on else (40, 40, 44), anchor="lm")
    if t > t_suivre:
        d.text((540, 1450), "À SUIVRE", font=ImageFont.truetype(MONT, 42), fill=(240, 240, 240), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))


# ---------------- frames ----------------
THOUGHTS += [(wt("n01", "onze") + 0.25, L_("n02") - 0.05, "onze ans…", 560, 1420, "light"),
             (t_hit + 0.5, wt("n03", "ouvrent") - 0.1, "ne t'arrête pas", 150, 1400, "light"),
             (line_t["n05"] + dur["n05"] + 0.05, L_("n06") - 0.05, "pas sans toi.", 180, 1390, "light"),
             (line_t["n08"] + dur["n08"] + 0.1, L_("k01") - 0.05, "Inès.", 400, 1400, "light")]
CUTS = [T_POUR, L_("n02"), L_("k00"), L_("q1"), L_("a1"), T_ASSOIS, L_("r6"), L_("n04"), L_("s01"), L_("n05"), L_("n06"), T_RULE, L_("n07"), T_GREEN, L_("n08"), L_("k01"), t_vote, T_SPLIT]


def render(i, t):
    tg = None; kind = "night"; light_hud = True; cap_y = None; chip = None; co = None; choice = None
    if t < T_POUR: im = ins_led(t); kind = "screen"; chip = ("NIVEAU -2 · HEURE LOCALE", 0.2)
    elif t < L_("n02"): im = samir_close(t, T_POUR, L_("n02"), badge=True); tg = "SAMIR L. · BADGE V-0451"
    elif t < L_("k00"): im = run_shot(t, L_("n02"), L_("k00")); kind = "basement"; chip = ("NIVEAU -2 · ALLÉE C", L_("n02") + 0.15)
    elif t < L_("q1"): im = kessler_dark(t, L_("k00"), L_("q1")); tg = "MME KESSLER · MANAGER"
    elif t < L_("a1"): im = run_shot(t, L_("n02"), L_("a1")); kind = "basement"; choice = ("live", None)
    elif t < T_ASSOIS: im = kessler_dark(t, L_("a1"), T_ASSOIS, close=True); choice = ("done", "A")
    elif t < L_("r6"): im = hero_perm(t, T_ASSOIS, L_("r6")); kind = "screen"; tg = "V-0452 · TOI"
    elif t < t_rew: im = ins_rule6(t, L_("r6"), t_rew); kind = "rules"; cap_y = 1470
    elif t < L_("b1"): return rewind_shot(i, t)
    elif t < t_hit - 3 * F:
        im = run_shot(t, L_("n02"), L_("a1")); kind = "basement"; choice = ("done", "B")
        im = Image.fromarray((np.asarray(im).astype(np.float32) * (1 - 0.92 * np.clip((t - t_sil) / 0.9, 0, 1))).astype(np.uint8))       # the silence: everything goes out
    elif t < t_hit + 3 * F:
        k = int(round((t - t_hit) / F)); pl = eyes_shot(t_hit + 0.2, t_hit, L_("n04"))
        if k < 0:                                                    # smear: the whole room snaps towards you
            sx = {-3: 2.2, -2: 1.6, -1: 1.2}[max(-3, k)]; zi = pl.resize((int(W * sx), H), Image.BILINEAR); o = (zi.width - W) // 2
            return night_grade(Image.blend(zi.crop((o, 0, o + W, H)), zi.crop((max(0, o - 90), 0, max(0, o - 90) + W, H)), 0.5), i, exp=0.6)
        a = np.asarray(pl).astype(np.float32) / 255; l = np.clip((a @ G.LUMA) * 4, 0, 1)
        return Image.fromarray(((np.stack([1 - l] * 3, -1) if k != 1 else np.zeros_like(a)) * 255).astype(np.uint8))
    elif t < L_("n04"): im = eyes_shot(t, t_hit, L_("n04")); kind = "basement"; chip = ("NIVEAU -2 · 1 247 REGARDS", t_hit + 0.3)
    elif t < L_("s01"): im = stairs_fall(t, L_("n04"), L_("s01")); kind = "stairs"; chip = ("ESCALIER DE SERVICE · 40 MARCHES", L_("n04") + 0.2)
    elif t < L_("n05"): im = samir_close(t, L_("s01"), L_("n05"), bg="stairsup", talk=True, tilt=-7); tg = "SAMIR L."
    elif t < L_("n06"): im = carry_shot(t, L_("n05"), L_("n06")); kind = "stairs"
    elif t < T_RULE:
        im = gate_red(t, L_("n06"), T_RULE); kind = "gate"; light_hud = False; cap_y = 1470; chip = ("HALL · SORTIE PRINCIPALE", L_("n06") + 0.2)
        co = (L_("n06") + 0.5, T_RULE, view_xy(ST["gate"].size, t, L_("n06"), T_RULE, 1.0, 1.1, 0.6, 0.55, *LED_GATE), (-300, -330), "LECTEUR B-04", "accès refusé · 18:07", RED)
    elif t < L_("n07"): im = ins_rules(t, T_RULE - 0.6, L_("n07")); kind = "rules"; cap_y = 1560
    elif t < T_GREEN: im = ins_rewind(t, L_("n07"), T_GREEN + 0.4); kind = "white"; light_hud = False; cap_y = 1570; chip = ("HALL · HORLOGE MURALE", L_("n07") + 0.2)
    elif t < L_("n08"): im = gate_green(t, T_GREEN, L_("n08")); kind = "gate"; light_hud = False; cap_y = 1470; chip = ("HALL · 17:59", T_GREEN + 0.2)
    elif t < L_("k01"): im = exit_shot(t, L_("n08"), L_("k01")); kind = "exit"; chip = ("SORTIE · RUE DE VALMONT", L_("n08") + 0.2)
    elif t < t_vote: im = ins_speaker(t, L_("k01"), t_vote); kind = "white"; light_hud = False; chip = ("ANNONCE GÉNÉRALE · DIRECTION", L_("k01") + 0.2)
    elif t < T_SPLIT:
        im = exit_shot(t, t_vote, T_SPLIT, 1.5, 1.6); kind = "exit"
        VOTE_PT[0] = view_xy(ST["exit"].size, t, t_vote, T_SPLIT, 1.5, 1.6, GIRL[0], GIRL[1] - 0.05, GIRL[0], (GIRL[1] + GIRL[3]) / 2, drift=0.5)
    else: im = ins_mum(t, T_SPLIT, D); kind = "phone"; VOTE_PT[0] = (760, 1215); cap_y = 1570
    hits = [T_TOMBE, T_GREEN]
    amp = sum(14 * np.exp(-(t - h_) * 9) for h_ in hits if 0 <= t - h_ < 0.6)
    if L_("n02") <= t < L_("k00"): amp += 5 * abs(np.sin((t - L_("n02")) * 2 * np.pi * 2.8)) ** 6          # footfalls
    if amp > 0.5:
        dx, dy = np.sin(t * 61) * amp, np.cos(t * 47) * amp; z_ = 1 + amp / 400
        im = im.resize((int(W * z_), int(H * z_)), Image.BILINEAR); ox_, oy_ = (im.width - W) / 2 + dx, (im.height - H) / 2 + dy
        im = im.crop((int(ox_), int(oy_), int(ox_) + W, int(oy_) + H))
    if kind in ("white", "rules"): im = white_grade(im, i)
    elif kind == "gate": im = white_grade(im, i, exp=-0.22)
    elif kind == "night": im = night_grade(im, i)
    elif kind == "night_warm": im = night_grade(im, i, exp=0.45, warm=True)
    elif kind == "screen": im = night_grade(im, i, exp=0.2)
    elif kind == "stairs": im = night_grade(im, i, exp=0.0, warm=True)
    elif kind == "basement": im = night_grade(im, i, exp=0.6)
    elif kind == "exit": im = night_grade(im, i, exp=0.5, warm=True)
    hud(im, dark=kind in ("phone", "rules"), light_text=light_hud)
    if kind == "screen" and chip: hud(im, light_text=True)
    if tg: tag(im, tg)
    if chip and not tg: hud_chip(im, chip[0], t, chip[1])
    if co and co[0] <= t < co[1]: im = callout(im, t, *co)
    thought(im, t)
    story_clock(im, t, kind)
    if choice: choice_cards(im, t, L_("q1") + 0.2, "Je me retourne", "Je cours", T_OU, L_("a1"), pick=choice[1])
    if t >= t_vote: cards(im, t)
    G.karaoke(im, words, t, "present", hl=RED, box=False, y0=cap_y, size0=66, stroke=7)
    if t > D - 0.45:                                       # loop back to the frozen clock
        q = (t - (D - 0.45)) / 0.45; im = Image.blend(im, night_grade(ins_led(0.0), i, exp=0.2), float(np.clip(q, 0, 1)))
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
basement_plate(); open_plate()
if __name__ == "__main__":
    from multiprocessing import Pool
    STEP = os.environ.get("EI_STEP"); RNG = os.environ.get("EI_RANGE")
    SIG = TMP + "timeline.json"; cur = {k: round(float(v), 3) for k, v in line_t.items()}; cur["D"] = D
    if RNG:
        old = json.load(open(SIG)) if os.path.exists(SIG) else None
        if old != cur or len(glob.glob(TMP + "f*.jpg")) != N: sys.exit("partial render refused: timeline changed or frames missing -> run a full render")
        sel = set()
        for part in RNG.split(","):
            a, b = [float(x) for x in part.split("-")]; sel |= set(range(max(0, int((a - 0.4) * FPS)), min(N, int((b + 0.4) * FPS) + 1)))
        idx = sorted(sel); print("partial render", len(idx), "of", N)
    elif STEP: idx = [i for i in range(N) if i % int(STEP) == 0]
    else:
        idx = range(N)
        if not AUDIO_ONLY:
            for f in glob.glob(TMP + "f*.jpg"): os.remove(f)
    if not AUDIO_ONLY:
        with Pool(4) as pool: pool.map(frame, idx, chunksize=6)
    if STEP and not RNG: print("test ok", D); sys.exit(0)
    if not AUDIO_ONLY and not RNG: json.dump(cur, open(SIG, "w"))

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
    def step(): n = int(0.09 * VSR); return np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same") * np.exp(-np.arange(n) / VSR * 45) * 6
    under = ts < L_("n06")                                                                                       # everything below ground
    drone = (np.sin(2 * np.pi * 41 * ts) + 0.6 * np.sin(2 * np.pi * 61.7 * ts) + 0.3 * np.sin(2 * np.pi * 82.4 * ts * (1 + 0.002 * np.sin(ts)))) * 0.05
    mix += drone * under
    hum = (np.sin(2 * np.pi * 100 * ts) * 0.4 + np.sin(2 * np.pi * 120 * ts) * 0.2) * 0.025 + np.convolve(rng.standard_normal(NS), np.ones(40) / 40, "same") * 0.02
    mix += hum * ((ts >= L_("n06")) & (ts < L_("n08")))
    wind = np.convolve(rng.standard_normal(NS), np.ones(400) / 400, "same") * 0.5 * (1 + 0.5 * np.sin(ts * 0.9))
    mix += wind * ((ts >= L_("n08")) & ((ts < L_("k01")) | (ts >= t_vote)))                                      # the night air through the open doors
    add(boom(), 0.0, 0.35); buzz = np.sign(np.sin(2 * np.pi * 100 * ts)) * 0.012 * (ts < T_POUR); mix += buzz     # the LED clock hums
    for tt in np.arange(0, t_sil, 0.045):                                                                        # a thousand keyboards, until she speaks
        if rng.random() < 0.7: add(click() * rng.uniform(0.2, 0.6), tt + rng.uniform(0, 0.04), 0.45)
    for k in range(3): add(tone(1200, 0.05, 60), t_hold + k * 0.3, 0.5)                              # the choice timer
    add(boom()[: int(0.5 * VSR)], T_ASSOIS, 0.6); add(np.convolve(rng.standard_normal(int(0.12 * VSR)), np.ones(40) / 40, "same") * 10, line_t["a2"], 0.7); add(thump(), line_t["a2"], 1.2)   # you sit; the stamp
    for k in range(22): add(click() * 0.5, L_("r6") + 0.3 + k * 0.055, 0.5)                                            # the marker on the poster
    x = np.arange(int(0.9 * VSR)) / VSR; add(np.sin(2 * np.pi * np.cumsum(1800 - 1500 * x / 0.9) / VSR) * 0.25 + rng.standard_normal(len(x)) * 0.12, t_rew, 0.8)   # tape rewind
    for k in range(int((t_sil - L_("q1")) * 5.6) + 1):
        tt_ = L_("q1") + k / 5.6
        if tt_ < L_("a1") or tt_ >= L_("b1"): add(step(), tt_, 0.5); add(thump(), tt_, 0.5)
    for k in range(int((L_("k00") - L_("n02")) * 5.6) + 1):                                                      # running: two pairs of feet
        add(step(), L_("n02") + 0.1 + k / 5.6, 0.5); add(thump(), L_("n02") + 0.1 + k / 5.6, 0.5)
    for b_ in np.arange(L_("n02"), t_sil, 0.5): add(thump(), b_, 0.7); add(thump(), b_ + 0.18, 0.45)             # fast heartbeat
    m = (ts > t_sil) & (ts < t_hit); mix[m] *= 0.03
    add(np.convolve(rng.standard_normal(int(0.14 * VSR)), np.ones(25) / 25, "same") * 9, t_hit - 3 * F - 0.04, 0.5)
    add(boom(), t_hit, 1.0)
    STG = NEW + "fxtest/stinger.wav"
    if os.path.exists(STG):
        st, sr = sf.read(STG); st = st if st.ndim == 1 else st.mean(1); g_ = G.gcd(sr, VSR); st = G.resample_poly(st, VSR // g_, sr // g_) / np.abs(st).max()
        st = st[: int(0.8 * VSR)] * np.linspace(1, 0, int(0.8 * VSR)) ** 2; add(st, t_hit, 0.45)
    hi = (np.sin(2 * np.pi * 3100 * ts) + np.sin(2 * np.pi * 3140 * ts)) * 0.006 * ((ts > t_hit) & (ts < L_("n04")))   # a thin ringing: they are all watching
    mix += hi
    add(np.convolve(rng.standard_normal(int(0.3 * VSR)), np.ones(60) / 60, "same") * 9 * np.exp(-np.arange(int(0.3 * VSR)) / VSR * 14), T_TOMBE, 0.7); add(thump(), T_TOMBE + 0.02, 1.0)   # the fall
    for k in range(int((L_("n06") - L_("n05")) * 3.0) + 1): add(step(), L_("n05") + 0.2 + k / 3.0, 0.45); add(thump(), L_("n05") + 0.2 + k / 3.0, 0.6)   # carrying him up, slow and heavy
    for k in range(3): add(tone(880, 0.12, 8) * (np.arange(int(0.12 * VSR)) < int(0.1 * VSR)), L_("n06") + 0.5 + k * 0.17, 0.45)        # access denied
    for k in range(9): add(tone(2600, 0.02, 220), L_("n07") + 0.5 + k * (T_GREEN - L_("n07") - 0.6) / 9, 0.35)       # the clock mechanism, ratcheting backwards
    add(bell(783.99) + bell(1046.5) * 0.6, T_GREEN, 0.45); add(tone(1500, 0.08, 30), T_GREEN + 0.25, 0.4)                               # 17:59: a clear chime, the gates release
    add(np.convolve(rng.standard_normal(int(0.25 * VSR)), np.ones(30) / 30, "same") * 6 * np.exp(-np.arange(int(0.25 * VSR)) / VSR * 18), T_GREEN + 0.35, 0.5)
    for k, f in enumerate((659.25, 523.25, 587.33, 392.0, 392.0, 587.33, 659.25, 523.25)):                                               # Inès's music box
        add(tone(f * 2, 1.6, 3) + tone(f * 4, 1.6, 6) * 0.25, L_("n08") + 0.3 + k * 0.6, 0.22)
    ch_ = np.concatenate([bell(659.25)[: int(0.4 * VSR)], bell(523.25)[: int(0.5 * VSR)]]); ch_[-int(0.25 * VSR):] *= np.linspace(1, 0, int(0.25 * VSR)); add(ch_, L_("k01") - 0.75, 0.35)
    for b_ in np.arange(t_vote, D - 0.5, 0.75): add(thump(), b_, 0.9); add(thump(), b_ + 0.22, 0.6)
    x = np.arange(int(0.6 * VSR)) / VSR; add(np.sin(2 * np.pi * 150 * x) * (np.sin(2 * np.pi * 6 * x) > 0) * 0.5, T_SPLIT + 0.02, 0.4)   # phone buzz: Maman
    vox = np.zeros(NS)
    for k, t0 in line_t.items():
        i0 = int(t0 * VSR); j0 = min(NS, i0 + len(VO_A[k])); vox[i0:j0] += VO_A[k][: j0 - i0] * (0.85 if k == "s01" else 1.0)
    act = np.convolve((np.convolve(np.abs(vox), np.ones(2205) / 2205, "same") > 0.01).astype(float), np.ones(13230) / 13230, "same")
    mix = mix / np.abs(mix).max() * 0.55 * (1 - 0.6 * np.clip(act, 0, 1)) + vox / (np.abs(vox).max() + 1e-9) * 0.9
    mix = mix[: int(D * VSR)]; mix *= np.clip((D - ts[: len(mix)]) / 0.4, 0, 1)
    sf.write(TMP + "mix.wav", mix / np.abs(mix).max() * 0.9, VSR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", TMP + "f%05d.jpg", "-i", TMP + "mix.wav",
                    "-c:v", "libx264", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M", "-preset", "veryslow", "-tune", "film", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-x264-params", "aq-mode=3:aq-strength=0.9:psy-rd=1.0,0.15:deblock=-1,-1", "-g", "60",
                    "-af", "loudnorm=I=-13:TP=-1.0:LRA=9,volume=1.3,alimiter=limit=0.89", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ok", OUT, D)
