"""Full-body characters and finished frames, after the reference creators' whole design (not only their faces):
our toon5 heads on simple bodies (a coloured top, tube arms, round hands, dark legs), set into a lit 3D set, a
contact shadow and the set's light on them, a fixed HUD (place + night, a counter on the right) and the captions
in heavy white capitals with one orange keyword.

figure5(who, pose) -> RGBA; frame(bg, figures, hud, caption, key) -> RGB 1080x1920."""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import toon5
from toon5 import Canvas, bez, tone, taper, SS

FONTS = os.environ.get("NVS_FONTS", "/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/fonts/dl2/")   # Anton.ttf: SIL OFL, Google Fonts
ORANGE = (255, 168, 38)
PANTS = dict(toi=(38, 36, 52, 255), double=(22, 20, 28, 255), samir=(60, 64, 80, 255), maman=(70, 52, 66, 255))


def ik(sh, hand, l1, l2, out):
    """Two-bone arm: the elbow that lets the hand reach `hand`, bending outward (out = -1 left, +1 right)."""
    dx, dy = hand[0] - sh[0], hand[1] - sh[1]; d = min(math.hypot(dx, dy), l1 + l2 - 1); base = math.atan2(dy, dx)
    a = math.acos(max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    ang = base - a * out if dy >= 0 else base + a * out
    return sh[0] + l1 * math.cos(ang), sh[1] + l1 * math.sin(ang)


def figure5(who="toi", pose="stand", look=(0.0, 0.0), mouth_="line", brow=0.0, wide=1.0, turn=0.0, boil=None, light=1.0):
    """A big head on a simple body, about 3.2 heads tall like the references: the head is our toon5 bust cut at the
    collar; the body is a coloured top, tube arms with elbows (2-bone IK toward a hand target), round hands, dark
    legs and shoes, in the same flat style (one shadow side, thick outline)."""
    L = toon5.LOOK[who]; W_, H_ = 1400, 2000; cv = Canvas(W_, H_); cx = 700
    top, dark = L["top"], L.get("top_d", L["top"]); legs = PANTS[who]
    sleeve = top if who != "maman" else dark
    targets = {"stand": ((cx - 236, 1290), (cx + 236, 1290)), "reach": ((cx - 236, 1290), (cx + 600, 880)),
               "phone": ((cx - 236, 1290), (cx + 222, 470)), "fear": ((cx - 120, 600), (cx + 120, 600))}[pose]
    for s in (-1, 1):                                                      # legs and shoes
        cv.poly([(cx + s * 26, 1240), (cx + s * 150, 1240), (cx + s * 140, 1880), (cx + s * 48, 1880)], legs, 7)
        cv.ell((cx + s * 94 - 80, 1850, cx + s * 94 + 80, 1940), (20, 18, 24, 255), 7)
    def arm(s, hand):
        sh = (cx + s * 200, 770); el = ik(sh, hand, 262, 262, s)
        cv.poly(taper([sh, el], 46, 42), sleeve, 7); cv.poly(taper([el, hand], 42, 38), sleeve, 7)
        cv.ell((el[0] - 43, el[1] - 43, el[0] + 43, el[1] + 43), sleeve, 0)
        cv.ell((hand[0] - 46, hand[1] - 46, hand[0] + 46, hand[1] + 46), L["skin"], 7)
    behind = [s for s in (-1, 1) if targets[(s + 1) // 2][1] > 1000]       # hanging arms go behind the top's edge
    for s in behind: arm(s, targets[(s + 1) // 2])
    body = cv.poly(bez((cx - 220, 1270), (cx - 240, 980), (cx - 250, 780), (cx - 120, 700)) + bez((cx + 120, 700), (cx + 250, 780), (cx + 240, 980), (cx + 220, 1270)), top, 8)
    cv.inside(body, pts=[(cx - 270, 1280), (cx - 270, 690), (cx - 120, 690), (cx - 150, 1280)], fill=tone(top))
    if who in ("toi", "double"):
        cv.poly([(cx - 60, 700), (cx + 60, 700), (cx + 70, 1270), (cx - 70, 1270)], L["inner"], 6)     # the hoodie inside
        stripe = (240, 240, 248, 255) if who == "toi" else (90, 30, 40, 255)
        for s in (-1, 1): cv.stroke(bez((cx + s * 200, 760), (cx + s * 236, 900), (cx + s * 236, 1100), (cx + s * 226, 1260)), 9, stripe)
        cv.ell((cx - 180, 850, cx - 120, 910), (226, 190, 96, 255), 5)                               # the moon brooch
    if who == "samir":
        for k in range(5): y = 820 + k * 95; cv.stroke(bez((cx - 230, y + 20), (cx - 100, y - 6), (cx + 100, y - 6), (cx + 230, y + 20)), 6, dark)
        cv.stroke([(cx, 720), (cx, 1270)], 5)
    if who == "maman":
        cv.poly([(cx - 70, 700), (cx + 70, 700), (cx + 40, 1270), (cx - 40, 1270)], L["inner"], 6)
    cv.rim(body)
    for s in (-1, 1):
        if s not in behind: arm(s, targets[(s + 1) // 2])
    head = toon5.bust5(who, look=look, mouth_=mouth_, brow=brow, wide=wide, turn=turn, light=light, size=1000).crop((0, 0, 1000, 740))
    hl = Image.new("RGBA", cv.im.size, (0, 0, 0, 0)); hl.paste(head.resize((1000 * SS, 740 * SS), Image.LANCZOS), ((cx - 500) * SS, -40 * SS))
    cv.im.alpha_composite(hl)
    for s in (-1, 1):                                                      # hands raised to the face stay in front of it
        hx, hy = targets[(s + 1) // 2]
        if hy < 760 and pose != "phone": cv.ell((hx - 46, hy - 46, hx + 46, hy + 46), L["skin"], 7)
    if pose == "phone":                                                    # the phone at the ear, hand over it
        cv.poly([(cx + 196, 400), (cx + 250, 400), (cx + 250, 520), (cx + 196, 520)], (24, 24, 30, 255), 5)
        cv.ell((cx + 176, 424, cx + 268, 516), L["skin"], 7)
    out = cv.done(1000)
    return toon5.line_boil(out, boil) if boil is not None else out


def back5(who="toi", boil=None):
    """Seen from behind, for over-the-shoulder shots: the back of the head is all hair, the ears show, the neck, the
    shoulders of the jacket with the hood and the headphones' band."""
    L = toon5.LOOK[who]; cv = Canvas(1400, 1400); cx = 700
    top = L["top"]; hair = L.get("hair", (40, 30, 26, 255))
    body = cv.poly(bez((cx - 520, 1400), (cx - 500, 980), (cx - 330, 860), (cx - 120, 840)) + bez((cx + 120, 840), (cx + 330, 860), (cx + 500, 980), (cx + 520, 1400)), top, 8)
    cv.inside(body, pts=[(cx - 560, 1400), (cx - 560, 820), (cx - 220, 820), (cx - 300, 1400)], fill=tone(top))
    if who in ("toi", "double"):
        hood = cv.poly(bez((cx - 260, 900), (cx - 220, 1180), (cx + 220, 1180), (cx + 260, 900)) + [(cx + 140, 860), (cx - 140, 860)], L["inner"], 7)
        cv.stroke(bez((cx - 250, 780), (cx - 300, 900), (cx + 300, 900), (cx + 250, 780)), 22, (34, 32, 44, 255))   # the headphones' band
    cv.poly([(cx - 70, 700), (cx + 70, 700), (cx + 80, 880), (cx - 80, 880)], tone(L["skin"]), 6)                  # the neck
    for s in (-1, 1): cv.ell((cx + s * 206 - 30, 400, cx + s * 206 + 30, 500), L["skin"], 6)                       # ears
    h = cv.poly(bez((cx, 140), (cx + 160, 136), (cx + 236, 240), (cx + 226, 420)) + bez((cx + 226, 420), (cx + 220, 600), (cx + 140, 740), (cx, 750))[1:]
                + bez((cx, 750), (cx - 140, 740), (cx - 220, 600), (cx - 226, 420))[1:] + bez((cx - 226, 420), (cx - 236, 240), (cx - 160, 136), (cx, 140))[1:], hair, 8)
    cv.inside(h, pts=[(cx - 260, 760), (cx - 260, 120), (cx - 90, 120), (cx - 130, 760)], fill=tone(hair, 0.8))
    for k in range(-3, 4):                                                 # the waves combed back, seen from behind
        cv.stroke(bez((cx + k * 50, 160), (cx + k * 64, 300), (cx + k * 60, 480), (cx + k * 46, 700), 16), 4, tone(hair, 0.6))
    if who == "toi": cv.stroke(bez((cx - 150, 200), (cx - 196, 260), (cx - 220, 330), (cx - 214, 380), 12), 9, L["lock"])  # the lock's blue shows at the side
    cv.rim(h)
    out = cv.done(1000)
    return toon5.line_boil(out, boil) if boil is not None else out


def place(bg, fig, x, foot_y, height, tint=(0.82, 0.86, 1.0), shade=0.85):
    """Stand a figure in the set: scale to `height` px, tint it with the set's light, a soft contact shadow."""
    k = height / fig.height; f = fig.resize((int(fig.width * k), int(fig.height * k)), Image.LANCZOS)
    a = np.asarray(f).astype(np.float32); a[..., :3] *= np.array(tint) * shade; f = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    sh = Image.new("RGBA", bg.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([x - f.width * 0.32, foot_y - 18, x + f.width * 0.32, foot_y + 22], fill=(0, 0, 0, 170))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    bg.alpha_composite(f, (int(x - f.width / 2), int(foot_y - f.height * 0.955)))
    return bg


def hud(im, place_txt, night, total=None, right_label=None, right_value=None):
    d = ImageDraw.Draw(im); small = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 22); big = ImageFont.truetype(FONTS + "Anton.ttf", 78)
    d.ellipse((56, 206, 68, 218), fill=ORANGE); d.text((78, 200), place_txt.upper(), font=small, fill=(236, 236, 240))
    d.text((56, 230), night.upper(), font=big, fill=(244, 244, 246), stroke_width=2, stroke_fill=(10, 10, 14))
    if total:
        w = d.textlength(night.upper(), font=big); d.text((56 + w + 12, 278), total, font=ImageFont.truetype(FONTS + "Anton.ttf", 34), fill=(190, 190, 200))
    if right_label:
        d.text((1024, 200), right_label.upper(), font=small, fill=ORANGE, anchor="ra")
        d.text((1024, 230), right_value, font=big, fill=ORANGE, anchor="ra", stroke_width=2, stroke_fill=(10, 10, 14))
    return im


def caption(im, words, key=None, y=1180):
    """Heavy white capitals, one keyword orange, a dark stroke, centred: the references' caption."""
    d = ImageDraw.Draw(im); f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 76)
    words = [w.upper() for w in words]; widths = [d.textlength(w + " ", font=f) for w in words]
    x = 540 - sum(widths) / 2
    for w, wd in zip(words, widths):
        d.text((x + 4, y + 6), w, font=f, fill=(0, 0, 0, 160))
        d.text((x, y), w, font=f, fill=ORANGE if (key and w == key.upper()) else (250, 250, 250), stroke_width=5, stroke_fill=(12, 10, 16))
        x += wd
    return im


def vignette(im, k=0.55):
    a = np.asarray(im.convert("RGB")).astype(np.float32); h, w = a.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
    v = np.clip(1 - (((xx - w / 2) / (w * 0.8)) ** 2 + ((yy - h * 0.48) / (h * 0.66)) ** 2), 0, 1) ** 0.8
    return Image.fromarray(np.clip(a * ((1 - k) + k * v[..., None]), 0, 255).astype(np.uint8))


if __name__ == "__main__":
    out = sys.argv[1]
    bg = Image.open(sys.argv[2]).convert("RGBA").resize((1080, 1920))
    fig = figure5("toi", "reach", look=(0.2, -0.1), boil=1)
    place(bg, fig, 430, 1660, 1120)
    hud(bg, "Caissier de nuit", "Nuit 1", "/ 30", "Caisse 3", "02:14")
    im = vignette(bg)
    caption(im, ["Une", "lumière", "s'allume"], key="lumière")
    im.save(out, quality=92); print("ok")


STYLE_LINE = ("Flat 2D cel animation, big-headed characters with bold black contours and flat colour fills, one hard "
              "shadow step leaning violet, a thin lavender moonlight rim; standing in a dark cinematic 3D night set.")


def render_shot(spec, sets):
    """Render one shot from the seven-field spec (references/prompts.md). The style and the identities are fixed in
    code (toon5, scene5); a spec may only choose what varies: framing, pose, expression, light, text."""
    from PIL import ImageFilter
    bg = sets[spec.get("set", "aisle")].copy()
    who, pose = spec.get("who", "toi"), spec.get("pose", "stand"); ex = spec.get("expr", {}); light = spec.get("light", 1.0)
    boil = spec.get("boil", 0); shot = spec.get("shot", "wide")
    def tinted(img, k=(0.84, 0.88, 1.0)):
        a = np.asarray(img).astype(np.float32); a[..., :3] *= np.array(k); return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    if shot == "wide":
        place(bg, figure5(who, pose, light=light, boil=boil, **ex), spec.get("x", 540), spec.get("foot", 1560), spec.get("height", 1050))
    elif shot == "close":
        bg = bg.filter(ImageFilter.GaussianBlur(14))
        bg.alpha_composite(tinted(toon5.bust5(who, light=light, boil=boil, **ex)).resize((1180, 1180)), (-50, 560))
    elif shot in ("far-threat", "over-shoulder"):
        far = spec.get("far", "double")
        place(bg, figure5(far, spec.get("far_pose", "stand"), boil=boil), spec.get("x", 560), spec.get("foot", 1010), spec.get("height", 300), tint=(1.0, 0.82, 0.62), shade=0.9)
        fg = tinted(back5(who, boil=boil), (0.7, 0.74, 0.86))
        bg.alpha_composite(fg.resize((1300, 1300)).filter(ImageFilter.GaussianBlur(2)), (-520, 900))
    hud(bg, *spec.get("hud", ("Caissier de nuit", "Nuit 1", "/ 30", "Caisse 3", "02:14")))
    im = vignette(bg, 0.6 if shot != "wide" else 0.55)
    if spec.get("text"): caption(im, spec["text"].split(), key=spec.get("key"), y=1240 if shot == "close" else 1180)
    return im
