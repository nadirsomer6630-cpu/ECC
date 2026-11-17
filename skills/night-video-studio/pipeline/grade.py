"""Colour grading + exposure for L'ASCENSEUR, two looks:
  present  - 'Noir & Rouge': black and white, only true reds kept, filmic contrast, bloom, grain
  tape     - 'Cassette de surveillance': green mono, barrel lens, scanlines, rolling tracking noise, REC overlay
Also builds the style demo: present shot -> tape rewind -> the same place 6 years earlier.
usage: grade.py demo <frames_dir> <out.mp4>"""
import glob, json, os, subprocess, sys, wave
import numpy as np
import soundfile as sf
from math import gcd
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.signal import resample_poly, butter, sosfiltfilt

W, H, FPS, VSR = 1080, 1920, 30, 44100
FP = "/tmp/claude-0/-home-user/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/fontpkg/"
NEW = "/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/"
MONT = FP + "mont900.woff"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
NX, NY = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
RR = NX ** 2 + NY ** 2
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def load(path):
    return np.asarray(Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32) / 255


def blur(a, r):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255


def filmic(x, contrast=1.2, pivot=0.42):
    """Soft S-curve around a pivot with a highlight shoulder (no hard clipping)."""
    y = pivot * (x / pivot) ** contrast
    hi = x > pivot
    y[hi] = 1 - (1 - pivot) * ((1 - x[hi]) / (1 - pivot)) ** contrast
    return np.clip(y, 0, 1)


def exposure(a, stops):
    return a * (2.0 ** stops)


