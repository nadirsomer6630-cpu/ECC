"""Render the missing frames of nuit5 (k-th of n slices) and nothing else."""
import sys, os
k, n = int(sys.argv[1]), int(sys.argv[2]); sys.argv = ["nuit5.py", "/tmp/unused.mp4"]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nuit5 as M
miss = [i for i in range(M.N) if not os.path.exists(M.TMP + f"f{i:05d}.jpg") or os.path.getsize(M.TMP + f"f{i:05d}.jpg") < 1000][k::n]
for i in miss: M.frame(i)
print("fill", k, "done", len(miss))
