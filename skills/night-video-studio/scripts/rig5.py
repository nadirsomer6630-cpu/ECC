"""Cut-out rig for the season 2 characters, the way the reference creators animate: each body part is a separate
drawing turning on its joint (hips, waist, neck, shoulders, elbows), poses are hand targets solved by 2-bone IK and
eased between keys at 30 fps, figures stand in the 3D set at the exact place and size a 1.75 m person has there
(calibration exported by supermarche.py), the outline keeps its screen weight at every size, and the camera pushes in.

Figure(who, height_px) -> .frame(pose) RGBA ; place in a set with proj(); see demo() at the bottom."""
import math, json, os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import toon5
from toon5 import Canvas, bez, tone, taper
import scene5

W_, H_, CX = 1400, 2000, 700
STATURE = 1880            # design px from the top of the hair to the soles: a 1.75 m person
FOOT = 1940
PANTS = scene5.PANTS


def rot(p, c, deg):
    """Rotate point p about c by deg, counter-clockwise on screen (the same sense as PIL's Image.rotate)."""
    t = math.radians(deg); dx, dy = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * math.cos(t) + dy * math.sin(t), c[1] - dx * math.sin(t) + dy * math.cos(t))


def ang(v):
    """The rotation that turns a limb hanging straight down into the direction v."""
    return math.degrees(math.atan2(v[0], v[1]))


