"""The night supermarket's checkout, caisse 3 (season 2, caissier de nuit), in the same lighting as supermarche.py:
cold tubes with two dead, one warm lamp far away in aisle 7, deep black.

python3 -I caisse_set.py out_dir samples [--calonly]
Renders two cameras at 1296x2304 (1.2x, room for camera moves):
  front  : the customer's side looking at you behind the till (wall of cigarettes, CAISSE 3 sign, the glass door)
  comptoir : over your till looking out into the shop (belt, scanner, the customer's place, the aisle ends 5-8)
and writes <cam>_cal.json (where a 1.75 m person stands) and <cam>_pts.json (screen points of the props)."""
import sys, math, random, json
import bpy, mathutils
from bpy_extras.object_utils import world_to_camera_view

OUT = sys.argv[1].rstrip("/"); SAMPLES = int(sys.argv[2]); CAL_ONLY = "--calonly" in sys.argv
CAMS = [a.split("=")[1] for a in sys.argv if a.startswith("--cam=")] or ["front", "comptoir", "cctv3"]
random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
RX, RY = 1296, 2304
CROT = float([a.split("=")[1] for a in sys.argv if a.startswith("--crot=")][0]) if any(a.startswith("--crot=") for a in sys.argv) else 142.0


def mat(name, col, rough=0.6, emit=None, strength=0.0, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
    return m


BATCH = {}
def box(loc, size, m, rot=None, solo=False):
    """Props near the till are real objects (the foreground mask needs them); the thousands of products and
    shelves are batched into one mesh per material (adding objects one by one is quadratic in Blender)."""
    if solo or rot:
        bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object
        o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); o.data.materials.append(m)
        if rot: o.rotation_euler = rot
        return o
    b = BATCH.setdefault(m.name, ([], [], m)); n = len(b[0]); hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    b[0].extend((loc[0] + sx * hx, loc[1] + sy * hy, loc[2] + sz * hz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1))
    b[1].extend([(n, n + 1, n + 3, n + 2), (n + 4, n + 6, n + 7, n + 5), (n, n + 4, n + 5, n + 1), (n + 2, n + 3, n + 7, n + 6), (n, n + 2, n + 6, n + 4), (n + 1, n + 5, n + 7, n + 3)])


def flush():
    for name, (v, f, m) in BATCH.items():
        me = bpy.data.meshes.new("b_" + name); me.from_pydata(v, [], f); me.update(); me.materials.append(m)
        o = bpy.data.objects.new("b_" + name, me); sc.collection.objects.link(o)
    BATCH.clear()


def text(body, loc, size, m, rot=(math.radians(90), 0, 0), extrude=0.01):
    bpy.ops.object.text_add(location=loc, rotation=rot); o = bpy.context.object
    o.data.body = body; o.data.size = size; o.data.align_x = "CENTER"; o.data.align_y = "CENTER"; o.data.extrude = extrude
    o.data.materials.append(m); return o


FLOOR = mat("floor", (0.11, 0.12, 0.15), rough=0.18)
CEIL = mat("ceil", (0.05, 0.05, 0.07), rough=0.9)
WALL = mat("wall", (0.16, 0.17, 0.22), rough=0.8)
SHELF = mat("shelf", (0.20, 0.22, 0.28), rough=0.45, metal=0.5)
COUNTER = mat("counter", (0.30, 0.32, 0.38), rough=0.35, metal=0.2)
COUNTER_SIDE = mat("cside", (0.42, 0.10, 0.12), rough=0.5)                  # the chain's red, on the till's front
BELT = mat("belt", (0.03, 0.03, 0.035), rough=0.75)
STEEL = mat("steel", (0.55, 0.57, 0.62), rough=0.25, metal=1.0)
GLASS_SCAN = mat("scan", (0.02, 0.02, 0.02), rough=0.05, emit=(1.0, 0.08, 0.05), strength=0.6)
SCREEN = mat("screen", (0.0, 0.0, 0.0), rough=0.3, emit=(0.25, 0.75, 0.85), strength=1.2)
MONITOR = mat("monitor", (0.0, 0.0, 0.0), rough=0.3, emit=(0.55, 0.62, 0.60), strength=0.8)
BLACK = mat("black", (0.02, 0.02, 0.025), rough=0.5)
PAPER = mat("paper", (0.85, 0.85, 0.80), rough=0.7)
TUBE = mat("tube", (1, 1, 1), emit=(0.70, 0.82, 1.0), strength=6.0)
TUBE_OFF = mat("tube_off", (0.2, 0.2, 0.22), rough=0.5)
SIGN = mat("sign", (0.9, 0.9, 0.9), emit=(1.0, 0.95, 0.85), strength=2.2)
SIGN_NUM = mat("signnum", (0.05, 0.05, 0.08), rough=0.6)
NEON = mat("neon", (1, 0.2, 0.2), emit=(1.0, 0.12, 0.10), strength=9.0)
NIGHT = mat("night", (0.0, 0.0, 0.0), emit=(0.05, 0.09, 0.20), strength=0.6)
DOORFRAME = mat("dframe", (0.08, 0.08, 0.1), rough=0.4, metal=0.6)
PROD = [mat(f"p{i}", c, rough=0.45) for i, c in enumerate([(0.62, 0.12, 0.10), (0.85, 0.62, 0.12), (0.18, 0.40, 0.22), (0.14, 0.24, 0.55),
                                                          (0.80, 0.78, 0.70), (0.55, 0.30, 0.55), (0.90, 0.45, 0.10), (0.25, 0.55, 0.60)])]

