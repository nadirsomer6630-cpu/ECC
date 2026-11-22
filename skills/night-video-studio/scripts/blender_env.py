"""L'ASCENSEUR environment kit: textured 3D sets with fog, hard shadows and black silhouettes.
usage: python blender_env.py <scene: interphone|escalier|duval> <out_prefix> [frames] [only_frame] [samples]"""
import math, random, sys
import bpy

SCENE = sys.argv[1]
OUT = sys.argv[2]
FRAMES = int(sys.argv[3]) if len(sys.argv) > 3 else 72
ONLY = int(sys.argv[4]) if len(sys.argv) > 4 else 0
SAMPLES = int(sys.argv[5]) if len(sys.argv) > 5 else 16
EYES = "--eyes" in sys.argv
TEX = "/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/tex/"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, FRAMES
sc.render.fps = 30 if "--fps30" in sys.argv else 24
REAL = "--real" in sys.argv
if REAL:   # camera realism: motion blur on every moving thing
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
sc.render.resolution_x, sc.render.resolution_y = (1080, 1920) if "--hires" in sys.argv else (720, 1280)
ARG = lambda k, d=None: next((a.split("=", 1)[1] for a in sys.argv if a.startswith(k + "=")), d)
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4
sc.cycles.volume_step_rate = 4.0
sc.cycles.volume_max_steps = 64
if "--guide" in sys.argv:   # Intel path guiding (CPU): cleaner indirect light per sample in dark scenes
    sc.cycles.use_guiding = True; sc.cycles.use_surface_guiding = True
    sc.cycles.denoising_prefilter = "ACCURATE"
    try: sc.cycles.denoising_quality = "HIGH"
    except Exception: pass
if "--half" in sys.argv:   # render every other frame, the in-betweens are motion-interpolated afterwards
    sc.frame_step = 2
if "--fast" in sys.argv:   # speed: keep scene data between frames, adaptive sampling, fog added later in 2D
    sc.render.use_persistent_data = True
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.05
    sc.cycles.max_bounces = 3; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 1; sc.cycles.transparent_max_bounces = 2
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
if "--eevee" in sys.argv:   # real-time engine: seconds per frame instead of a minute
    sc.render.engine = "BLENDER_EEVEE"
    ee = sc.eevee
    for attr, val in (("taa_render_samples", 32), ("use_shadows", True), ("use_raytracing", True), ("volumetric_tile_size", "4"),
                      ("volumetric_samples", 64), ("use_volumetric_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 8)):
        try: setattr(ee, attr, val)
        except Exception as e: print("eevee skip", attr, e)
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = OUT
world = bpy.data.worlds.new("w"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.002, 0.002, 0.003, 1)
sc.world = world
rnd = random.Random(13)


def mat(name, color, metal=0.0, rough=0.5, emit=None, strength=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def tex_mat(name, asset, scale=1.0, tint=(1, 1, 1), bump=0.6):
    """Poly Haven texture, box-projected in object space so plain cubes need no UVs."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])

    def img(kind, non_color):
        n = N.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(TEX + f"{asset}_{kind}.jpg")
        n.projection = "BOX"; n.projection_blend = 0.2
        if non_color: n.image.colorspace_settings.name = "Non-Color"
        L.new(mp.outputs["Vector"], n.inputs["Vector"]); return n
    d = img("diff", False)
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    L.new(d.outputs["Color"], mix.inputs["A"]); mix.inputs["B"].default_value = (*tint, 1)
    L.new(mix.outputs["Result"], b.inputs["Base Color"])
    L.new(img("rough", True).outputs["Color"], b.inputs["Roughness"])
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = bump
    L.new(img("nor_gl", True).outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def box(name, loc, size, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(m)
    return o


def cyl(name, loc, r, depth, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=24)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def fog(center, size, density=0.025, color=(0.8, 0.85, 1.0)):
    if "--fast" in sys.argv and "--fog3d" not in sys.argv:
        return None
    m = bpy.data.materials.new("fog"); m.use_nodes = True
    N = m.node_tree.nodes; N.remove(N["Principled BSDF"])
    v = N.new("ShaderNodeVolumePrincipled"); v.inputs["Density"].default_value = density
    v.inputs["Color"].default_value = (*color, 1)
    m.node_tree.links.new(v.outputs["Volume"], N["Material Output"].inputs["Volume"])
    o = box("fog", center, size, m); o.visible_shadow = False
    return o


SIL = mat("sil", (0.004, 0.004, 0.005), 0, 0.95)


OUTFITS = {   # the established look of each character since episode 1
    "toi": dict(skin=(0.36, 0.22, 0.13), hair=(0.02, 0.018, 0.016), top=(0.62, 0.42, 0.08), pants=(0.06, 0.07, 0.11), shoes=(0.02, 0.02, 0.02), strings=True),
    "boy": dict(skin=(0.45, 0.3, 0.2), top=(0.11, 0.12, 0.14), pants=(0.07, 0.07, 0.08), shoes=(0.02, 0.02, 0.02)),
    "duval": dict(skin=(0.6, 0.45, 0.36), hair=(0.42, 0.42, 0.42), top=(0.17, 0.18, 0.2), pants=(0.15, 0.16, 0.18), shoes=(0.02, 0.02, 0.02), tie=True),
}
_MATS = {}


def _m(key, col, rough=0.8):
    if key not in _MATS: _MATS[key] = mat(key, col, 0, rough)
    return _MATS[key]


def silhouette(name, loc, height=1.8, pose="stand", turn=0.0, coat=True, material=None, hood=False, glasses=False, eyes=None, outfit=None):
    """Human figure from overlapping primitives. Without an outfit: the solid black 'bonhomme noir'.
    With an outfit (toi, boy, duval): skin, hair, clothes and accessories in each character's colours."""
    import mathutils
    root = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(root)
    k = height / 1.8
    eyes = EYES if eyes is None else eyes
    O = OUTFITS.get(outfit) if outfit else None
    def M(region):
        if not O: return material or SIL
        col = O.get(region) or O["top"]
        return _m(f"{outfit}_{region}", col, 0.55 if region == "hair" else 0.8)

    def part(prim, co, scale, rot=(0, 0, 0), m=None):
        if prim == "s": bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=(0, 0, 0))
        elif prim == "c": bpy.ops.mesh.primitive_cylinder_add(vertices=20, location=(0, 0, 0))
        else: bpy.ops.mesh.primitive_cone_add(vertices=24, location=(0, 0, 0))
        o = bpy.context.object; o.scale = scale; o.location = co; o.rotation_euler = rot
        o.data.materials.append(m or M("top")); bpy.ops.object.shade_smooth(); o.parent = root
        return o
    def limb(p0, p1, r0, r1, m=None):
        p0, p1 = mathutils.Vector(p0), mathutils.Vector(p1); d = p1 - p0
        bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=r0, radius2=r1, depth=d.length, location=(p0 + p1) / 2)
        o = bpy.context.object; o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        o.data.materials.append(m or M("top")); bpy.ops.object.shade_smooth(); o.parent = root
        part("s", p0, (r0, r0, r0), m=m); part("s", p1, (r1, r1, r1), m=m)
    hip = 0.95
    part("s", (0, 0, 1.66), (0.105, 0.115, 0.125), m=M("skin"))                       # head
    if O and O.get("hair") and not hood:                                               # hair cap, a little higher at the back
        part("s", (0, 0.02, 1.71), (0.112, 0.12, 0.1), m=M("hair"))
    limb((0, 0, 1.44), (0, 0.01, 1.56), 0.05, 0.05, m=M("skin"))                       # neck
    part("s", (0, 0, 1.25), (0.21, 0.13, 0.25))                                        # chest
    limb((-0.19, 0, 1.40), (0.19, 0, 1.40), 0.075, 0.075)                              # shoulders
    part("s", (0, 0, 1.0), (0.17, 0.12, 0.2))                                          # waist
    if coat and not O:
        bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.27, radius2=0.18, depth=0.75, location=(0, 0, 0.78))
        o = bpy.context.object; o.scale = (1, 0.65, 1); o.data.materials.append(M("top")); bpy.ops.object.shade_smooth(); o.parent = root
    for sd in (-1, 1):
        limb((sd * 0.22, 0, 1.38), (sd * 0.26, 0.02, 1.08), 0.06, 0.05)                 # upper arm
        limb((sd * 0.26, 0.02, 1.08), (sd * 0.25, 0.05, 0.82), 0.05, 0.04)              # forearm
        part("s", (sd * 0.25, 0.06, 0.76), (0.045, 0.035, 0.06), m=M("skin"))          # hand
        limb((sd * 0.1, 0, hip), (sd * 0.11, 0, 0.5), 0.085, 0.065, m=M("pants"))        # thigh
        limb((sd * 0.11, 0, 0.5), (sd * 0.11, 0, 0.08), 0.065, 0.05, m=M("pants"))      # shin
        part("s", (sd * 0.11, -0.06, 0.04), (0.06, 0.13, 0.045), m=M("shoes"))          # foot
    if O and O.get("strings"):   # hoodie: hood folded on the back, white drawstrings, front pocket
        part("s", (0, 0.1, 1.47), (0.17, 0.09, 0.08))
        W_ = _m("strings", (0.85, 0.83, 0.78))
        for sd in (-1, 1): limb((sd * 0.035, -0.125, 1.42), (sd * 0.045, -0.13, 1.25), 0.008, 0.008, m=W_)
        part("s", (0, -0.1, 1.05), (0.13, 0.04, 0.07))
    if O and O.get("tie"):       # suit: white shirt V and the red tie
        part("s", (0, -0.118, 1.34), (0.075, 0.03, 0.1), m=_m("shirt", (0.82, 0.82, 0.8)))
        limb((0, -0.15, 1.37), (0, -0.155, 1.08), 0.02, 0.03, m=_m("tie", (0.45, 0.04, 0.05), 0.5))
    if O and not hood:   # a face: dark eyes, brows (frowning for Duval), mouth line
        INK = _m("ink_face", (0.02, 0.015, 0.012), 0.6)
        frown = 0.35 if outfit == "duval" else 0.0
        for sd in (-1, 1):
            part("s", (sd * 0.042, -0.108, 1.685), (0.014, 0.008, 0.016), m=INK)
            part("s", (sd * 0.045, -0.112, 1.725), (0.028, 0.008, 0.006), (0, sd * frown, 0), m=_m(f"{outfit}_hair", O.get("hair") or (0.05, 0.04, 0.03)))
        part("s", (0, -0.112, 1.6), (0.03, 0.006, 0.004), m=INK)
    if hood:   # a hood around the head, face sunk in its shadow
        part("s", (0, 0.055, 1.69), (0.15, 0.15, 0.165))
        FACE = mat("face_shadow", (0.025, 0.02, 0.018), 0, 0.9)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, location=(0, -0.06, 1.66)); fo = bpy.context.object
        fo.scale = (0.09, 0.05, 0.105); fo.data.materials.append(FACE); bpy.ops.object.shade_smooth(); fo.parent = root
    if glasses:   # Duval: round lenses and frames that catch the light
        GL = mat("glass", (0.9, 0.9, 0.95), 1.0, 0.05)
        for sd in (-1, 1):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.032, minor_radius=0.006, location=(sd * 0.042, -0.122, 1.685), rotation=(math.radians(90), 0, 0))
            g = bpy.context.object; g.data.materials.append(GL); g.parent = root
    if eyes:   # two glowing eyes: the series signature
        EYE = mat("eye", (1, 1, 1), 0, 0.3, (1.0, 0.97, 0.9), 40)
        for sd in (-1, 1):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1, location=(sd * 0.038, -0.1, 1.68))
            e = bpy.context.object; e.scale = (0.018, 0.01, 0.011); e.data.materials.append(EYE); e.parent = root
    root.location = loc; root.rotation_euler = (0, 0, turn); root.scale = (k, k, k)
    return root


def camera(loc, look, lens=26):
    bpy.ops.object.camera_add(location=loc); cam = bpy.context.object
    cam.data.lens = lens; sc.camera = cam
    d = (look[0] - loc[0], look[1] - loc[1], look[2] - loc[2])
    import mathutils
    cam.rotation_euler = mathutils.Vector(d).to_track_quat("-Z", "Y").to_euler()
    return cam


def light(kind, loc, energy, color=(1, 1, 1), size=0.2, rot=(0, 0, 0), spot=None):
    bpy.ops.object.light_add(type=kind, location=loc, rotation=rot); l = bpy.context.object
    l.data.energy = energy; l.data.color = color
    if kind == "AREA": l.data.size = size
    else: l.data.shadow_soft_size = size
    if spot: l.data.spot_size = math.radians(spot); l.data.spot_blend = 0.35
    return l


def flicker(l, base, low, every=2, p=0.25):
    for f in range(1, FRAMES + 1, every):
        l.data.energy = low if rnd.random() < p else base
        l.data.keyframe_insert("energy", frame=f)


CONC = tex_mat("conc", "concrete_wall_008", 0.6, (0.75, 0.75, 0.78))
PLAS = tex_mat("plaster", "painted_plaster_wall", 0.8, (0.62, 0.58, 0.52))
PLANK = tex_mat("planks", "worn_planks", 0.7, (0.55, 0.45, 0.38))
STEEL = mat("steel", (0.5, 0.52, 0.55), 0.9, 0.35)
DARK = mat("dark", (0.02, 0.02, 0.025), 0.2, 0.6)
BRASS = mat("brass", (0.75, 0.6, 0.3), 1.0, 0.3)

if SCENE == "interphone":
    # technical room: the dead intercom panel, cut cables, a torch beam, a figure in the far doorway
    box("floor", (0, 3, -0.02), (3.2, 8, 0.04), CONC)
    box("ceil", (0, 3, 2.62), (3.2, 8, 0.04), CONC)
    box("wl", (-1.6, 3, 1.3), (0.04, 8, 2.6), CONC); box("wr", (1.6, 3, 1.3), (0.04, 8, 2.6), CONC)
    for x in (-1.0, 1.0):
        box("we", (x, 7.0, 1.3), (1.2, 0.04, 2.6), CONC)
    box("lintel", (0, 7.0, 2.35), (0.8, 0.04, 0.5), CONC)
    # intercom on the left wall, close to camera
    PX, PY = 0.85, 6.96
    box("panel", (PX, PY, 1.35), (0.42, 0.05, 0.62), STEEL)
    box("screen", (PX, PY - 0.03, 1.52), (0.24, 0.02, 0.14), DARK)
    for r in range(3):
        for c in range(2):
            box("btn", (PX - 0.07 + c * 0.14, PY - 0.03, 1.32 - r * 0.08), (0.1, 0.02, 0.05), mat("btn", (0.15, 0.15, 0.15), 0.3, 0.4))
    for k in range(5):
        cyl("grill", (PX, PY - 0.03, 1.14 - k * 0.018), 0.004, 0.2, DARK, (0, math.radians(90), 0))
    # cut cables hanging below the panel
    for k in range(4):
        cyl("cable", (PX - 0.08 + 0.05 * k, PY - 0.02, 0.86 - 0.04 * k), 0.008, 0.3 + 0.08 * k, mat("cab", (0.05, 0.05, 0.05), 0, 0.5),
            (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), 0))
        box("copper", (PX - 0.08 + 0.05 * k, PY - 0.02, 0.86 - 0.04 * k - (0.15 + 0.04 * k)), (0.012, 0.012, 0.02), BRASS)
    bpy.ops.object.text_add(location=(PX, PY - 0.045, 1.5)); t = bpy.context.object
    t.data.body = "HORS SERVICE"; t.data.size = 0.035; t.data.align_x = "CENTER"; t.rotation_euler = (math.radians(90), 0, 0)
    t.data.materials.append(mat("red_txt", (0.1, 0, 0), 0, 0.4, (1, 0.05, 0.02), 6))
    box("floor2", (0, 8.5, -0.02), (3.2, 3, 0.04), CONC); box("wback2", (0, 9.9, 1.3), (3.2, 0.04, 2.6), CONC)
    box("ceil2", (0, 8.5, 2.62), (3.2, 3, 0.04), CONC)
    box("wl2", (-1.6, 8.5, 1.3), (0.04, 3, 2.6), CONC); box("wr2", (1.6, 8.5, 1.3), (0.04, 3, 2.6), CONC)
    fog((0, 4.5, 1.3), (3.1, 10.8, 2.55), 0.012)
    torch = light("SPOT", (0.6, -0.4, 1.5), 900, (1.0, 0.93, 0.8), 0.03, spot=9)
    import mathutils
    torch.rotation_euler = mathutils.Vector((PX - 0.6, PY + 0.4, 1.3 - 1.5)).to_track_quat("-Z", "Y").to_euler()
    if "--nofig" not in sys.argv:
        silhouette("figure", (-0.05, 7.7, 0), 1.85)
    back = light("AREA", (0, 8.7, 2.5), 700, (0.75, 0.82, 1.0), 1.4, rot=(math.radians(35), 0, 0))
    flicker(back, 700, 60, 3, 0.2)
    if "--dark" in sys.argv:   # power cut: only the eyes remain
        back.data.animation_data_clear(); back.data.energy = 0.0; torch.data.energy = 0
        light("POINT", (0, 3.0, 2.4), 10, (0.6, 0.65, 0.8), 0.5); back.data.energy = 18
    cam = camera((-0.3, 0.2, 1.5), (0.25, 7.0, 1.2), 26)
    cam.keyframe_insert("location", frame=1)
    cam.location = (-0.2, 1.6, 1.48); cam.keyframe_insert("location", frame=FRAMES)