def ik_low(sh, hand, l1, l2):
    """Two-bone arm whose elbow hangs as low as possible: a raised hand (phone at the ear, hand to the face) keeps
    its elbow down and out, the forearm rising to the hand, instead of folding over the upper arm."""
    dx, dy = hand[0] - sh[0], hand[1] - sh[1]; d = min(math.hypot(dx, dy), l1 + l2 - 1); base = math.atan2(dy, dx)
    a = math.acos(max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    c = [(sh[0] + l1 * math.cos(base + k * a), sh[1] + l1 * math.sin(base + k * a)) for k in (-1, 1)]
    return max(c, key=lambda p: p[1])


def ease(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)


class Figure:
    def __init__(self, who, height_px, exprs=None):
        self.who = who; self.s = height_px / STATURE
        self.linek = max(1.0, min(3.2, 0.42 / self.s)); toon5.LINE_K = self.linek  # same outline width on screen at any size
        L = toon5.LOOK[who]; self.L = L
        top = L["top"]; dark = L.get("top_d", top); sleeve = top if who != "maman" else dark
        def part(draw):
            cv = Canvas(W_, H_); draw(cv); im = cv.done(1000)
            return im.resize((max(1, int(W_ * self.s)), max(1, int(H_ * self.s))), Image.LANCZOS)
        self.parts = {}
        for s in (-1, 1):
            def leg(cv, s=s):
                cv.poly([(CX + s * 26, 1240), (CX + s * 150, 1240), (CX + s * 140, 1880), (CX + s * 48, 1880)], PANTS[who], 7)
                cv.ell((CX + s * 94 - 80, 1850, CX + s * 94 + 80, 1940), (20, 18, 24, 255), 7)
            def upper(cv, s=s):
                x = CX + s * 200; cv.poly(taper([(x, 770), (x, 1032)], 46, 42), sleeve, 7)
            def fore(cv, s=s):
                x = CX + s * 200; cv.ell((x - 43, 989, x + 43, 1075), sleeve, 7); cv.poly(taper([(x, 1032), (x, 1294)], 42, 38), sleeve, 7)
                cv.ell((x - 46, 1248, x + 46, 1340), L["skin"], 7)
            self.parts[("leg", s)] = part(leg); self.parts[("upper", s)] = part(upper); self.parts[("fore", s)] = part(fore)
        def torso(cv):
            body = cv.poly(bez((CX - 220, 1270), (CX - 240, 980), (CX - 250, 780), (CX - 120, 700)) + bez((CX + 120, 700), (CX + 250, 780), (CX + 240, 980), (CX + 220, 1270)), top, 8)
            cv.inside(body, pts=[(CX - 270, 1280), (CX - 270, 690), (CX - 120, 690), (CX - 150, 1280)], fill=tone(top))
            if who in ("toi", "double"):
                cv.poly([(CX - 60, 700), (CX + 60, 700), (CX + 70, 1270), (CX - 70, 1270)], L["inner"], 6)
                stripe = (240, 240, 248, 255) if who == "toi" else (90, 30, 40, 255)
                for s in (-1, 1): cv.stroke(bez((CX + s * 200, 760), (CX + s * 236, 900), (CX + s * 236, 1100), (CX + s * 226, 1260)), 9, stripe)
                cv.ell((CX - 180, 850, CX - 120, 910), (226, 190, 96, 255), 5)
            if who == "samir":
                for k in range(5): y = 820 + k * 95; cv.stroke(bez((CX - 230, y + 20), (CX - 100, y - 6), (CX + 100, y - 6), (CX + 230, y + 20)), 6, dark)
            if who == "maman":
                cv.poly([(CX - 70, 700), (CX + 70, 700), (CX + 40, 1270), (CX - 40, 1270)], L["inner"], 6)
            cv.rim(body)
        self.parts["torso"] = part(torso)
        self.heads = {}
        for key, ex in (exprs or {"n": {}}).items():
            h = toon5.bust5(who, size=1000, **ex).crop((0, 0, 1000, 740))
            full = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); full.paste(h, (CX - 500, -40))
            self.heads[key] = full.resize((int(W_ * self.s), int(H_ * self.s)), Image.LANCZOS)
        toon5.LINE_K = 1.0
        self.hip = (CX, 1250); self.neck = (CX, 690); self.sh = {s: (CX + s * 200, 770) for s in (-1, 1)}
        self.rest_el = {s: (CX + s * 200, 1032) for s in (-1, 1)}

    def face(self, key, ex):
        """Heads are drawn on demand and kept: emotions move through several drawings instead of one switch."""
        if key not in self.heads:
            toon5.LINE_K = self.linek
            h = toon5.bust5(self.who, size=1000, **ex).crop((0, 0, 1000, 740)); toon5.LINE_K = 1.0
            full = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); full.paste(h, (CX - 500, -40))
            self.heads[key] = full.resize((int(W_ * self.s), int(H_ * self.s)), Image.LANCZOS)
        return key

    def frame(self, pose):
        """pose: torso (deg), head (deg), bob (design px), legs (deg, +/-), hands {-1: (x, y), 1: (x, y)} in design px,
        face (key of the head drawings), phone (bool)."""
        s = self.s; S = lambda p: (p[0] * s, p[1] * s)
        out = Image.new("RGBA", self.parts["torso"].size, (0, 0, 0, 0))
        t_ = pose.get("torso", 0.0); bob = pose.get("bob", 0.0); legs = pose.get("legs", 0.0)
        def paste(img, deg, pivot, world):
            c = S(pivot); w = S(world)
            out.alpha_composite(img.rotate(deg, resample=Image.BICUBIC, center=c, translate=(w[0] - c[0], w[1] - c[1])))
        for sd in (-1, 1):
            hip = (CX + sd * 88, 1250); paste(self.parts[("leg", sd)], legs * sd, hip, hip)
        hipw = (CX, 1250 + bob)
        arms = {}
        for sd in (-1, 1):
            shw = rot(self.sh[sd], self.hip, t_); shw = (shw[0], shw[1] + bob)
            hand = pose["hands"][sd]
            el = ik_low(shw, hand, 262, 262) if hand[1] < 1000 else scene5.ik(shw, hand, 262, 262, sd)
            arms[sd] = (shw, el, ang((el[0] - shw[0], el[1] - shw[1])), ang((hand[0] - el[0], hand[1] - el[1])), hand)
        def arm(sd):
            shw, el, au, af, hand = arms[sd]
            paste(self.parts[("upper", sd)], au, self.sh[sd], shw); paste(self.parts[("fore", sd)], af, self.rest_el[sd], el)
        behind = [sd for sd in (-1, 1) if arms[sd][4][1] > 1000]
        for sd in behind: arm(sd)
        paste(self.parts["torso"], t_, self.hip, hipw)
        nw = rot(self.neck, self.hip, t_); nw = (nw[0], nw[1] + bob)
        paste(self.heads[pose.get("face", "n")], t_ + pose.get("head", 0.0), self.neck, nw)
        for sd in (-1, 1):
            if sd not in behind: arm(sd)
        if pose.get("phone"):
            hx, hy = pose["hands"][1]; d = ImageDraw.Draw(out)
            d.rounded_rectangle([S((hx - 30, hy - 74))[0], S((hx - 30, hy - 74))[1], S((hx + 22, hy + 30))[0], S((hx + 22, hy + 30))[1]], radius=max(1, 8 * s), fill=(24, 24, 32, 255), outline=(10, 8, 14, 255), width=max(1, int(4 * s * max(1, 0.42 / s))))
        return out


