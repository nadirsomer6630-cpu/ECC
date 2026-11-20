"""The night courier, drawn in 2D: a round head, a purple cap with a moon, a grey hoodie, a red thread bracelet.
char(h, **pose) returns an RGBA sprite of height h whose feet are at the bottom centre. Every pose is a set of
angles, so the same function gives the walk cycle, the acting beats and the close-ups (draw it big, it stays sharp).
dark=True draws the other one: the same outline, black, with white eyes and a grin."""
import math
from PIL import Image, ImageDraw, ImageFilter

OL = (22, 18, 34, 255)
SKIN, SKIN_D = (236, 190, 150, 255), (205, 150, 112, 255)
HOOD, HOOD_D = (150, 156, 170, 255), (112, 118, 134, 255)
CAP, CAP_D = (112, 72, 226, 255), (78, 46, 170, 255)
PANTS, SHOE = (40, 44, 62, 255), (236, 236, 232, 255)
REDB = (214, 30, 30, 255)
BAG, BAG_D = (196, 138, 70, 255), (150, 100, 48, 255)


def char(h=900, back=False, dark=False, head=(0.0, 0.0), look=(0.0, 0.0), wide=1.0, brow=0.0, mouth="line", blink=False,
         armL=(0.08, 0.1), armR=(0.08, 0.1), legs=(0.0, 0.0), lean=0.0, sweat=False, phone=None, bag=None, bill=False,
         cap=True, pack=True, glow=None, crop_top=None, mum=False, samir=False):
    """Angles in radians. arm=(shoulder, elbow): 0 hangs down, positive swings outwards and up. legs=(left, right)
    swing forward (+) or back (-), drawn as a sideways stride. head=(tilt, nod). phone/bag: "L" or "R" hand."""
    S = h / 1000 * 2; Wc, Hc = int(700 * S), int(1000 * S)
    im = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def P(x, y): return ((350 + x) * S, y * S)
    ow = 9 * S
    if dark:
        C = dict(skin=(8, 8, 14, 255), skin_d=(8, 8, 14, 255), hood=(10, 10, 16, 255), hood_d=(6, 6, 10, 255), cap=(12, 10, 20, 255), cap_d=(6, 5, 12, 255), pants=(6, 6, 10, 255), shoe=(14, 14, 20, 255), ol=(60, 62, 90, 255))
    else:
        C = dict(skin=SKIN, skin_d=SKIN_D, hood=HOOD, hood_d=HOOD_D, cap=CAP, cap_d=CAP_D, pants=PANTS, shoe=SHOE, ol=OL)
    if samir:                                                         # Samir, his best friend: same company, green cap and bag, a short beard
        C.update(skin=(196, 146, 108, 255), skin_d=(166, 118, 84, 255), hood=(58, 64, 82, 255), hood_d=(44, 48, 62, 255), cap=(46, 150, 96, 255), cap_d=(30, 108, 68, 255), pants=(34, 34, 40, 255))
    if mum:                                                           # his mother: a soft rose cardigan, a grey bun, no cap, no bag
        C.update(hood=(196, 128, 138, 255), hood_d=(160, 96, 108, 255), pants=(64, 58, 76, 255), shoe=(90, 70, 60, 255)); cap = False; pack = False
    def capsule(a, b, w, fill, outline=True):
        if outline:
            d.line([a, b], fill=C["ol"], width=int(w * S + ow * 2)); r = (w * S + ow * 2) / 2
            for p in (a, b): d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=C["ol"])
        d.line([a, b], fill=fill, width=int(w * S)); r = w * S / 2
        for p in (a, b): d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)
    def limb(pts, w, fill):
        r1 = (w * S + ow * 2) / 2; r2 = w * S / 2
        for a, b in zip(pts, pts[1:]): d.line([a, b], fill=C["ol"], width=int(w * S + ow * 2))
        for p in pts: d.ellipse((p[0] - r1, p[1] - r1, p[0] + r1, p[1] + r1), fill=C["ol"])
        for a, b in zip(pts, pts[1:]): d.line([a, b], fill=fill, width=int(w * S))
        for p in pts: d.ellipse((p[0] - r2, p[1] - r2, p[0] + r2, p[1] + r2), fill=fill)
    def disc(c, r, fill, outline=True):
        if outline: d.ellipse((c[0] - r * S - ow, c[1] - r * S - ow, c[0] + r * S + ow, c[1] + r * S + ow), fill=C["ol"])
        d.ellipse((c[0] - r * S, c[1] - r * S, c[0] + r * S, c[1] + r * S), fill=fill)
    def rrect(x0, y0, x1, y1, r, fill, outline=True):
        a, b = P(x0, y0), P(x1, y1)
        if outline: d.rounded_rectangle((a[0] - ow, a[1] - ow, b[0] + ow, b[1] + ow), r * S + ow, fill=C["ol"])
        d.rounded_rectangle((a[0], a[1], b[0], b[1]), r * S, fill=fill)
    lx = lean * 120                                                  # the whole upper body shifts when he leans
    hipy, sh_y = 668, 452
    # legs
    for side, a in ((-1, legs[0]), (1, legs[1])):
        # seen from the front or the back, a step is a knee that lifts (a > 0) or a leg that trails (a < 0), not a sideways swing
        lift, trail = max(0.0, a), max(0.0, -a); hx = side * 42 + lx * 0.3
        fx = hx + side * 4; fy = hipy + 286 - lift * 105 - trail * 22; kx = (hx + fx) / 2 + side * lift * 26; ky = (hipy + fy) / 2 - lift * 12
        limb([P(hx, hipy), P(kx, ky), P(fx, fy)], 60, C["pants"])
        sx = fx + (12 if not back else 0) * side; g_ = 1 + (0.28 * lift - 0.1 * trail) * (-1 if back else 1)
        capsule(P(sx - 20 * g_, fy + 30), P(sx + 26 * g_, fy + 30), 40 * g_, C["shoe"])
    def arm(side, ang, front=True):
        a1, a2 = ang; sx = side * 100 + lx; ex = sx + side * math.sin(a1) * 118; ey = sh_y + 18 + math.cos(a1) * 118
        hx_ = ex + side * math.sin(a1 + a2) * 112; hy_ = ey + math.cos(a1 + a2) * 112
        limb([P(sx, sh_y + 18), P(ex, ey), P(hx_, hy_)], 58, C["hood"])
        cx_, cy_ = ex + side * math.sin(a1 + a2) * 92, ey + math.cos(a1 + a2) * 92
        capsule(P(cx_, cy_), P(cx_ + side * math.sin(a1 + a2) * 8, cy_ + math.cos(a1 + a2) * 8), 58, C["hood_d"], outline=False)       # cuff
        hand = P(hx_ + side * math.sin(a1 + a2) * 22, hy_ + math.cos(a1 + a2) * 22)
        if side == 1 and not dark and not mum and not samir:                                    # the red thread bracelet on his right wrist
            bx, by = hx_ + side * math.sin(a1 + a2) * 2, hy_ + math.cos(a1 + a2) * 2
            capsule(P(bx, by), P(bx + side * math.sin(a1 + a2) * 5, by + math.cos(a1 + a2) * 5), 60, REDB, outline=False)
        return hand
    def props(side, hand):
        s_ = "L" if side == -1 else "R"
        if bag == s_:
            x, y = hand[0] / S - 350, hand[1] / S
            d.line([P(x - 26, y + 6), P(x - 34, y + 60)], fill=C["ol"], width=int(7 * S)); d.line([P(x + 26, y + 6), P(x + 34, y + 60)], fill=C["ol"], width=int(7 * S))
            rrect(x - 78, y + 56, x + 78, y + 250, 8, BAG if not dark else (16, 14, 14, 255)); d.rectangle((*P(x - 78, y + 56), *P(x + 78, y + 86)), fill=BAG_D if not dark else (10, 9, 9, 255))
            if not dark: d.rectangle((*P(x - 44, y + 120), *P(x + 44, y + 190)), fill=(244, 242, 236, 255)); d.rectangle((*P(x - 34, y + 132), *P(x + 20, y + 142)), fill=REDB); d.rectangle((*P(x - 34, y + 154), *P(x + 34, y + 160)), fill=(120, 120, 126, 255)); d.rectangle((*P(x - 34, y + 170), *P(x + 6, y + 176)), fill=(120, 120, 126, 255))
        if phone == s_:
            x, y = hand[0] / S - 350, hand[1] / S
            rrect(x - 34, y - 96, x + 34, y + 22, 10, (16, 16, 22, 255))
            if not back: d.rounded_rectangle((*P(x - 27, y - 88), *P(x + 27, y + 12)), 6 * S, fill=(150, 190, 255, 255) if glow is None else glow)
        if bill and side == 1:
            x, y = hand[0] / S - 350, hand[1] / S
            rrect(x - 20, y - 20, x + 110, y + 44, 4, (120, 150, 200, 255) if not dark else (70, 90, 130, 255))
            if not dark: d.text(P(x + 26, y - 6), "20", fill=(240, 244, 252, 255), font_size=int(40 * S))
    if back:                                                          # seen from behind: arms first, then the big delivery bag over the torso
        hands = {s_: arm(s_, a) for s_, a in ((-1, armL), (1, armR))}
        rrect(-112 + lx, 418, 112 + lx, 690, 60, C["hood"])
        for s_ in (-1, 1): disc(hands[s_], 30, C["skin"]); props(s_, hands[s_])
        if pack:
            rrect(-132 + lx, 400, 132 + lx, 660, 26, C["cap"]); d.rectangle((*P(-132 + lx, 470), *P(132 + lx, 492)), fill=(230, 226, 250, 255) if not dark else (20, 20, 30, 255))
            if not dark:
                c = P(lx, 572); d.ellipse((c[0] - 42 * S, c[1] - 42 * S, c[0] + 42 * S, c[1] + 42 * S), fill=(244, 242, 252, 255)); d.ellipse((c[0] - 18 * S, c[1] - 50 * S, c[0] + 56 * S, c[1] + 24 * S), fill=C["cap"])
    else:
        if pack: rrect(-150 + lx, 410, 150 + lx, 650, 30, C["cap_d"])
        rrect(-112 + lx, 418, 112 + lx, 690, 60, C["hood"])
        d.rounded_rectangle((*P(-62 + lx, 590), *P(62 + lx, 656)), 14 * S, fill=C["hood_d"])                             # the hoodie pocket
        d.line([P(lx, 470), P(lx, 590)], fill=C["hood_d"], width=int(6 * S))
        if pack:
            for s_ in (-1, 1): d.line([P(s_ * 74 + lx, 420), P(s_ * 80 + lx, 600)], fill=C["cap"], width=int(22 * S))
        hands = {s_: arm(s_, a) for s_, a in ((-1, armL), (1, armR))}
        for s_ in (-1, 1): props(s_, hands[s_]); disc(hands[s_], 30, C["skin"])
    # head
    hx0, hy0 = lx * 1.25 + head[0] * 60, 268 + head[1] * 26; R = 156
    capsule(P(lx, 420), P(hx0 * 0.7 + lx * 0.3, 400), 70, C["skin_d"] if not back else C["hood"], outline=False)
    if not back: d.pieslice((*P(lx - 96, 380), *P(lx + 96, 470)), 180, 360, fill=C["hood_d"])                           # the hood collar
    disc(P(hx0, hy0), R, C["skin"])
    if back and not dark and not mum:                                   # seen from behind: short hair down to the nape
        HC = (30, 24, 22, 255) if samir else (62, 44, 34, 255); c = P(hx0, hy0)
        d.chord((c[0] - R * S, c[1] - R * S, c[0] + R * S, c[1] + R * S), -200, 20, fill=HC)
        d.ellipse((c[0] - R * S * 0.94, c[1] - R * S * 0.6, c[0] + R * S * 0.94, c[1] + R * S * 0.86), fill=HC)
    if not back and not dark:                                         # soft shading on the lower cheek
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh); c = P(hx0, hy0)
        sd.ellipse((c[0] - R * S, c[1] - R * S, c[0] + R * S, c[1] + R * S), fill=(190, 120, 90, 70)); sd.ellipse((c[0] - R * S * 1.15, c[1] - R * S * 1.35, c[0] + R * S * 0.9, c[1] + R * S * 0.72), fill=(0, 0, 0, 0))
        im.alpha_composite(sh); d = ImageDraw.Draw(im)
        for s_ in (-1, 1): d.ellipse((*P(hx0 + s_ * 96 - 26, hy0 + 44), *P(hx0 + s_ * 96 + 26, hy0 + 78)), fill=(243, 170, 150, 255))
    if mum:
        c = P(hx0, hy0); HAIR, HAIR_D = (140, 128, 124, 255), (110, 100, 98, 255)
        bc = P(hx0 + 40, hy0 - R - 18); d.ellipse((bc[0] - 62 * S - ow, bc[1] - 52 * S - ow, bc[0] + 62 * S + ow, bc[1] + 52 * S + ow), fill=C["ol"]); d.ellipse((bc[0] - 62 * S, bc[1] - 52 * S, bc[0] + 62 * S, bc[1] + 52 * S), fill=HAIR_D)
        outer = [(c[0] + (R + 8) * S * math.cos(math.radians(a_)), c[1] + (R + 8) * S * math.sin(math.radians(a_))) for a_ in range(158, 383, 5)]
        if back: inner = [(c[0] + R * S * 0.7 * math.cos(math.radians(a_)), c[1] + R * S * 0.2) for a_ in range(20, -200, -20)]
        else:
            inner = [(c[0] + R * S * 0.86, c[1] + R * S * 0.3), (c[0] + R * S * 0.78, c[1] - R * S * 0.1)]
            inner += [(c[0] + R * S * (0.62 - 1.24 * k / 8), c[1] - R * S * (0.42 + 0.06 * math.sin(k * 1.4))) for k in range(9)]       # the fringe
            inner += [(c[0] - R * S * 0.78, c[1] - R * S * 0.1), (c[0] - R * S * 0.86, c[1] + R * S * 0.3)]
        d.polygon(outer + inner, fill=HAIR, outline=C["ol"], width=int(ow))
        d.arc((c[0] - R * 0.6 * S, c[1] - (R + 4) * S, c[0] + R * 0.9 * S, c[1] - R * 0.1 * S), 200, 300, fill=HAIR_D, width=int(8 * S))
    if cap and samir:                                                 # Samir wears a knitted beanie, not the courier's cap
        c = P(hx0, hy0); top = P(0, hy0 - R - 46)[1]; cuff = P(0, hy0 - R * 0.32)[1]
        dome = (c[0] - (R + 6) * S, top, c[0] + (R + 6) * S, cuff + (R * 0.9) * S)
        d.pieslice((dome[0] - ow, dome[1] - ow, dome[2] + ow, dome[3]), 180, 360, fill=C["ol"]); d.pieslice(dome, 180, 360, fill=C["cap"])
        for k in range(-5, 6): x_ = c[0] + k * R * 0.17 * S; d.line([(x_, top + (R * 0.5 + abs(k) * 6) * S * 0.6), (x_, cuff - 8 * S)], fill=C["cap_d"], width=int(5 * S))   # knit ribs
        cb = (c[0] - (R + 12) * S, cuff - 42 * S, c[0] + (R + 12) * S, cuff + 10 * S)
        d.rounded_rectangle((cb[0] - ow, cb[1] - ow, cb[2] + ow, cb[3] + ow), 20 * S, fill=C["ol"]); d.rounded_rectangle(cb, 20 * S, fill=C["cap_d"])
        for k in range(-9, 10): x_ = c[0] + k * R * 0.105 * S; d.line([(x_, cb[1] + 6 * S), (x_, cb[3] - 6 * S)], fill=tuple(int(v * 0.8) for v in C["cap_d"][:3]) + (255,), width=int(4 * S))
        pp = (c[0] + 10 * S, top + 4 * S); r_ = 34 * S
        d.ellipse((pp[0] - r_ - ow, pp[1] - r_ - ow, pp[0] + r_ + ow, pp[1] + r_ + ow), fill=C["ol"]); d.ellipse((pp[0] - r_, pp[1] - r_, pp[0] + r_, pp[1] + r_), fill=(236, 236, 228, 255) if not dark else C["cap"])
    elif cap:
        c = P(hx0, hy0); top = hy0 - R - 4
        d.pieslice((c[0] - (R + 10) * S - ow, P(0, top)[1] - ow, c[0] + (R + 10) * S + ow, P(0, hy0 + R * 0.6)[1]), 180, 360, fill=C["ol"])
        d.pieslice((c[0] - (R + 10) * S, P(0, top)[1], c[0] + (R + 10) * S, P(0, hy0 + R * 0.6)[1] - ow), 180, 360, fill=C["cap"])
        yb = hy0 - R * 0.3
        if not back:
            vx = look[0] * 16; capsule(P(hx0 - 150 + vx, yb + 8), P(hx0 + 150 + vx, yb + 8), 26, C["cap_d"])            # the visor
            if not dark:
                mc = P(hx0, hy0 - R * 0.72); d.ellipse((mc[0] - 30 * S, mc[1] - 30 * S, mc[0] + 30 * S, mc[1] + 30 * S), fill=(248, 246, 255, 255)); d.ellipse((mc[0] - 12 * S, mc[1] - 36 * S, mc[0] + 42 * S, mc[1] + 18 * S), fill=C["cap"])
        else:
            capsule(P(hx0 - 110, yb + 6), P(hx0 + 110, yb + 6), 14, C["cap_d"], outline=False); rrect(hx0 - 30, yb - 6, hx0 + 30, yb + 22, 8, C["cap_d"], outline=False)
    if not back:
        ey = hy0 + 30; ex = 62; er = 44 * wide
        for s_ in (-1, 1):
            c = P(hx0 + s_ * ex + look[0] * 8, ey + look[1] * 5)
            if dark: continue
            if blink:
                d.arc((c[0] - er * S, c[1] - er * S * 0.5, c[0] + er * S, c[1] + er * S * 0.5), 20, 160, fill=C["ol"], width=int(9 * S)); continue
            d.ellipse((c[0] - er * S - ow * 0.45, c[1] - er * S - ow * 0.45, c[0] + er * S + ow * 0.45, c[1] + er * S + ow * 0.45), fill=C["ol"])
            d.ellipse((c[0] - er * S, c[1] - er * S, c[0] + er * S, c[1] + er * S), fill=(252, 252, 250, 255))
            pr = 19 if wide < 1.2 else 15; pc = (c[0] + look[0] * (er - pr - 4) * S, c[1] + look[1] * (er - pr - 4) * S)
            d.ellipse((pc[0] - pr * S, pc[1] - pr * S, pc[0] + pr * S, pc[1] + pr * S), fill=(24, 20, 34, 255)); d.ellipse((pc[0] - pr * S * 0.1, pc[1] - pr * S * 0.75, pc[0] + pr * S * 0.5, pc[1] - pr * S * 0.15), fill=(255, 255, 255, 255))
            by = ey - er - 22 - (10 if wide > 1.15 else 0)             # eyebrows: brow > 0 lifts the inner end (worry)
            d.line([P(hx0 + s_ * (ex - 34), by - brow * 30), P(hx0 + s_ * (ex + 38), by + brow * 14)], fill=C["ol"], width=int(12 * S))
        my = hy0 + 108; mx = hx0 + look[0] * 6
        if samir and not dark:                                        # the beard, under the mouth and along the jaw
            d.chord((*P(hx0 - R * 0.86, hy0 - R * 0.2), *P(hx0 + R * 0.86, hy0 + R * 1.02)), 18, 162, fill=(52, 38, 32, 255))
            d.ellipse((*P(mx - 46, my - 26), *P(mx + 46, my + 22)), fill=C["skin"])
        if dark: c0 = P(hx0, hy0); monster_face(d, c0[0], c0[1], R * S, look=look)
        elif mouth == "o": d.ellipse((*P(mx - 20, my - 22), *P(mx + 20, my + 22)), fill=(60, 24, 30, 255), outline=C["ol"], width=int(6 * S))
        elif mouth == "open": d.chord((*P(mx - 40, my - 44), *P(mx + 40, my + 30)), 0, 180, fill=(60, 24, 30, 255), outline=C["ol"], width=int(6 * S))
        elif mouth == "frown": d.arc((*P(mx - 36, my - 4), *P(mx + 36, my + 44)), 200, 340, fill=C["ol"], width=int(10 * S))
        elif mouth == "smile": d.arc((*P(mx - 36, my - 40), *P(mx + 36, my + 10)), 20, 160, fill=C["ol"], width=int(10 * S))
        elif mouth == "wavy": d.line([P(mx - 34, my), P(mx - 17, my - 9), P(mx, my), P(mx + 17, my + 9), P(mx + 34, my)], fill=C["ol"], width=int(9 * S), joint="curve")
        else: d.line([P(mx - 28, my), P(mx + 28, my)], fill=C["ol"], width=int(10 * S))
        if sweat and not dark:
            c = P(hx0 + 128, hy0 - 6); d.polygon([(c[0], c[1] - 34 * S), (c[0] - 15 * S, c[1]), (c[0] + 15 * S, c[1])], fill=(150, 205, 255, 255)); d.ellipse((c[0] - 15 * S, c[1] - 14 * S, c[0] + 15 * S, c[1] + 16 * S), fill=(150, 205, 255, 255))
    im = im.resize((Wc // 2, Hc // 2), Image.LANCZOS)
    if dark:                                                          # the faintest cold edge so the outline reads against a dark set
        a = im.getchannel("A"); edge = Image.eval(a.filter(ImageFilter.GaussianBlur(4)), lambda v: 0 if v > 235 or v < 20 else 90)
        im.alpha_composite(Image.merge("RGBA", (Image.new("L", im.size, 90), Image.new("L", im.size, 110), Image.new("L", im.size, 170), edge)))
    if crop_top: im = im.crop((0, 0, im.width, int(im.height * crop_top)))
    return im


def monster_face(d, cx, cy, R, style="face", seed=7, look=(0.0, 0.0), skin=None):
    """The double's face, drawn on a head of radius R centred at (cx, cy), in pixels.
    Almond eyes slanted down towards the nose, one a little bigger, with a pin-point pupil; a wide crescent grin whose
    corners climb into the cheeks, a dark-red mouth, two rows of uneven pointed teeth, and creases at the corners.
    style="paint": the same face painted on a wall (no pupils, white paint, teeth cut out of it)."""
    import random as _r
    rg = _r.Random(seed); WHITE = (244, 242, 236, 255); INK = (8, 8, 14, 255)
    def almond(ex, ey, w, h, tilt, scale):
        pts = []
        for k in range(40):
            a = 2 * math.pi * k / 40; x = math.cos(a) * w * scale; y = math.sin(a) * h * scale * (1.0 if math.sin(a) > 0 else 0.8)
            y += (abs(x) / (w * scale)) ** 2 * h * 0.25 * scale                                     # pointed corners
            ca, sa = math.cos(tilt), math.sin(tilt); pts.append((ex + x * ca - y * sa, ey + x * sa + y * ca))
        return pts
    for side, scale in ((-1, 1.08), (1, 0.94)):
        ex, ey = cx + side * R * 0.40, cy + R * 0.16; tilt = side * -0.32
        pts = almond(ex, ey, R * 0.22, R * 0.15, tilt, scale)
        d.polygon(pts, fill=WHITE)
        bg_ = (skin or INK) if style == "face" else None                         # a heavy brow cuts the top of the eye, lower at the nose: menace
        if bg_: d.polygon([(ex - side * R * 0.32, ey - R * 0.26), (ex + side * R * 0.30, ey - R * 0.26), (ex + side * R * 0.30, ey - R * 0.02), (ex - side * R * 0.32, ey - R * 0.16)], fill=bg_)
        if style == "face":
            px, py = ex + look[0] * R * 0.06, ey + look[1] * R * 0.04 + R * 0.01
            d.ellipse((px - R * 0.035, py - R * 0.035, px + R * 0.035, py + R * 0.035), fill=INK)
    hw, top, bot, corner = R * 0.74, cy + R * 0.50, cy + R * 0.92, cy + R * 0.30
    def curve(depth, lift_k):
        out = []
        for k in range(41):
            u = -1 + 2 * k / 40; x = cx + u * hw
            y = corner + (depth - corner) * (1 - u * u) ** 0.85 - lift_k * R * 0.06 * u ** 4
            out.append((x, y))
        return out
    lower, upper = curve(bot, 1.0), curve(top, 0.0)
    mouth = lower + upper[::-1]
    d.polygon(mouth, fill=(76, 10, 16, 255) if style == "face" else WHITE)
    def tooth_row(line, down, n):
        xs = [line[0][0] + (line[-1][0] - line[0][0]) * (0.1 + 0.8 * (k + 0.5) / n) for k in range(n)]
        for x in xs:
            j = min(range(len(line)), key=lambda q: abs(line[q][0] - x)); y = line[j][1]
            c_ = 1 - abs(x - cx) / hw; wdt = R * (0.06 + rg.uniform(-0.008, 0.008)) * (0.6 + 0.4 * c_); ln = R * rg.uniform(0.15, 0.21) * (0.45 + 0.55 * c_)
            tip = (x + rg.uniform(-0.01, 0.01) * R, y + ln if down else y - ln)
            d.polygon([(x - wdt, y), (x + wdt, y), tip], fill=WHITE if style == "face" else (44, 40, 44, 255))
    tooth_row(upper, True, 9); tooth_row(lower, False, 8)
    if style == "face":
        d.line(upper + [], fill=(20, 6, 10, 255), width=max(2, int(R * 0.025)))
        for side in (-1, 1):                                             # the creases where the grin folds into the cheeks
            x0, y0 = cx + side * hw, corner
            d.arc((x0 - R * 0.14 + side * R * 0.02, y0 - R * 0.16, x0 + R * 0.14 + side * R * 0.02, y0 + R * 0.12), 200 if side < 0 else -20, 290 if side < 0 else 70, fill=(90, 92, 120, 255), width=max(2, int(R * 0.03)))
    return mouth


def hand_out(w=700, dark=True, bill=True, reach=1.0):
    """An arm coming out of a doorway from the right edge: his sleeve, his hand, the same red bracelet, a 20 euro note."""
    S = 2; im = Image.new("RGBA", (w * S, 300 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x1 = w * S; x0 = x1 - int(reach * (w - 130)) * S; y = 150 * S
    d.line([(x1 + 40, y), (x0 + 90 * S, y)], fill=(60, 62, 90, 255), width=96 * S + 12); d.line([(x1 + 40, y), (x0 + 90 * S, y)], fill=(12, 12, 18, 255), width=96 * S)
    d.line([(x0 + 96 * S, y), (x0 + 108 * S, y)], fill=REDB, width=98 * S)
    d.ellipse((x0 + 4 * S, y - 52 * S, x0 + 108 * S, y + 52 * S), fill=(12, 12, 18, 255), outline=(60, 62, 90, 255), width=6)
    if bill:
        d.rounded_rectangle((x0 - 150 * S, y - 44 * S, x0 + 40 * S, y + 44 * S), 8 * S, fill=(96, 132, 196, 255), outline=(22, 18, 34, 255), width=10)
        d.ellipse((x0 - 90 * S, y - 26 * S, x0 - 38 * S, y + 26 * S), outline=(214, 226, 248, 255), width=6); d.text((x0 - 20 * S, y - 28 * S), "20", fill=(232, 240, 252, 255), font_size=52 * S)
        d.ellipse((x0 + 6 * S, y - 22 * S, x0 + 60 * S, y + 30 * S), fill=(12, 12, 18, 255))
    return im.resize((w, 300), Image.LANCZOS)


def rider(h=300, spin=0.0, up=0.0, light=True):
    """The courier on his scooter, from the side, riding to the right: seated, one hand on the bar, the box behind him.
    spin turns the wheels, up (0..1) lifts his face towards the building once he has stopped."""
    S = h / 470 * 2; im = Image.new("RGBA", (int(640 * S), int(470 * S)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); ow = 7 * S
    def P(x, y): return (x * S, y * S)
    def capsule(a, b, w, fill):
        d.line([P(*a), P(*b)], fill=OL, width=int(w * S + ow * 2)); r = (w * S + ow * 2) / 2
        for p in (P(*a), P(*b)): d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=OL)
        d.line([P(*a), P(*b)], fill=fill, width=int(w * S)); r = w * S / 2
        for p in (P(*a), P(*b)): d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)
    def rr(x0, y0, x1, y1, r, fill):
        d.rounded_rectangle((x0 * S - ow, y0 * S - ow, x1 * S + ow, y1 * S + ow), r * S + ow, fill=OL); d.rounded_rectangle((x0 * S, y0 * S, x1 * S, y1 * S), r * S, fill=fill)
    DK = (30, 30, 40, 255)
    capsule((470, 392), (432, 208), 16, DK)                                                     # the fork and the steering column
    for cx in (130, 480):                                                                        # wheels, with spokes that turn
        c = P(cx, 392); R = 62 * S
        d.ellipse((c[0] - R - ow, c[1] - R - ow, c[0] + R + ow, c[1] + R + ow), fill=OL); d.ellipse((c[0] - R, c[1] - R, c[0] + R, c[1] + R), fill=(26, 26, 32, 255)); d.ellipse((c[0] - R * 0.58, c[1] - R * 0.58, c[0] + R * 0.58, c[1] + R * 0.58), fill=(150, 152, 164, 255))
        for k in range(3):
            a_ = spin + k * math.pi / 3; d.line([(c[0] - math.cos(a_) * R * 0.56, c[1] - math.sin(a_) * R * 0.56), (c[0] + math.cos(a_) * R * 0.56, c[1] + math.sin(a_) * R * 0.56)], fill=(70, 72, 84, 255), width=int(7 * S))
        d.ellipse((c[0] - R * 0.16, c[1] - R * 0.16, c[0] + R * 0.16, c[1] + R * 0.16), fill=DK)
    rr(150, 350, 440, 378, 12, CAP_D)                                                            # the deck
    d.polygon([P(60, 372), P(70, 280), P(250, 268), P(290, 372)], fill=OL); d.polygon([P(70, 366), P(78, 288), P(246, 276), P(280, 366)], fill=CAP)      # the rear body
    rr(92, 252, 262, 276, 12, DK)                                                                # the seat
    d.polygon([P(428, 222), P(476, 240), P(492, 350), P(440, 350)], fill=OL); d.polygon([P(436, 232), P(469, 245), P(483, 343), P(447, 343)], fill=CAP)   # the front shield
    capsule((412, 200), (448, 196), 12, DK)                                                      # the handlebar
    if light: d.ellipse((*P(470, 236), *P(500, 268)), fill=(255, 240, 190, 255), outline=OL, width=int(4 * S))
    d.ellipse((*P(56, 300), *P(76, 322)), fill=(230, 40, 34, 255))
    rr(22, 118, 150, 250, 10, CAP); d.rectangle((*P(22, 150), *P(150, 164)), fill=(232, 228, 250, 255))                                                   # the delivery box
    c = P(86, 204); d.ellipse((c[0] - 26 * S, c[1] - 26 * S, c[0] + 26 * S, c[1] + 26 * S), fill=(246, 244, 255, 255)); d.ellipse((c[0] - 10 * S, c[1] - 32 * S, c[0] + 36 * S, c[1] + 14 * S), fill=CAP)
    capsule((206, 250), (318, 262), 50, PANTS); capsule((318, 262), (330, 344), 44, PANTS); capsule((322, 356), (366, 356), 30, SHOE)                     # thigh, shin, shoe on the deck
    capsule((206, 240), (244, 132), 84, HOOD)                                                    # the torso, leaning forward
    capsule((252, 140), (318, 196), 42, HOOD); capsule((318, 196), (404, 198), 38, HOOD)       # the arm to the bar
    capsule((396, 198), (400, 198), 40, REDB); c = P(418, 198); d.ellipse((c[0] - 22 * S - ow, c[1] - 22 * S - ow, c[0] + 22 * S + ow, c[1] + 22 * S + ow), fill=OL); d.ellipse((c[0] - 22 * S, c[1] - 22 * S, c[0] + 22 * S, c[1] + 22 * S), fill=SKIN)
    hx, hy, R = 268 - 10 * up, 66, 64                                                            # the head, in profile
    c = P(hx, hy); d.ellipse((c[0] - R * S - ow, c[1] - R * S - ow, c[0] + R * S + ow, c[1] + R * S + ow), fill=OL); d.ellipse((c[0] - R * S, c[1] - R * S, c[0] + R * S, c[1] + R * S), fill=SKIN)
    d.pieslice((c[0] - (R + 5) * S - ow, c[1] - (R + 6) * S - ow, c[0] + (R + 5) * S + ow, c[1] + R * 0.5 * S), 180, 360, fill=OL); d.pieslice((c[0] - (R + 5) * S, c[1] - (R + 6) * S, c[0] + (R + 5) * S, c[1] + R * 0.5 * S - ow), 180, 360, fill=CAP)
    vy = hy - 18 - 14 * up; capsule((hx + 30, hy - 18), (hx + 96, vy), 14, CAP_D)                # the visor
    ex, ey = hx + 30, hy + 10 - 8 * up; d.ellipse((*P(ex - 18, ey - 18), *P(ex + 18, ey + 18)), fill=(252, 252, 250, 255), outline=OL, width=int(4 * S)); d.ellipse((*P(ex + 3, ey - 9 - 5 * up), *P(ex + 17, ey + 5 - 5 * up)), fill=(24, 20, 34, 255))
    d.line([P(hx + 26, hy + 40), P(hx + 48, hy + 40 - 2 * up)], fill=OL, width=int(6 * S))
    return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)


if __name__ == "__main__":
    import sys
    poses = [dict(), dict(look=(0, 0.7), armR=(0.35, 2.1), phone="R", brow=0.5, mouth="frown", head=(0, 0.6)), dict(wide=1.3, brow=1, mouth="o", sweat=True, armL=(0.3, 1.9), armR=(0.3, 1.9), lean=-0.15),
             dict(legs=(0.45, -0.45), armL=(-0.3, 0.3), armR=(0.4, 0.5), bag="L", look=(0.6, 0)), dict(back=True, bag="R"), dict(dark=True), dict(dark=True, bill=True, armR=(1.2, 0.5)), dict(blink=True, mouth="smile")]
    sh = Image.new("RGB", (len(poses) * 380, 560), (44, 42, 66))
    for k, p in enumerate(poses): s = char(540, **p); sh.paste(s, (k * 380, 10), s)
    h = rider(300, 0.4, 0.0); sh.paste(h, (1150, 250), h); h = rider(300, 1.0, 1.0); sh.paste(h, (1560, 250), h)
    for k, a_ in enumerate((-0.9, -0.4, 0.0, 0.5, 0.9)): w_ = char(300, legs=(a_, -a_)); sh.paste(w_, (k * 180, 250), w_)
    sh.save(sys.argv[1], quality=90)
