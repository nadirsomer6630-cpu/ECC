import re
S = "/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/"
src = open(S + "ei1sprsrc/samir.html").read()
# --- Samir, one night (or years?) later: stubble, dark circles, bloodshot eyes, worried brows, messy hair, open collar
t = src.replace('fill="#f5f2ec"', 'fill="#efd9d2"')
t = t.replace('<g class="brows">', '''<ellipse cx="163" cy="198" rx="24" ry="8" fill="#4a2a3a" opacity="0.45"/><ellipse cx="237" cy="198" rx="24" ry="8" fill="#4a2a3a" opacity="0.45"/>
      <path d="M150 182 L158 180 M245 183 L252 180" stroke="#c0393b" stroke-width="1.6" opacity="0.8"/>
      <g class="brows">''')
t = re.sub(r'<line x1="138" y1="148" x2="188" y2="148"[^>]*/>', '<line x1="140" y1="152" x2="186" y2="140" stroke="#1c1e22" stroke-width="7" stroke-linecap="round"/>', t)
t = re.sub(r'<line x1="212" y1="148" x2="262" y2="148"[^>]*/>', '<line x1="214" y1="140" x2="260" y2="152" stroke="#1c1e22" stroke-width="7" stroke-linecap="round"/>', t)
import random as _r
_rb = _r.Random(3)
def _in_beard(x, y):
    """Jaw, chin, cheeks and moustache area; the lips and the middle of the cheeks stay clear."""
    if ((x - 200) / 90) ** 2 + ((y - 172) / 96) ** 2 > 0.97: return False            # outside the face
    if abs(x - 200) < 24 and 229 < y < 247: return False                              # the lips
    jaw = y > 214 + 0.0035 * (x - 200) ** 2 * -1 + 22 * (abs(x - 200) / 90) ** 2 * -1 + 16 * (1 - abs(x - 200) / 90)
    side = abs(x - 200) > 62 and y > 176                                               # sideburns running down the cheeks
    mous = abs(x - 200) < 34 and 216 < y < 230
    return (y > 226 + 10 * (1 - abs(x - 200) / 90)) or side or mous
_hairs = []
for _ in range(2600):
    x, y = _rb.uniform(108, 292), _rb.uniform(170, 268)
    if not _in_beard(x, y): continue
    a_ = _rb.uniform(-0.5, 0.5) + (x - 200) / 160; L_ = _rb.uniform(2.2, 4.6)
    _hairs.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + L_ * a_:.1f}" y2="{y + L_:.1f}" stroke="#17100c" stroke-width="{_rb.uniform(0.7, 1.3):.2f}" stroke-linecap="round" opacity="{_rb.uniform(0.35, 0.8):.2f}"/>')
stub = ('<defs><clipPath id="facec"><circle cx="200" cy="170" r="95"/></clipPath><filter id="bsoft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5"/></filter></defs>'
        '<g clip-path="url(#facec)">'
        '<path d="M106 178 Q108 240 150 262 Q200 282 250 262 Q292 240 294 178 Q282 224 248 236 Q226 226 200 226 Q174 226 152 236 Q118 224 106 178Z" fill="#20140e" opacity="0.42" filter="url(#bsoft)"/>'   # the shadow of a two-day beard
        '<path d="M166 224 Q200 212 234 224 Q200 220 166 224Z" fill="#20140e" opacity="0.5" filter="url(#bsoft)"/>'
        + "".join(_hairs) + '</g>')
t = t.replace('<g class="mouth"', stub + '<g class="mouth"')
t = t.replace('<path d="M105 160 Q110 70 200 68 Q290 70 295 160 Q260 110 200 112 Q140 110 105 160Z" fill="#1e1a1a"/>',
              '<path d="M105 160 Q110 70 200 68 Q290 70 295 160 Q260 110 200 112 Q140 110 105 160Z" fill="#1e1a1a"/><path d="M150 84 L140 58 L168 78 L178 50 L196 74 L214 52 L222 78 L250 60 L246 88Z" fill="#1e1a1a"/><path d="M196 112 Q204 136 188 150" fill="none" stroke="#1e1a1a" stroke-width="7" stroke-linecap="round"/>')
t = t.replace('<path d="M178 262 L200 300 L170 290Z" fill="#f2f2f0"/><path d="M222 262 L200 300 L230 290Z" fill="#f2f2f0"/>',
              '<path d="M170 262 L200 318 L160 296Z" fill="#e4e0d6"/><path d="M230 262 L200 318 L240 296Z" fill="#e4e0d6"/><path d="M186 262 L200 312 L214 262Z" fill="#8a5a3c"/>')
