"""Automatic check of a finished episode against its script.
usage: HF_HOME=... python3 qa_episode.py <episode module, e.g. ei3> <video.mp4>

For every line of the script it cuts the final audio exactly on that line's own window (taken from the episode
timeline, so no clip ever starts or ends in the middle of a word), transcribes it, and scores it against the
script. It also checks duration, loudness and that every frame exists. Exit code 1 if anything needs a look."""
import difflib, importlib, os, re, subprocess, sys, unicodedata
import numpy as np

mod, video = sys.argv[1], sys.argv[2]
sys.argv = [mod + ".py", "/tmp/qa_unused.mp4"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
E = importlib.import_module(mod)

NUM = {"dix-huit": "18", "dix-sept": "17", "cinquante-neuf": "59", "onze": "11", "quatre": "4", "six": "6", "mille": "1000", "deux": "2", "quarante": "40"}


def norm(s):
    s = s.lower().replace("’", "'")
    for k, v in NUM.items(): s = s.replace(k, v)
    s = re.sub(r"(\d+)\s*h(eures?)?\s*(\d+)?", lambda m: m.group(1) + (m.group(3) or ""), s)         # 17h59 / 18 heures -> 1759 / 18
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", video, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
audio = np.frombuffer(raw, np.float32); sr = 16000
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")
order = sorted(E.line_t, key=lambda k: E.line_t[k]); bad = []
print(f"{'line':5s} {'start':>6s} {'score':>5s}  heard  |  script")
for n, k in enumerate(order):
    t0 = max(0.0, E.line_t[k] - 0.12)
    t1 = min(len(audio) / sr, E.line_t[k] + E.dur[k] + 0.2, (E.line_t[order[n + 1]] - 0.05) if n + 1 < len(order) else 1e9)
    clip = audio[int(t0 * sr):int(t1 * sr)]
    segs, _ = model.transcribe(clip, language="fr", initial_prompt="Samir, Kessler, Valmont, Inès, badge, portique.")
    heard = " ".join(s.text.strip() for s in segs)
    score = difflib.SequenceMatcher(None, norm(heard), norm(E.SCRIPT[k])).ratio()
    flag = "" if score >= 0.86 else "  <-- LISTEN"
    if flag: bad.append(k)
    print(f"{k:5s} {E.line_t[k]:6.2f} {score:5.2f}  {heard}  |  {E.SCRIPT[k]}{flag}")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout)
lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", video, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1]
frames = len([f for f in os.listdir(E.TMP) if f.startswith("f") and f.endswith(".jpg")])
print(f"\nduration {dur:.2f} s (timeline {E.D})   loudness {lufs} LUFS (target -13 to -14)   frames {frames}/{E.N}")
ok = not bad and abs(dur - E.D) < 0.2 and -15 < float(lufs) < -12 and frames == E.N
print("RESULT:", "all lines match" if not bad else f"listen to: {', '.join(bad)}", "| format ok" if ok or bad else "| CHECK duration/loudness/frames")
sys.exit(0 if ok else 1)