# ---------------------------------------------------------------- the room: you are at y > 0, the shop at y < 0
box((0, -8, -0.05), (16, 26, 0.1), FLOOR)
box((0, -8, 3.4), (16, 26, 0.1), CEIL)
box((0, 2.6, 1.7), (16, 0.1, 3.4), WALL)                                     # the wall behind you

# the till: a counter along X, the belt on the customer's half, the scanner glass, the screen, the printer
box((0, 0.0, 0.45), (2.2, 0.9, 0.9), COUNTER_SIDE, solo=True)
box((0, 0.0, 0.915), (2.3, 0.95, 0.04), COUNTER, solo=True)
box((-0.45, -0.05, 0.945), (1.2, 0.6, 0.03), BELT, solo=True)                            # the belt, toward the customer's left
for xx in (-1.05, 0.15):
    box((xx, -0.05, 0.945), (0.06, 0.62, 0.05), STEEL, solo=True)
box((0.45, -0.05, 0.937), (0.42, 0.42, 0.012), GLASS_SCAN, solo=True)                    # the scanner glass, lit red
box((0.45, 0.22, 1.08), (0.42, 0.06, 0.28), BLACK, solo=True)                            # the scanner's tower
box((0.45, 0.19, 1.12), (0.30, 0.01, 0.12), GLASS_SCAN, solo=True)
box((0.85, 0.3, 1.25), (0.08, 0.08, 0.6), STEEL, solo=True)                             # the screen's arm
box((0.85, 0.27, 1.55), (0.42, 0.06, 0.30), BLACK, rot=(math.radians(-10), 0, math.radians(15)))
box((0.85, 0.238, 1.555), (0.36, 0.01, 0.24), SCREEN, rot=(math.radians(-10), 0, math.radians(15)))
box((0.78, -0.25, 1.0), (0.22, 0.26, 0.14), BLACK, solo=True)                            # the ticket printer
box((0.78, -0.375, 1.06), (0.16, 0.01, 0.01), PAPER, solo=True)
box((-0.85, 0.32, 1.0), (0.4, 0.26, 0.12), BLACK, solo=True)                             # the cash drawer's lid, your side
box((1.02, 0.15, 1.24), (0.04, 0.04, 0.6), STEEL, solo=True)                             # the lane light's pole and "3"
box((1.02, 0.15, 1.70), (0.30, 0.30, 0.30), SIGN, solo=True)
for s in (-1, 1):
    text("3", (1.02, 0.15 + s * 0.152, 1.70), 0.26, SIGN_NUM, rot=(math.radians(90), 0, math.radians(0 if s < 0 else 180)))
# the CCTV monitor, on a bracket above the till at your right: the grey screen we fill in 2D
box((-0.8, 0.62, 2.3), (0.62, 0.36, 0.42), BLACK, solo=True)
box((-0.8, 0.435, 2.3), (0.54, 0.01, 0.34), MONITOR, solo=True)
box((-0.8, 0.7, 2.7), (0.05, 0.05, 0.45), STEEL, solo=True)

# behind you: cigarettes and bottles, a CAISSE 3 lightbox, the glass door to the night with OUVERT 24/24
for lv in range(4):
    z = 1.05 + lv * 0.36
    box((-0.6, 2.42, z), (3.2, 0.3, 0.03), SHELF)
    x = -2.15
    while x < 0.95:
        w = random.choice((0.06, 0.08, 0.1)); h = random.uniform(0.14, 0.24); m = random.choice(PROD)
        for k in range(random.randint(3, 8)):
            if x > 0.95: break
            if random.random() > 0.08: box((x + w / 2, 2.40, z + 0.015 + h / 2), (w * 0.92, 0.22, h), m)
            x += w
        x += 0.02