t = t.replace('fill="#3b5b8c"', 'fill="#33507c"')    # the same shirt, a day darker
t = t.replace('<circle cx="208" cy="330" r="4.5" fill="#e8e8e8"/>', '<path d="M150 300 Q170 360 140 420" stroke="#00000033" stroke-width="5" fill="none"/>')
# details: the bead bracelet his daughter made, sweat on the forehead, the red Valmont strip on his badge, a crumpled sleeve
BR = '<g id="brac">' + "".join(f'<circle cx="{279 + k * 9}" cy="{499 + (k % 2) * 2}" r="5.5" fill="{c}" stroke="#00000055" stroke-width="1"/>' for k, c in enumerate(["#e94b5a", "#f6c443", "#ffffff", "#4aa3e8", "#ffffff", "#5fc27a"])) + '</g>'
t = t.replace('<circle cx="301" cy="532" r="24" fill="#8a5a3c"/></g>', '<circle cx="301" cy="532" r="24" fill="#8a5a3c"/>' + BR + '</g>')
t = t.replace('<g class="brows">', '<path d="M128 118 q-5 10 0 14 q5 -4 0 -14Z" fill="#cfe6ff" opacity="0.85"/><path d="M274 128 q-5 10 0 14 q5 -4 0 -14Z" fill="#cfe6ff" opacity="0.8"/><g class="brows">', 1)
t = t.replace('<rect x="185" y="398" width="30" height="40" rx="4" fill="#f4f4f2" stroke="#9a9a9a" stroke-width="2"/>', '<g transform="rotate(9 200 418)"><rect x="185" y="398" width="30" height="40" rx="4" fill="#f4f4f2" stroke="#9a9a9a" stroke-width="2"/><rect x="186" y="399" width="28" height="9" fill="#c81919"/><rect x="190" y="413" width="12" height="12" fill="#8a5a3c"/><rect x="205" y="415" width="7" height="2" fill="#777"/><rect x="205" y="420" width="7" height="2" fill="#777"/><rect x="190" y="430" width="20" height="2" fill="#777"/></g>')
t = t.replace('<rect x="276" y="496" width="50" height="18" rx="6" fill="#5a7cb0"/>', '<rect x="276" y="470" width="50" height="14" rx="6" fill="#5a7cb0"/><path d="M280 330 q20 30 0 60 M320 380 q-18 30 0 60" stroke="#00000030" stroke-width="4" fill="none"/>')
open(S + "ei2sprsrc/samir_tired.html", "w").write(t)
HEADSET = '<path d="M100 170 Q100 56 200 56 Q300 56 300 170" fill="none" stroke="#15161a" stroke-width="12"/><rect x="86" y="150" width="30" height="62" rx="12" fill="#15161a"/><rect x="284" y="150" width="30" height="62" rx="12" fill="#15161a"/><path d="M100 205 Q104 262 168 252" fill="none" stroke="#15161a" stroke-width="6"/><circle cx="170" cy="252" r="9" fill="#15161a"/><circle cx="101" cy="181" r="5" fill="#e23a3a"/>'
t = re.sub(r'<g id="brac">.*?</g>', '', t).replace('<g class="mouth"', HEADSET + '<g class="mouth"')
# --- anonymous employees of level -2: varied skin, hair, shirts; same tired face
V = [("w1", "#e2b994", "#3a2a1e", "#e6e6e4", False), ("w2", "#6b4228", "#141010", "#5d6470", False), ("w3", "#f0caa6", "#8a8a8a", "#2e3a52", True),
     ("w4", "#b98258", "#2a1a12", "#d8dde4", True), ("w5", "#c99872", "#5a3a22", "#4a4e56", False)]
for name, skin, hair, shirt, bun in V:
    w = t.replace("#8a5a3c", skin).replace("#1e1a1a", hair).replace("#33507c", shirt).replace("#e4e0d6", shirt)
    w = w.replace(stub, "")
    if bun: w = w.replace('<g class="eyes">', f'<circle cx="200" cy="66" r="34" fill="{hair}"/><path d="M104 150 Q96 230 120 260 L132 170Z" fill="{hair}"/><path d="M296 150 Q304 230 280 260 L268 170Z" fill="{hair}"/><g class="eyes">')
    open(S + f"ei2sprsrc/{name}.html", "w").write(w)

# --- Inès, 6: waiting outside under the street lamp with her drawing
g = src.replace("#3b5b8c", "#e88bb0").replace("#5a7cb0", "#f3b6cf").replace("#282c3c", "#8a5a3c").replace("#6b3e22", "#f4f4f4").replace("#2c4670", "#d06a96").replace("#335282", "#e88bb0")
g = g.replace('<path d="M176 280 L190 400 L210 400 L224 280" fill="none" stroke="#1e88a8" stroke-width="5"/>', "").replace('<rect x="185" y="398" width="30" height="40" rx="4" fill="#f4f4f2" stroke="#9a9a9a" stroke-width="2"/>', "").replace('<rect x="236" y="306" width="6" height="22" fill="#d4af37"/>', "")
g = g.replace('<g class="eyes">', '<circle cx="92" cy="120" r="36" fill="#1e1a1a"/><circle cx="308" cy="120" r="36" fill="#1e1a1a"/><circle cx="112" cy="136" r="9" fill="#e23a3a"/><circle cx="288" cy="136" r="9" fill="#e23a3a"/><g class="eyes">')
g = g.replace('<g class="head">', '<path d="M96 500 L304 500 L340 640 L60 640Z" fill="#e88bb0"/><rect x="262" y="500" width="110" height="140" rx="4" fill="#faf8f0" stroke="#bbb" stroke-width="2" transform="rotate(8 300 560)"/><path d="M285 540 l30 -24 l30 24 M290 540 v40 h50 v-40" stroke="#c0392b" stroke-width="4" fill="none" transform="rotate(8 300 560)"/><g class="head">')
open(S + "ei2sprsrc/ines.html", "w").write(g)
print("ok")
