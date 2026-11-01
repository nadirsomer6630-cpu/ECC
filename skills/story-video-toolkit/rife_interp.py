"""Frame interpolation with RIFE 4.9 (ONNX, CPU). usage: rife_interp.py <in_glob_dir> <out_dir> [factor]
Takes frames rendered every Nth frame and writes the full sequence (factor-1 new frames between each pair)."""
import glob, os, sys, time
import numpy as np, onnxruntime as ort
from PIL import Image
M = os.environ.get("RIFE_ONNX", "rife49_ensemble_True_scale_1_sim.onnx")  # from huggingface.co/yuvraj108c/rife-onnx
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession(M, so, providers=["CPUExecutionProvider"])


def load(p):
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32) / 255
    return a.transpose(2, 0, 1)[None]


def pad(x, m=64):
    h, w = x.shape[2:]; ph, pw = (m - h % m) % m, (m - w % m) % m
    return np.pad(x, ((0, 0), (0, 0), (0, ph), (0, pw)), mode="edge"), h, w


def mid(a, b, t):
    pa, h, w = pad(a); pb, _, _ = pad(b)
    out = sess.run(None, {"img0": pa, "img1": pb, "timestep": np.array([t], np.float32)})[0]
    return out[:, :3, :h, :w]


def save(x, p):
    Image.fromarray((np.clip(x[0].transpose(1, 2, 0), 0, 1) * 255 + 0.5).astype(np.uint8)).save(p)


if __name__ == "__main__":
    src = sorted(glob.glob(os.path.join(sys.argv[1], "*.png"))); out = sys.argv[2]
    f = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    os.makedirs(out, exist_ok=True); k = 1; t0 = time.time()
    prev = load(src[0])
    for i in range(len(src)):
        cur = prev
        save(cur, os.path.join(out, f"esc_{k:04d}.png")); k += 1
        if i + 1 < len(src):
            nxt = load(src[i + 1])
            for j in range(1, f):
                save(mid(cur, nxt, j / f), os.path.join(out, f"esc_{k:04d}.png")); k += 1
            prev = nxt
    print("frames", k - 1, "in", round(time.time() - t0, 1), "s")