box((-0.6, 2.5, 0.5), (3.2, 0.2, 1.0), WALL)
box((0.1, 2.52, 2.9), (1.4, 0.06, 0.34), SIGN)
text("CAISSE 3", (0.1, 2.485, 2.9), 0.2, SIGN_NUM, extrude=0.005)
box((1.95, 2.55, 1.2), (1.3, 0.04, 2.4), NIGHT)                               # the glass door, night behind it
for xx in (1.3, 2.6): box((xx, 2.52, 1.2), (0.06, 0.08, 2.4), DOORFRAME)
box((1.95, 2.52, 2.42), (1.36, 0.08, 0.06), DOORFRAME); box((1.95, 2.52, 1.0), (1.3, 0.06, 0.04), STEEL)
text("OUVERT 24/24", (1.95, 2.5, 2.1), 0.17, NEON, extrude=0.01)

# the shop: gondola ends 5, 6, 7, 8 opening onto the front aisle, aisle 7 straight ahead with its warm lamp
AISLE_X = {5: 3.9, 6: 1.3, 7: -1.3, 8: -3.9}
for k_ in range(5):
    gx = -5.2 + k_ * 2.6                                                      # gondolas between the aisles
    for lv in range(5):
        z = 0.12 + lv * 0.44
        box((gx, -10.5, z), (0.9, 14, 0.03), SHELF)
        y = -3.6
        while y > -17.3:
            w = random.choice((0.12, 0.18, 0.24)); h = random.uniform(0.18, 0.34); m = random.choice(PROD)
            for k in range(random.randint(2, 5)):
                if y - w < -17.3: break
                for s in (-1, 1):
                    if random.random() > 0.07: box((gx + s * 0.27, y - w / 2, z + 0.03 + h / 2), (0.34, w * 0.92, h), m)
                y -= w
            y -= 0.02
    box((gx, -10.5, 1.15), (0.06, 14, 2.3), WALL)
    box((gx, -3.45, 1.1), (0.95, 0.12, 2.2), SHELF)                           # the gondola's end panel
    for lv in range(4):                                                       # a promotion at the end
        box((gx, -3.33, 0.3 + lv * 0.45), (0.85, 0.12, 0.03), SHELF)
        for q in range(5): box((gx - 0.34 + q * 0.17, -3.3, 0.42 + lv * 0.45), (0.14, 0.12, 0.2), PROD[(k_ * 3 + q + lv) % len(PROD)])
for n_, x_ in AISLE_X.items():                                                # hanging aisle numbers
    box((x_, -3.6, 2.75), (0.7, 0.05, 0.42), SIGN)
    for s in (-1, 1):
        text(f"ALLÉE {n_}" if n_ != 7 else "ALLÉE 7", (x_, -3.6 + s * 0.03, 2.75), 0.13, SIGN_NUM, rot=(math.radians(90), 0, math.radians(0 if s < 0 else 180)))
    box((x_, -3.6, 3.1), (0.02, 0.02, 0.6), STEEL)
box((0, -18.2, 1.7), (16, 0.1, 3.4), WALL)

# light: tubes along the front of the shop, two dead; the lane light; the warm pool deep in aisle 7
for k, (x_, y_, on) in enumerate(((-2.6, -1.2, True), (0.0, -1.2, False), (2.6, -1.2, True), (0.0, 1.4, True), (-2.6, 1.4, False), (2.6, 1.4, True),
                                  (AISLE_X[5], -8, True), (AISLE_X[6], -8, False), (AISLE_X[7], -6, False), (AISLE_X[8], -8, True))):
    box((x_, y_, 3.3), (0.12 if y_ < -3 else 1.6, 1.6 if y_ < -3 else 0.12, 0.05), TUBE if on else TUBE_OFF)
    if on:
        bpy.ops.object.light_add(type="AREA", location=(x_, y_, 3.2)); lt = bpy.context.object
        lt.data.shape = "RECTANGLE"; lt.data.size = 1.6 if y_ > -3 else 0.3; lt.data.size_y = 0.3 if y_ > -3 else 1.6
        lt.data.energy = 85 if y_ > -3 else 60; lt.data.color = (0.62, 0.74, 1.0)