def calib(path):
    c = json.load(open(path)); xs = sorted(set(d["x"] for d in c))
    cols = {x: sorted([d for d in c if d["x"] == x], key=lambda d: d["y"]) for x in xs}
    def proj(xw, yw):
        def at(x):
            col = cols[x]; Y = [d["y"] for d in col]
            return [float(np.interp(yw, Y, [d[k] for d in col])) for k in ("fx", "fy", "hy")]
        i = int(np.clip(np.searchsorted(xs, xw) - 1, 0, len(xs) - 2)); x0, x1 = xs[i], xs[i + 1]; u = (xw - x0) / (x1 - x0)
        a, b = at(x0), at(x1); fx, fy, hy = [p + (q - p) * u for p, q in zip(a, b)]
        return fx, fy, fy - hy                                          # foot x, foot y, height in px
    return proj


def stand_in(frame_im, fig_img, fx, fy, tint, shadow=True):
    a = np.asarray(fig_img).astype(np.float32); a[..., :3] *= np.array(tint); f = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    k = fig_img.width / W_
    if shadow:
        sh = Image.new("RGBA", frame_im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([fx - 170 * k, fy - 16 * k - 4, fx + 170 * k, fy + 26 * k + 4], fill=(0, 0, 0, 170))
        frame_im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(max(2, 14 * k))))
    frame_im.alpha_composite(f, (int(fx - CX * k), int(fy - FOOT * k)))


def camera(im, z, cx=540, cy=1000):
    a = np.asarray(im); M = np.float32([[z, 0, cx - z * cx], [0, z, cy - z * cy]])
    return Image.fromarray(cv2.warpAffine(a, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT))


def demo(out_dir, seconds=6.0, fps=30):
    os.makedirs(out_dir, exist_ok=True)
    bg = Image.open("s2/aisle.png").convert("RGBA").resize((1080, 1920)); proj = calib("s2/aisle_cal.json")
    hx, hy, hh = proj(0.32, 0.35)
    hero = Figure("toi", hh, {"n": {}, "b": {"blink": True}, "l": {"look": (0.5, -0.2), "wide": 1.2, "brow": 0.6}, "lb": {"look": (0.5, -0.2), "blink": True}})
    dbl = Figure("double", proj(0.0, -12)[2], {"n": {}})
    rest = {-1: (CX - 236, 1290), 1: (CX + 236, 1290)}; ear = (CX + 222, 470)
    n = int(seconds * fps)
    for f in range(n):
        t = f / fps; im = bg.copy()
        # the double walks toward you, from the dark into the warm pool
        yw = -15 + 5.0 * ease((t - 0.3) / (seconds - 0.3)); dx, dy, dh = proj(0.05, yw)
        if abs(dh - dbl.s * STATURE) > 6: dbl = Figure("double", dh, {"n": {}})
        ph = t * 2 * math.pi / 0.95
        dp = {"torso": 1.5 * math.sin(ph), "head": -2 * math.sin(ph), "bob": -10 * abs(math.sin(ph)), "legs": 18 * math.sin(ph),
              "hands": {-1: (CX - 236 + 60 * math.sin(ph), 1280), 1: (CX + 236 - 60 * math.sin(ph), 1280)}, "face": "n"}
        warm = min(1.0, max(0.0, (yw + 13) / 3.5))
        stand_in(im, dbl.frame(dp), dx, dy, tint=(0.45 + 0.55 * warm, 0.42 + 0.40 * warm, 0.58 + 0.04 * warm))
        # you: breathing, a blink, the phone raised to the ear, the head tilts to listen, then you look down the aisle
        u = ease((t - 1.3) / 0.8); hand = (rest[1][0] + (ear[0] - rest[1][0]) * u, rest[1][1] + (ear[1] - rest[1][1]) * u)
        look = t > 3.4; blink = (1.0 < t < 1.1) or (4.3 < t < 4.4)
        face = ("lb" if blink else "l") if look else ("b" if blink else "n")
        hp = {"torso": 0.8 * math.sin(t * 2 * math.pi / 3.2), "head": -5 * ease((t - 2.0) / 0.6) + 3 * ease((t - 3.4) / 0.5), "bob": 4 * math.sin(t * 2 * math.pi / 3.2),
              "hands": {-1: rest[-1], 1: hand}, "face": face, "phone": u > 0.6}
        stand_in(im, hero.frame(hp), hx, hy, tint=(0.84, 0.88, 1.0))
        im = camera(im, 1.0 + 0.07 * ease(t / seconds))
        scene5.hud(im, "Caissier de nuit", "Nuit 1", "/ 30", "Caisse 3", "02:14" if t < 4 else "02:15")
        im = scene5.vignette(im, 0.55)
        if t < 2.3: scene5.caption(im, ["Ta", "mère", "t'appelle"], key="mère")
        else: scene5.caption(im, ["Elle", "dort", "pourtant"], key="dort")
        im.save(f"{out_dir}/f{f:04d}.jpg", quality=90)
    print("ok", n)


