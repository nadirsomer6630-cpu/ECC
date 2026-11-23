"""Three shots rendered from seven-field specs, as written in references/prompts.md."""
import json
from PIL import Image
import scene5
sets = {"aisle": Image.open("s2/aisle.png").convert("RGBA").resize((1080, 1920))}
specs = [
    {"shot": "wide", "who": "toi", "pose": "phone", "expr": {"look": [0.4, -0.1]}, "light": 1.0, "text": "Ta mère t'écrit", "key": "mère", "boil": 1},
    {"shot": "close", "who": "toi", "expr": {"wide": 1.35, "brow": 1.0, "mouth_": "o", "look": [0.6, 0.0]}, "light": -0.5, "text": "Elle dort pourtant", "key": "dort", "boil": 2,
     "hud": ["Caissier de nuit", "Nuit 1", "/ 30", "Caisse 3", "02:17"]},
    {"shot": "far-threat", "who": "toi", "far": "maman", "text": "Elle est là", "key": "là", "boil": 3, "hud": ["Caissier de nuit", "Nuit 1", "/ 30", "Caisse 3", "02:18"]},
]
for s in specs:
    if "expr" in s and "look" in s["expr"]: s["expr"]["look"] = tuple(s["expr"]["look"])
ims = [scene5.render_shot(s, sets) for s in specs]
S = Image.new("RGB", (1620, 960))
for i, im in enumerate(ims): S.paste(im.resize((540, 960)), (i * 540, 0))
S.save("/home/user/prompts_plans_demo.jpg", quality=90); json.dump(specs, open("s2/shots_demo.json", "w"), ensure_ascii=False, indent=1); print("ok")
