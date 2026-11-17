"""Render the frames a stopped render left missing or truncated, then record the timeline signature."""
import sys, os, json
sys.argv = ["nuit1.py", "/tmp/x.mp4"]; import nuit1 as N
from PIL import Image
from multiprocessing import Pool
def bad(i):
    p = N.TMP + f"f{i:05d}.jpg"
    if not os.path.exists(p) or os.path.getsize(p) < 5000: return True
    try: Image.open(p).load(); return False
    except Exception: return True
if __name__ == "__main__":
    with Pool(4) as pool: flags = pool.map(bad, range(N.N), chunksize=50)
    todo = [i for i, b in enumerate(flags) if b]; print("to render", len(todo), todo[:5], todo[-3:])
    with Pool(4) as pool: pool.map(N.frame, todo, chunksize=4)
    open(N.TMP + "timeline.sig", "w").write(json.dumps(sorted(N.line_t.items()))); print("filled")