class Spring:
    """Follow-through: a part reaches its target a little late and overshoots softly (stiffness k, damping ratio z)."""
    def __init__(self, x, k=180.0, z=0.62):
        self.x = np.array(x, float); self.v = np.zeros_like(self.x); self.k = k; self.c = 2 * math.sqrt(k) * z
    def step(self, target, dt=1 / 30):
        a = self.k * (np.array(target, float) - self.x) - self.c * self.v; self.v += a * dt; self.x += self.v * dt
        return tuple(self.x) if self.x.shape else float(self.x)


def back_out(u, k=1.6):
    u = max(0.0, min(1.0, u)); u -= 1; return u * u * ((k + 1) * u + k) + 1


def blink_lid(t, t0):
    """A real blink: open, half, closed, half, open over about 150 ms."""
    seq = [1.0, 0.55, 0.1, 0.1, 0.55, 1.0]; i = int((t - t0) * 30)
    return seq[i] if 0 <= i < len(seq) else 1.0


def demo2(out_dir, seconds=7.0, fps=30):
    """Acting test: calm, the phone buzzes (startle with anticipation and overshoot), the phone rises to the ear, he
    listens with a worried half-lid, sees the double, fear builds in steps, a step back, a hand to the chest, a tremor;
    the double walks into the warm pool. Hands and head follow on springs; blinks in five drawings."""
    os.makedirs(out_dir, exist_ok=True)
    bg = Image.open("s2/aisle.png").convert("RGBA").resize((1080, 1920)); proj = calib("s2/aisle_cal.json")
    x0, y0 = 0.32, 0.35; hx0, hy0, hh0 = proj(x0, y0)
    hero = Figure("toi", hh0); dbl = Figure("double", proj(0.0, -12)[2])
    rest = {-1: (CX - 236, 1290), 1: (CX + 236, 1290)}; ear = (CX + 222, 470); chest = (CX - 40, 930)
    hand_r, hand_l = Spring(rest[1], 160, 0.55), Spring(rest[-1], 140, 0.6); head_s = Spring(0.0, 90, 0.5); bob_s = Spring(0.0, 220, 0.45)
    n = int(seconds * fps); rng = np.random.default_rng(1)
    for f in range(n):
        t = f / fps; im = bg.copy()
        yw = -13 + 4.2 * ease((t - 0.2) / (seconds - 0.2)); dx, dy, dh = proj(0.05, yw)
        if abs(dh - dbl.s * STATURE) > 6: dbl = Figure("double", dh)
        ph = t * 2 * math.pi / 1.05
        dp = {"torso": 1.5 * math.sin(ph), "head": -2 * math.sin(ph), "bob": -10 * abs(math.sin(ph)), "legs": 16 * math.sin(ph),
              "hands": {-1: (CX - 236 + 55 * math.sin(ph), 1280), 1: (CX + 236 - 55 * math.sin(ph), 1280)}, "face": dbl.face("n", {})}
        warm = min(1.0, max(0.0, (yw + 12) / 3.0))
        stand_in(im, dbl.frame(dp), dx, dy, tint=(0.45 + 0.55 * warm, 0.42 + 0.40 * warm, 0.58 + 0.04 * warm))
        # --- the hero's acting
        fear = ease((t - 3.9) / 0.6); startle = t > 1.2
        lid = min(blink_lid(t, 0.7), blink_lid(t, 3.1), blink_lid(t, 5.9))
        if t < 1.2: ex = {"look": (-0.2, 0.25)}; key = "calm"
        elif t < 2.4: ex = {"look": (0.1, -0.1), "wide": 1.0 + 0.3 * min(1, (t - 1.2) / 0.13), "brow": 0.5 * min(1, (t - 1.2) / 0.13)}; key = "startle"
        elif t < 3.8: ex = {"look": (0.2, 0.0), "brow": 0.45}; lid = min(lid, 0.82); key = "worry"
        else:
            st = min(3, int((t - 3.8) / 0.1)); ex = {"look": (0.15 + 0.12 * st, -0.15), "wide": 1.0 + 0.13 * st, "brow": 0.35 * st, "mouth_": "fear" if st >= 2 else "line"}; key = f"fear{st}"
        q = round(lid, 2); key = f"{key}_{round(ex.get('wide', 1), 2)}_{q}"; ex = dict(ex, lid=lid)
        face = hero.face(key, ex)
        # hands: anticipation (a small dip) then the phone rises with overshoot; later the left hand to the chest
        if t < 1.55: tr = rest[1]
        elif t < 1.7: tr = (rest[1][0], rest[1][1] + 30)
        else:
            u = back_out((t - 1.7) / 0.5); tr = (rest[1][0] + (ear[0] - rest[1][0]) * u, rest[1][1] + (ear[1] - rest[1][1]) * u)
        tl = chest if t > 4.45 else rest[-1]
        trem = fear * (3.0 * math.sin(t * 2 * math.pi * 9.0) + 2.0 * math.sin(t * 2 * math.pi * 11.3))
        hr = hand_r.step(tr); hl = hand_l.step(tl)
        head_t = (-6 if 2.0 < t < 3.8 else 0) + 3 * fear + 0.5 * trem
        bob_t = (-16 if 1.2 < t < 1.45 else 0) - 10 * fear + 3 * math.sin(t * 2 * math.pi / 3.0)   # startle, shoulders up in fear, breathing
        pose = {"torso": 0.8 * math.sin(t * 2 * math.pi / 3.0) - 1.5 * fear, "head": head_s.step(head_t), "bob": bob_s.step(bob_t),
                "hands": {-1: (hl[0] + trem, hl[1]), 1: (hr[0] + trem * 0.6, hr[1])}, "face": face, "phone": t > 1.95}
        img = hero.frame(pose)
        step = 0.35 * ease((t - 4.4) / 0.7); hx, hy, hh = proj(x0, y0 + step)                   # a step back toward you
        if abs(hh - hh0) > 1: img = img.resize((int(img.width * hh / hh0), int(img.height * hh / hh0)), Image.LANCZOS)
        stand_in(im, img, hx, hy, tint=(0.84, 0.88, 1.0))
        z = 1.0 + 0.06 * ease(t / seconds) + 0.03 * fear; im = camera(im, z, 540 + 4 * math.sin(t * 1.7), 1000 + 3 * math.sin(t * 2.3))
        scene5.hud(im, "Caissier de nuit", "Nuit 1", "/ 30", "Caisse 3", "02:14" if t < 5 else "02:15")
        im = scene5.vignette(im, 0.55 + 0.1 * fear)
        if t < 1.2: scene5.caption(im, ["Tu", "es", "seul"], key="seul")
        elif t < 3.8: scene5.caption(im, ["Ta", "mère", "t'appelle"], key="mère")
        else: scene5.caption(im, ["Elle", "est", "là"], key="là")
        im.save(f"{out_dir}/f{f:04d}.jpg", quality=90)
    print("ok", n)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "acting":
        demo2(sys.argv[1]); sys.exit()
    demo(sys.argv[1] if len(sys.argv) > 1 else "rigtest")
