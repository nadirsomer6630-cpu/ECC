import sys, os
names = sys.argv[1:]; sys.argv = ["nuit1.py", "/tmp/x.mp4"]; import nuit1 as N
from PIL import Image
ts = [eval(x, vars(N)) for x in names]; c = min(7, len(ts)); r = (len(ts) + c - 1) // c; sh = Image.new("RGB", (c * 360, r * 640))
for n, t in enumerate(ts): sh.paste(N.render(int(t * 30), t).resize((360, 640)), (n % c * 360, n // c * 640))
sh.save("qa4/p.jpg", quality=86); print("ok")
