"""A night supermarket aisle for season 2 (caissier de nuit), as the reference creators do it: a real 3D set lit
like cinema (pools of cold light, deep black at the end), the characters added in 2D on top.

python3 -I supermarche.py out.png [cam] [samples]   cam: aisle (looking down the aisle) | low (low angle, ominous)"""
import sys, math, random
import bpy

OUT = sys.argv[1]; CAM = sys.argv[2] if len(sys.argv) > 2 else "aisle"; SAMPLES = int(sys.argv[3]) if len(sys.argv) > 3 else 32
random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(name, col, rough=0.6, emit=None, strength=0.0, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
    return m


def box(loc, size, m):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); o.data.materials.append(m); return o


FLOOR = mat("floor", (0.10, 0.11, 0.15), rough=0.16)
SHELF = mat("shelf", (0.20, 0.22, 0.28), rough=0.45, metal=0.5)
BACK = mat("back", (0.10, 0.12, 0.18), rough=0.8)
TAG = mat("tag", (0.9, 0.9, 0.86), rough=0.5)
TUBE = mat("tube", (1, 1, 1), emit=(0.70, 0.82, 1.0), strength=6.0)
TUBE_OFF = mat("tube_off", (0.2, 0.2, 0.22), rough=0.5)
CEIL = mat("ceil", (0.05, 0.05, 0.07), rough=0.9)
PROD = [mat(f"p{i}", c, rough=0.45) for i, c in enumerate([(0.62, 0.12, 0.10), (0.85, 0.62, 0.12), (0.18, 0.40, 0.22), (0.14, 0.24, 0.55),
                                                          (0.80, 0.78, 0.70), (0.55, 0.30, 0.55), (0.90, 0.45, 0.10), (0.25, 0.55, 0.60)])]

L = 24.0                                                       # aisle length (m), along -Y
box((0, -L / 2 + 2, -0.05), (6, L + 6, 0.1), FLOOR)
box((0, -L / 2 + 2, 3.2), (6, L + 6, 0.1), CEIL)
for side in (-1, 1):
    x0 = side * 1.25                                           # aisle 2.5 m wide
    box((x0 + side * 0.35, -L / 2 + 2, 1.1), (0.04, L, 2.2), BACK)
    for lv in range(5):
        z = 0.12 + lv * 0.46
        box((x0 + side * 0.05, -L / 2 + 2, z), (0.62, L, 0.03), SHELF)
        box((x0 - side * 0.25, -L / 2 + 2, z + 0.03), (0.02, L, 0.05), TAG)          # the price-tag rail
        y = 1.8
        while y > -L + 2:                                      # products, in facings of the same item
            w = random.choice((0.10, 0.14, 0.2, 0.26)); h = random.uniform(0.18, 0.36); m = random.choice(PROD)
            n = random.randint(2, 6)
            for k in range(n):
                if y - w < -L + 2: break
                if random.random() > 0.06:                     # a few gaps, a lived-in shop
                    box((x0 + side * 0.08, y - w / 2, z + 0.03 + h / 2), (0.36, w * 0.92, h), m)
                y -= w
            y -= 0.02
    for k in range(int(L / 0.9)):                              # uprights
        box((x0 - side * 0.27, 1.8 - k * 0.9 * 1.0 - 0.45, 1.1), (0.04, 0.03, 2.25), SHELF)
for k in range(7):                                             # ceiling tubes, some dead: the night shift
    y = 1.0 - k * 3.6; on = k in (0, 2, 6)
    box((0, y, 3.1), (0.12, 1.6, 0.05), TUBE if on else TUBE_OFF)
    if on:
        bpy.ops.object.light_add(type="AREA", location=(0, y, 3.0)); lt = bpy.context.object
        lt.data.shape = "RECTANGLE"; lt.data.size = 0.3; lt.data.size_y = 1.6; lt.data.energy = 70 if k > 0 else 90
        lt.data.color = (0.62, 0.74, 1.0)
bpy.ops.object.light_add(type="SPOT", location=(0.4, -9.5, 2.9)); sp = bpy.context.object  # one warm pool far away
sp.data.energy = 260; sp.data.spot_size = 0.7; sp.data.color = (1.0, 0.75, 0.45); sp.rotation_euler = (0, 0, 0)

w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.005, 0.01, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0

bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam
if CAM == "low":
    cam.location = (0.35, 3.2, 0.55); cam.rotation_euler = (math.radians(92), 0, math.radians(180 + 3)); cam.data.lens = 18
else:
    cam.location = (-0.15, 3.6, 1.55); cam.rotation_euler = (math.radians(86), 0, math.radians(180 - 2)); cam.data.lens = 22
cam.data.sensor_fit = "VERTICAL"

sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"; sc.view_settings.exposure = -0.8
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
print("ok", OUT)