elif SCENE == "escalier":
    # stairwell going down into the dark, green exit sign, a figure on the landing above casting a long shadow
    box("land_up", (0, 0, 0), (2.4, 2.2, 0.2), CONC)
    nsteps = 14
    for i in range(nsteps):
        box(f"step{i}", (0, 1.1 + 0.28 * i + 0.14, -0.17 * (i + 1)), (1.4, 0.28, 0.17 + 0.17 * (i + 1) * 0 + 0.17), CONC)
    box("land_dn", (0, 1.1 + 0.28 * nsteps + 1.0, -0.17 * nsteps - 0.1), (2.4, 2.0, 0.2), CONC)
    box("wl", (-1.2, 3.5, 0.2), (0.04, 9, 6), CONC); box("wr", (1.2, 3.5, 0.2), (0.04, 9, 6), CONC)
    box("ceil", (0, 3.5, 3.0), (2.4, 9, 0.04), CONC)
    box("wend", (0, 7.5, -1.0), (2.4, 0.04, 4), CONC)
    for i in range(nsteps):   # handrail posts
        cyl("post", (0.62, 1.1 + 0.28 * i + 0.14, -0.17 * (i + 1) + 0.5), 0.015, 0.9, STEEL)
    rail_len = math.hypot(0.28 * nsteps, 0.17 * nsteps)
    cyl("rail", (0.62, 1.1 + 0.14 * nsteps, -0.085 * nsteps + 0.95), 0.025, rail_len, STEEL,
        (math.atan2(0.28, 0.17) * 0 + math.radians(90) - math.atan2(0.17, 0.28), 0, 0))
    box("exit", (0, 7.46, 0.15), (0.5, 0.04, 0.2), mat("exit", (0, 0.2, 0.05), 0, 0.4, (0.1, 1.0, 0.3), 25))
    light("POINT", (0, 7.2, 0.15), 6, (0.2, 1.0, 0.4), 0.1)
    bpy.ops.object.text_add(location=(0.75, -1.07, 1.75)); t = bpy.context.object
    t.data.body = "-13"; t.data.size = 0.5; t.data.align_x = "CENTER"; t.rotation_euler = (math.radians(90), 0, math.radians(180))
    t.data.materials.append(mat("paint", (0.5, 0.04, 0.03), 0, 0.8))
    box("wtop", (0, -1.1, 1.5), (2.4, 0.04, 3.0), CONC)
    light("AREA", (0, -0.6, 2.9), 300, (1.0, 0.85, 0.65), 0.8, rot=(math.radians(-35), 0, 0))
    silhouette("figure", (0.0, 0.3, 0.1), 1.8, turn=math.radians(180))
    back = light("SPOT", (0.0, -0.8, 2.6), 1500, (1.0, 0.9, 0.75), 0.05, spot=55)
    import mathutils
    back.rotation_euler = mathutils.Vector((0, 4.5, -2.6)).to_track_quat("-Z", "Y").to_euler()
    flicker(back, 1500, 150, 3, 0.18)
    fog((0, 3.5, 0.2), (2.35, 8.9, 5.9), 0.02)
    if "--abandoned" in sys.argv:
        import mathutils
        CARD = mat("card", (0.33, 0.24, 0.14), 0, 0.92)
        PAPER = mat("paper", (0.72, 0.67, 0.52), 0, 0.85)
        RUST = mat("rust", (0.32, 0.16, 0.08), 0.6, 0.75)
        BAG = mat("bag", (0.02, 0.02, 0.02), 0, 0.25)
        STAIN = mat("stain", (0.05, 0.045, 0.035), 0, 0.95)
        STAIN.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.55
        step_top = lambda i: -0.17 * i
        step_y = lambda i: 1.1 + 0.28 * i + 0.14
        # broken step noses: a chunk cut out with a boolean, the chunk lying on the step below
        for i in (2, 5, 6, 9, 11):
            st = bpy.data.objects[f"step{i}"]
            cx = rnd.uniform(-0.45, 0.45)
            bpy.ops.mesh.primitive_cube_add(location=(cx, step_y(i) - 0.14, step_top(i)), rotation=(rnd.uniform(0.3, 0.8), rnd.uniform(-0.4, 0.4), rnd.uniform(-0.5, 0.5)))
            cut = bpy.context.object; cut.scale = (rnd.uniform(0.12, 0.3), 0.09, 0.09); cut.hide_render = True; cut.display_type = "WIRE"
            md = st.modifiers.new("chip", "BOOLEAN"); md.object = cut; md.operation = "DIFFERENCE"
            box("chunk", (cx + rnd.uniform(-0.1, 0.1), step_y(i + 1) - 0.05, step_top(i + 1) + 0.04), (0.2, 0.12, 0.08), CONC,
                (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), rnd.uniform(0, 3)))
        # rubble and dust all over the steps
        for _ in range(110):
            i = rnd.randrange(0, 14); sz = rnd.uniform(0.012, 0.045)
            box("rubble", (rnd.uniform(-0.65, 0.55), step_y(i) + rnd.uniform(-0.1, 0.12), step_top(i) + sz / 2), (sz, sz * rnd.uniform(0.6, 1.4), sz * 0.7), CONC,
                (rnd.uniform(0, 3), rnd.uniform(0, 3), rnd.uniform(0, 3)))
        # handrail: two posts gone, one bent
        for i in (6, 7):
            for o in [o for o in bpy.data.objects if o.name.startswith("post") and abs(o.location.y - step_y(i)) < 0.01]:
                bpy.data.objects.remove(o)
        bent = [o for o in bpy.data.objects if o.name.startswith("post") and abs(o.location.y - step_y(10)) < 0.01]
        if bent: bent[0].rotation_euler = (0.5, 0.35, 0)
        # pipes and a conduit along the walls, rusty
        for k, z in enumerate((2.55, 2.4)):
            cyl("pipe", (1.12, 3.5, z), 0.045 - k * 0.012, 9, RUST, (math.radians(90), 0, 0))
        cyl("vpipe", (-1.13, 2.4, 0.4), 0.035, 5.5, RUST)
        for z in (2.0, 1.0, 0.0, -1.0):
            box("clamp", (-1.15, 2.4, z), (0.03, 0.1, 0.03), RUST)
        # peeling posters, notices and water stains on both walls
        for _ in range(16):
            sd = rnd.choice((-1, 1)); y = rnd.uniform(0.4, 6.8); z = 1.4 - 0.6 * (y - 1.1) + rnd.uniform(-0.2, 0.9)
            w_, h_ = rnd.uniform(0.18, 0.42), rnd.uniform(0.25, 0.55)
            box("poster", (sd * 1.175, y, z), (0.004, w_, h_), PAPER, (rnd.uniform(-0.12, 0.12), 0, 0))
            if rnd.random() < 0.5:   # a torn corner hanging off
                box("peel", (sd * 1.165, y + w_ / 3, z - h_ / 2), (0.004, w_ / 2.5, h_ / 3), PAPER, (0.25, sd * 0.12, 0))
        for _ in range(10):
            sd = rnd.choice((-1, 1)); y = rnd.uniform(0.5, 7); z = 1.6 - 0.6 * (y - 1.1) + rnd.uniform(-0.5, 1.4)
            box("stain", (sd * 1.177, y, z), (0.002, rnd.uniform(0.3, 0.9), rnd.uniform(0.4, 1.4)), STAIN, (rnd.uniform(-0.3, 0.3), 0, 0))
        # boxes, bags and a fallen chair on the upper landing
        for k in range(4):
            box("crate", (0.75 + rnd.uniform(-0.1, 0.1), -0.4 + k * 0.32, 0.1 + 0.18 + (0.36 if k == 1 else 0)), (0.4, 0.34, 0.36), CARD, (0, 0, rnd.uniform(-0.3, 0.3)))
        for k in range(3):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(-0.85 + k * 0.18, -0.6 + k * 0.25, 0.25))
            o = bpy.context.object; o.scale = (1, 0.8, 0.75); o.data.materials.append(BAG); bpy.ops.object.shade_smooth()
        box("chair", (-0.7, 0.6, 0.35), (0.45, 0.45, 0.05), RUST, (1.2, 0, 0.4))
        # dead light: a fluorescent fixture hanging by one wire halfway up, tube almost dead
        fx, fy, fz = 0.1, 3.4, 2.0
        box("fixture", (fx, fy, fz), (0.18, 1.2, 0.06), STEEL, (0.55, 0.15, 0))
        cyl("wire", (fx - 0.05, fy - 0.55, 2.55), 0.005, 0.7, DARK)
        TUBE = mat("tube", (0.9, 0.9, 0.9), 0, 0.3, (0.75, 0.9, 1.0), 0.0)
        tb = box("tube", (fx, fy, fz - 0.05), (0.03, 1.1, 0.03), TUBE, (0.55, 0.15, 0))
        tl = light("AREA", (fx, fy, fz - 0.1), 0, (0.75, 0.9, 1.0), 1.0, rot=(0.55, 0.15, 0))
        es = TUBE.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        for f in range(1, FRAMES + 1, 2):   # dead most of the time, a stutter now and then
            on = rnd.random() < 0.12
            es.default_value = 8 if on else 0.05; es.keyframe_insert("default_value", frame=f)
            tl.data.energy = 120 if on else 0; tl.data.keyframe_insert("energy", frame=f)
        # hard side light through the rail posts, throwing bar shadows across the left wall
        side = light("SPOT", (1.05, 2.0, 1.6), 700, (0.95, 0.85, 0.7), 0.01, spot=50)
        side.rotation_euler = mathutils.Vector((-2.2, 1.2, -1.4)).to_track_quat("-Z", "Y").to_euler()
        back.data.energy = 1100; flicker(back, 1100, 90, 3, 0.2)
        for o in bpy.data.objects:   # kill the green exit glow and dim the fill: let the shadows win
            if o.type == "LIGHT" and o.data.type == "POINT": o.data.energy = 0.5
            if o.type == "LIGHT" and o.data.type == "AREA" and o.location.z > 2.8: o.data.energy = 140
    if "--boy" in sys.argv:
        HOOD = mat("hoodie", (0.11, 0.12, 0.14), 0, 0.85)
        if "--empty" not in sys.argv: silhouette("boy", (0.42, 5.35, -2.38 + 0.0), 1.55, turn=math.radians(212), hood=True, eyes=False, outfit="boy")
        rim = light("SPOT", (1.0, 4.6, -0.6), 260, (0.95, 0.85, 0.7), 0.05, spot=35)
        import mathutils
        rim.rotation_euler = mathutils.Vector((-0.65, 0.6, -1.0)).to_track_quat("-Z", "Y").to_euler()

    if REAL:   # slow climb up the stairs towards the figure
        cam = camera((-0.45, 6.6, -1.75), (0.0, 0.3, 1.0), 24)
        cam.keyframe_insert("location", frame=1)
        cam.location = (-0.3, 4.4, -0.55); cam.keyframe_insert("location", frame=FRAMES)
    else:
        cam = camera((-0.45, 6.4, -1.6), (0.0, 0.2, 0.9), 22)
        cam.keyframe_insert("location", frame=1)
        cam.location = (-0.4, 6.0, -1.45); cam.keyframe_insert("location", frame=FRAMES)

elif SCENE == "duval":
    # Duval's flat: blinds throwing stripes, a desk lamp, a wall of photos with crossed-out faces, him seated, back to us
    box("floor", (0, 2, -0.02), (5, 6, 0.04), PLANK)
    box("ceil", (0, 2, 2.6), (5, 6, 0.04), PLAS)
    box("wback", (0, 4.6, 1.3), (5, 0.04, 2.6), PLAS)
    box("wl", (-2.2, 2, 1.3), (0.04, 6, 2.6), PLAS)
    box("wr_a", (2.2, 1.0, 1.3), (0.04, 4, 2.6), PLAS)
    # window with blinds in the right wall
    for k in range(14):
        box("slat", (2.18, 3.6, 0.7 + k * 0.1), (0.02, 1.4, 0.05), mat("slat", (0.6, 0.58, 0.55), 0, 0.6), (math.radians(30), 0, 0))
    box("wr_top", (2.2, 3.6, 2.35), (0.04, 1.6, 0.5), PLAS); box("wr_bot", (2.2, 3.6, 0.3), (0.04, 1.6, 0.6), PLAS)
    box("wr_b", (2.2, 4.45, 1.3), (0.04, 0.3, 2.6), PLAS)
    moon = light("AREA", (3.6, 3.5, 1.9), 1400, (0.65, 0.75, 1.0), 0.5, rot=(0, math.radians(75), 0))
    # photo wall with red crosses
    PH = mat("photo", (0.75, 0.72, 0.65), 0, 0.7)
    REDX = mat("redx", (0.6, 0.02, 0.02), 0, 0.6)
    slots = [(r, c) for r in range(3) for c in range(5)][:13] if "--photos13" in sys.argv else [(r, c) for r in range(3) for c in range(5)]
    for n_, (r, c) in enumerate(slots):
            x, z = -1.3 + c * 0.42 + rnd.uniform(-0.04, 0.04), 1.95 - r * 0.38 + rnd.uniform(-0.03, 0.03)
            if "--photos13" in sys.argv and n_ == 12:   # the empty frame waiting for number 13
                box("frame13", (x, 4.57, z), (0.28, 0.012, 0.34), DARK)
                box("frame13_in", (x, 4.562, z), (0.22, 0.006, 0.28), mat("void", (0.01, 0.01, 0.01), 0, 0.9))
                bpy.ops.object.text_add(location=(x, 4.555, z - 0.06)); t13 = bpy.context.object
                t13.data.body = "13"; t13.data.size = 0.14; t13.data.align_x = "CENTER"; t13.rotation_euler = (math.radians(90), 0, 0)
                t13.data.materials.append(mat("red13", (0.5, 0.02, 0.02), 0, 0.5, (1, 0.05, 0.02), 3))
                continue
            box("ph", (x, 4.57, z), (0.26, 0.01, 0.32), PH, (0, rnd.uniform(-0.12, 0.12), 0))
            box("face", (x, 4.562, z + 0.04), (0.12, 0.005, 0.14), mat("face", (0.25, 0.2, 0.18), 0, 0.8))
            if "--photos13" in sys.argv or rnd.random() < 0.75:
                for a in (45, -45):
                    box("x", (x, 4.555, z), (0.3, 0.004, 0.025), REDX, (0, math.radians(a), 0))
    # desk, lamp, chair, seated figure
    box("desk", (-0.2, 3.7, 0.74), (1.6, 0.7, 0.05), PLANK)
    for dx in (-0.9, 0.5):
        box("leg", (dx, 3.7, 0.37), (0.05, 0.6, 0.74), DARK)
    for k in range(6):
        box("paper", (-0.6 + rnd.uniform(-0.3, 0.6), 3.6 + rnd.uniform(-0.15, 0.15), 0.775), (0.21, 0.29, 0.002), PH, (0, 0, rnd.uniform(-0.6, 0.6)))
    cyl("lamp_arm", (0.35, 3.85, 0.95), 0.012, 0.42, BRASS, (0.3, 0, 0))
    bpy.ops.mesh.primitive_cone_add(radius1=0.11, radius2=0.04, depth=0.14, location=(0.35, 3.75, 1.15), rotation=(math.radians(200), 0, 0))
    bpy.context.object.data.materials.append(mat("shade", (0.1, 0.25, 0.12), 0.3, 0.4))
    lamp = light("SPOT", (0.35, 3.72, 1.04), 140, (1.0, 0.75, 0.45), 0.03, spot=80, rot=(math.radians(20), 0, 0))
    box("chair_seat", (-0.2, 2.9, 0.45), (0.55, 0.55, 0.08), DARK)
    box("chair_back", (-0.2, 2.62, 0.85), (0.55, 0.06, 0.75), DARK)
    if "--tape" in sys.argv:   # the VHS tape on the desk, label facing up
        box("vhs", (-0.35, 3.55, 0.79), (0.19, 0.1, 0.025), mat("vhs", (0.03, 0.03, 0.03), 0.2, 0.4), (0, 0, 0.25))
        box("vhs_label", (-0.35, 3.55, 0.8035), (0.13, 0.055, 0.001), PH, (0, 0, 0.25))
        bpy.ops.object.text_add(location=(-0.35, 3.55, 0.8045), rotation=(0, 0, 0.25)); tv = bpy.context.object
        tv.data.body = "31.10.2020"; tv.data.size = 0.018; tv.data.align_x = "CENTER"; tv.data.align_y = "CENTER"
        tv.data.materials.append(mat("ink2", (0.02, 0.02, 0.02), 0, 0.6))
    # entrance wall with a doorway, a cold hallway light behind it
    box("wfront_l", (-1.3, -0.9, 1.3), (1.8, 0.04, 2.6), PLAS); box("wfront_r", (1.4, -0.9, 1.3), (1.6, 0.04, 2.6), PLAS)
    box("wfront_t", (0.05, -0.9, 2.35), (1.0, 0.04, 0.5), PLAS)
    box("hall_floor", (0, -2.2, -0.02), (3, 2.6, 0.04), PLANK); box("hall_w", (0, -3.4, 1.3), (3, 0.04, 2.6), PLAS)
    light("AREA", (0.05, -2.0, 2.4), 260, (0.8, 0.88, 1.0), 0.9, rot=(math.radians(-25), 0, 0))
    if "--duvaldoor" in sys.argv:
        if "--empty" not in sys.argv: silhouette("duval", (0.05, -1.25, 0.0), 1.78, turn=0, glasses=True, eyes=False, outfit="duval")
        import mathutils
        key = light("SPOT", (0.5, 1.4, 1.9), 160, (1.0, 0.82, 0.62), 0.15, spot=22)   # desk-lamp key light on his face and tie
        key.rotation_euler = mathutils.Vector((0.05 - 0.5, -1.25 - 1.4, 1.45 - 1.9)).to_track_quat("-Z", "Y").to_euler()
    elif "--hidden" in sys.argv:   # a figure in the dark corner, only a few frames in the edit
        silhouette("hidden", (-1.0, 4.25, 0.0), 1.8, turn=math.radians(-20), eyes=True)
    elif "--nofig" not in sys.argv:
        silhouette("duval", (1.6, 3.55, 0.0), 1.75, turn=math.radians(90))
    fog((0, 2, 1.3), (4.9, 5.9, 2.55), 0.018, (0.85, 0.9, 1.0))
    flicker(lamp, 140, 60, 4, 0.15)
    CAMS = {"wide": ((-1.4, 0.2, 1.55), (0.7, 3.9, 1.15), 24), "wall": ((-0.4, 2.6, 1.55), (-0.45, 4.6, 1.6), 30),
            "desk": ((-0.45, 3.05, 1.25), (-0.35, 3.6, 0.78), 35), "door": ((0.15, 2.8, 1.5), (0.05, -1.2, 1.45), 30)}
    cl, ct, cf = CAMS[ARG("--cam", "wide")]
    cam = camera(cl, ct, cf)
    cam.keyframe_insert("location", frame=1)
    cam.location = (cl[0] + 0.3 * (ct[0] - cl[0]) / 4, cl[1] + 0.3 * (ct[1] - cl[1]) / 4, cl[2]); cam.keyframe_insert("location", frame=FRAMES)

