"""Three test frames of season 2 night 1 composed like the references: wide, close, the double far away."""
import sys, numpy as np
from PIL import Image, ImageFilter
import scene5, toon5
B = Image.open("s2/aisle.png").convert("RGBA").resize((1080, 1920))
HUD = ("Caissier de nuit", "Nuit 1", "/ 30", "Caisse 3", "02:14")
# 1. wide: the hero in the aisle, under the dead tube
im = B.copy(); scene5.place(im, scene5.figure5("toi", "stand", look=(0.3, -0.2), boil=1), 560, 1560, 1050)
scene5.hud(im, *HUD); im = scene5.vignette(im); scene5.caption(im, ["Tu", "es", "seul"], key="seul"); im.save("s2/f1.jpg", quality=92)
# 2. close: his face, the set blurred behind (depth of field by layers)
im = B.copy().filter(ImageFilter.GaussianBlur(14)); f = toon5.bust5("toi", wide=1.25, brow=0.8, look=(0.5, 0.0), light=-0.4, boil=2)
a = np.asarray(f).astype(np.float32); a[..., :3] *= np.array([0.84, 0.88, 1.0]); f = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
im.alpha_composite(f.resize((1180, 1180)), (-50, 560)); scene5.hud(im, *HUD); im = scene5.vignette(im, 0.6)
scene5.caption(im, ["Quelqu'un", "t'appelle"], key="appelle", y=1240); im.save("s2/f2.jpg", quality=92)
# 3. the double far down the aisle in the only warm pool, the hero in the foreground, from behind his shoulder
im = B.copy(); scene5.place(im, scene5.figure5("double", "stand", boil=3), 560, 1010, 300, tint=(1.0, 0.82, 0.62), shade=0.9)
fg = scene5.back5("toi", boil=3)
a = np.asarray(fg).astype(np.float32); a[..., :3] *= np.array([0.7, 0.74, 0.86]); fg = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
im.alpha_composite(fg.resize((1300, 1300)).filter(ImageFilter.GaussianBlur(2)), (-520, 900))
scene5.hud(im, *HUD); im = scene5.vignette(im, 0.6); scene5.caption(im, ["Au", "fond", "de", "l'allée"], key="fond"); im.save("s2/f3.jpg", quality=92)
print("ok")