bpy.ops.object.light_add(type="SPOT", location=(AISLE_X[7], -11.5, 3.1)); sp = bpy.context.object
sp.data.energy = 320; sp.data.spot_size = 0.75; sp.data.color = (1.0, 0.72, 0.42); sp.data.shadow_soft_size = 0.05
box((AISLE_X[7], -11.5, 3.25), (0.36, 0.36, 0.18), BLACK)
bpy.ops.object.light_add(type="POINT", location=(1.02, 0.15, 1.7)); lp = bpy.context.object; lp.data.energy = 12; lp.data.color = (1.0, 0.9, 0.75)
bpy.ops.object.light_add(type="POINT", location=(0.45, -0.05, 1.0)); lr = bpy.context.object; lr.data.energy = 6; lr.data.color = (1.0, 0.1, 0.06)

flush()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.005, 0.01, 1)

sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = RX, RY; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"; sc.view_settings.exposure = -0.6

PTS = {"scanner": (0.45, -0.05, 0.94), "printer": (0.78, -0.38, 1.06), "belt": (-0.45, -0.05, 0.95), "monitor": (-0.8, 0.43, 2.3),
       "mon_tl": (-1.07, 0.43, 2.47), "mon_tr": (-0.53, 0.43, 2.47), "mon_bl": (-1.07, 0.43, 2.13), "mon_br": (-0.53, 0.43, 2.13),
       "sheet": (0.2, -0.47, 0.82), "lamp7": (AISLE_X[7], -11.5, 0.0), "aisle7": (AISLE_X[7], -3.6, 2.75), "lane3": (1.02, 0.15, 1.7),
       "door": (1.95, 2.55, 1.2), "cust": (0.0, -0.95, 0.0), "you": (0.0, 1.0, 0.0)}
for name in CAMS:
    bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.sensor_fit = "VERTICAL"
    if name == "front":
        cam.location = (0.3, -3.2, 1.6); cam.rotation_euler = (math.radians(88), 0, math.radians(2)); cam.data.lens = 22
    elif name == "cctv3":                                                    # the shop's camera high in the corner above the lane
        cam.location = (-2.4, -2.9, 3.15); cam.data.lens = 13
        cam.rotation_euler = (mathutils.Vector((-0.2, 0.1, 0.5)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    else:
        cam.location = (0.35, 1.3, 1.85); cam.rotation_euler = (math.radians(76), 0, math.radians(CROT)); cam.data.lens = 19
    bpy.context.view_layer.update()
    cal = []
    for yw in [2.0 - k * 0.25 for k in range(80)]:
        for xw in (-2.25, -1.5, -0.75, 0.0, 0.75, 1.5):
            f = world_to_camera_view(sc, cam, mathutils.Vector((xw, yw, 0.0))); h = world_to_camera_view(sc, cam, mathutils.Vector((xw, yw, 1.75)))
            if f.z > 0.3: cal.append(dict(x=xw, y=yw, fx=f.x * RX, fy=(1 - f.y) * RY, hx=h.x * RX, hy=(1 - h.y) * RY))
    json.dump(cal, open(f"{OUT}/{name}_cal.json", "w"))
    pts = {}
    for k, p in PTS.items():
        v = world_to_camera_view(sc, cam, mathutils.Vector(p)); pts[k] = (v.x * RX, (1 - v.y) * RY, v.z)
    json.dump(pts, open(f"{OUT}/{name}_pts.json", "w"))
    if not CAL_ONLY:
        sc.render.filepath = f"{OUT}/{name}.png"; bpy.ops.render.render(write_still=True)
    if "--fg" in sys.argv:
        # the till and its props as a mask: the 2D characters go between the set and this foreground
        keep = lambda o: not o.name.startswith("b_") and o.type in ("MESH", "FONT") and -0.62 < o.location.y < 0.66 and abs(o.location.x) < 2.0 and o.location.z < 2.7
        hidden = [o for o in sc.objects if o.type in ("MESH", "FONT") and not keep(o)]
        for o in hidden: o.hide_render = True
        sc.render.film_transparent = True; s0 = sc.cycles.samples; sc.cycles.samples = 2; sc.cycles.use_denoising = False
        sc.render.filepath = f"{OUT}/{name}_fg.png"; bpy.ops.render.render(write_still=True)
        for o in hidden: o.hide_render = False
        sc.render.film_transparent = False; sc.cycles.samples = s0; sc.cycles.use_denoising = True
    print("ok", name)
