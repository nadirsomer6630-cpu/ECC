"""Voices for LIVREUR DE NUIT, night 1. eleven_v3 with acting tags; each take is transcribed and scored against the
line; a line that scores under 0.9 is retried with another seed, then with eleven_multilingual_v2. Best take -> fin/."""
import json, urllib.request, urllib.error, subprocess, sys, re, difflib, unicodedata, shutil, os
S = "/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/elv8/"
V = {"narr": "GupDAaofQtpwvAknVJOn", "mere": "OCSReEsKi1h7oqlTe8e3"}
NUM = {"dix-huit": "18", "cinquante et une": "51", "cinquante": "50", "vingt-sept": "27", "vingt": "20", "soixante": "60", "treize": "13", "quatorze": "14", "deux": "2", "trois": "3", "un": "1"}
def norm(s):
    s = re.sub(r"\[[^\]]*\]", "", s).lower().replace("’", "'")
    for k, v in NUM.items(): s = re.sub(r"\b%s\b" % k, v, s)
    s = re.sub(r"(\d+)\s*h(eures?)?\s*(\d+)?", lambda m: m.group(1) + (m.group(3) or ""), s).replace("€", "euros").replace("premier", "1er").replace("deuxieme", "2e")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)
from faster_whisper import WhisperModel
import numpy as np
M = WhisperModel("small", device="cpu", compute_type="int8")
def heard(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    segs, _ = M.transcribe(np.frombuffer(raw, np.float32), language="fr", initial_prompt="Livreur, interphone, appli, pourboire, paillasson, minuterie.")
    return " ".join(s.text.strip() for s in segs)
def gen(k, who, t, model, seed):
    txt = t if model == "eleven_v3" else re.sub(r"\[[^\]]*\]\s*", "", t)
    b = {"text": txt, "model_id": model, "seed": seed, "language_code": "fr", "voice_settings": {"stability": 0.5} if model == "eleven_v3" else {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "speed": 1.0}}
    if model != "eleven_v3": b.pop("language_code")
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{V[who]}?output_format=mp3_44100_128", data=json.dumps(b).encode(), headers={"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    p = S + f"{k}_{model[-2:]}_{seed}"
    try: open(p + ".mp3", "wb").write(urllib.request.urlopen(r, timeout=180).read())
    except urllib.error.HTTPError as e: print(k, e.code, e.read()[:300], flush=True); return None
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", p + ".mp3", "-ac", "1", "-ar", "44100", p + ".wav"], check=True); return p + ".wav"
only = sys.argv[1:]; rep = {}
for k, who, t in json.load(open(S + "lines.json")):
    if only and k not in only: continue
    best = (0, None, "")
    for model, seed in (("eleven_v3", 13), ("eleven_v3", 26), ("eleven_v3", 39), ("eleven_multilingual_v2", 13), ("eleven_multilingual_v2", 26)):
        p = gen(k, who, t, model, seed)
        if not p: continue
        h = heard(p); sc = difflib.SequenceMatcher(None, norm(h), norm(t)).ratio(); d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
        if sc > best[0]: best = (sc, p, h, model, d)
        if sc >= 0.93: break
    if best[1]: shutil.copy(best[1], S + f"fin/{k}.wav")
    print(f"{k} {best[0]:.2f} {os.path.basename(best[1] or '-')} {best[4] if best[1] else 0:.1f}s | {best[2]}", flush=True)
