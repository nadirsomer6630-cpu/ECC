"""Render a list of time spans of an episode in N independent processes (no multiprocessing pool, which hung twice).
usage: python3 slices.py <module> <k> <n> <spans>   renders the k-th of n interleaved slices of the frames in spans."""
import sys, os
mod, k, n, spans = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
sys.argv = [mod + ".py", "/tmp/unused.mp4"]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib; M = importlib.import_module(mod)
sp = [tuple(float(v) for v in r.split("-")) for r in spans.split(",")]
todo = [i for i in range(M.N) if any(a - 0.25 <= i * M.F <= b + 0.25 for a, b in sp)][k::n]
for i in todo: M.frame(i)
print("slice", k, "done", len(todo))