if SCENE == "valmont":
    # EMPLOI INSTABLE: Valmont headquarters, clinical white, cold neons, hard clean shadows
    import mathutils
    WH = mat("white", (0.86, 0.87, 0.89), 0, 0.4); FL = mat("floor", (0.78, 0.79, 0.8), 0, 0.12)
    GREY = mat("grey", (0.35, 0.36, 0.38), 0.2, 0.4); BLK = mat("blk", (0.03, 0.03, 0.035), 0.3, 0.3)
    GL = mat("glass", (0.9, 0.95, 0.97), 0, 0.05); GL.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.9
    NEON = mat("neon", (1, 1, 1), 0, 0.5, (0.85, 0.93, 1.0), 9)
    RED = mat("vred", (0.6, 0.03, 0.03), 0, 0.4)
    ANTH = mat("anth", (0.08, 0.09, 0.1), 0.3, 0.45)                 # anthracite frames and skirting
    OAK = tex_mat("oak", "worn_planks", 0.9, (1.15, 0.95, 0.75), 0.3)   # warm oak doors
    TEAL = mat("teal", (0.06, 0.22, 0.25), 0, 0.55)                  # deep teal accent wall
    STEELB = mat("steelb", (0.75, 0.76, 0.78), 1.0, 0.28)            # brushed steel handles
    CARPET = mat("carpet", (0.12, 0.13, 0.16), 0, 0.95)

    def door(x, y, face, w=0.95, h=2.1, m=None, label=None, num=None):
        """Door with anthracite frame, lever handle, kick plate, number plate. face=+1 opens towards +x."""
        m = m or OAK
        vx = face * 0.02
        if face == 0:   # door in an end wall facing -y
            box("dleaf", (x, y - 0.02, h / 2), (w, 0.04, h), m)
            for sx in (-1, 1): box("dfr", (x + sx * (w / 2 + 0.04), y - 0.03, h / 2 + 0.03), (0.08, 0.06, h + 0.06), ANTH)
            box("dfrt", (x, y - 0.03, h + 0.06), (w + 0.16, 0.06, 0.08), ANTH)
            box("kick", (x, y - 0.045, 0.12), (w - 0.06, 0.01, 0.22), STEELB)
            cyl("rose", (x + w / 2 - 0.12, y - 0.05, 1.0), 0.03, 0.02, STEELB, (math.radians(90), 0, 0))
            box("lever", (x + w / 2 - 0.2, y - 0.08, 1.0), (0.16, 0.02, 0.025), STEELB)
            if num: box("nplate", (x, y - 0.045, 1.6), (0.36, 0.01, 0.12), ANTH)
            return
        box("dleaf", (x, y, h / 2), (0.04, w, h), m)
        for sy in (-1, 1): box("dfr", (x - vx, y + sy * (w / 2 + 0.04), h / 2 + 0.03), (0.06, 0.08, h + 0.06), ANTH)
        box("dfrt", (x - vx, y, h + 0.06), (0.06, w + 0.16, 0.08), ANTH)
        box("kick", (x - face * 0.025, y, 0.12), (0.01, w - 0.06, 0.22), STEELB)
        cyl("rose", (x - face * 0.03, y + w / 2 - 0.12, 1.0), 0.03, 0.02, STEELB, (0, math.radians(90), 0))
        box("lever", (x - face * 0.06, y + w / 2 - 0.2, 1.0), (0.02, 0.16, 0.025), STEELB)
        box("nplate", (x - face * 0.025, y, 1.62), (0.01, 0.34, 0.11), ANTH)
    view = ARG("--cam", "hall")

    def char3d(name, loc, face, skin, shirt, hair, pants=(0.05, 0.055, 0.08), run=0.0, lean=0.0, beard=None, bun=False, eyes_emit=0.0, dark=False, arm_out=0.0, h=1.72, brow=-0.25, badge=False):
        """A simple 3D character in the series' look: big round head, rounded torso, tube limbs. face = heading angle (0 looks towards -y)."""
        root = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(root); k = h / 1.72
        if dark: skin = shirt = hair = pants = (0.012, 0.013, 0.018)
        SK = mat(name + "sk", skin, 0, 0.55); SH = mat(name + "sh", shirt, 0, 0.7); HA = mat(name + "ha", hair, 0, 0.6); PA = mat(name + "pa", pants, 0, 0.8)
        def part(o): o.parent = root; return o
        def ball(loc_, sc_, m):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=20, radius=1, location=loc_); o = bpy.context.object; o.scale = sc_; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return part(o)
        def limb(pivot, ang, length, r, m, side=0.0):
            """A tube hanging from pivot, swung forward (ang > 0 = towards the face) and outwards."""
            dy, dz = -math.sin(ang) * length, -math.cos(ang) * length; dx = math.sin(side) * length
            c = (pivot[0] + dx / 2, pivot[1] + dy / 2, pivot[2] + dz / 2)
            bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=length, location=c, vertices=20); o = bpy.context.object
            o.rotation_euler = mathutils.Vector((dx, dy, dz)).to_track_quat("-Z", "Y").to_euler(); o.data.materials.append(m); bpy.ops.object.shade_smooth(); part(o)
            return (pivot[0] + dx, pivot[1] + dy, pivot[2] + dz)
        ly = -lean * 0.45
        for sd in (-1, 1):
            a = run * sd * 0.75
            knee = limb((sd * 0.09, 0, 0.86), a, 0.42, 0.075, PA); foot = limb(knee, a - (0.9 if (run and sd * run < 0) else 0.15 * run), 0.42, 0.065, PA)
            part(box(name + "shoe", (foot[0], foot[1] - 0.06, max(0.04, foot[2])), (0.11, 0.26, 0.08), mat(name + "shoe", (0.25, 0.14, 0.08) if not dark else skin, 0, 0.5)))
        ball((0, ly * 0.5, 1.13), (0.215, 0.16, 0.33), SH)                                   # torso
        for sd in (-1, 1):
            a = -run * sd * 0.9
            elbow = limb((sd * 0.235, ly * 0.8, 1.36), a, 0.3, 0.058, SH, side=sd * (0.12 + arm_out)); hand = limb(elbow, a + (1.1 if run else 0.1), 0.28, 0.052, SH, side=sd * 0.05)
            ball(hand, (0.06, 0.06, 0.06), SK)
        hz = 1.62; hy = ly
        ball((0, hy, hz), (0.2, 0.2, 0.2), SK); ball((0, hy, 1.4), (0.07, 0.07, 0.09), SK)                               # head, neck
        ball((0, hy + 0.035, hz + 0.045), (0.205, 0.2, 0.185), HA)                             # hair cap: sits back and up, the face stays clear
        if bun: ball((0, hy + 0.06, hz + 0.26), (0.085, 0.085, 0.085), HA)
        if beard: ball((0, hy - 0.006, hz - 0.115), (0.19, 0.192, 0.1), mat(name + "bd", beard, 0, 0.95))
        if badge: part(box(name + "bdg", (0.02, ly * 0.5 - 0.165, 1.12), (0.07, 0.01, 0.1), mat(name + "bg", (0.92, 0.92, 0.9), 0, 0.4))); part(box(name + "bdr", (0.02, ly * 0.5 - 0.171, 1.158), (0.07, 0.004, 0.022), RED)); part(box(name + "lan", (0.02, ly * 0.6 - 0.15, 1.3), (0.012, 0.01, 0.28), mat(name + "ln", (0.1, 0.5, 0.62), 0, 0.5)))
        EW = mat(name + "ew", (0.95, 0.94, 0.9), 0, 0.3, (1, 1, 1) if eyes_emit else None, eyes_emit); EP = mat(name + "ep", (0.02, 0.02, 0.03), 0, 0.2)
        for sd in (-1, 1):
            ball((sd * 0.075, hy - 0.178, hz + 0.02), (0.045, 0.02, 0.032), EW)
            if not eyes_emit: ball((sd * 0.075, hy - 0.194, hz + 0.018), (0.02, 0.01, 0.02), EP)
            if not dark: part(box(name + "brow", (sd * 0.075, hy - 0.19, hz + 0.075), (0.085, 0.02, 0.014), mat(name + "br", (0.03, 0.03, 0.035), 0, 0.6), (0, sd * brow, 0)))
        if dark: part(box(name + "sq", (0.1, -0.165, 1.3), (0.05, 0.01, 0.04), mat(name + "sqr", (0.5, 0, 0), 0, 0.3, (1.0, 0.05, 0.03), 5)))   # the red pocket square
        root.scale = (k, k, k); root.rotation_euler = (lean * 0.5, 0, face); root.location = loc
        return root

    def toon(name, loc, face, yaw=0.0, pitch=0.0, look=(0.0, 0.0), wide=1.0, brow=0.0, brow_up=0.0, mouth="line", armL=(0.0, 0.1), armR=(0.0, 0.1), lean=0.0, dark=False, cap=True, bag=True, h=1.74, legs=(0.04, 0.04), phone=None):
        """The night courier, built with care: hoodie with hood and pocket, cap, thermal backpack, lanyard, a face that can act.
        face = heading (0 looks towards -y); yaw/pitch turn the head; look moves the pupils; armX = (swing forward, elbow bend)."""
        root = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(root)
        head = bpy.data.objects.new(name + "_head", None); bpy.context.collection.objects.link(head); head.parent = root; head.location = (0, 0, 1.44)
        def M(n, col, metal=0.0, rough=0.5, emit=None, strength=0.0):
            m = mat(name + n, (0.012, 0.013, 0.017) if dark and not emit else col, metal, 0.6 if dark else rough, emit, strength)
            return m
        SK = M("sk", (0.62, 0.34, 0.2), 0, 0.5); HO = M("ho", (0.36, 0.37, 0.41), 0, 0.92); HO2 = M("ho2", (0.27, 0.28, 0.32), 0, 0.92); PA = M("pa", (0.045, 0.05, 0.075), 0, 0.85)
        PU = M("pu", (0.2, 0.09, 0.55), 0, 0.55); PU2 = M("pu2", (0.12, 0.05, 0.36), 0, 0.5); WHT = M("wh", (0.9, 0.9, 0.88), 0, 0.5); DK = M("dk", (0.02, 0.02, 0.025), 0, 0.4)
        def ball(loc_, sc_, m, par=root):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1, location=loc_); o = bpy.context.object; o.scale = sc_; o.data.materials.append(m); bpy.ops.object.shade_smooth(); o.parent = par; return o
        def bbox(loc_, size, m, rot=(0, 0, 0), bev=0.02, par=root):
            o = box(name + "b", loc_, size, m, rot); md = o.modifiers.new("bv", "BEVEL"); md.width = bev; md.segments = 4; bpy.ops.object.shade_smooth(); o.parent = par; return o
        def limb(pivot, ang, length, r, m, side=0.0, r2=None):
            dy, dz = -math.sin(ang) * length, -math.cos(ang) * length; dx = math.sin(side) * length
            bpy.ops.mesh.primitive_cone_add(radius1=r2 or r, radius2=r, depth=length, vertices=28, location=(pivot[0] + dx / 2, pivot[1] + dy / 2, pivot[2] + dz / 2)); o = bpy.context.object
            o.rotation_euler = mathutils.Vector((-dx, -dy, -dz)).to_track_quat("Z", "Y").to_euler(); o.data.materials.append(m); bpy.ops.object.shade_smooth(); o.parent = root
            ball(pivot, (r * 1.02,) * 3, m); return (pivot[0] + dx, pivot[1] + dy, pivot[2] + dz)
        ly = -lean * 0.4
        for sd in (-1, 1):                                          # legs, trainers
            la = legs[0] if sd == 1 else legs[1]; knee = limb((sd * 0.1, 0, 0.88), la, 0.43, 0.082, PA, side=sd * 0.02); foot = limb(knee, la - (0.55 if la < -0.1 else 0.07), 0.4, 0.072, PA, r2=0.062)       # a stride: the back leg bends at the knee
            fz = max(0.0, foot[2] - 0.04); bbox((foot[0], foot[1] - 0.06, fz + 0.05), (0.12, 0.27, 0.1), WHT, (0.5 if la < -0.1 else 0, 0, 0), bev=0.035); bbox((foot[0], foot[1] - 0.06, fz + 0.012), (0.125, 0.28, 0.025), DK, (0.5 if la < -0.1 else 0, 0, 0), bev=0.008)
        ball((0, ly * 0.5, 1.15), (0.205, 0.158, 0.335), HO); cyl(name + "hem", (0, ly * 0.2, 0.87), 0.178, 0.08, HO2).parent = root
        ball((0, ly * 0.8, 1.36), (0.23, 0.13, 0.1), HO)                                                                                           # shoulder line                    # hoodie body and hem
        ball((0, ly * 0.5 - 0.118, 1.0), (0.11, 0.03, 0.05), HO2)                                                                      # kangaroo pocket
        ball((0, ly + 0.1, 1.43), (0.19, 0.14, 0.12), HO2)                                                                                         # the hood, resting on the shoulders
        for sd in (-1, 1): cyl(name + "str", (sd * 0.07, ly * 0.7 - 0.148, 1.27), 0.006, 0.17, WHT, (0.12, 0, 0)).parent = root                   # drawstrings
        hands = {}
        for sd, (sw, bend) in ((-1, armR), (1, armL)):                                                                                             # arms: shoulder swing, elbow bend, cuff, hand, thumb
            elbow = limb((sd * 0.232, ly * 0.8, 1.37), sw, 0.3, 0.058, HO, side=sd * 0.12); wrist = limb(elbow, sw + bend, 0.27, 0.05, HO, side=sd * -0.02 if bend > 0.5 else sd * 0.05)
            ball(wrist, (0.056, 0.056, 0.03), HO2); ca, sa = math.cos(sw + bend), math.sin(sw + bend); hd_ = (wrist[0], wrist[1] - 0.045 * sa, wrist[2] - 0.045 * ca)
            ball(hd_, (0.047, 0.036, 0.052), SK); ball((hd_[0] - sd * 0.04, hd_[1] - 0.012 * sa, hd_[2] + 0.004), (0.016, 0.016, 0.03), SK)                    # palm and thumb
            for q in range(4): ball((hd_[0] + (q - 1.5) * 0.021, hd_[1] - 0.05 * sa, hd_[2] - 0.05 * ca), (0.0115, 0.0115, 0.03), SK)                              # four fingers
            hands[sd] = hd_
        if phone:                                                    # his phone: a dark slab with a lit screen, in the hand or against the ear
            SCRN = mat(name + "pscr", (0.05, 0.06, 0.08), 0, 0.15, (0.6, 0.8, 1.0), 7.0); hx, hy, hz_ = hands[-1]
            if phone == "ear":
                bbox((hx + 0.012, hy + 0.01, hz_ + 0.05), (0.014, 0.078, 0.158), DK, (0.25, 0, 0), bev=0.006); bbox((hx + 0.021, hy + 0.01, hz_ + 0.05), (0.003, 0.068, 0.145), SCRN, (0.25, 0, 0), bev=0.002)
            else:
                bbox((hx, hy - 0.02, hz_ + 0.07), (0.078, 0.014, 0.158), DK, (-0.5, 0, 0), bev=0.006); bbox((hx, hy - 0.013, hz_ + 0.074), (0.068, 0.003, 0.145), SCRN, (-0.5, 0, 0), bev=0.002)
                bpy.ops.object.light_add(type="POINT", location=(hx, hy + 0.12, hz_ + 0.16)); lp = bpy.context.object; lp.data.energy = 2.2; lp.data.color = (0.6, 0.8, 1.0); lp.data.shadow_soft_size = 0.05; lp.parent = root
        if bag:                                                      # thermal backpack, straps, the made-up brand's moon
            bbox((0, ly * 0.5 + 0.24, 1.17), (0.44, 0.24, 0.5), PU, bev=0.045); bbox((0, ly * 0.5 + 0.365, 1.25), (0.445, 0.01, 0.07), WHT, bev=0.004); bbox((0, ly * 0.5 + 0.24, 1.435), (0.3, 0.16, 0.03), PU2, bev=0.012)
            for sd in (-1, 1): bbox((sd * 0.105, ly * 0.6 - 0.136, 1.2), (0.04, 0.024, 0.44), PU2, (0.2, 0, sd * -0.06), bev=0.01)
            bbox((0, ly * 0.6 - 0.156, 1.13), (0.22, 0.018, 0.03), PU2, bev=0.008)
        if not dark:                                                 # lanyard and badge
            for sd in (-1, 1): bbox((sd * 0.03, ly * 0.6 - 0.152, 1.24), (0.012, 0.012, 0.24), mat(name + "lan", (0.6, 0.03, 0.03), 0, 0.5), (0.15, sd * 0.2, 0), bev=0.003)
            bbox((0, ly * 0.5 - 0.164, 1.08), (0.07, 0.012, 0.1), WHT, bev=0.006); bbox((0, ly * 0.5 - 0.172, 1.115), (0.07, 0.004, 0.02), mat(name + "bdr", (0.6, 0.03, 0.03), 0, 0.5), bev=0.002)
        cyl(name + "neck", (0, ly, 1.45), 0.07, 0.1, SK).parent = root
        hz = 0.2                                                     # ---- the head (children of the head pivot) ----
        hb = ball((0, ly, hz), (0.2, 0.195, 0.205), SK, head)
        for sd in (-1, 1): ball((sd * 0.198, ly + 0.01, hz - 0.01), (0.03, 0.04, 0.05), SK, head)
        ball((0, ly - 0.194, hz - 0.045), (0.02, 0.024, 0.02), SK, head)                                                                           # nose
        ball((0, ly + 0.04, hz + 0.03), (0.2, 0.19, 0.19), M("hair", (0.03, 0.025, 0.025), 0, 0.7), head)
        if cap:
            ball((0, ly + 0.005, hz + 0.145), (0.206, 0.205, 0.125), PU, head); ball((0, ly + 0.005, hz + 0.268), (0.022, 0.022, 0.012), PU2, head); bpy.ops.mesh.primitive_cylinder_add(radius=0.165, depth=0.016, vertices=40, location=(0, ly - 0.15, hz + 0.158), rotation=(0.1, 0, 0)); v = bpy.context.object; v.scale = (1, 0.62, 1); v.data.materials.append(PU2); bpy.ops.object.shade_smooth(); v.parent = head
            ball((0, ly - 0.178, hz + 0.21), (0.028, 0.008, 0.028), WHT, head); ball((0.011, ly - 0.184, hz + 0.217), (0.024, 0.008, 0.024), PU, head)
        for sd in (-1, 1): ball((sd * 0.178, ly - 0.03, hz + 0.02), (0.03, 0.05, 0.06), M("hair2", (0.03, 0.025, 0.025), 0, 0.7), head)                 # sideburns under the cap   # the moon badge
        # ---- the face is DRAWN, then projected onto the front of the head: clean cartoon eyes, brows and a real mouth ----
        import os as _os
        from PIL import Image as _I, ImageDraw as _D, ImageFilter as _F
        S_ = 2048; fc = _I.new("RGBA", (S_, S_), (0, 0, 0, 0)); d = _D.Draw(fc)
        X = lambda x: (x + 1) / 2 * S_
        Z = lambda z: (1 - (z + 1) / 2) * S_
        R_ = lambda r: r / 2 * S_
        INK = (34, 22, 22, 255); glow = (255, 255, 255, 255)
        def ell(cx, cz, rx, rz, **kw): d.ellipse((X(cx) - R_(rx), Z(cz) - R_(rz), X(cx) + R_(rx), Z(cz) + R_(rz)), **kw)
        for sd in (-1, 1):
            ex, ez = sd * 0.37, 0.0; rx, rz = 0.18, 0.2 * wide
            if dark: ell(ex, ez, rx * 1.05, rz * 1.05, fill=glow); continue
            ell(ex, ez, rx + 0.022, rz + 0.022, fill=INK); ell(ex, ez, rx, rz, fill=(252, 250, 246, 255))                    # outlined white
            ix, iz = ex + look[0] * 0.06, ez - 0.02 + look[1] * 0.06; ir = 0.118 if wide < 1.15 else 0.092                     # the iris shrinks when he is scared
            ell(ix, iz, ir, ir * 1.08, fill=(92, 52, 28, 255)); ell(ix, iz, ir * 0.82, ir * 0.9, fill=(58, 30, 16, 255)); ell(ix, iz, ir * 0.5, ir * 0.55, fill=(14, 10, 10, 255))
            ell(ix + 0.04, iz + 0.05, 0.034, 0.038, fill=(255, 255, 255, 255)); ell(ix - 0.035, iz - 0.045, 0.016, 0.018, fill=(255, 255, 255, 230))
            d.arc((X(ex) - R_(rx + 0.03), Z(ez) - R_(rz + 0.03), X(ex) + R_(rx + 0.03), Z(ez) + R_(rz + 0.03)), 195, 345, fill=INK, width=int(R_(0.04)))   # a thicker upper lash line
            bz = 0.3 + brow_up * 0.05                                                                                       # brows: thick, rounded; the inner end rises with worry
            p0 = (X(ex - sd * 0.15), Z(bz + brow * 0.2)); p1 = (X(ex + sd * 0.17), Z(bz - brow * 0.06))
            d.line((p0, p1), fill=INK, width=int(R_(0.056)))
            for px_, pz_ in (p0, p1): d.ellipse((px_ - R_(0.028), pz_ - R_(0.028), px_ + R_(0.028), pz_ + R_(0.028)), fill=INK)
        mz = -0.5
        if dark:                                                     # the double: a grin too wide, teeth one by one
            d.pieslice((X(0) - R_(0.5), Z(mz + 0.3) - R_(0.42), X(0) + R_(0.5), Z(mz + 0.3) + R_(0.42)), 20, 160, fill=glow)
            d.rectangle((X(-0.5), Z(mz + 0.3) - 2, X(0.5), Z(mz + 0.3) + R_(0.115)), fill=(0, 0, 0, 0))
            for q in range(-4, 5): d.line((X(q * 0.092), Z(mz + 0.2), X(q * 0.092), Z(mz - 0.15)), fill=(0, 0, 0, 0), width=int(R_(0.014)))
        elif mouth == "o":                                           # a gasp: rounded mouth, teeth on top, tongue at the bottom, a clean outline
            mk = _I.new("L", (S_, S_), 0); md = _D.Draw(mk); bx = (X(0) - R_(0.135), Z(mz) - R_(0.17), X(0) + R_(0.135), Z(mz) + R_(0.17)); md.ellipse(bx, fill=255)
            inner = _I.new("RGBA", (S_, S_), (108, 22, 34, 255)); di = _D.Draw(inner)
            di.rectangle((X(-0.2), Z(mz) - R_(0.2), X(0.2), Z(mz) - R_(0.105)), fill=(250, 250, 246, 255))                                             # teeth
            di.ellipse((X(0) - R_(0.1), Z(mz - 0.13) - R_(0.085), X(0) + R_(0.1), Z(mz - 0.13) + R_(0.085)), fill=(236, 112, 124, 255))                # tongue
            fc.paste(inner, (0, 0), mk); d = _D.Draw(fc); d.ellipse(bx, outline=INK, width=int(R_(0.03)))
        else:                                                        # closed and worried: one smooth line that dips, corners turned down
            pts = [(X(a * 0.15), Z(mz + 0.035 - 0.07 * a * a)) for a in [q / 20 - 1 for q in range(41)]]
            d.line(pts, fill=INK, width=int(R_(0.042)), joint="curve")
            for a in (-1, 1): ell(a * 0.15, mz - 0.035, 0.021, 0.021, fill=INK)
        if not dark:
            bl = _I.new("RGBA", (S_, S_), (0, 0, 0, 0)); bd = _D.Draw(bl)
            for sd in (-1, 1): bd.ellipse((X(sd * 0.62) - R_(0.14), Z(-0.26) - R_(0.1), X(sd * 0.62) + R_(0.14), Z(-0.26) + R_(0.1)), fill=(238, 112, 104, 120))
            fc = _I.alpha_composite(bl.filter(_F.GaussianBlur(S_ * 0.02)), fc)
        fpath = _os.path.join(_os.path.dirname(OUT), "face_%s_%s.png" % (name, _os.path.basename(OUT)))
        fc.resize((1024, 1024), _I.LANCZOS).save(fpath)
        FM = bpy.data.materials.new(name + "face"); FM.use_nodes = True; nt = FM.node_tree; Nn = nt.nodes; Ll = nt.links; bs = Nn["Principled BSDF"]
        tc = Nn.new("ShaderNodeTexCoord"); sp_ = Nn.new("ShaderNodeSeparateXYZ"); Ll.new(tc.outputs["Object"], sp_.inputs["Vector"])
        def half(sock):
            n_ = Nn.new("ShaderNodeMath"); n_.operation = "MULTIPLY_ADD"; n_.inputs[1].default_value = 0.5; n_.inputs[2].default_value = 0.5; Ll.new(sock, n_.inputs[0]); return n_.outputs[0]
        cb = Nn.new("ShaderNodeCombineXYZ"); Ll.new(half(sp_.outputs["X"]), cb.inputs["X"]); Ll.new(half(sp_.outputs["Z"]), cb.inputs["Y"])
        im_ = Nn.new("ShaderNodeTexImage"); im_.image = bpy.data.images.load(fpath); im_.extension = "CLIP"; Ll.new(cb.outputs["Vector"], im_.inputs["Vector"])
        front = Nn.new("ShaderNodeMath"); front.operation = "LESS_THAN"; front.inputs[1].default_value = -0.2; Ll.new(sp_.outputs["Y"], front.inputs[0])
        fac = Nn.new("ShaderNodeMath"); fac.operation = "MULTIPLY"; Ll.new(im_.outputs["Alpha"], fac.inputs[0]); Ll.new(front.outputs[0], fac.inputs[1])
        mx = Nn.new("ShaderNodeMix"); mx.data_type = "RGBA"; Ll.new(fac.outputs[0], mx.inputs["Factor"]); mx.inputs["A"].default_value = ((0.012, 0.013, 0.017, 1) if dark else (0.62, 0.34, 0.2, 1)); Ll.new(im_.outputs["Color"], mx.inputs["B"])
        Ll.new(mx.outputs["Result"], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.5
        if dark:
            bs.inputs["Emission Color"].default_value = (1, 1, 1, 1); em = Nn.new("ShaderNodeMath"); em.operation = "MULTIPLY"; em.inputs[1].default_value = 5.0; Ll.new(fac.outputs[0], em.inputs[0]); Ll.new(em.outputs[0], bs.inputs["Emission Strength"])
        hb.data.materials.clear(); hb.data.materials.append(FM)
        head.rotation_euler = (pitch, 0, yaw); k = h / 1.74; root.scale = (k, k, k); root.rotation_euler = (lean * 0.35, 0, face); root.location = loc
        return root

    FL = mat("vfloor", (0.8, 0.81, 0.83), 0, 0.14)
    LEAF = mat("leaf", (0.12, 0.2, 0.12), 0, 0.6); POT = mat("pot", (0.15, 0.15, 0.16), 0, 0.5)
    PAPER = mat("vpaper", (0.92, 0.92, 0.9), 0, 0.8)

    MODELS = "/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/models/"

    def prop(name, loc, height, rz=0.0, fit="z"):
        """Import a real Poly Haven model, scale it to a height in metres, stand it on loc."""
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=f"{MODELS}{name}/{name}.gltf")
        new = [o for o in bpy.data.objects if o not in before]
        root = bpy.data.objects.new(name + "_root", None); bpy.context.collection.objects.link(root)
        for o in new:
            if o.parent is None: o.parent = root
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ mathutils.Vector(c) for o in new if o.type == "MESH" for c in o.bound_box]
        zmin, zmax = min(p.z for p in pts), max(p.z for p in pts)
        cx_ = (min(p.x for p in pts) + max(p.x for p in pts)) / 2; cy_ = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
        ext = max(max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts), zmax - zmin)
        k = height / max(1e-3, ext if fit == "max" else zmax - zmin)      # flat objects (notepads, binders) are sized by their longest side
        for o in new:
            if o.parent is root: o.location = (o.location.x - cx_, o.location.y - cy_, o.location.z - zmin)
        root.scale = (k, k, k); root.location = loc; root.rotation_euler = (0, 0, rz)
        return root

    def plant(x, y, s_=1.0):
        return prop("potted_plant_01" if rnd.random() < 0.5 else "potted_plant_04", (x, y, 0), 1.25 * s_, rnd.uniform(0, 6.28))
        cyl("pot", (x, y, 0.25 * s_), 0.22 * s_, 0.5 * s_, POT)
        for k in range(9):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22 * s_, location=(x + rnd.uniform(-.2, .2) * s_, y + rnd.uniform(-.2, .2) * s_, (0.65 + rnd.uniform(0, 0.7)) * s_))
            o = bpy.context.object; o.scale = (1, 1, 1.5); o.data.materials.append(LEAF); bpy.ops.object.shade_smooth()

    def windows(xw, y0, d, h):
        """Replace the left wall by a glazed facade: mullions throw hard stripes of daylight across the floor."""
        for o in [o for o in bpy.data.objects if o.name.startswith("wl")]: bpy.data.objects.remove(o)
        box("sill", (xw, y0 + d / 2, 0.15), (0.12, d, 0.3), GREY); box("lintel", (xw, y0 + d / 2, h - 0.2), (0.12, d, 0.4), GREY)
        for k in range(int(d / 0.9) + 1):
            box("mull", (xw, y0 + k * 0.9, h / 2), (0.1, 0.07, h), GREY)
        box("transom", (xw, y0 + d / 2, h * 0.62), (0.1, d, 0.05), GREY)
        if "--evening" in sys.argv:   # 18:00 in November: night outside, only the neons inside
            sky = mat("sky", (0.02, 0.03, 0.06), 0, 0.5, (0.12, 0.17, 0.35), 0.35); sb = box("skybox", (xw - 3, y0 + d / 2, h / 2), (0.05, d + 6, h + 4), sky); sb.visible_shadow = False
            return
        sky = mat("sky", (1, 1, 1), 0, 0.5, (0.8, 0.88, 1.0), 2.2); sb = box("skybox", (xw - 3, y0 + d / 2, h / 2), (0.05, d + 6, h + 4), sky); sb.visible_shadow = False
        sun = light("SUN", (xw - 5, y0 + d / 2, h + 3), 7.0, (1.0, 0.96, 0.9), 0.015)
        sun.rotation_euler = mathutils.Vector((1.0, 0.35, -0.55)).to_track_quat("-Z", "Y").to_euler()

    def ceiling_grid(w, y0, d, h):
        TL = mat("tileline", (0.7, 0.71, 0.73), 0, 0.5)
        for k in range(int(w / 1.2) + 1): box("tile", (-w / 2 + k * 1.2, y0 + d / 2, h - 0.03), (0.01, d, 0.01), TL)
        for k in range(int(d / 1.2) + 1): box("tile", (0, y0 + k * 1.2, h - 0.03), (w, 0.01, 0.01), TL)
    def room(w, d, h, y0=0):
        box("floor", (0, y0 + d / 2, -0.02), (w, d, 0.04), FL); box("ceil", (0, y0 + d / 2, h), (w, d, 0.04), WH)
        box("wl", (-w / 2, y0 + d / 2, h / 2), (0.04, d, h), WH); box("wr", (w / 2, y0 + d / 2, h / 2), (0.04, d, h), WH)
        box("wb", (0, y0 + d, h / 2), (w, 0.04, h), WH)
        for k in range(int(d / 2)):
            box("neon", (0, y0 + 1 + k * 2, h - 0.02), (w * 0.7, 0.12, 0.02), NEON)
            light("AREA", (0, y0 + 1 + k * 2, h - 0.05), 120, (0.88, 0.94, 1.0), 1.2)
    if view == "hall":
        room(9, 9, 4)
        bpy.ops.object.text_add(location=(0, 8.97, 2.6)); t = bpy.context.object
        t.data.body = "VALMONT"; t.data.size = 0.75; t.data.align_x = "CENTER"; t.data.extrude = 0.03; t.rotation_euler = (math.radians(90), 0, 0)
        t.data.materials.append(GREY)
        box("redline", (0, 8.97, 2.25), (4.6, 0.02, 0.05), RED)
        for x in (-1.8, -0.6, 0.6, 1.8):
            box("gate", (x, 4.0, 0.5), (0.18, 1.0, 1.0), GREY)
            box("glassdoor", (x + 0.3, 4.0, 0.75), (0.42, 0.02, 0.5), GL)
            box("reader", (x, 3.52, 1.02), (0.12, 0.04, 0.1), BLK)
        box("desk", (-3, 6.5, 0.55), (2.2, 0.8, 1.1), WH); box("desktop", (-3, 6.5, 1.12), (2.4, 0.95, 0.05), GREY)
        box("deskscreen", (-3.3, 6.6, 1.32), (0.5, 0.03, 0.32), BLK)
        windows(-4.5, 0, 9, 4); ceiling_grid(9, 0, 9, 4)
        for x in (-2.7, 2.7):
            box("pillar", (x, 2.0, 2), (0.5, 0.5, 4), WH)
        plant(3.6, 7.8, 1.3); plant(-3.9, 3.0, 1.1); plant(3.7, 2.2, 1.0)
        box("bench", (3.4, 5.0, 0.24), (0.55, 2.2, 0.08), GREY)
        for y in (4.3, 5.7): prop("modern_arm_chair_01", (3.7, y, 0), 0.85, math.radians(-90))
        box("rug", (3.3, 5.0, 0.003), (1.8, 2.8, 0.006), TEAL)
        for y in (4.2, 5.8): box("benchleg", (3.4, y, 0.12), (0.5, 0.06, 0.24), BLK)
        box("frame", (4.47, 6.5, 2.0), (0.04, 1.6, 1.0), BLK); box("art", (4.44, 6.5, 2.0), (0.02, 1.45, 0.85), mat("art", (0.7, 0.05, 0.05), 0, 0.6))
        box("cam_dome", (3.9, 0.6, 3.9), (0.18, 0.18, 0.12), BLK)
        cam = camera((-0.6, -0.8, 1.6), (0.2, 8.5, 1.5), 24)
    elif view == "gate":   # 18:00, the lobby: polished tiles, steel turnstiles, the glass exit doors and the night just behind them
        room(9, 9, 4); windows(-4.5, 0, 9, 4); ceiling_grid(9, 0, 9, 4)
        TILE = mat("tile", (0.74, 0.75, 0.77), 0, 0.07); JOINT = mat("joint", (0.45, 0.46, 0.48), 0, 0.5)
        for o in [o for o in bpy.data.objects if o.name.startswith("floor")]: o.data.materials.clear(); o.data.materials.append(TILE)
        for k in range(16):
            box("jx", (-4.5 + k * 0.6, 4.5, 0.001), (0.008, 9, 0.002), JOINT); box("jy", (0, k * 0.6, 0.001), (9, 0.008, 0.002), JOINT)
        # back wall rebuilt around the exit doors
        for o in [o for o in bpy.data.objects if o.name.startswith("wb")]: bpy.data.objects.remove(o)
        box("wbl", (-2.1, 9, 2), (4.8, 0.04, 4), WH); box("wbr", (3.6, 9, 2), (1.8, 0.04, 4), WH); box("wbt", (1.5, 9, 3.25), (2.4, 0.04, 1.5), WH)
        for x in (0.3, 1.5, 2.7): box("exfr", (x, 8.98, 1.25), (0.07, 0.08, 2.5), ANTH)
        box("exfrt", (1.5, 8.98, 2.5), (2.47, 0.08, 0.08), ANTH)
        for x in (0.9, 2.1):
            box("exglass", (x, 8.98, 1.25), (1.13, 0.015, 2.42), GL); box("exbar", (x, 8.93, 1.05), (0.9, 0.04, 0.05), STEELB)
            box("exlock", (x + (0.5 if x < 1.5 else -0.5), 8.93, 1.05), (0.06, 0.05, 0.16), mat("lockr", (0.3, 0, 0), 0, 0.3, (1.0, 0.05, 0.03), 14))      # both doors locked: red
        box("exsign", (1.5, 8.94, 2.75), (0.7, 0.03, 0.22), mat("exitg3", (0, 0.2, 0.05), 0, 0.4, (0.1, 1.0, 0.3), 10))
        box("mat", (1.5, 8.0, 0.004), (2.6, 1.4, 0.008), mat("doormat", (0.07, 0.07, 0.08), 0, 0.95))
        # the night outside: wet pavement, a street lamp, lit windows far away
        box("pave", (1.5, 25, -0.03), (50, 32, 0.04), mat("pave", (0.05, 0.05, 0.06), 0, 0.15))
        cyl("lamp", (2.9, 12.3, 2.2), 0.05, 4.4, BLK); light("POINT", (2.5, 12.0, 4.1), 320, (1.0, 0.72, 0.4), 0.15)
        box("lamph", (2.6, 12.25, 4.35), (0.6, 0.16, 0.08), mat("lamph", (1, 1, 1), 0, 0.3, (1.0, 0.75, 0.45), 30))
        for k in range(16):
            box("citywin", (rnd.uniform(-14, 18), rnd.uniform(30, 40), rnd.uniform(0.6, 11)), (rnd.uniform(0.3, 0.6), 0.05, rnd.uniform(0.4, 0.8)),
                mat("cw%d" % k, (1, 1, 1), 0, 0.5, rnd.choice([(1.0, 0.7, 0.35), (0.6, 0.75, 1.0), (1.0, 0.8, 0.5)]), rnd.uniform(0.8, 2.2)))
        box("citybody", (1.5, 41, 7), (50, 1, 16), mat("cityb", (0.01, 0.012, 0.02), 0, 0.8))
        # signage
        bpy.ops.object.text_add(location=(-2.1, 8.97, 2.6)); t = bpy.context.object
        t.data.body = "VALMONT"; t.data.size = 0.7; t.data.align_x = "CENTER"; t.data.extrude = 0.03; t.rotation_euler = (math.radians(90), 0, 0); t.data.materials.append(GREY)
        box("redline", (-2.1, 8.97, 2.25), (4.2, 0.02, 0.05), RED)
        prop("wall_clock", (3.75, 8.93, 2.5), 0.42, 0)
        # turnstiles: brushed steel bodies, black glass tops, glass wings, red closed bars
        OPENF = "--open" in sys.argv        # 17:59 again: every light turns green, the exit doors swing open
        LEDR = mat("ledr", (0.5, 0, 0), 0, 0.3, (0.1, 1.0, 0.25) if OPENF else (1.0, 0.05, 0.03), 60); LEDS = mat("leds", (0.4, 0, 0), 0, 0.3, (0.1, 1.0, 0.3) if OPENF else (1.0, 0.06, 0.03), 9)
        if OPENF:
            for o in [o for o in bpy.data.objects if o.name.startswith(("exglass", "exbar", "exlock"))]: bpy.data.objects.remove(o)
            for x, sd in ((0.33, -1), (2.67, 1)):       # the two leaves pushed outwards
                box("exleaf", (x + sd * 0.06, 9.55, 1.25), (0.02, 1.13, 2.42), GL); box("exleafbar", (x + sd * 0.03, 9.55, 1.05), (0.04, 0.9, 0.05), STEELB)
        BGL = mat("bglass", (0.02, 0.02, 0.025), 0.4, 0.04)
        for x in (-1.8, -0.6, 0.6, 1.8):
            box("gate", (x, 4.0, 0.5), (0.2, 1.3, 1.0), STEELB); box("gtop", (x, 4.0, 1.012), (0.22, 1.32, 0.025), BGL)
            box("gbase", (x, 4.0, 0.03), (0.26, 1.36, 0.06), ANTH)
            box("gstrip", (x - 0.102, 4.0, 0.62), (0.006, 1.1, 0.03), LEDS); box("gstrip", (x + 0.102, 4.0, 0.62), (0.006, 1.1, 0.03), LEDS)
            box("glassdoor", (x + 0.33, 4.0, 0.72), (0.46, 0.012, 0.62), GL); box("gwtop", (x + 0.33, 4.0, 1.04), (0.46, 0.02, 0.02), LEDS)
            box("reader", (x, 3.36, 1.035), (0.13, 0.11, 0.03), BLK); box("led", (x, 3.36, 1.052), (0.075, 0.03, 0.004), LEDR)
            box("readerscr", (x, 3.44, 1.027), (0.1, 0.05, 0.004), mat("rscr%d" % int(x * 10), (0.02, 0.02, 0.02), 0, 0.1, (1.0, 0.1, 0.05), 3))
            cyl("gcross", (x, 3.34, 0.75), 0.05, 0.012, LEDS, (math.radians(90), 0, 0))
        light("POINT", (0.6, 3.25, 1.2), 1.4, (0.1, 1.0, 0.3) if OPENF else (1.0, 0.1, 0.05), 0.05)
        for x, y in ((-2.5, 2.9), (-2.5, 1.7), (2.5, 2.9), (2.5, 1.7)):              # queue posts with red belts
            cyl("post", (x, y, 0.5), 0.025, 1.0, STEELB); cyl("postb", (x, y, 0.015), 0.16, 0.03, STEELB); cyl("postc", (x, y, 1.0), 0.04, 0.05, BLK)
        for x in (-2.5, 2.5): box("belt", (x, 2.3, 0.93), (0.006, 1.2, 0.05), RED)
        for x in (-2.7, 2.7): box("pillar", (x, 6.0, 2), (0.5, 0.5, 4), WH); 
        # reception and waiting corner
        box("desk", (-3, 6.5, 0.55), (2.2, 0.8, 1.1), WH); box("desktop", (-3, 6.5, 1.12), (2.4, 0.95, 0.05), OAK); box("deskfront", (-3, 6.08, 0.55), (2.2, 0.02, 0.9), TEAL)
        box("deskscreen", (-3.3, 6.6, 1.38), (0.55, 0.03, 0.34), BLK); box("deskscr", (-3.3, 6.58, 1.38), (0.5, 0.005, 0.29), mat("dscr", (0.05, 0.06, 0.08), 0, 0.2, (0.55, 0.7, 0.95), 2.5))
        prop("desk_lamp_arm_01", (-2.3, 6.55, 1.145), 0.5, 2.2, fit="max"); prop("office_notepads", (-2.75, 6.35, 1.145), 0.32, 0.4, fit="max")
        prop("modern_arm_chair_01", (3.6, 6.9, 0), 0.85, math.radians(-110)); prop("modern_arm_chair_01", (3.7, 5.6, 0), 0.85, math.radians(-80))
        box("rug", (3.4, 6.2, 0.003), (1.7, 2.6, 0.006), TEAL); plant(3.9, 8.2, 1.3); plant(-0.4, 8.5, 1.1); plant(-4.0, 3.0, 1.1)
        prop("korean_fire_extinguisher_01", (4.3, 4.4, 0), 0.6, math.radians(-90)); prop("metal_trash_can", (2.95, 7.6, 0), 0.55)
        prop("hanging_picture_frame_01", (4.46, 6.3, 1.6), 0.7, math.radians(-90))
        cyl("camarm", (2.6, 8.9, 3.3), 0.02, 0.3, GREY, (math.radians(90), 0, 0)); box("cambody", (2.6, 8.7, 3.25), (0.1, 0.24, 0.1), WH, (0.3, 0, 0.3)); cyl("camled", (2.63, 8.58, 3.2), 0.012, 0.01, LEDR, (math.radians(90), 0, 0))
        for x in (-1.2, 1.2): light("SPOT", (x, 3.6, 3.9), 220, (0.92, 0.96, 1.0), 0.1, (0, 0, 0), 70)
        cam = camera((0.22, 2.2, 1.42), (0.95, 5.6, 1.0), 23)
        if "--exitcam" in sys.argv: cam = camera((1.35, 5.2, 1.45), (1.6, 9.6, 1.2), 24)        # past the gates, facing the open doors and the street
        if "--clockcam" in sys.argv: cam = camera((3.2, 7.2, 1.7), (3.75, 8.93, 2.5), 40)       # looking up at the lobby wall clock
        import json as _j
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update(); v = world_to_camera_view(sc, cam, mathutils.Vector((0.6, 3.36, 1.055)))
        g0 = world_to_camera_view(sc, cam, mathutils.Vector((2.3, 11.6, 0.0))); g1 = world_to_camera_view(sc, cam, mathutils.Vector((2.3, 11.6, 1.15)))
        c0 = world_to_camera_view(sc, cam, mathutils.Vector((3.75, 8.93, 2.5))); c1 = world_to_camera_view(sc, cam, mathutils.Vector((3.75, 8.93, 2.71)))
        _j.dump({"x": v.x, "y": 1 - v.y, "girl": [g0.x, 1 - g0.y, g1.x, 1 - g1.y], "clock": [c0.x, 1 - c0.y, c1.x, 1 - c1.y]}, open(OUT + "led.json", "w"))
    elif view in ("bed_door", "bed_window"):   # LIVREUR DE NUIT, nuit 3: his childhood bedroom; --home=dark|lit as for the flat
        import json as _j
        from bpy_extras.object_utils import world_to_camera_view
        lit = ARG("--home") == "lit"
        PARQ = tex_mat("parq", "herringbone_parquet", 1.6, (0.9, 0.78, 0.66), 0.4); WALLB = mat("wallb", (0.42, 0.55, 0.68), 0, 0.85); PAINT = mat("paint", (0.78, 0.76, 0.7), 0, 0.85)
        box("bfl", (0, 1.7, -0.01), (3.2, 3.4, 0.02), PARQ); box("bce", (0, 1.7, 2.5), (3.2, 3.4, 0.02), PAINT)
        for sx in (-1, 1): box("bwl", (sx * 1.61, 1.7, 1.25), (0.02, 3.4, 2.5), WALLB)
        box("bfront", (0, -0.01, 1.25), (3.2, 0.02, 2.5), WALLB)
        box("bback_l", (-0.5, 3.41, 1.25), (2.2, 0.02, 2.5), WALLB); box("bback_r", (1.45, 3.41, 1.25), (0.3, 0.02, 2.5), WALLB)
        box("bback_b", (0.95, 3.41, 0.45), (0.7, 0.02, 0.9), WALLB); box("bback_t", (0.95, 3.41, 2.2), (0.7, 0.02, 0.6), WALLB)
        win_open = "--winopen" in sys.argv
        for x in (0.62, 1.28): box("bwf", (x, 3.42, 1.4), (0.05, 0.06, 1.0), PAINT)
        box("bwft", (0.95, 3.42, 1.9), (0.7, 0.06, 0.05), PAINT); box("bwfb", (0.95, 3.42, 0.9), (0.7, 0.08, 0.05), PAINT)
        if win_open: box("bwleaf", (1.05, 3.1, 1.4), (0.04, 0.6, 0.95), GL, (0, 0, math.radians(-50)))
        else: box("bwglass", (0.95, 3.42, 1.4), (0.62, 0.01, 0.95), mat("bglass", (0.04, 0.06, 0.1), 0, 0.04))
        box("city", (0, 9, 2), (14, 0.1, 8), mat("night", (0.01, 0.015, 0.03), 0, 1, (0.04, 0.06, 0.12), 1.0))
        for k in range(60): box("cw", (rnd.uniform(-4, 5), 8.9, rnd.uniform(-1.5, 3.5)), (0.25, 0.02, 0.3), mat("bcw%d" % k, (1, 1, 1), 0, 0.5, rnd.choice([(1.0, 0.7, 0.35), (0.5, 0.65, 1.0)]), rnd.uniform(0.6, 2.0)))
        CURT = mat("curt", (0.7, 0.25, 0.22), 0, 0.95)
        for k, x in enumerate((0.5, 1.4)): box("curt", (x + (0.08 if win_open and k else 0), 3.3, 1.35), (0.18, 0.08 + (0.12 if win_open else 0), 1.4), CURT, (0, 0, math.radians(15 if win_open and k else 0)))
        # the bed of a child who grew up: low frame, blue duvet, a pillow, a worn plush rabbit
        WOOD = mat("bwood", (0.55, 0.38, 0.24), 0, 0.6)
        box("bedf", (-1.15, 1.9, 0.18), (0.95, 2.0, 0.36), WOOD); box("bedm", (-1.15, 1.9, 0.42), (0.9, 1.95, 0.14), mat("matt", (0.9, 0.9, 0.88), 0, 0.8))
        box("duvet", (-1.15, 1.7, 0.52), (0.94, 1.5, 0.1), mat("duvet", (0.2, 0.3, 0.6), 0, 0.9)); box("pillow", (-1.15, 2.7, 0.55), (0.7, 0.35, 0.14), mat("pillow", (0.92, 0.92, 0.9), 0, 0.8))
        box("headb", (-1.15, 2.92, 0.6), (0.95, 0.06, 0.8), WOOD)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(-0.95, 2.6, 0.7)); o = bpy.context.object; o.data.materials.append(mat("rabbit", (0.85, 0.82, 0.78), 0, 0.95))
        for sx in (-1, 1): box("ear", (-0.95 + sx * 0.04, 2.6, 0.86), (0.03, 0.02, 0.14), mat("rabbit2", (0.85, 0.82, 0.78), 0, 0.95))
        prop("SchoolDesk_01", (1.25, 1.2, 0), 0.75, math.radians(90)); prop("SchoolChair_01", (0.85, 1.2, 0), 0.85, math.radians(-90))
        prop("alarm_clock_01", (1.25, 1.45, 0.76), 0.12); prop("Shelf_01", (1.5, 2.5, 0), 1.6, math.radians(90))
        for k, (x, z, c) in enumerate(((-1.0, 1.55, (0.85, 0.3, 0.2)), (-1.35, 1.65, (0.2, 0.5, 0.85)), (1.55, 1.85, (0.95, 0.75, 0.2)))):
            if x < 0: box("poster", (x, 3.39, z), (0.4, 0.01, 0.55), mat("pst%d" % k, c, 0, 0.7))
            else: box("poster", (1.59, 1.1, z), (0.01, 0.45, 0.6), mat("pst%d" % k, c, 0, 0.7))
        for k in range(26):                                           # glow-in-the-dark stars on the ceiling, from when he was small
            box("star", (rnd.uniform(-1.4, 1.4), rnd.uniform(0.6, 3.2), 2.485), (0.05, 0.05, 0.005), mat("star%d" % k, (0.8, 1, 0.8), 0, 0.5, (0.55, 1.0, 0.6), 2.5 if not lit else 0.3), (0, 0, rnd.uniform(0, 1)))
        box("rug", (0, 1.6, 0.006), (1.4, 1.0, 0.01), mat("brug", (0.6, 0.45, 0.2), 0, 0.95))
        cyl("sock", (0, 1.7, 2.44), 0.035, 0.08, BLK)                  # the empty socket
        box("switch", (-0.75, 0.0, 1.1), (0.08, 0.02, 0.12), mat("switch", (0.9, 0.9, 0.88), 0, 0.4))
        mo = light("AREA", (0.95, 4.0, 1.5), 150 if not win_open else 190, (0.55, 0.68, 1.0), 0.9, (math.radians(90), 0, math.radians(180))); mo.visible_camera = False
        light("POINT", (-0.2, 1.4, 2.2), 6 if not lit else 0, (0.5, 0.62, 1.0), 1.2)
        if lit: light("AREA", (0, 0.3, 1.7), 220, (0.95, 0.97, 1.0), 1.2, (math.radians(-90), 0, 0)); light("POINT", (0, 1.7, 2.2), 60, (1.0, 0.96, 0.9), 0.5)
        if view == "bed_door": cam = camera((-0.1, 0.2, 1.55), (0.15, 3.4, 1.15), 19)
        else: cam = camera((-0.3, 1.2, 1.4), (0.95, 3.4, 1.35), 26)
        bpy.context.view_layer.update(); pos = {}
        for k_, pt in (("grin", (-0.5, 3.39, 1.55)), ("window", (0.95, 3.41, 1.4)), ("switch", (-0.75, 0.0, 1.1)), ("bed", (-1.15, 1.9, 0.55)), ("floor", (-0.3, 2.2, 0.0))):
            v = world_to_camera_view(sc, cam, mathutils.Vector(pt)); pos[k_] = [v.x, 1 - v.y]
        _j.dump(pos, open(OUT + "pos.json", "w"))
    elif view in ("home_entry", "home_kitchen"):   # LIVREUR DE NUIT, nuit 2: his mother's flat. --home=dark (moonlight only) or lit (even fill, revealed by the phone torch in 2D)
        import json as _j
        from bpy_extras.object_utils import world_to_camera_view
        lit = ARG("--home") == "lit"
        PARQ = tex_mat("parq", "herringbone_parquet", 1.6, (0.9, 0.78, 0.66), 0.4); WALLP = tex_mat("wallp", "decrepit_wallpaper", 1.1, (0.8, 0.82, 0.78), 0.3)
        TILEK = tex_mat("tilek", "long_white_tiles", 1.4, (0.86, 0.86, 0.84), 0.4); PAINT = mat("paint", (0.72, 0.7, 0.64), 0, 0.85)
        # corridor: y 0..5, x -0.65..0.65
        box("cfl", (0, 2.5, -0.01), (1.3, 5, 0.02), PARQ); box("cce", (0, 2.5, 2.5), (1.3, 5, 0.02), PAINT)
        for sx in (-1, 1): box("cwl", (sx * 0.66, 2.5, 1.25), (0.02, 5, 2.5), WALLP); box("csk", (sx * 0.645, 2.5, 0.05), (0.02, 5, 0.1), mat("skirt%d" % sx, (0.85, 0.84, 0.8), 0, 0.5))
        box("cend_l", (-0.55, 5.0, 1.25), (0.22, 0.04, 2.5), WALLP); box("cend_r", (0.55, 5.0, 1.25), (0.22, 0.04, 2.5), WALLP); box("cend_t", (0, 5.0, 2.3), (0.9, 0.04, 0.4), WALLP)
        for y in (1.0, 2.5, 4.0):                                     # bare ceiling sockets: the bulbs have been unscrewed
            cyl("sock", (0, y, 2.44), 0.035, 0.08, BLK); cyl("wire", (0, y, 2.47), 0.006, 0.05, BLK)
        door(-0.66, 3.0, 1, w=0.85, m=OAK); box("hook", (0.63, 1.4, 1.75), (0.04, 0.7, 0.04), BRASS)
        box("coat", (0.58, 1.25, 1.35), (0.1, 0.32, 0.75), mat("coat", (0.25, 0.08, 0.1), 0, 0.9)); box("coat2", (0.58, 1.6, 1.4), (0.1, 0.3, 0.65), mat("coat2", (0.32, 0.3, 0.26), 0, 0.9))
        box("shoes", (0.5, 2.2, 0.06), (0.22, 0.3, 0.1), mat("shoe", (0.15, 0.12, 0.1), 0, 0.6)); box("rug", (0, 1.2, 0.006), (0.8, 1.6, 0.01), mat("rug", (0.35, 0.12, 0.1), 0, 0.95))
        prop("hanging_picture_frame_02", (0.64, 3.6, 1.45), 0.45, math.radians(-90))
        # kitchen: y 5..9.2, x -1.8..1.8
        box("kfl", (0, 7.1, -0.01), (3.6, 4.2, 0.02), TILEK); box("kce", (0, 7.1, 2.5), (3.6, 4.2, 0.02), PAINT)
        for sx in (-1, 1): box("kwl", (sx * 1.81, 7.1, 1.25), (0.02, 4.2, 2.5), PAINT)
        box("kback_l", (-1.15, 9.2, 1.25), (1.3, 0.04, 2.5), PAINT); box("kback_r", (1.15, 9.2, 1.25), (1.3, 0.04, 2.5), PAINT); box("kback_b", (0, 9.2, 0.45), (1.0, 0.04, 0.9), PAINT); box("kback_t", (0, 9.2, 2.3), (1.0, 0.04, 0.4), PAINT)
        box("wsill", (0, 9.15, 0.92), (1.1, 0.12, 0.04), mat("sill", (0.85, 0.85, 0.82), 0, 0.4))
        for x in (-0.5, 0.0, 0.5): box("wfr", (x, 9.18, 1.5), (0.04, 0.05, 1.2), mat("wfr", (0.8, 0.8, 0.78), 0, 0.5))
        box("city", (0, 13, 2), (14, 0.1, 8), mat("night", (0.01, 0.015, 0.03), 0, 1, (0.04, 0.06, 0.12), 1.0))
        for k in range(90): box("cw", (rnd.uniform(-4, 4), 12.9, rnd.uniform(0.2, 3.8)), (0.25, 0.02, 0.3), mat("cw%d" % k, (1, 1, 1), 0, 0.5, rnd.choice([(1.0, 0.7, 0.35), (0.5, 0.65, 1.0)]), rnd.uniform(0.6, 2.0)))
        prop("dining_table", (0, 7.45, 0), 0.76, 0)
        CH_ROT = float(ARG("--chairrot") or 0)
        prop("dining_chair_02", (-0.45, 8.15, 0), 0.95, math.radians(CH_ROT)); prop("dining_chair_02", (0.85, 8.3, 0) if "--bag" in sys.argv else (0.45, 8.15, 0), 0.95, math.radians(CH_ROT + (35 if "--bag" in sys.argv else 0)))
        if "--bag" in sys.argv:                                       # his delivery bag on the pulled-out chair
            BAGM = mat("kbag", (0.75, 0.42, 0.12), 0, 0.8); bx, by, bz = 0.86, 8.25, 0.47
            box("kbag", (bx, by, bz + 0.17), (0.32, 0.22, 0.34), BAGM, (0, 0, math.radians(-20))); box("kbagt", (bx, by, bz + 0.35), (0.2, 0.02, 0.07), mat("kbagh", (0.6, 0.32, 0.08), 0, 0.8), (0, 0, math.radians(-20)))
            box("kbagl", (bx - 0.03, by - 0.11, bz + 0.2), (0.16, 0.005, 0.12), WH, (0, 0, math.radians(-20)))
        prop("carved_wooden_plate", (-0.62, 7.45, 0.8), 0.26, 0, fit="max"); prop("carved_wooden_plate", (0.62, 7.45, 0.8), 0.26, 0, fit="max")
        prop("wooden_bowl_01", (0.0, 7.6, 0.8), 0.26, 0, fit="max"); prop("jug_01", (0.2, 7.35, 0.8), 0.22)
        prop("electric_stove", (1.45, 8.75, 0), 0.9, math.radians(180)); prop("vintage_electric_kettle", (1.45, 8.85, 0.92), 0.22, math.radians(200))
        prop("modern_wooden_cabinet", (-1.5, 8.2, 0), 0.9, math.radians(-90)); prop("potted_plant_02", (-1.5, 8.6, 0.9), 0.35)
        prop("modern_ceiling_lamp_01", (0, 7.3, 2.0), 0.45); prop("brass_pan_01", (1.35, 8.6, 0.92), 0.3, 0, fit="max"); prop("wall_clock", (-1.79, 7.2, 1.75), 0.32, math.radians(-90), fit="max")
        for k in range(3): box("ucab", (-1.62, 7.6 + k * 0.55, 1.95), (0.34, 0.52, 0.62), mat("ucab%d" % k, (0.55, 0.42, 0.3), 0, 0.6))
        box("ctop", (-1.5, 7.9, 0.9), (0.6, 1.8, 0.04), mat("ctop", (0.2, 0.2, 0.22), 0.1, 0.35)); box("splash", (-1.79, 7.9, 1.2), (0.01, 1.8, 0.55), TILEK)
        box("drawing", (1.195, 6.1, 1.35), (0.005, 0.24, 0.32), mat("drawing", (0.95, 0.94, 0.9), 0, 0.8)); box("magnet", (1.19, 6.1, 1.5), (0.01, 0.03, 0.03), mat("magnet", (0.8, 0.1, 0.1), 0, 0.5))
        for k in range(3): box("dline", (1.19, 6.05 + k * 0.03, 1.3 - k * 0.04), (0.004, 0.08, 0.012), mat("dl%d" % k, ((0.8, 0.1, 0.1), (0.1, 0.3, 0.8), (0.1, 0.6, 0.2))[k], 0, 0.8))
        box("towel", (1.17, 8.2, 0.75), (0.02, 0.2, 0.3), mat("towel", (0.75, 0.2, 0.18), 0, 0.9))
        if lit: light("POINT", (0, 6.4, 2.2), 160, (1.0, 0.95, 0.88), 0.6); light("POINT", (0, 8.4, 2.0), 70, (1.0, 0.95, 0.88), 0.6)
        box("fridge", (1.5, 6.0, 0.9), (0.6, 0.62, 1.8), mat("fridge", (0.82, 0.83, 0.84), 0.2, 0.3)); box("fh", (1.19, 5.8, 1.2), (0.02, 0.03, 0.4), STEELB)
        box("stoveclock", (1.17, 8.4, 0.86), (0.01, 0.12, 0.04), mat("sclock", (0, 0, 0), 0, 0.3, (0.2, 0.6, 1.0), 18))
        light("AREA", (0, 9.6, 1.6), 55, (0.55, 0.68, 1.0), 1.1, (math.radians(-90), 0, 0))        # moonlight through the window
        light("POINT", (1.1, 8.4, 0.9), 2.5, (0.3, 0.6, 1.0), 0.05)                                  # the stove clock
        light("POINT", (0, 5.6, 2.0), 3 if not lit else 0, (0.55, 0.68, 1.0), 0.5)
        if lit:                                                       # what the phone torch reveals: soft, cool-white, from the viewer
            light("AREA", (0, 4.6, 1.6), 180, (0.95, 0.97, 1.0), 1.2, (math.radians(-90), 0, 0)); light("AREA", (0, 0.4, 1.6), 120, (0.95, 0.97, 1.0), 1.0, (math.radians(-90), 0, 0))
        if view == "home_entry": cam = camera((0.05, 0.25, 1.55), (0.0, 6.5, 1.2), 24)
        else: cam = camera((0.0, 5.45, 1.5), (0.0, 7.6, 0.8), 20)
        bpy.context.view_layer.update(); pos = {}
        for k_, pt in (("chairL", (-0.45, 8.15, 0.47)), ("chairR", (0.45, 8.15, 0.47)), ("bag", (0.86, 8.25, 0.82)), ("table", (0.0, 7.3, 0.77)), ("door", (0.0, 5.0, 0.0)), ("side", (-0.64, 3.0, 1.0))):
            v = world_to_camera_view(sc, cam, mathutils.Vector(pt)); pos[k_] = [v.x, 1 - v.y]
        _j.dump(pos, open(OUT + "pos.json", "w"))
    elif view in ("entry", "landing"):   # LIVREUR DE NUIT: a building entrance at 2 a.m. and the landing upstairs
        import json as _j
        from bpy_extras.object_utils import world_to_camera_view
        BRICK = tex_mat("lbrick", "concrete_wall_008", 0.9, (0.62, 0.5, 0.44)); PAVE = mat("lpave", (0.06, 0.06, 0.07), 0, 0.12)
        WARM = (1.0, 0.78, 0.5); TILEW = mat("ltile", (0.6, 0.56, 0.5), 0, 0.2)
        if view == "entry":
            box("pave", (0, 2, -0.02), (14, 12, 0.04), PAVE); box("kerb", (0, 3.55, 0.05), (14, 0.5, 0.1), mat("kerb", (0.2, 0.2, 0.21), 0, 0.6))
            box("wl", (-3.3, 4, 2.2), (5.4, 0.3, 4.4), BRICK); box("wr", (2.95, 4, 2.2), (4.7, 0.3, 4.4), BRICK); box("wt", (0, 4, 3.4), (1.2, 0.3, 2.0), BRICK)
            for sx in (-1, 1): box("dfr", (sx * 0.6, 3.86, 1.2), (0.08, 0.1, 2.4), ANTH)
            box("dfrt", (0, 3.86, 2.4), (1.28, 0.1, 0.08), ANTH); box("dglass", (0, 3.9, 1.2), (1.12, 0.02, 2.32), GL); box("dhandle", (0.42, 3.82, 1.1), (0.04, 0.05, 0.5), STEELB)
            box("lfloor", (0, 6.5, -0.01), (3, 5, 0.04), TILEW); box("lceil", (0, 6.5, 2.7), (3, 5, 0.04), WH)
            for sx in (-1, 1): box("lwall", (sx * 1.5, 6.5, 1.35), (0.04, 5, 2.7), mat("lw%d" % sx, (0.75, 0.7, 0.6), 0, 0.7))
            box("lend", (0, 9.0, 1.35), (3, 0.04, 2.7), mat("lend", (0.7, 0.66, 0.58), 0, 0.7))
            for r in range(3):
                for c in range(4): box("mailbox", (-1.46, 5.0 + c * 0.34, 1.0 + r * 0.26), (0.06, 0.3, 0.22), mat("mb%d%d" % (r, c), (0.35, 0.2, 0.12), 0.2, 0.5))
            for k in range(7): box("lstep", (0.6, 7.2 + k * 0.26, 0.09 + k * 0.18), (1.6, 0.26, 0.18), GREY)
            light("AREA", (0, 5.6, 2.6), 90, WARM, 1.2); box("lneon", (0, 5.6, 2.67), (0.9, 0.2, 0.03), mat("lneon", (1, 1, 1), 0, 0.4, WARM, 7))
            # the intercom: steel plate, lit screen, speaker, name buttons, a camera eye
            PX, PZ = 1.12, 1.38
            box("iplate", (PX, 3.83, PZ), (0.26, 0.03, 0.46), STEELB); box("iscreen", (PX, 3.812, PZ + 0.13), (0.19, 0.008, 0.12), mat("iscr", (0.05, 0.08, 0.1), 0, 0.2, (0.5, 0.8, 1.0), 9))
            for q in range(5): box("igrille", (PX, 3.812, PZ + 0.02 - q * 0.012), (0.16, 0.006, 0.005), BLK)
            for q in range(4):
                box("ibtn", (PX - 0.06, 3.81, PZ - 0.07 - q * 0.036), (0.05, 0.01, 0.024), mat("ibtn%d" % q, (0.8, 0.8, 0.8), 0.6, 0.3))
                box("iname", (PX + 0.035, 3.811, PZ - 0.07 - q * 0.036), (0.11, 0.006, 0.024), mat("inm%d" % q, (0.9, 0.88, 0.8), 0, 0.5, (1.0, 0.9, 0.7), 1.2 if q != 2 else 6.0))
            cyl("icam", (PX, 3.808, PZ + 0.205), 0.014, 0.01, BLK, (math.radians(90), 0, 0)); light("POINT", (PX, 3.6, PZ + 0.1), 3.5, (0.5, 0.8, 1.0), 0.05)
            box("wlamp", (0, 3.8, 2.75), (0.5, 0.14, 0.1), mat("wlamp", (1, 1, 1), 0, 0.4, WARM, 16)); light("POINT", (0, 3.45, 2.6), 60, WARM, 0.12)
            box("numplate", (-0.95, 3.84, 1.75), (0.26, 0.02, 0.2), mat("nump", (0.05, 0.1, 0.3), 0, 0.4))
            bpy.ops.object.text_add(location=(-0.95, 3.825, 1.69)); t = bpy.context.object
            t.data.body = "27"; t.data.size = 0.14; t.data.align_x = "CENTER"; t.rotation_euler = (math.radians(90), 0, 0); t.data.materials.append(WH)
            prop("metal_trash_can", (-2.2, 3.6, 0.1), 0.75); plant(2.6, 3.5, 0.9)
            box("pipe", (2.2, 3.82, 2.2), (0.09, 0.09, 4.4), mat("lpipe", (0.2, 0.22, 0.24), 0.6, 0.5))
            for k in range(3): box("win", (-2.6 + k * 0.0, 3.84, 3.2), (1.0, 0.03, 1.1), mat("lwin", (0.02, 0.02, 0.03), 0.2, 0.1)) if k == 0 else None
            box("win2", (2.9, 3.84, 3.2), (1.0, 0.03, 1.1), mat("lwin2", (0.02, 0.02, 0.03), 0, 0.3, (1.0, 0.8, 0.5), 1.5))
            light("AREA", (0.8, -1.5, 3.5), 70, (0.55, 0.68, 1.0), 3.0, (math.radians(55), 0, 0))                    # cold street light behind us
            cam = camera((0.35, 0.15, 1.5), (0.55, 4.0, 1.42), 26)
            pose = ARG("--pose")
            if pose:                                                 # the courier, three acting beats in front of the intercom
                P = {"s": {}, "a": dict(yaw=-0.6, pitch=0.05, look=(-0.8, 0.0), wide=1.0, brow=0.05, mouth="line", armR=(0.5, 1.2), armL=(0.0, 0.15)),            # he has just rung: looking back at the panel, finger still raised
                     "b": dict(yaw=-0.25, pitch=-0.03, look=(-0.9, 0.1), wide=1.28, brow=0.3, brow_up=0.6, mouth="o", armR=(0.15, 0.5), armL=(0.0, 0.15), lean=-0.12),    # the voice answers: eyes to the side, frozen
                     "c": dict(yaw=0.0, pitch=0.02, look=(0.0, 0.0), wide=1.32, brow=0.34, brow_up=0.8, mouth="o", armR=(0.35, 1.5), armL=(0.3, 1.45), lean=-0.2)}[pose if not pose.startswith("s") else "s"]   # he turns to us, hands up to his chest: do I go up?
                toon("courier", (0.2, 2.3, 0), 0.12, **P) if not pose.startswith("s") else None
                light("AREA", (0.5, 0.9, 1.9), 14, (1.0, 0.9, 0.8), 0.9, (math.radians(78), 0, 0))                                    # a soft warm fill so the face keeps its colour
                light("AREA", (-1.2, 1.2, 2.2), 26, (0.6, 0.72, 1.0), 1.2, (math.radians(60), 0, math.radians(-40)))            # cool key from the street
                light("POINT", (0.9, 3.3, 1.7), 9, (0.55, 0.82, 1.0), 0.12)                                                    # the intercom screen on his cheek
                light("AREA", (0.2, 3.6, 2.5), 30, WARM, 0.6, (math.radians(-60), 0, 0))                                        # warm rim from the door lamp behind him
                cam = camera((0.12, 0.95, 1.5), (0.5, 4.0, 1.42), 30); cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 1.32; cam.data.dof.aperture_fstop = 3.2
            if pose and pose.startswith("s"):                        # he walked away: the street, his scooter, the lit entrance behind him
                for o in [o for o in bpy.data.objects if o.name.startswith("courier")]:
                    for c_ in list(o.children_recursive): bpy.data.objects.remove(c_)
                    bpy.data.objects.remove(o)
                SC1 = mat("scbody", (0.2, 0.09, 0.55), 0.3, 0.35); SC2 = mat("scdark", (0.03, 0.03, 0.035), 0.3, 0.4); SX, SY = 1.75, 2.75
                for dx in (-0.55, 0.55): cyl("scwheel", (SX + dx, SY, 0.2), 0.2, 0.1, SC2, (math.radians(90), 0, 0)); cyl("schub", (SX + dx, SY, 0.2), 0.07, 0.11, STEELB, (math.radians(90), 0, 0))
                box("scdeck", (SX, SY, 0.32), (0.75, 0.3, 0.1), SC1); box("scseat", (SX - 0.22, SY, 0.72), (0.5, 0.3, 0.1), SC2); box("scbody", (SX - 0.25, SY, 0.5), (0.5, 0.3, 0.36), SC1)
                cyl("sccol", (SX + 0.48, SY, 0.62), 0.035, 0.8, SC2, (0, 0.25, 0)); box("scbar", (SX + 0.38, SY, 1.04), (0.05, 0.56, 0.05), SC2); box("scshield", (SX + 0.56, SY, 0.6), (0.06, 0.34, 0.5), SC1)
                box("sclight", (SX + 0.6, SY, 0.82), (0.03, 0.12, 0.08), mat("sclight", (1, 1, 1), 0, 0.3, (1.0, 0.95, 0.8), 9)); box("sctail", (SX - 0.5, SY, 0.6), (0.03, 0.14, 0.05), mat("sctail", (0.5, 0, 0), 0, 0.3, (1.0, 0.05, 0.03), 6))
                box("scbox", (SX - 0.42, SY, 1.02), (0.44, 0.44, 0.44), SC1); box("scboxs", (SX - 0.42, SY - 0.223, 1.08), (0.44, 0.006, 0.07), WH); box("scboxl", (SX - 0.42, SY, 1.245), (0.46, 0.46, 0.03), mat("scbl", (0.12, 0.05, 0.36), 0, 0.5))
                cyl("post", (-1.9, 3.3, 2.0), 0.05, 4.0, SC2); box("posth", (-1.9, 2.9, 3.95), (0.14, 0.9, 0.08), SC2); box("postl", (-1.9, 2.55, 3.9), (0.12, 0.3, 0.03), mat("postl", (1, 1, 1), 0, 0.3, (1.0, 0.85, 0.6), 18)); light("POINT", (-1.9, 2.5, 3.6), 110, (1.0, 0.85, 0.6), 0.2)
                for k in range(3): box("bollard", (-0.6 + k * 1.3, 3.3, 0.35), (0.1, 0.1, 0.7), SC2)
                box("far", (13.5, 2.5, 5), (0.4, 26, 10), mat("farw", (0.03, 0.03, 0.04), 0, 0.8))
                for k in range(9): box("farwin", (13.28, rnd.uniform(-6, 9), rnd.uniform(1.2, 8.5)), (0.03, 0.5, 0.75), mat("fw%d" % k, (1, 1, 1), 0, 0.5, rnd.choice([(1.0, 0.7, 0.35), (0.5, 0.65, 1.0)]), rnd.uniform(0.5, 1.4)))
                SP = {"s1": dict(pitch=0.22, look=(0.0, -0.7), brow=0.22, brow_up=0.2, mouth="line", armR=(0.75, 1.5), armL=(-0.35, 0.25), legs=(0.38, -0.3), phone="look", lean=0.08),
                      "s1b": dict(pitch=0.2, look=(0.0, -0.7), brow=0.25, brow_up=0.3, mouth="line", armR=(0.75, 1.5), armL=(0.3, 0.3), legs=(-0.3, 0.38), phone="look", lean=0.08),
                      "s2": dict(pitch=-0.02, look=(0.0, 0.0), wide=1.22, brow=0.3, brow_up=0.7, mouth="o", armR=(0.55, 2.45), armL=(0.0, 0.15), phone="ear"),
                      "s3": dict(pitch=-0.02, yaw=0.0, look=(0.95, 0.05), wide=1.3, brow=0.34, brow_up=0.9, mouth="o", armR=(0.55, 2.45), armL=(0.15, 0.6), phone="ear", lean=-0.1)}.get(pose)
                if SP: toon("courier", (-1.05, 1.9, 0), -1.3, **SP)
                if "--noscoot" in sys.argv:
                    for o in [o for o in bpy.data.objects if o.name.startswith(("scwheel", "schub", "scdeck", "scseat", "scbody", "sccol", "scbar", "scshield", "sclight", "sctail", "scbox"))]: bpy.data.objects.remove(o)
                if pose == "s3":                                             # he is right behind you: only his outline, his eyes and his grin
                    toon("double", (0.1, 1.72, 0), -1.25, dark=True, wide=1.05, mouth="smile"); light("AREA", (1.8, 1.6, 2.2), 40, (0.5, 0.65, 1.0), 0.8, (math.radians(70), 0, math.radians(100)))
                light("AREA", (-2.6, 0.6, 2.4), 22, (0.6, 0.72, 1.0), 1.2, (math.radians(55), 0, math.radians(-60)))
                light("AREA", (-2.4, 1.9, 1.7), 9, (1.0, 0.9, 0.8), 0.8, (math.radians(85), 0, math.radians(-90)))
                cam = camera((-2.8, 1.5, 1.5), (-0.4, 2.2, 1.4), 30); cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 1.82 if SP else 2.6; cam.data.dof.aperture_fstop = 3.5 if SP else 9
            bpy.context.view_layer.update(); v = world_to_camera_view(sc, cam, mathutils.Vector((PX, 3.81, PZ + 0.13)))
            _j.dump({"x": v.x, "y": 1 - v.y}, open(OUT + "pos.json", "w"))
        else:
            box("cfloor", (0, 3.5, -0.02), (2.0, 9, 0.04), mat("cfl", (0.16, 0.13, 0.11), 0, 0.35)); box("cceil", (0, 3.5, 2.6), (2.0, 9, 0.04), mat("ccl", (0.5, 0.5, 0.48), 0, 0.8))
            for sx in (-1, 1): box("cwall", (sx * 1.0, 3.5, 1.3), (0.04, 9, 2.6), mat("cw%d" % sx, (0.42, 0.44, 0.4), 0, 0.8)); box("cskirt", (sx * 0.97, 3.5, 0.06), (0.03, 9, 0.12), ANTH)
            box("endl", (-0.75, 6.5, 1.3), (0.5, 0.06, 2.6), mat("cend", (0.42, 0.44, 0.4), 0, 0.8)); box("endr", (0.75, 6.5, 1.3), (0.5, 0.06, 2.6), mat("cend2", (0.42, 0.44, 0.4), 0, 0.8)); box("endt", (0, 6.5, 2.35), (1.0, 0.06, 0.5), mat("cend3", (0.42, 0.44, 0.4), 0, 0.8))
            for sx in (-1, 1): box("afr", (sx * 0.5, 6.46, 1.05), (0.07, 0.1, 2.1), ANTH)
            box("afrt", (0, 6.46, 2.1), (1.07, 0.1, 0.07), ANTH)
            if "--closed" in sys.argv: box("aleaf", (0.0, 6.5, 1.05), (0.94, 0.05, 2.08), OAK); box("aknob", (-0.36, 6.46, 1.02), (0.05, 0.05, 0.12), BRASS)
            elif "--wide" in sys.argv: box("aleaf", (0.49, 6.5 + 0.47, 1.05), (0.04, 0.9, 2.06), OAK, (0, 0, math.radians(-4)))
            else: box("aleaf", (0.47 + 0.3, 6.5 + 0.36, 1.05), (0.04, 0.9, 2.06), OAK, (0, 0, math.radians(-38)))                  # the door, ajar, opening inwards
            box("aroom", (0, 9.5, 1.3), (4, 0.05, 2.6), mat("aroom", (1, 1, 1), 0, 0.5, WARM, 3.2)); light("AREA", (0, 7.6, 1.6), 140, WARM, 1.0, (math.radians(90), 0, 0))
            box("afloor", (0, 8, -0.01), (4, 3, 0.03), mat("afl", (0.3, 0.2, 0.12), 0, 0.4))
            box("mat", (0, 6.0, 0.006), (0.8, 0.5, 0.012), mat("dmat", (0.1, 0.09, 0.08), 0, 0.95)); box("anum", (0.78, 6.455, 1.6), (0.14, 0.01, 0.1), BRASS)
            if "--nobag" not in sys.argv: box("bag", (0.05, 5.95, 0.17), (0.32, 0.22, 0.3), mat("bag", (0.75, 0.42, 0.12), 0, 0.8))
            if "--nobag" not in sys.argv: box("bagtop", (0.05, 5.95, 0.33), (0.2, 0.02, 0.06), mat("bagh", (0.6, 0.32, 0.08), 0, 0.8))
            for k, y in enumerate((1.5, 4.2)):
                door(-0.97, y, -1, m=OAK); door(0.97, y + 1.2, 1, m=OAK)
            box("clamp", (0, 3.0, 2.56), (0.5, 0.14, 0.03), mat("clamp", (1, 1, 1), 0, 0.4, (0.7, 0.82, 1.0), 5)); light("POINT", (0, 3.0, 2.4), 16, (0.7, 0.82, 1.0), 0.1)
            prop("hanging_picture_frame_01", (-0.96, 5.4, 1.5), 0.5, math.radians(90))
            cam = camera((-0.05, 0.6, 1.5), (0.0, 6.5, 1.25), 28)
            pose = ARG("--pose")
            if pose in ("l1", "l2"):                                 # over his shoulder: the open door at the end of the landing
                toon("courier", (-0.3, 1.8, 0), math.pi + 0.1, yaw=0.0, armL=(0.0, 0.15), armR=(0.0, 0.15), lean=-0.1 if pose == "l2" else 0.0)
                light("POINT", (-0.2, 0.9, 2.2), 14, (0.6, 0.72, 1.0), 0.3)
                cam = camera((0.28, 0.45, 1.62), (-0.02, 6.5, 1.28), 30); cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 6.3 if pose == "l2" else 5.6; cam.data.dof.aperture_fstop = 2.8
            if pose in ("l2", "l3"):                                 # the one who answered: him, in the doorway, black against the warm room
                toon("double", (-0.05, 6.78, 0), 0.0, dark=True, wide=1.05, mouth="smile", yaw=0.0, pitch=0.06 if pose == "l3" else 0.0, armL=(0.0, 0.1), armR=(0.0, 0.1))
            if pose == "l3":
                light("POINT", (0.0, 5.6, 1.9), 3, (0.6, 0.72, 1.0), 0.2)
                cam = camera((0.02, 5.75, 1.6), (-0.05, 6.78, 1.6), 46); cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 1.0; cam.data.dof.aperture_fstop = 2.8
            if "--appt" in sys.argv:                                 # inside flat 13: a table under one lamp, thirteen delivery bags, nobody
                DK = mat("apdk", (0.16, 0.15, 0.14), 0, 0.8)
                box("apback", (0, 9.3, 1.3), (4.2, 0.06, 2.6), DK)
                for sx in (-1, 1): box("apside", (sx * 2.0, 8.0, 1.3), (0.06, 3, 2.6), DK)
                box("apceil", (0, 8, 2.6), (4.2, 3, 0.05), DK)
                box("ttop", (0, 8.2, 0.74), (1.9, 0.85, 0.05), OAK)
                for sx in (-1, 1):
                    for sy in (-1, 1): box("tleg", (sx * 0.86, 8.2 + sy * 0.36, 0.36), (0.06, 0.06, 0.72), OAK)
                BG = [mat("apbag%d" % q, c_, 0, 0.85) for q, c_ in enumerate(((0.75, 0.42, 0.12), (0.68, 0.38, 0.11), (0.8, 0.5, 0.2)))]
                n_ = 0
                for row, (yy, cnt) in enumerate(((8.42, 7), (8.02, 6))):
                    for q in range(cnt):
                        xx = (q - (cnt - 1) / 2) * 0.27 + rnd.uniform(-0.015, 0.015); hh = rnd.uniform(0.26, 0.34)
                        box("abag", (xx, yy, 0.765 + hh / 2), (0.21, 0.15, hh), BG[n_ % 3], (0, 0, rnd.uniform(-0.25, 0.25)))
                        box("atick", (xx, yy - 0.085, 0.765 + hh * 0.62), (0.1, 0.012, 0.07), WH, (0, 0, 0)); n_ += 1
                cyl("apcord", (0, 8.2, 2.25), 0.008, 0.7, BLK); cyl("apshade", (0, 8.2, 1.86), 0.2, 0.12, mat("apsh", (0.05, 0.05, 0.05), 0.4, 0.4))
                light("SPOT", (0, 8.2, 1.82), 260, WARM, 0.08) if False else light("POINT", (0, 8.2, 1.72), 60, WARM, 0.07)
                box("chair", (1.25, 8.0, 0.45), (0.42, 0.42, 0.05), OAK, (0, 0, 0.5)); box("chairb", (1.42, 8.1, 0.75), (0.04, 0.42, 0.6), OAK, (0, 0, 0.5))
                for o in [o for o in bpy.data.objects if o.name.startswith("aroom")]: bpy.data.objects.remove(o)
                for o in [o for o in bpy.data.objects if o.type == "LIGHT" and abs(o.location.y - 7.6) < 0.01]: bpy.data.objects.remove(o)
                cam = camera((0.0, 6.35, 1.72), (0.0, 8.3, 0.9), 22)
            bpy.context.view_layer.update(); f0 = world_to_camera_view(sc, cam, mathutils.Vector((-0.08, 6.75, 0.0))); f1 = world_to_camera_view(sc, cam, mathutils.Vector((-0.08, 6.75, 1.75)))
            _j.dump({"fx": f0.x, "fy": 1 - f0.y, "hx": f1.x, "hy": 1 - f1.y}, open(OUT + "pos.json", "w"))
    elif view in ("stairs", "stairdoor", "stairsup"):   # the service staircase: raw concrete, steel rail, one caged bulb
        WALLC = tex_mat("vconc", "concrete_wall_008", 0.7, (0.78, 0.79, 0.82)); STEP = tex_mat("vstep", "concrete_wall_008", 1.2, (0.62, 0.62, 0.64))
        YELLOW = mat("nosing", (0.75, 0.6, 0.05), 0, 0.5)
        n_, tr, ri = 14, 0.3, 0.18
        for k in range(n_):
            top = -k * ri
            box("step", (0, 0.4 + k * tr, top - 0.6), (1.3, tr, 1.2), STEP)
            box("nose", (0, 0.4 + k * tr - tr / 2 + 0.02, top + 0.002), (1.3, 0.04, 0.006), YELLOW)
        yl = 0.4 + n_ * tr; zl = -n_ * ri
        box("landing", (0, yl + 1.0, zl - 0.6 + 0.0), (2.6, 2.4, 1.2), STEP)
        box("top", (0, -0.6, 0.0 - 0.6), (2.6, 2.0, 1.2), STEP)
        for sd in (-1, 1): box("swall", (sd * 0.68, 2.6, 0.0), (0.06, 7.0, 7.0), WALLC)
        box("endw", (0, yl + 2.2, zl + 1.5), (2.6, 0.06, 4.0), WALLC); box("ceilst", (0, 2.6, 2.6), (2.6, 7.0, 0.06), WALLC)
        RAIL = mat("rail", (0.5, 0.06, 0.05), 0.6, 0.4)
        ang = math.atan2(ri, tr); L_ = math.hypot(n_ * tr, n_ * ri)
        cyl("rail", (0.6, 0.4 + n_ * tr / 2, 0.9 - n_ * ri / 2), 0.025, L_, RAIL, (math.pi / 2 + ang, 0, 0))
        for k in range(0, n_, 3): cyl("post", (0.6, 0.4 + k * tr, 0.45 - k * ri), 0.012, 0.9, RAIL)
        for k, y in enumerate((1.2, 2.6, 4.0)): box("pipe", (-0.6, y, 2.3), (0.06, 1.4, 0.06), STEELB)
        cyl("cage", (0, 1.5, 2.45), 0.07, 0.18, BLK); bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0, 1.5, 2.4))
        bpy.context.object.data.materials.append(mat("bulb", (1, 1, 1), 0, 0.3, (1.0, 0.88, 0.7), 30))
        light("POINT", (0, 1.5, 2.3), 90, (1.0, 0.88, 0.72), 0.06)
        light("POINT", (0, yl + 1.0, zl + 2.3), 22, (0.75, 0.85, 1.0), 0.06)
        box("exitsign", (0, yl + 2.16, zl + 2.4), (0.45, 0.03, 0.16), mat("exitg2", (0, 0.2, 0.05), 0, 0.4, (0.1, 1.0, 0.3), 10))
        # the steel door to level -2, stencilled number, a reader blinking green
        DOORG = mat("doorg", (0.32, 0.34, 0.36), 0.6, 0.45)
        door(0, yl + 2.16, 0, w=1.0, h=2.1, m=DOORG)
        for o in [o for o in bpy.data.objects if o.name.startswith(("dleaf", "dfr", "dfrt", "kick", "rose", "lever", "nplate"))]: o.location.z += zl
        bpy.ops.object.text_add(location=(0.0, yl + 2.105, zl + 1.62)); t = bpy.context.object
        t.data.body = "-2"; t.data.size = 0.36; t.data.align_x = "CENTER"; t.rotation_euler = (math.radians(90), 0, 0); t.data.materials.append(mat("stencil", (0.8, 0.04, 0.03), 0, 0.7, (0.6, 0.02, 0.02), 0.6))
        box("reader2", (0.62, yl + 2.12, zl + 1.2), (0.09, 0.03, 0.13), BLK)
        box("led2", (0.62, yl + 2.1, zl + 1.24), (0.05, 0.005, 0.02), mat("ledg", (0, 0.4, 0.1), 0, 0.3, (0.1, 1.0, 0.25), 60))
        # Samir's badge on the 4th step, lanyard trailing
        BADGE = mat("badge", (0.92, 0.92, 0.9), 0, 0.35)
        box("badge", (-0.22, 0.4 + 3 * tr - 0.02, -3 * ri + 0.004), (0.054, 0.086, 0.003), BADGE, (0, 0, 0.35))
        box("bstrip", (-0.225, 0.4 + 3 * tr + 0.01, -3 * ri + 0.0062), (0.054, 0.018, 0.0008), RED, (0, 0, 0.35))
        for q in range(6): box("lan", (-0.2 + q * 0.03, 0.4 + 3 * tr - 0.08 - q * 0.02, -3 * ri + 0.003), (0.012, 0.05, 0.002), RED, (0, 0, 0.6 + q * 0.15))
        if view == "stairsup":   # from the bottom landing: forty steps, and a rectangle of white light at the top
            box("toplight", (0, -1.56, 1.15), (1.25, 0.05, 2.3), mat("toplight", (1, 1, 1), 0, 0.5, (0.85, 0.92, 1.0), 9))
            light("AREA", (0, -1.3, 1.2), 160, (0.85, 0.92, 1.0), 1.4, (math.radians(-90), 0, 0))
            cam = camera((0.05, yl + 0.75, zl + 1.25), (0.0, 0.2, 0.75), 21)
        elif view == "stairs":
            cam = camera((0.15, -0.35, 1.45), (-0.1, 2.6, -0.9), 24)
        else:
            cam = camera((0.1, yl - 0.4, zl + 1.5), (0.0, yl + 2.2, zl + 1.2), 28)
    elif view == "basement":   # level -2: offices to infinity, no lights, only screens; the workers are 2D, placed from SPOTS
        DFL = mat("dfloor", (0.05, 0.05, 0.06), 0, 0.3); DW = mat("dwall", (0.08, 0.085, 0.09), 0, 0.7)
        box("floor", (0, 20, -0.02), (18, 44, 0.04), DFL); box("ceil", (0, 20, 2.6), (18, 44, 0.04), DW)
        for sd in (-1, 1): box("wall", (sd * 9, 20, 1.3), (0.04, 44, 2.6), DW)
        for k in range(12): box("cneon", (0, 1 + k * 3.4, 2.57), (6, 0.12, 0.02), mat("neonoff", (0.2, 0.21, 0.23), 0, 0.4))
        SCRB = mat("scrb", (0.05, 0.06, 0.08), 0, 0.2, (0.55, 0.72, 1.0), 5.0)
        spots = []
        for r in range(14):
            for c in range(5):
                x, y = -6 + c * 3, 1.5 + r * 2.4
                box("desk", (x, y, 0.74), (1.6, 0.8, 0.04), GREY)
                box("mon", (x, y - 0.2, 1.05), (0.6, 0.03, 0.36), BLK); box("scr", (x, y - 0.18, 1.05), (0.54, 0.005, 0.3), SCRB)   # screens face the workers (away from us)
                box("stand", (x, y - 0.2, 0.82), (0.06, 0.06, 0.12), GREY)
                box("seat", (x, y + 0.65, 0.48), (0.5, 0.5, 0.06), BLK); box("back", (x, y + 0.9, 0.85), (0.5, 0.05, 0.7), BLK)
                light("AREA", (x, y + 0.05, 1.08), 9, (0.6, 0.75, 1.0), 0.45, (math.radians(90), 0, 0))       # the screen glow on the worker's face
                spots.append((r, c, x, y + 0.55))
        for k in range(4): box("emerg", (rnd.choice((-8.95, 8.95)), 4 + k * 8, 2.3), (0.03, 0.4, 0.12), mat("emr", (0.4, 0, 0), 0, 0.4, (1.0, 0.05, 0.05), 6))
        cam = camera((-1.5, -1.8, 1.2), (-1.2, 20.0, 1.0), 28)
        import json as _j
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update(); out = []
        for r, c, x, y in spots:
            hd = world_to_camera_view(sc, cam, mathutils.Vector((x, y, 1.72))); ft = world_to_camera_view(sc, cam, mathutils.Vector((x, y, 0.0)))
            mt = world_to_camera_view(sc, cam, mathutils.Vector((x, y - 0.75, 1.23)))
            if 0 < hd.x < 1 and hd.z > 0: out.append({"r": r, "c": c, "hx": hd.x, "hy": 1 - hd.y, "fx": ft.x, "fy": 1 - ft.y, "my": 1 - mt.y, "d": hd.z})
        _j.dump(out, open(OUT + "spots.json", "w"))
        if "--run" in sys.argv:   # episode 3 test shot with 3D characters: you and Samir running up the aisle, a thousand heads turned, Kessler behind
            SKINS = [(0.78, 0.6, 0.46), (0.36, 0.22, 0.14), (0.85, 0.68, 0.54), (0.6, 0.42, 0.28), (0.7, 0.5, 0.36)]
            for r, c, x, y in spots:
                if rnd.random() < 0.15 or abs(x + 1.5) > 6.2: continue
                tx, ty = -1.5 - x, 0.3 - y; ang = math.atan2(tx, -ty)                       # every head turned to the camera
                w = char3d("w%d_%d" % (r, c), (x, y + 0.1, -0.42), ang, rnd.choice(SKINS), rnd.choice([(0.8, 0.8, 0.8), (0.2, 0.24, 0.3), (0.35, 0.36, 0.4)]), rnd.choice([(0.05, 0.04, 0.04), (0.25, 0.15, 0.08), (0.5, 0.5, 0.5)]), eyes_emit=7.0 if y < 22 else 3.0, h=1.6)
            char3d("samir", (-2.05, 4.3, 0), 0.1, (0.54, 0.35, 0.24), (0.2, 0.31, 0.49), (0.06, 0.05, 0.05), run=1.0, lean=0.28, beard=(0.16, 0.1, 0.07), brow=0.3, badge=True)
            char3d("hero", (-0.95, 3.2, 0), -0.1, (0.54, 0.35, 0.24), (0.44, 0.45, 0.49), (0.05, 0.04, 0.04), run=-1.0, lean=0.3, brow=0.12, badge=True)
            char3d("kess", (-1.5, 10.5, 0), 0, (0, 0, 0), (0, 0, 0), (0, 0, 0), dark=True, bun=True, eyes_emit=14.0, h=1.78)
            light("AREA", (-1.5, 1.2, 2.3), 60, (0.85, 0.85, 1.0), 1.6, (math.radians(25), 0, 0)); light("POINT", (-1.5, 6.5, 2.2), 30, (0.5, 0.62, 1.0), 0.6); light("POINT", (-1.5, 9.5, 2.3), 14, (0.5, 0.62, 1.0), 0.4)
            cam = camera((-1.45, 0.9, 1.22), (-1.5, 7.0, 1.3), 22)
    else:
        room(10, 12, 3)
        for r in range(5):
            for c in range(3):
                x, y = -3 + c * 3, 1.2 + r * 2.0
                messy = (r, c) == (4, 2)
                box("desk", (x, y, 0.74), (1.6, 0.8, 0.04), WH)
                for dx in (-0.75, 0.75): box("leg", (x + dx, y, 0.37), (0.04, 0.7, 0.74), GREY)
                box("mon", (x, y + 0.28, 1.05), (0.6, 0.03, 0.36), BLK)
                box("kb", (x, y - 0.1, 0.77), (0.45, 0.15, 0.02), GREY if messy else WH)
                box("seat", (x, y - 0.65, 0.48), (0.5, 0.5, 0.06), GREY); box("back", (x, y - 0.9, 0.85), (0.5, 0.05, 0.7), GREY)
                if messy:
                    MX, MY = x, y
                    CX_, CY_ = x + 0.45, y - 0.05
                    CER = mat("ceramic", (0.93, 0.92, 0.9), 0, 0.12)
                    cyl("saucer", (CX_, CY_, 0.768), 0.085, 0.012, CER); cyl("saucerrim", (CX_, CY_, 0.776), 0.07, 0.006, mat("saucer2", (0.88, 0.87, 0.85), 0, 0.15))
                    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=0.036, radius2=0.047, depth=0.1, location=(CX_, CY_, 0.832))   # tapered cup
                    o = bpy.context.object; o.data.materials.append(CER); bpy.ops.object.shade_smooth()
                    box("cupband", (CX_, CY_ - 0.0, 0.862), (0.001, 0.001, 0.001), CER)
                    cyl("cupred", (CX_, CY_, 0.86), 0.0465, 0.012, mat("cupred", (0.7, 0.05, 0.05), 0, 0.3))                       # Valmont red band
                    bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.006, location=(CX_ + 0.052, CY_, 0.838), rotation=(math.radians(90), 0, 0))
                    o = bpy.context.object; o.data.materials.append(CER)                                                             # handle
                    cyl("coffee", (CX_, CY_, 0.8835), 0.044, 0.003, mat("cof", (0.09, 0.04, 0.015), 0, 0.08))
                    cyl("crema", (CX_ + 0.008, CY_ - 0.006, 0.8855), 0.024, 0.001, mat("crema", (0.45, 0.28, 0.14), 0, 0.3))
                    box("spoon", (CX_ - 0.065, CY_ + 0.01, 0.778), (0.008, 0.075, 0.003), STEELB, (0, 0, 0.4))
                    box("sugar", (CX_ + 0.03, CY_ + 0.085, 0.772), (0.05, 0.022, 0.006), PAPER, (0, 0, -0.3))
                    JK = mat("jacket", (0.07, 0.11, 0.24), 0, 0.85); JL = mat("jacketl", (0.05, 0.08, 0.18), 0, 0.7)
                    box("jacket", (x, y - 0.955, 0.86), (0.58, 0.035, 0.66), JK, (0.06, 0, 0))                 # back panel hanging on the chair
                    box("jacketc", (x, y - 0.9, 1.215), (0.6, 0.16, 0.05), JL)                                   # collar folded over the top
                    for sx in (-1, 1):
                        cyl("jacketsl", (x + sx * 0.3, y - 0.965, 0.8), 0.038, 0.58, JK, (0.1, sx * 0.05, 0))  # sleeves hanging
                        cyl("jacketcf", (x + sx * 0.315, y - 0.98, 0.52), 0.04, 0.04, JL, (0.1, sx * 0.05, 0))
                    box("jacketv", (x, y - 0.975, 0.62), (0.02, 0.01, 0.3), JL)                                  # back vent
                    box("jacketbadge", (x + 0.17, y - 0.98, 1.0), (0.07, 0.006, 0.1), mat("jbadge", (0.9, 0.9, 0.9), 0, 0.5))
                    box("phone", (x - 0.45, y - 0.12, 0.765), (0.08, 0.16, 0.01), mat("pscr", (0.1, 0.1, 0.1), 0, 0.2, (0.6, 0.8, 1.0), 4))
                    for k in range(5):
                        box("paper", (x + rnd.uniform(-0.6, 0.2), y + rnd.uniform(-0.25, 0.2), 0.762 + k * 0.002), (0.21, 0.29, 0.002), WH, (0, 0, rnd.uniform(-0.5, 0.5)))
        if view in ("open", "desk", "chair"):
            windows(-5, 0, 12, 3); ceiling_grid(10, 0, 12, 3)
            for y in (3.2, 7.2):
                box("glasswall", (2.8, y, 1.1), (0.02, 1.6, 2.2), GL); box("gwframe", (2.8, y, 2.2), (0.05, 1.6, 0.04), GREY)
            plant(4.4, 10.8, 1.2); plant(-4.4, 10.8, 1.0); plant(4.4, 1.0, 0.9)
            box("printer", (-4.2, 6.0, 0.5), (0.7, 0.6, 1.0), GREY); box("ptop", (-4.2, 6.0, 1.02), (0.6, 0.45, 0.04), WH)
            box("board", (4.97, 5.5, 1.5), (0.02, 2.2, 1.1), WH)
            for k in range(6): box("ink", (4.95, 5.0 + rnd.uniform(-0.8, 0.8), 1.2 + k * 0.13), (0.005, rnd.uniform(0.4, 1.4), 0.025), mat("ink2", (0.15, 0.2, 0.5), 0, 0.5))
            box("accent", (0, 11.97, 1.5), (10, 0.02, 3), TEAL)
            box("carpet", (0, 5.2, 0.002), (8.6, 10, 0.004), CARPET)
            prop("wall_clock", (0, 11.9, 2.3), 0.4, 0)
            door(1.6, 11.96, 0, m=OAK); door(-2.2, 11.96, 0, m=OAK)
            for x in (-3.6, 3.6): prop("steel_frame_shelves_01", (x, 11.6, 0), 1.9, 0)
            for k in range(4): prop("metal_trash_can", (-3 + (k % 3) * 3 + 0.7, 1.2 + k * 2.4 + 0.35, 0), 0.38)
            prop("modern_arm_chair_01", (-4.2, 3.0, 0), 0.85, math.radians(70))
            SCR = mat("screen", (0.05, 0.06, 0.08), 0, 0.2, (0.55, 0.7, 0.95), 1.6)
            for o in [o for o in bpy.data.objects if o.name.startswith("mon")]:          # monitors on, faces lit
                box("scr", (o.location.x, o.location.y - 0.02, o.location.z), (0.54, 0.005, 0.3), SCR)
                box("stand", (o.location.x, o.location.y, 0.82), (0.06, 0.06, 0.12), GREY)
            for k in range(5):                                                         # filing cabinets along the right wall
                box("cab", (4.7, 1.6 + k * 0.62, 0.65), (0.55, 0.58, 1.3), GREY)
                for dz in (0.35, 0.75, 1.1): box("handle", (4.41, 1.6 + k * 0.62, dz), (0.02, 0.18, 0.03), BLK)
                for q in range(rnd.randint(1, 4)): box("binder", (4.7, 1.45 + k * 0.62 + q * 0.09, 1.42), (0.28, 0.07, 0.25), mat("bind", rnd.choice([(0.7, 0.05, 0.05), (0.15, 0.2, 0.35), (0.85, 0.85, 0.85)]), 0, 0.5))
            cyl("cooler", (-4.4, 9.0, 0.55), 0.17, 1.1, WH); cyl("bottle", (-4.4, 9.0, 1.3), 0.15, 0.45, GL)
            cyl("rack", (4.5, 9.2, 0.9), 0.02, 1.8, BLK)
            for a_ in range(3): box("coat", (4.5 + 0.12 * math.cos(a_ * 2), 9.2 + 0.12 * math.sin(a_ * 2), 1.4), (0.3, 0.12, 0.7), mat("coat", (0.12, 0.13, 0.16), 0, 0.8))
            for k, y in enumerate((2.0, 6.0, 10.0)):                                   # framed company posters
                box("pframe", (-4.95, y, 1.7), (0.03, 1.0, 0.7), BLK); box("poster", (-4.93, y, 1.7), (0.01, 0.9, 0.6), mat("vposter", (0.75, 0.06, 0.06) if k == 1 else (0.85, 0.85, 0.86), 0, 0.6))
            for o in [o for o in bpy.data.objects if o.name.startswith("desk")]:
                if rnd.random() < 0.45:
                    cyl("lampbase", (o.location.x - 0.65, o.location.y + 0.25, 0.78), 0.06, 0.02, BLK)
                    cyl("lamparm", (o.location.x - 0.65, o.location.y + 0.25, 0.98), 0.012, 0.4, BLK)
                    bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0.03, depth=0.1, location=(o.location.x - 0.6, o.location.y + 0.2, 1.16), rotation=(0.5, 0, 0)); bpy.context.object.data.materials.append(BLK)
                for q in range(rnd.randint(0, 3)):                                        # sticky notes on screens
                    box("note", (o.location.x - 0.22 + q * 0.12, o.location.y + 0.25, 1.17), (0.07, 0.004, 0.07), mat("ynote", (0.95, 0.85, 0.3), 0, 0.7))

            for o in [o for o in bpy.data.objects if o.name.startswith("seat")]: o.rotation_euler = (0, 0, rnd.uniform(-0.5, 0.5))
            for r in range(5):
                for c in range(3):
                    if rnd.random() < 0.5:
                        x, y = -3 + c * 3, 1.2 + r * 2.0
                        for k in range(rnd.randint(2, 6)): box("stack", (x - 0.55, y + 0.15, 0.765 + k * 0.004), (0.21, 0.29, 0.004), PAPER, (0, 0, rnd.uniform(-0.2, 0.2)))
                        cyl("mug", (x + 0.5, y + 0.1, 0.81), 0.04, 0.1, mat("mug", rnd.choice([(0.7, 0.05, 0.05), (0.9, 0.9, 0.9), (0.1, 0.1, 0.12)]), 0, 0.4))
        if "--rich" in sys.argv and view == "open":      # lived-in office: laptops, notepads, binders, drawer units, vents, exit sign, cables
            desks = [(o.location.x, o.location.y) for o in bpy.data.objects if o.name.startswith("desk")]
            for k, (x, y) in enumerate(desks):
                r_ = rnd.random()
                if r_ < 0.5: prop("classic_laptop", (x - 0.35, y - 0.05, 0.762), 0.36, rnd.uniform(2.8, 3.5), fit="max")
                if rnd.random() < 0.6: prop("office_notepads", (x + 0.25, y - 0.2, 0.762), 0.3, rnd.uniform(0, 6), fit="max")
                if rnd.random() < 0.45: prop("binder_notebook", (x + 0.6, y + 0.22, 0.762), 0.32, rnd.uniform(-0.3, 0.3), fit="max")
                if rnd.random() < 0.7: prop("drawer_cabinet", (x + 0.55, y + 0.05, 0), 0.62, math.pi, fit="max")
                if rnd.random() < 0.35: prop("desk_lamp_arm_01", (x - 0.62, y + 0.2, 0.762), 0.5, rnd.uniform(0, 6), fit="max")
                box("cable", (x + 0.1, y + 0.34, 0.4), (0.012, 0.012, 0.72), BLK, (rnd.uniform(-0.1, 0.1), 0, 0))
                box("mouse", (x + 0.3, y - 0.12, 0.772), (0.06, 0.1, 0.025), BLK if rnd.random() < 0.6 else WH, (0, 0, rnd.uniform(-0.4, 0.4)))
            VENT = mat("vent", (0.6, 0.61, 0.63), 0.3, 0.4)
            for x, y in ((-2.4, 3.0), (2.4, 6.6), (-2.4, 9.6)):
                box("ventf", (x, y, 2.975), (0.58, 0.58, 0.02), VENT)
                for q in range(5): box("vents", (x, y - 0.2 + q * 0.1, 2.962), (0.5, 0.02, 0.012), GREY)
            for x, y in ((0, 2.0), (0, 6.0), (0, 10.0), (3.2, 4.0), (-3.2, 8.0)): cyl("sprk", (x, y, 2.95), 0.03, 0.06, STEELB)
            box("exitsg", (1.6, 11.93, 2.32), (0.5, 0.03, 0.16), mat("exitg4", (0, 0.2, 0.05), 0, 0.4, (0.1, 1.0, 0.3), 8))
            box("skirtb", (0, 11.95, 0.06), (10, 0.03, 0.12), ANTH); box("skirtr", (4.97, 6, 0.06), (0.03, 12, 0.12), ANTH)
            for k in range(8): box("seam", (-4.3 + k * 1.23, 5.2, 0.0045), (0.012, 10, 0.001), mat("seam", (0.08, 0.085, 0.1), 0, 0.9))
            for k in range(3): prop("metal_trash_can", (-4.5, 2.0 + k * 3.4, 0), 0.4)
            box("tv", (4.96, 9.0, 1.75), (0.03, 1.3, 0.75), BLK); box("tvs", (4.94, 9.0, 1.75), (0.005, 1.22, 0.68), mat("tvs", (0.03, 0.03, 0.04), 0, 0.2, (0.9, 0.2, 0.15), 1.2))
        if view == "open":
            cam = camera((-1.0, -1.2, 1.65), (MX, MY, 0.9), 26)
        elif view == "desk":
            cam = camera((MX + 1.05, MY - 0.55, 1.28), (MX + 0.05, MY + 0.02, 0.8), 30)
        elif view == "chair":   # Samir's jacket still hanging on his chair
            for o in [o for o in bpy.data.objects if o.name.startswith(("glasswall", "gwframe"))]: bpy.data.objects.remove(o)
            cam = camera((MX - 1.0, MY - 2.4, 1.45), (MX, MY - 0.75, 0.88), 34)
        if view in ("door", "exit"):   # the corridor: lit wall panels, side doors, signage, everyday clutter
            CW = 1.8
            for sd in (-1, 1): box("cwall", (sd * CW, 6, 1.5), (0.04, 12, 3), WH)                 # a real, narrow corridor
            ceiling_grid(2 * CW, 0, 12, 3)
            WOOD = mat("wood2", (0.55, 0.52, 0.48), 0, 0.5)
            for sd in (-1, 1):
                box("skirt", (sd * (CW - 0.03), 6, 0.06), (0.03, 12, 0.12), ANTH)
                box("wains", (sd * (CW - 0.025), 6, 0.5), (0.02, 12, 0.9), TEAL)                  # teal lower wall panel
                box("rail2", (sd * (CW - 0.05), 6, 0.97), (0.05, 12, 0.06), OAK)                 # oak handrail
                box("stripe", (sd * (CW - 0.03), 6, 2.3), (0.02, 12, 0.05), RED)                 # Valmont red line
                for k, y in enumerate((2.5, 6.0, 9.5)):
                    door(sd * (CW - 0.04), y, sd)
                    box("sconce", (sd * (CW - 0.07), y + 1.6, 2.1), (0.06, 0.25, 0.12), mat("sconce", (1, 1, 1), 0, 0.4, (1.0, 0.95, 0.85), 6))
                    light("POINT", (sd * (CW - 0.4), y + 1.6, 2.1), 25, (1.0, 0.95, 0.85), 0.2)
            prop("korean_fire_extinguisher_01", (-CW + 0.16, 4.3, 0), 0.6, math.radians(90)); box("extsign", (-CW + 0.03, 4.3, 1.1), (0.02, 0.22, 0.22), mat("exts", (0.7, 0.05, 0.05), 0, 0.5))
            plant(CW - 0.35, 11.4, 0.9); plant(-CW + 0.35, 7.9, 0.8)
            box("bench2", (CW - 0.3, 4.3, 0.22), (0.4, 1.4, 0.06), GREY)
            box("trolley", (-CW + 0.4, 10.4, 0.45), (0.55, 0.8, 0.8), GREY)
            for k in range(3): box("box2", (-CW + 0.4, 10.3 + rnd.uniform(-0.1, 0.1), 0.95 + k * 0.28), (0.5, 0.5, 0.28), mat("card2", (0.55, 0.45, 0.32), 0, 0.9), (0, 0, rnd.uniform(-0.2, 0.2)))
            box("dome", (0, 11.8, 2.9), (0.16, 0.16, 0.1), BLK)
            prop("metal_trash_can", (CW - 0.25, 7.7, 0), 0.6); prop("wall_clock", (0, 11.9, 2.35), 0.35, 0)
            for y in (4.0, 8.0): prop("hanging_picture_frame_01", (-CW + 0.04, y, 1.45), 0.6, math.radians(90))
            for k in range(4): box("tag", (rnd.choice((-CW + 0.06, CW - 0.06)), rnd.uniform(1, 11), rnd.uniform(1.3, 1.9)), (0.01, 0.21, 0.29), PAPER)
        if view == "door":    # CCTV: corridor to the director's office
            for o in [o for o in bpy.data.objects if o.name.startswith(("desk", "leg", "mon", "kb", "seat", "back", "cup", "coffee", "jacket", "phone", "paper"))]: bpy.data.objects.remove(o)
            box("endwall", (0, 11.98, 1.5), (3.6, 0.03, 3), TEAL)
            door(0.6, 11.96, 0, w=1.0, m=mat("walnut", (0.12, 0.06, 0.04), 0, 0.35))
            box("plate", (0.6, 11.93, 1.75), (0.5, 0.02, 0.12), RED)
            bpy.ops.object.text_add(location=(0.6, 11.91, 1.72)); t = bpy.context.object
            t.data.body = "DIRECTION · M. KESSLER"; t.data.size = 0.045; t.data.align_x = "CENTER"; t.rotation_euler = (math.radians(90), 0, 0); t.data.materials.append(WH)
            cam = camera((-1.55, 6.2, 2.75), (0.5, 11.8, 0.95), 15)
        if view == "exit":    # CCTV: the only exit, nobody comes out
            for o in [o for o in bpy.data.objects if o.name.startswith(("desk", "leg", "mon", "kb", "seat", "back", "cup", "coffee", "jacket", "phone", "paper"))]: bpy.data.objects.remove(o)
            door(0, 11.96, 0, w=1.6, h=2.2, m=STEELB)
            box("bar", (0, 11.9, 1.0), (1.2, 0.05, 0.06), BLK)
            box("sign", (0, 11.92, 2.5), (0.6, 0.03, 0.22), mat("exitg", (0, 0.2, 0.05), 0, 0.4, (0.1, 1.0, 0.3), 12))
            cam = camera((1.55, 6.2, 2.75), (0, 11.8, 0.9), 15)

