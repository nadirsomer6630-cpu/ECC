"""Animation curves for the 2D characters, after the keyframe and graph-editor principles of Blender animation:
nothing moves linearly, a move is prepared (anticipation), overshoots and settles, holds give it weight, and loose
parts (a lock of hair, a pompom) follow late (follow-through). All functions take a time t in seconds."""
import math

def clamp(x): return max(0.0, min(1.0, x))
def ease_in_out(u): u = clamp(u); return u * u * (3 - 2 * u)
def ease_out(u): u = clamp(u); return 1 - (1 - u) ** 3
def back_out(u, k=1.7):                                    # overshoot past the target, then settle
    u = clamp(u) - 1; return 1 + u * u * ((k + 1) * u + k)
def anticipate(u, k=0.18):                                 # a small move the other way before the real one
    u = clamp(u); return -k * math.sin(math.pi * u / 0.3) if u < 0.3 else ease_out((u - 0.3) / 0.7)

def keys(t, kf):
    """Piecewise animation: kf = [(time, value, curve), ...]; the curve shapes the move that ends at that key."""
    if t <= kf[0][0]: return kf[0][1]
    for (t0, v0, _), (t1, v1, c) in zip(kf, kf[1:]):
        if t <= t1: return v0 + (v1 - v0) * c((t - t0) / max(1e-6, t1 - t0))
    return kf[-1][1]

def follow(t, driver, delay=0.08, freq=3.2, damp=4.0, dt=1 / 60):
    """Follow-through: a loose part that lags behind a driver curve and swings past it like a damped spring."""
    x, v, tt = driver(0.0), 0.0, 0.0
    while tt < t:
        target = driver(max(0.0, tt - delay)); a = (2 * math.pi * freq) ** 2 * (target - x) - 2 * damp * v
        v += a * dt; x += v * dt; tt += dt
    return x