def haze(a, strength=0.5):
    """2D volumetric look: soft haze plus light rays streaming from the brightest area (replaces 3D fog)."""
    lum = a @ LUMA
    small = blur(np.stack([lum] * 3, -1), 40)[..., 0]
    cy, cx = np.unravel_index(np.argmax(small), small.shape)
    src = np.clip(a - 0.45, 0, 1)
    im = Image.fromarray((np.clip(src, 0, 1) * 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    acc = np.zeros((H // 4, W // 4, 3), np.float32); ccx, ccy = cx / 4, cy / 4
    for k in range(10):                         # radial zoom blur around the light
        s_ = 1 + k * 0.045
        z = im.resize((int(W / 4 * s_), int(H / 4 * s_)), Image.BILINEAR)
        ox, oy = int(ccx * s_ - ccx), int(ccy * s_ - ccy)
        acc += np.asarray(z.crop((ox, oy, ox + W // 4, oy + H // 4))).astype(np.float32) / 255 * (1 - k / 10)
    rays = np.asarray(Image.fromarray((np.clip(acc / 4, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    mist = blur(np.clip(a, 0, 1), 60) * 0.35
    return a + rays * strength + mist * strength * 0.6


def grade_present(a, t, exp=0.15, contrast=1.28, bloom=0.22, grain=0.03, seed=0):
    a = haze(exposure(a, exp))
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = np.clip(((r - np.maximum(g, b)) / np.maximum(r, 1e-3) - 0.55) * 5, 0, 1) * (r > 0.08)
    lum = filmic(np.clip(a @ LUMA, 0, 1), contrast)
    lum = 0.02 + lum * 0.97                                   # lifted blacks, film-like
    mono = np.stack([lum, lum, lum * 1.02], -1)               # a hair of cold in the shadows
    reds = np.stack([np.clip(r * 1.7, 0, 1), g * 0.12, b * 0.12], -1)
    out = mono * (1 - red[..., None]) + reds * red[..., None]
    hl = np.clip(out - 0.62, 0, 1)                             # bloom from highlights only
    out = out + blur(hl, 26) * bloom * 2.2
    out *= np.clip(1.18 - RR * 0.42, 0.2, 1)[..., None]       # lens vignette
    ca = 2                                                     # faint chromatic fringe at the edges
    out[..., 0] = out[..., 0] * (1 - RR * 0.15) + np.roll(out[..., 0], ca, 1) * RR * 0.15
    rng = np.random.default_rng(seed)
    out += (rng.normal(0, grain, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1))
    return np.clip(out, 0, 1)


def grade_tape(a, t, seed=0, exp=0.35, tear=0.0):
    rng = np.random.default_rng(seed)
    a = haze(exposure(a, exp), 0.35)
    k = 0.12                                                  # barrel lens
    sx = np.clip((W / 2 + NX * (1 - k * RR) * W / 2).astype(int), 0, W - 1)
    sy = np.clip((H / 2 + NY * (1 - k * RR) * H / 2).astype(int), 0, H - 1)
    a = a[sy, sx]
    lum = filmic(np.clip(a @ LUMA, 0, 1), 1.1) * 1.1
    out = np.stack([lum * 0.84, lum, lum * 0.87], -1)
    out[::4] *= 0.74                                          # scanlines
    band_y = int((t * 420) % (H + 200)) - 100                 # rolling tracking band
    bs = slice(max(0, band_y), min(H, band_y + 46))
    out[bs] = np.roll(out[bs], int(rng.integers(12, 40)), 1) * 1.15
    if tear > 0:                                              # rewind: horizontal tears everywhere
        for _ in range(int(14 * tear)):
            y0 = int(rng.integers(0, H - 30)); hh = int(rng.integers(4, 30))
            out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], int(rng.integers(-160, 160)), 1)
            out[y0:y0 + 2] = 0.9
    out[..., 0] = np.maximum(out[..., 0], np.roll(out[..., 0], 6, 1) * 0.5)
    out = blur(out, 0.9)
    out *= np.clip(1.3 - RR * 0.6, 0.2, 1)[..., None]
    out += rng.normal(0, 0.05, (H, W, 1))
    return np.clip(out, 0, 1)


def tape_overlay(im, t, date="31.10.2020", start=(3, 13, 13), rew=False, cam="CAM 13 · ESCALIER B"):
    d = ImageDraw.Draw(im); fm = ImageFont.truetype(MONO, 40); fs = ImageFont.truetype(MONO, 34)
    if rew:
        d.text((130, 236), "◀◀ REW", font=fm, fill=(240, 240, 240))
    elif int(t * 2) % 2 == 0:
        d.ellipse((130, 240, 160, 270), fill=(230, 20, 20)); d.text((175, 236), "REC", font=fm, fill=(240, 240, 240))
    d.text((130, 300), cam, font=fs, fill=(230, 230, 230))
    s = start[0] * 3600 + start[1] * 60 + start[2] + int(t)
    d.text((130, 1360), date, font=fs, fill=(230, 230, 230))
    d.text((130, 1405), f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}", font=fm, fill=(230, 230, 230))
    for (x0, y0) in ((110, 220), (930, 220), (110, 1460), (930, 1460)):
        dx = 1 if x0 < 500 else -1; dy = 1 if y0 < 500 else -1
        d.line((x0, y0, x0 + 40 * dx, y0), fill=(220, 220, 220), width=4); d.line((x0, y0, x0, y0 + 40 * dy), fill=(220, 220, 220), width=4)


def present_overlay(im):
    d = ImageDraw.Draw(im); fs = ImageFont.truetype(MONT, 30)
    d.text((124, 236), "L'ASCENSEUR", font=fs, fill=(235, 235, 235)); d.text((124, 276), "ÉTAGE -13", font=fs, fill=(225, 30, 30))


def karaoke(im, words, t, style, hl=(225, 30, 30), box=False, y0=None, size0=84, stroke=8):
    """Readable captions: whole phrase chunks (up to 4 words or a comma) shown in full from the start,
    the spoken word highlighted; a chunk stays until the next one so there is no flicker."""
    clean = []
    for w in words:                       # tidy tokens: no stray leading punctuation, "-toi" stays glued to "Abonne"
        w = dict(w, w=w["w"].lstrip(",.;: "))
        if not w["w"]: continue
        if clean and w["w"].startswith("-") and clean[-1].get("line") == w.get("line"):
            clean[-1] = dict(clean[-1], w=clean[-1]["w"] + w["w"], e=w["e"]); continue
        clean.append(w)
    groups, cur = [], []
    for w in clean:
        cur.append(w)
        if len(cur) == 3 or w["w"].endswith((".", ",", "…", "?", ":")):
            groups.append(cur); cur = []
    if cur: groups.append(cur)
    g = None
    for n, gr in enumerate(groups):
        end = groups[n + 1][0]["s"] - 0.05 if n + 1 < len(groups) and groups[n + 1][0].get("line") == gr[-1].get("line") else gr[-1]["e"] + 0.6
        if gr[0]["s"] - 0.12 <= t < end: g = gr
    if not g: return
    d = ImageDraw.Draw(im)
    if style == "present":
        txt = [x["w"].upper() for x in g]; size = size0
        while size > 48 and d.textlength(" ".join(txt), font=ImageFont.truetype(MONT, size)) > 760: size -= 4
        f = ImageFont.truetype(MONT, size); y = y0 or 1200
        widths = [d.textlength(x + " ", font=f) for x in txt]
        x = W / 2 - (sum(widths) - d.textlength(" ", font=f)) / 2
        for wd, x_w, wi in zip(g, txt, widths):
            if t < wd["s"] - 0.04:          # a word appears only when it is spoken: the text never runs ahead of the voice
                x += wi; continue
            now = wd["s"] - 0.04 <= t <= wd["e"] + 0.08
            age = t - (wd["s"] - 0.04); yy0 = y; y = y + int(14 * max(0.0, 1 - age / 0.09))     # word rises into place
            if box and now:   # the spoken word sits in a coloured box (keyword-box captions)
                tw_ = d.textlength(x_w, font=f); d.rectangle((x - 10, y - size * 0.82, x + tw_ + 10, y + size * 0.16), fill=hl)
                d.text((x, y), x_w, font=f, fill=(15, 15, 15), anchor="ls")
            else:
                col = hl if now else (255, 255, 255)
                d.text((x, y), x_w, font=f, fill=col, anchor="ls", stroke_width=stroke, stroke_fill=(0, 0, 0))
            y = yy0; x += wi
    else:
        full = " ".join(x["w"].upper() for x in g); size = 58
        while size > 34 and d.textlength(full, font=ImageFont.truetype(MONO, size)) > 780: size -= 4
        f = ImageFont.truetype(MONO, size); y = 1150
        wdt = d.textlength(full, font=f)
        shown = " ".join(x["w"].upper() for x in g if t >= x["s"] - 0.04)
        if shown:
            d.rectangle((W / 2 - wdt / 2 - 16, y - 8, W / 2 - wdt / 2 + d.textlength(shown, font=f) + 16, y + size + 12), fill=(0, 0, 0))
            d.text((W / 2 - wdt / 2, y), shown, font=f, fill=(240, 240, 240))


def word_times(wav_path, offset, script=None):
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", wav_path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(np.frombuffer(raw, np.float32), language="fr", word_timestamps=True)
    ws = []
    for w in (w for s in segs for w in s.words):
        t = w.word.strip()
        if ws and (t.startswith("'") or t.startswith("’")):     # "quelqu" + "'un" -> one word
            ws[-1]["w"] += t; ws[-1]["e"] = w.end + offset
        else:
            ws.append({"w": t, "s": w.start + offset, "e": w.end + offset})
    if script:                                                   # spelling from the script, timing from whisper
        sw = script.split()
        if len(sw) == len(ws):
            for x, t in zip(ws, sw): x["w"] = t
        else:
            print("word count mismatch", len(sw), len(ws), [x["w"] for x in ws])
    return ws


def voice(path, lp=9000):
    a, sr = sf.read(path); a = a.astype(np.float64)
    env = np.convolve(np.abs(a), np.ones(int(0.02 * sr)) / int(0.02 * sr), "same"); idx = np.where(env > 0.006)[0]
    a = a[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.25 * sr)]
    g = gcd(int(sr), VSR); a = resample_poly(a, VSR // g, int(sr) // g)
    a = sosfiltfilt(butter(2, 70, btype="high", fs=VSR, output="sos"), a)
    # no dynamic de-esser (its fast gain changes made the voice gritty): a smooth roll-off of the synthetic hiss instead
    if lp: a = sosfiltfilt(butter(2, lp, btype="low", fs=VSR, output="sos"), a)
    a = a / (np.sqrt((a ** 2).mean()) + 1e-9) * 0.12
    fi, fo = int(0.01 * VSR), int(0.12 * VSR)                                     # no click at either end
    a[:fi] *= np.linspace(0, 1, fi); a[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    return a


def demo(frames_dir, out):
    frames = sorted(glob.glob(frames_dir + "/esc_*.png"))
    n = len(frames)
    T_A, T_REW, T_B = n / FPS, 0.6, n / FPS
    D = T_A + T_REW + T_B
    va, vb = voice(NEW + "demo/a_pick.wav"), voice(NEW + "demo/b_pick.wav")
    VA0, VB0 = 0.35, T_A + T_REW + 0.3
    tmp = NEW + "demo/tmp/"; os.makedirs(tmp, exist_ok=True)
    for f in glob.glob(tmp + "*"): os.remove(f)
    sf.write(tmp + "va.wav", va, VSR); sf.write(tmp + "vb.wav", vb, VSR)
    words = (word_times(tmp + "va.wav", VA0, "Dans cet immeuble, treize personnes ont disparu.")
             + word_times(tmp + "vb.wav", VB0, "Il y a six ans… quelqu'un attendait déjà."))
    json.dump(words, open(NEW + "demo/words.json", "w"), ensure_ascii=False, indent=0)
    # brightness per frame drives the electrical buzz when the light drops
    bright = [float(load(f).mean()) for f in frames]
    k = 0
    for i, f in enumerate(frames):                                # 1. present, Noir & Rouge
        t = i / FPS
        im = Image.fromarray((grade_present(load(f), t, seed=i) * 255).astype(np.uint8))
        present_overlay(im); karaoke(im, words, t, "present"); im.save(tmp + f"f{k:05d}.png"); k += 1
    nrew = int(T_REW * FPS)                                       # 2. the tape rewinds
    for j in range(nrew):
        src = frames[int((n - 1) * (1 - j / (nrew - 1)))]; t = T_A + j / FPS
        im = Image.fromarray((grade_tape(load(src), t, seed=1000 + j, tear=1.0) * 255).astype(np.uint8))
        tape_overlay(im, t, rew=True); im.save(tmp + f"f{k:05d}.png"); k += 1
    for i, f in enumerate(frames):                                # 3. six years earlier, surveillance tape
        t = T_A + T_REW + i / FPS
        im = Image.fromarray((grade_tape(load(f), t, seed=2000 + i) * 255).astype(np.uint8))
        tape_overlay(im, i / FPS); karaoke(im, words, t, "tape"); im.save(tmp + f"f{k:05d}.png"); k += 1
    # sound: drone, footsteps on the stairs, buzz on light drops, rewind whirr, tape hiss
    N = int(D * VSR) + VSR; ts = np.arange(N) / VSR; mix = np.zeros(N)
    def add(s, at, g=1.0):
        i0 = int(at * VSR); j0 = min(N, i0 + len(s)); mix[i0:j0] += s[: j0 - i0] * g
    mix += (np.sin(2 * np.pi * 49 * ts) + 0.5 * np.sin(2 * np.pi * 73.4 * ts)) * 0.05
    rng = np.random.default_rng(1)
    for st in np.arange(0.2, T_A, 0.55):
        x = np.arange(int(0.09 * VSR)) / VSR
        add(np.convolve(rng.standard_normal(len(x)), np.ones(4) / 4, "same") * np.exp(-x * 40) * 0.5 + np.sin(2 * np.pi * 75 * x) * np.exp(-x * 30), st, 0.35)
    for i in range(1, n):
        if bright[i] < bright[i - 1] * 0.7:
            x = np.arange(int(0.12 * VSR)) / VSR
            add(np.sign(np.sin(2 * np.pi * 120 * x)) * (rng.random(len(x)) > 0.3) * np.exp(-x * 12) * 0.25, i / FPS)
            add(np.sign(np.sin(2 * np.pi * 120 * x)) * (rng.random(len(x)) > 0.3) * np.exp(-x * 12) * 0.25, T_A + T_REW + i / FPS)
    x = np.arange(int(T_REW * VSR)) / VSR
    add(np.sin(2 * np.pi * np.cumsum(300 + 1400 * x / T_REW) / VSR) * 0.25 + rng.standard_normal(len(x)) * 0.08, T_A)
    hiss = rng.standard_normal(N) * 0.015 * (ts > T_A)
    mix += hiss
    add(va, VA0, 1.0); add(vb, VB0, 1.0)
    mix = mix[: int(D * VSR)]; mix *= np.clip((D - ts[: len(mix)]) / 0.3, 0, 1)
    sf.write(tmp + "mix.wav", mix / np.abs(mix).max() * 0.9, VSR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", tmp + "f%05d.png", "-i", tmp + "mix.wav",
                    "-c:v", "libx264", "-crf", "20", "-maxrate", "14M", "-bufsize", "28M", "-preset", "slow", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("ok", out, round(D, 2), "s", len(words), "words")


if __name__ == "__main__":
    if sys.argv[1] == "demo":
        demo(sys.argv[2], sys.argv[3])