if SCENE == "pfp":
    # profile picture: the black figure between two half-open doors, A (blue) and B (red), in fog
    import mathutils
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1080
    FLOORM = mat("pfloor", (0.03, 0.03, 0.035), 0.4, 0.25)
    box("floor", (0, 2, -0.02), (8, 8, 0.04), FLOORM)
    WALLM = tex_mat("pwall", "concrete_wall_008", 0.8, (0.35, 0.35, 0.38), 0.6)
    box("wall", (0, 3.0, 2), (8, 0.1, 4), WALLM)
    ANTH = mat("panth", (0.05, 0.05, 0.06), 0.5, 0.35)
    for sx, col, letter in ((-1, (0.15, 0.4, 1.0), "A"), (1, (1.0, 0.08, 0.05), "B")):
        x = sx * 1.05
        box("hole", (x, 2.97, 1.05), (0.95, 0.12, 2.1), mat("hole" + letter, (1, 1, 1), 0, 0.5, col, 6.0))   # light behind the door
        for fx in (-1, 1): box("fr", (x + fx * 0.51, 2.9, 1.07), (0.08, 0.14, 2.16), ANTH)
        box("frt", (x, 2.9, 2.17), (1.1, 0.14, 0.08), ANTH)
        leaf = box("leaf", (x - sx * 0.35, 2.55, 1.05), (0.05, 0.9, 2.1), mat("pleaf", (0.06, 0.06, 0.07), 0.3, 0.4), (0, 0, sx * 0.6))
        box("sign", (x, 2.9, 2.45), (0.34, 0.06, 0.28), mat("sign" + letter, (0.02, 0.02, 0.02), 0, 0.4, col, 0.6))
        bpy.ops.object.text_add(location=(x, 2.86, 2.37)); t = bpy.context.object
        t.data.body = letter; t.data.size = 0.24; t.data.align_x = "CENTER"; t.data.extrude = 0.01; t.rotation_euler = (math.radians(90), 0, 0)
        t.data.materials.append(mat("letter" + letter, (1, 1, 1), 0, 0.3, col, 25))
        L = light("SPOT", (x, 3.4, 1.4), 1400, col, 0.3, spot=60); L.rotation_euler = mathutils.Vector((-x * 0.3, -1, -0.15)).to_track_quat("-Z", "Y").to_euler()
        rim = light("AREA", (x * 1.4, 1.2, 2.0), 160, col, 0.6); rim.rotation_euler = mathutils.Vector((-x * 1.4, -1.2, -0.4)).to_track_quat("-Z", "Y").to_euler()
    COAT = mat("coat", (0.012, 0.012, 0.015), 0, 0.55)
    root = silhouette("figure", (0, 0, 0), 1.85, eyes=True, material=COAT)
    k = 1.85 / 1.8
    def part(prim, loc, size, m, rot=(0, 0, 0)):
        if prim == "cyl": bpy.ops.mesh.primitive_cylinder_add(vertices=48, location=loc, rotation=rot)
        else: bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
        o = bpy.context.object; o.scale = size; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
    HAT = mat("hat", (0.01, 0.01, 0.012), 0, 0.45); BAND = mat("band", (0.5, 0.02, 0.03), 0, 0.4)
    part("cyl", (0, 0.0, 1.735 * k), (0.2 * k, 0.21 * k, 0.008 * k), HAT, (0.08, 0, 0))            # fedora brim, tipped down
    part("cyl", (0, 0.015, 1.79 * k), (0.115 * k, 0.12 * k, 0.06 * k), HAT)                        # crown
    part("cube", (0, 0.015, 1.84 * k), (0.07 * k, 0.11 * k, 0.012 * k), HAT)                       # pinch
    part("cyl", (0, 0.015, 1.755 * k), (0.118 * k, 0.123 * k, 0.014 * k), BAND)                    # red hat band
    for sx in (-1, 1):                                                                               # raised coat collar
        part("cube", (sx * 0.085 * k, 0.0, 1.5 * k), (0.05 * k, 0.012 * k, 0.075 * k), COAT, (0.25, 0, sx * 0.45))
    SH = mat("shirtp", (0.7, 0.7, 0.68), 0, 0.5)
    for sx in (-1, 1): part("cube", (sx * 0.028 * k, -0.128 * k, 1.385 * k), (0.012 * k, 0.004 * k, 0.05 * k), SH, (0, sx * 0.45, 0))   # shirt collar V
    part("cube", (0, -0.133 * k, 1.395 * k), (0.016 * k, 0.006 * k, 0.014 * k), BAND)                                                   # tie knot
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.026 * k, radius2=0.012 * k, depth=0.24 * k, location=(0, -0.132 * k, 1.26 * k), rotation=(0, 0, math.radians(45)))
    o = bpy.context.object; o.scale = (1, 0.2, 1); o.data.materials.append(BAND)                                                          # tie blade
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.011 * k, location=(0.1 * k, -0.128 * k, 1.36 * k)); bpy.context.object.data.materials.append(mat("pin", (0.8, 0.65, 0.3), 1, 0.25))   # gold lapel pin
    for sx in (-1, 1): part("cube", (sx * 0.07 * k, -0.12 * k, 1.33 * k), (0.012 * k, 0.004 * k, 0.11 * k), mat("lapel", (0.03, 0.03, 0.035), 0.1, 0.35), (0, sx * 0.35, 0))  # lapels
    fog((0, 1.5, 1.5), (7.8, 3, 3), 0.05, (0.9, 0.9, 1.0))
    key = light("AREA", (0.3, -1.6, 1.9), 22, (0.85, 0.8, 1.0), 1.2); key.rotation_euler = mathutils.Vector((-0.3, 1.6, -0.4)).to_track_quat("-Z", "Y").to_euler()
    cam = camera((0, -1.55, 1.68), (0, 0.6, 1.5), 40)

if SCENE == "escalier" and "--boy" in sys.argv:   # close on the boy, the black figure watching from the top
    for o in [o for o in bpy.data.objects if o.type == "CAMERA"]: bpy.data.objects.remove(o)
    cam = camera((-0.4, 6.9, -1.0), (0.12, 4.4, -0.65), 30)

if SCENE == "lift":
    # elevator cabin seen from the CCTV dome in the top corner: the boy and you, six years ago
    W_, D_, H_ = 1.6, 1.8, 2.4
    box("floor", (0, 0, -0.02), (W_, D_, 0.04), mat("lfloor", (0.06, 0.06, 0.065), 0, 0.6))
    box("ceil", (0, 0, H_), (W_, D_, 0.04), STEEL)
    for sx in (-1, 1):
        box("wall", (sx * W_ / 2, 0, H_ / 2), (0.04, D_, H_), STEEL)
    box("back", (0, D_ / 2, H_ / 2), (W_, 0.04, H_), STEEL)
    box("door_l", (-0.4, -D_ / 2, H_ / 2), (0.8, 0.04, H_), STEEL); box("door_r", (0.4, -D_ / 2 - 0.03, H_ / 2), (0.8, 0.04, H_), STEEL)
    box("rail", (0, D_ / 2 - 0.05, 0.95), (W_ * 0.9, 0.04, 0.04), STEEL)
    box("panel", (W_ / 2 - 0.03, -0.5, 1.2), (0.02, 0.18, 0.5), DARK)
    for k in range(6):
        box("btn", (W_ / 2 - 0.045, -0.5, 1.38 - k * 0.06), (0.01, 0.04, 0.03), mat("lbtn", (0.2, 0.2, 0.2), 0, 0.4, (1, 0.1, 0.05) if k == 5 else None, 4 if k == 5 else 0))
    box("lamp", (0, 0, H_ - 0.02), (0.9, 0.5, 0.02), mat("llamp", (1, 1, 1), 0, 0.5, (1, 0.95, 0.85), 5))
    light("AREA", (0, 0, H_ - 0.05), 70, (1, 0.95, 0.85), 0.8, rot=(0, 0, 0))
    HOOD = mat("hoodie", (0.11, 0.12, 0.14), 0, 0.85)
    TOI = mat("toi", (0.55, 0.4, 0.12), 0, 0.85)
    if "--empty" not in sys.argv:
        silhouette("boy", (-0.35, 0.35, 0.0), 1.5, turn=math.radians(170), hood=True, eyes=False, outfit="boy")
        silhouette("toi", (0.3, 0.1, 0.0), 1.72, turn=math.radians(200), eyes=False, outfit="toi")
        cam = camera((-W_ / 2 + 0.12, -D_ / 2 + 0.12, H_ - 0.12), (0.2, 0.3, 0.6), 11)
    else:   # plate for 2D characters: CCTV dome above the doors, looking at the back of the cabin
        cam = camera((0.55, -D_ / 2 + 0.1, H_ - 0.1), (-0.05, D_ / 2, 0.95), 14)

if REAL:
    cam = sc.camera
    tgt = [o for o in bpy.context.scene.objects if o.type == "EMPTY"]
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.0
    if tgt: cam.data.dof.focus_object = tgt[0]
    # handheld: smooth noise on the camera rotation, eased keyframes on the move
    cam.keyframe_insert("rotation_euler", frame=1)
    ad = cam.animation_data
    fcs = ad.action.fcurves if hasattr(ad.action, "fcurves") else [fc for l in ad.action.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
    for fc in fcs:
        for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.easing = "AUTO"
        if fc.data_path == "rotation_euler":
            m = fc.modifiers.new("NOISE"); m.scale = 28; m.strength = 0.012 if fc.array_index != 1 else 0.006; m.phase = fc.array_index * 7

if OUT == "info":
    dg = bpy.context.evaluated_depsgraph_get()
    for o in bpy.context.scene.objects:
        if o.type in ("META", "CAMERA", "LIGHT"):
            e = o.evaluated_get(dg)
            print(o.name, o.type, tuple(round(v, 2) for v in o.location), tuple(round(v, 2) for v in e.dimensions))
    sys.exit(0)
if ONLY:
    sc.frame_set(ONLY); sc.render.filepath = OUT + f"{ONLY:04d}.png"
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("done")
