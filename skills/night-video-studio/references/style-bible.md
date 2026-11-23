# Style bible: the series' own DNA (from season 2 on)

## CURRENT CHARACTERS (v19, November 23): read this first

Engine: `scripts/toon5.py` (`bust5`), sheets `assets/persos_v19.jpg`, `persos_v19_gros_plan.jpg`,
`persos_v19_fiche_modele.jpg`. Everything below this section is the history of how we got here (v1 to v19): keep it
for its lessons, do not draw from it.

Style: the creators' flat 2D (big heads, big expressive eyes, thick brows, thick black outline, flat colours, ONE
shadow shape per form, hair drawn by hand as a few shapes, one bright garment), with dark fantasy as the only theme
(shadows lean violet, a thin lavender moonlight line on the lit edge, the gold moon brooch, the double).

| Character | Fixed identity (change one thing at a time, only when the creator asks) |
|---|---|
| Toi (the hero, never speaks) | slicked-back wavy dark brown-black hair, no lock (removed Nov 23 at the creator's request), one small wisp each side of the parting; **hazel eyes: amber-brown round the pupil, a faint green rim** (`iris_in`, `iris`); hybrid almond slightly slanted eyes; scar through the left brow and cheek; tired crescents; open purple track jacket with white stripes, dark hoodie, headphones round the neck, gold moon brooch |
| Samir (companion, video call) | green beanie with a cream pompom, curls under it, short beard along the jaw and a moustache, brown eyes, thick brows, gold stud in the left ear, green quilted puffer, a thin chain; one or two funny lines per part |
| Maman (texts, the door) | grey hair, centre parting, bun with a gold pin, round gold glasses, pearl earrings, blush, pink cardigan over a cream turtleneck |
| Le double (the monster) | the hero's hair and clothes in darker colours, cold grey skin, black eyes with a glowing red slit iris, hollow violet sockets with veins, black tears, a crack, the grin cut into the cheeks with needle teeth and two fangs set along the lip curves |

Expressions: `mouth_` line / smile / o / fear, `brow`, `wide`, `look`, `blink`. Views: `turn` -0.5..0.5 (three-quarter
cheat), no profile yet. Light: `light` -1..1 moves the shadow shape. Animation: `boil=seed` per drawing, on twos.
Checks before delivering a face: render at 1000 px with a red centre line; look for stains, asymmetry, teeth or
strands crossing an outline; compare with the previous version so only the asked change moved.


Decided with the creator on November 23, 2026, after a frame-by-frame comparison of the first two seconds of the
reference videos with ours: they are flat 2D, one readable scene, motion from frame 0, frank colours, little text;
ours were 2D characters on dark 3D renders with a phone-in-phone frame 0 and five overlays. The look below takes one
mechanism from each reference and ties them to signatures that only exist in our world, so it cannot be copied
without copying the story itself. Style frames: `adn_1_accroche.png`, `adn_2_indice.png`, `adn_3_regle.png`.

## Borrowed mechanisms (one per creator, never their characters or art)

| Mechanism | From |
|---|---|
| Whole video in flat 2D: sets drawn in the same style as the characters, no 3D renders | all the 185 k-2.1 M references |
| One readable scene at frame 0, something already moving (a knock, a hand, a light) | ilfautsurvivre, jolavanille |
| A big digital clock at the top, the only HUD element | chapkasurvie, recits.hommebaton |
| "Imagine." over an ordinary place, the viewer is "tu" | mission.creepy, chapkasurvie, amayn20 |
| Big expressive face for every reaction, one yellow banner that states the meaning | tesvideosvirales |
| Labels stuck on people and objects ("PAS DE BUÉE", "DEHORS : -4°") | salle13recap |
| Wrong choice -> loss -> rule card -> rewind | mission.creepy |
| Shot / reverse shot and one funny line from the companion | zak.kho |
| One palette per place (lit interior against the blue night) | echo.science |
| Parts of about 60 s, the choice as the post title | ilfautsurvivre, apokalyps.pov |

## Our signatures (the part nobody else has)

1. **Nuit Express**: every season is a night job ordered through the same app. Its moon logo, purple, opens the
   rule slip and the phone screens. The seasons are connected by it.
2. **The rule slip**: a receipt that keeps every rule since rule 1, the new one handwritten in red. It grows each
   episode; viewers can screenshot and save it.
3. **Two lights**: the double only exists in the dark (rule 5). Lit places are safe and flat-bright; the dark is
   flat navy. In every episode, two small **red eyes are hidden** somewhere in the dark before the reveal: a game
   for the comments ("vous les avez vus à quelle seconde ?").
4. **The colour code**: you purple (moon cap), Samir green (beanie with pompom), the mother pink (bun), the double
   black with red eyes. Nobody else wears these colours.
5. **The fair clue is physical** (dry in the rain, no mist on the glass, no shadow): shown before the choice,
   never said, then replayed after the loss.
6. **The loop**: the last image or line of a season is the first one of its first episode.
7. **Sound**: the three-note Nuit Express chime at 0 s, the heartbeat under every choice, the tape rewind.

## What frame 0 contains, and nothing more

The flat scene with one moving element, the clock with its one-line place under it, at most one notification, and
the spoken "Imagine." as the only caption. No phone held in the hand at frame 0, no banner before the premise is
spoken, no recap.

## Second layer: cinematic light and a survival-game interface (added the same day)

From two more accounts the creator sent (method only): zak.kho (2.4 M views on "première nuit au bled": stylised
cinematic 3D, dramatic moonlight-blue and warm-lamp lighting, acting close-ups, time jumps written as captions
"4 H 30") and daybyday1to30 (a 30-day series dressed as a retro game: gauges, RPG tags, boss bar, PAUSE menu,
"VOS VOTES" screen with percentages, choice buttons, countdown). Our version, frames `adn_4..6`:

- **Light**: the flat 2D scene is lit like a cut-scene: the room sinks into night blue, a hard warm cone from the
  ceiling lamp, a hard moonlight band through the window. Cel-shaded edges, the red eyes stay the brightest thing.
- **Survival HUD** in a pixel font (Press Start 2P, SIL OFL, from Google Fonts): night number, three hearts (one per
  wrong choice: a lost heart is a loss with its rule card), a FEAR gauge that rises with the music, the clock.
- **RPG tags** for a first appearance: "TOI (CLASSE : CAISSIER)", "MAMAN ?" (the question mark when it may be the
  double).
- **The double is a boss**: a red "LE DOUBLE (BOSS)" bar appears when he is near.
- **The in-video choice is a PAUSE menu**: the frame freezes and darkens, two buttons with one line on what each
  costs, a 10-second countdown, "ÉCRIS A OU B".
- **Each episode opens on "VOS VOTES"** with the real percentages counted from the previous episode's comments (never
  invented), then "PARTIE SAUVEGARDÉE": the rule slip as a save file ("Enregistre la vidéo = ta sauvegarde") to turn
  TikTok saves into a game mechanic.
- Pixel font only for the game layer; captions, notifications and the slip keep their own fonts.

## Third layer: Blender sets shaded like the drawings, and the PS1 "danger" picture (November 23)

From two YouTube tutorials the creator sent: a Blender-to-Photoshop concept-art overpaint (build the scene in 3D for
perspective and light, then repaint it flat) and a PS1-style low-poly tutorial (low resolution, crunchy textures,
nearest-neighbour pixels, few colours, dithering). Only titles and descriptions could be read from this server
(YouTube blocked the download), so the methods below are the well-known core of both techniques.

- **`blender_env.py --toon`** (frames `adn_7`): every material keeps its colour (a texture is reduced to its average
  colour, the paint-over flattens grain), lit with a two-tone Toon BSDF plus a flat 0.35 emission fill so shadows keep
  their colour, "Standard" view transform, and Freestyle ink lines 2.4 px in the characters' ink colour. The set
  then matches the 2D characters while keeping real perspective and camera moves. An automatic 2D filter on a normal
  render (mean-shift + palette) was tried first and rejected: banding rings on every light gradient.
- **Night is added in 2D** on the toon render: the room sinks into night blue, a hard warm cone under the lamp.
- **`blender_env.py --ps1`** follows the tutorial's own settings (transcript read on Nov 23): every texture
  scaled to 128 px and read with "Closest" interpolation, film filter size 0; the pixelation (x0.25 down, nearest
  back up, the tutorial's "Scale 0.25 / Pixelate / Scale 4" compositor chain) is done in 2D by the episode script
  because Blender 5 moved the compositor. The overpaint tutorial's rule also holds: 3D solves perspective, light and
  proportions, but must not dictate the final look; simplify and push shapes in 2D on top.
- **The PS1 picture is a signal** (frame `adn_8`): when the double is near, the image drops to a sixth of the
  resolution, 16 levels per channel with ordered dithering, nearest-neighbour upscale and a slight horizontal
  wobble, while the boss bar appears. The viewer learns that the picture breaking down means danger. Calm scenes stay
  clean.

## Characters, style 2 (season 2 on)

The creator's choice: a dark-blue lock of hair and hybrid eyes, almond and slanted. `toon2d.char(..., style2=True)`:
- **Hybrid eyes** (`hybrid_eye`): an almond whose outer corner lifts, a heavy ink upper lid with a flick at the
  corner, a coloured iris with a darker ring, a pupil and two highlights. Iris colour is part of the colour code:
  you deep blue, Samir and the mother brown, the double keeps its white eyes with red irises. `wide` opens them
  rounder for fear; the eyebrows stay and carry the emotion.
- **The lock** (`hair_strand`, the hero only): dark hair at the temples under the cap and one long dark-blue lock with
  a light-blue shine falling over the forehead. The double has the same lock, black: the silhouette lies, the eyes
  do not. `strand` (-1..1) swings it.
- Sheet: `assets/persos_style2.jpg`.

## Animation rules (`scripts/anim.py`)

From an animation tutorial the creator sent ("How to Animate ANYTHING in Blender!": keyframes shaped in the graph
editor). Nothing moves linearly:
- every move ends on an eased key (`keys` with `ease_in_out`, `ease_out`);
- a move is prepared by a small opposite move (anticipation: he shrinks and looks down before turning);
- fast moves overshoot and settle (`back_out`);
- holds give weight: a beat of stillness before and after a scare;
- loose parts follow late and swing past (`follow`: a damped spring on the lock, the pompom, the bag strap);
- blinks punctuate: one in the calm hold, one after the shock.
Test clip: a knock, anticipation, a fast turn with overshoot, eyes snapping wide, the lock swinging behind.

## Characters v3: a new design from scratch (`scripts/toon3.py`, sheet `assets/persos_v3.jpg`)

Replaces the round-headed season 1 drawings for season 2 (the creator asked for a complete redesign with the same
criteria). Busts for close-ups and dialogue; every part is a mask with an ink line grown around it.
- **You**: an egg-shaped head with a defined jaw (anime-leaning, after the cinematic sketches), spiky black hair with
  a pointed fringe and **one dark-blue lock** with a light shine over the left eye, **hybrid eyes** (almond, outer
  corner lifted, heavy upper lid with a flick, blue iris with two highlights), a purple bomber with the Nuit Express
  moon patch, headphones around the neck. No cap any more: the lock must be seen.
- **Samir**: green knitted beanie with pompom, curls under it, short beard, brown eyes, green jacket.
- **The mother**: grey bun, thin round glasses, lashes, pink cardigan with buttons.
- **The double**: your face and hair with grey-blue skin, a black lock, red irises with pin pupils, a grin too wide.
`bust(who, look, brow, mouth, wide, blink, sway, tilt, size)`; `sway` swings the lock for follow-through.

## Effects (`scripts/fx.py`, demo `assets/fx_demo.jpg`)

From "8 MIND-BLOWING Photoshop Effects In Under 8 Minutes!" (Wave Index; transcript read Nov 23), rebuilt for frames:
`halation` (threshold, blur, screen, red tint: lamps and neons), `frosted` (frosted-glass panel for the PAUSE menu
and notifications), `halftone` (grungy halftone: the clue replayed "TOUT À L'HEURE"), `text_behind` (the title
between set and character: covers), `pixel_stretch` (a stretched column with noise: the double's glitch),
`line_drawing` (pen drawing: memories, the rule card). The gradient-sky and liquid-chrome effects were left out:
nothing in the series needs them.

## Characters v4 (November 23): hair after Zak, clothes after the reference creators (sheet `assets/persos_v4.jpg`)

- **Your hair**: messy slicked-back, smooth waves, dark brown-black (base, light-brown wave strokes combed back,
  near-black sides at the temples), a high hairline so the forehead shows, two loose wavy strands falling forward:
  the dark-blue lock with its shine over the left eye, and a brown one on the right. Both swing with `sway`.
- **Faces**: tapered eyebrows in the hair colour, a lid crease above each hybrid eye, a nose drawn with its bridge in
  shadow colour and an inked tip, a lower lip in shadow colour.
- **Clothes**: you wear an open purple track jacket with white sleeve stripes, a stand-up collar, zip teeth and the
  moon patch, over a dark hoodie whose hood shows behind the neck, headphones around the neck; Samir a quilted green
  puffer with a high collar over a grey hood; the mother a pink cardigan over a cream turtleneck.

## Animation, completed with the tutorial itself (watched by Gemini on Nov 23)

"How to Animate ANYTHING in Blender!" read by Gemini (`scripts/gemini_look.py`): keyframes and the graph editor,
easing, **Vector keys for hard impacts** (`anim.vector`), anticipation, overshoot, **overlapping action: loose parts
stop 2 to 5 frames after the body** (`anim.overlap`), **arcs** (`anim.arc`), timing (a fast impact has almost no
in-between frames), and **squash and stretch with constant volume** (`anim.squash`, the "Maintain Volume" idea).
Test clip with the v4 hero: hold, knock, he sinks (squash, anticipation), the head snaps on a Vector key with a
stretch, overshoots and settles, the eyes open on the impact frame, the locks follow three frames late.

## Characters v6 (November 23): dark fantasy x gritty city (sheet `assets/persos_v6.jpg`, `bust(..., grim=True)`)

Mood references only (a rainy, sepia, hard-lit city crime game; a gold-and-ruin dark fantasy RPG): never their
characters, symbols, logos or UI. What the 12 Gemini design reads of our reference TikToks agreed on, applied here:
thick black outlines, flat cel colour, one signature colour and one signature accessory per character, emotions
through mobile brows and widened eyes, the villain marked by a white predatory grin and red eyes.

- **Finish (`engrave`)**: colour 28 % desaturated with a warm sepia cast (the gritty city), except saturated
  signature colours that stay vivid; key light from the right, so the left third of every figure falls in a hard
  shadow, hatched, cross-hatched where it is darkest; a thin gold rim light on the right edge; grain.
- **Toi**: purple leather jacket with gold piping, frayed dark cloak fastened by a gold moon brooch, stubble, a scar
  through the left eyebrow, tired under-eyes; the dark-blue lock and blue eyes are the only vivid colours.
- **Samir**: green beanie with pompom, olive quilted bomber, a gold chain, full beard: the warm one.
- **Maman**: plum shawl with gold embroidery, round glasses, a rosary, a gold hairpin in the bun, the only blush.
- **Le double**: your clothes and hair on porcelain-grey skin, gold kintsugi cracks, black tears, red eyes, the grin.

## Characters v7 (November 23): one bone structure per face (sheet `assets/persos_v7.jpg`, `FACE` in `toon3.py`)

The v6 heads were one egg shape for everyone. Now each face has its own skull, cheekbone, jaw and chin (`head_pts`),
its own eyes (width, height, slant), brows (thickness, arch, slant), nose kind and mouth width:

- **Toi**: high cheekbones, a V jaw to a narrow chin, the most slanted almond eyes, low brooding brows, a straight
  nose with nostril wings, thin lips, faint nose-to-mouth lines, stubble, the scar: young but worn by the nights.
- **Samir**: broad square jaw under a full trimmed beard from the sideburns, thick straight brows, heavy upper lids,
  rounder eyes, a broad nose, a full lower lip, a gold stud in his ear.
- **Maman**: a round face, soft jaw, small droopy-cornered eyes with crow's feet, thin arched brows, forehead lines,
  a small nose, thin lips, gold-rimmed round glasses, blush.
- **Le double**: your face stretched: long chin, hollow cheeks, black-purple sunken eye sockets, eyes slanted even
  further with a long flick, sharp rising brows, a long hooked nose, deep folds, the grin as wide as the jaw allows.

Rendering: form shadows instead of the v6 vertical split, light from the upper right (left edge of the face, eye
sockets, under the cheekbones, side of and under the nose, under the lower lip, the chin's shadow on the neck),
stored in `cv.shade` so `engrave` hatches exactly there; light strokes on the nose bridge and the right cheekbone.

## Characters v8 (November 23): semi-realistic faces after the creator's model (sheet `assets/persos_v8.jpg`, `REAL`)

The creator sent a semi-realistic 3D portrait as the model for the 2D faces. We take its face construction, not its
identity (not its hair colours, eye colours or outfit): small intense eyes whose iris is cut by the upper lid, with
the lid's shadow on the eyeball and a single small highlight; low, heavy, flat brows close to the eyes; a sculpted
nose (bridge line, light down the bridge, rounded tip, wings, dark nostrils); real lips (cupid's bow, fuller lower
lip with a highlight, philtrum); a strong jaw for the hero; form shadows blurred so they read as painted. The hero's
scar now runs from the forehead through the brow and down the cheek. `FACE[who].update(REAL[who])` switches it on;
`toon3_v7.py` keeps the cartoon-eyed v7.

## Characters v9 (November 23): our style, "Nuit gravée" (sheet `assets/persos_v9.jpg`)

The house style, stated once: flat cel-shaded 2D with thick ink, semi-realistic faces (v8), a gritty sepia city grade,
dark-fantasy gold accents and rim light, and engraved hatching inside the form shadows. Added in v9:

- **Hair (`hair_slick`)**: one silhouette from ear to ear (no gaps at the temples), a symmetric hairline with the
  hair's soft shadow on the forehead, 13 clumps combed back in waves converging to the crown, strand lines in each
  clump, a sheen band across the crown, faded sides, the loose locks falling forward, flyaways and two messy tufts.
  The mother: a centred bun and a centre parting with grey and white strands, one loose white strand. Samir: a
  shine on each curl under the beanie.
- **Faces**: brows tapered from head to tail with single hairs combed outwards; iris fibres; lips wider; the
  philtrum short; nose-to-mouth folds short and faint on the young faces, long only on the mother and the double;
  soft blurred plane lights (nose bridge, cheekbone, forehead, chin) instead of hard strokes; stubble as a blue-grey
  shadow with fine hairs; the hairpin in the centred bun.
- **Symmetry check**: render a bust at 1000 px with a red centre line before delivering a new face; everything
  mirrors except what is meant not to (the light from the right, the blue lock, the scar, the double's cracks).

## Characters v10 (November 23): redrawn from scratch, "render then comic" (`scripts/toon4.py`, `assets/persos_v10*.jpg`)

Sources: the creator's semi-realistic portrait (anatomy and lighting only, not its identity) and chazee_xiao's
"2D ANIMATIC -> RENDER -> FINAL" (Spider-Verse-style fan animation, 6 s, 619 k views, read by Gemini): the final
image is a 3D-lit render redrawn as a comic: flat tones, halftone dots in the half-shadow, hatching in the deep
shadow, a stylised coloured rim light, ink weight that varies with the light, colour misregistration, paper grain,
animation on twos, hand-drawn speed lines instead of motion blur.

How `toon4.py` does it: every shape has a height map (a distance-transform dome plus gaussian bumps and creases:
brow ridge, sockets, eyeballs, cheekbones and hollows, nose bridge, tip and wings, nostrils, philtrum, lips, chin,
nose-to-mouth folds, wrinkles, hair clumps, cloth folds and quilting); `Canvas.shade` derives normals, lights them
(sodium key from the upper right, cold moonlight rim from the left, ambient occlusion from the height map, a small
specular), quantises to three tones, adds halftone dots, hatching and the rim band, then inks the outline thicker
on the shadow side. `done()` applies the night-city grade (signature colours kept), a red misregistration ghost of
the ink and grain. Eyes, brows (single hairs), mouths, glasses, cracks and stubble are drawn on top.

Use: `bust4(who, look, brow, mouth, wide, blink, sway)` -> RGBA 1000x1250; `python3 toon4.py out.jpg` (sheet) or
`python3 toon4.py out.jpg big` (four neutral busts). About 18 s per bust. When animating, hold each drawing for two
frames (on twos) and use drawn speed lines, as in the reference.

## v11 (November 23): jaws in harmony with each face

The creator found the v10 jaws too square. `head_pts` now continues the cheek's direction into the jaw (no corner)
and curves round to a narrow chin; `round` (0 to 1) sets how soft the turn is: you 0.7 (an oval to a defined chin),
Samir 0.6 (solid, under the beard), the mother 0.9 (round and soft), the double 0.55 (long and pointed).

## v12 (November 23): the hero's haircut after the creator's reference, denser and wavier

The cut of the reference portrait (only the cut: our colours stay dark brown-black with the blue lock): slicked
back with tall volume, an M hairline with a small widow's peak, 21 thick clumps swept back with clear waves (amplitude
7 to 13, 2.4 periods), the sides combed back over the temples, five strand lines per clump and a sheen band, two
heavier wavy strands falling in front of each ear, the blue lock and one more strand on the forehead, and the back
of the hair as one mass behind the ears ending in a few points on the nape. Too many thin strands read as worms and
long nape points read as pigtails: keep the loose strands few and thick.

## v13 (November 23): hair, mouths and chins redone from scratch, with the lessons of the earlier tries

Mistakes found by rendering each part large, and the rule that replaced each:

- **Hair as noodles** (thin wiggly lines everywhere) -> hair is made of thick clumps (`ribbon`), each lit with its
  own rounded section, one strand line at most, one crisp pointed highlight (`streak`) per clump so the highlights
  line up into a band across the crown.
- **Random waves read as messy or crimped** -> one `wave(y)` for the whole head, so every clump ripples in step
  like combed hair; long wavelength (170 px): a short one (64 px) reads as crimped zigzags.
- **A slicked-back cut that read as a fringe or a bowl** -> clumps are broad at the root and pointed at the crown
  (thin roots at the forehead read as tips falling down), they fan back over the skull, and the hair is drawn
  under the skin: the forehead is clipped on an uneven hairline with no ink, so the hair grows out of the scalp,
  with a soft shadow under the hairline. The temple strands and the blue lock are drawn on top afterwards.
- **Jagged silhouette** -> a smooth crown; the clumps give the texture inside it.
- **Lips as blurred colour** -> lips are drawn shapes, each lit: an upper lip with a cupid's bow, darker; a fuller
  lower lip with a highlight; a mouth line heavier in the middle, inked corners. Smile: corners up, upper teeth,
  dimples. Surprise: a round opening framed by the lips, upper teeth, tongue. Fear: stretched wide, corners down,
  both rows of teeth. Samir's moustache falls over his upper lip.
- **A shapeless chin with a hard line across it** -> a muzzle under the lips, the fold under the lower lip, the
  chin as a ball below it (wider for a wider jaw), a faint cleft for the hero; the stubble has a soft upper edge,
  and the nose-to-mouth folds are wide and shallow (narrow deep ones drew vertical bars on the mother's face).

## v14 (November 23): faces after the reference face's structure

Structure only, never the identity: a long angular face, high cheekbones as a long ridge toward the temple, the
plane under them hollowed toward the mouth (shadow side only), a strong brow ridge, thick low brows drawn down
toward the centre, deep-set hooded eyes (a skin fold over the outer lid, a low heavy crease), a long straight nose,
fuller lips with a marked philtrum (two ridges and a groove), corners slightly down at rest, a defined chin, a
thicker neck with an Adam's apple. Dosed per character in `FACE` (`hood`, `philtrum`, `corners`, `adam`, `cb`,
`hollow`, `brow_r`, `lipf`): full on you, heavier on Samir, pushed to the extreme on the double, only cheekbones and
gaze on the mother (her forehead lines are faint ink, not relief: relief lines read as shiny bars).

Shader lesson: every small dip in the height map leaves an isolated shadow island in the light, which reads as a
stain. `Canvas.shade` now removes shadow islands under 7000 px (at 2x), edge included, before the tones are drawn.

## v15 (November 23): softened after lucdgain (136.6 k followers, 13.5 M likes)

lucdgain's characters (watched on three recent videos: "LE SUPERMARCHÉ EP 01" 72 s, 12.5 k views; its finale; a
244 s hotel story): big round pale heads, small soft eyes with a half-moon line of tiredness under them, thin brows,
minimal nose and mouth, hair as solid shapes, a thick even outline, flat colours with one gentle shadow, warm
cheeks. We take the softness, never the characters: `soften()` (`SOFT` = 0.62) lowers the relief of the v14
structure (cheekbones, hollows, brow ridge, sockets, chin, nose, philtrum, hooded lids), rounds the jaw higher
while the chin stays narrow (a wide chin read square again), opens the eyes a little and calms their slant and the
frown, thins the brows. Shading: wider tone edges, lighter halftone and hatching, a steadier outline on the head;
warm cheeks on everyone but the double; soft under-eye crescents (tired night workers) on everyone but the double.
`SOFT = 1` gives back the angular v14 faces.

## v16 (November 23): back to 2D, oval faces

The creator asked for 2D again and oval faces. `FLAT = 0.55` pulls every normal toward the viewer so the relief
reads as flat colour shapes, not a 3D render; `SPEC = 0.35` keeps little gloss; tone edges are crisp again
(0.345-0.365 and 0.70-0.72): soft edges on flattened relief looked like smudged make-up, not 2D. Heads are eggs
(`OVAL[who]` = half-width, top, chin, chin taper): widest at the cheekbones, narrowing to the chin (you 150 wide,
taper 0.22; Samir broader, 0.16; the mother rounder, 0.14; the double long and pointed, 0.30). With less relief the
nose needs ink: a thin bridge line on the shadow side.

## v17 (November 23): hair and accessories redesigned after research ("too bland")

Sources read: Clip Studio Tips (stylized hair, clumps as ribbons, strands only at clump edges, counter-flow
strands), AnimeOutline (anime hair shading, highlights as zigzags), cel-shading guides (two shadow levels, crisp
edges, highlight band in an "H" across the clumps), Arcane style write-ups (strong contrast, sculpted hair with sharp
highlights, accessories and scars that tell a story), character-design guides (silhouette test, shape language,
60/30/10 colour with one accent, the 70/30 rule: one odd detail makes a character memorable, story props not random
ones).

Applied:
- **Hair (you and the double)**: seven big clumps combed back with volume, sides flicking out past the ears, three
  spikes breaking the silhouette at the back (triangles: restless); a two-tone gradient from root to tip (dark brown
  to blue-night for you, to blood red for the double: his signature), a deep shadow between clumps, a zigzag highlight
  band dipping across the clumps, one fine strand per clump edge, two strands against the flow.
- **Accent per character**: you electric blue (the lock, the eyes, a glowing ring on each headphone cup, the collar
  lining) plus a silver hoop in the right ear; Samir gold and orange (a heavy two-row gold chain, an orange stripe on
  the beanie cuff, a gold tooth when he smiles); the mother gold and rose (a glasses chain hanging to her shoulders,
  pearl earrings, two crossed hairpins with rose beads); the double red (red rings on the cups, red lining).

## v18 (November 23): the CURRENT characters, redrawn from zero (`scripts/toon5.py`, `assets/persos_v18*.jpg`)

Supersedes v10 to v17 (`toon4.py` stays only as a record). The creator found v17 full of hair errors and too radical
a change, and asked for the creators' style, with dark fantasy as the only theme (GTA IV and Elden Ring dropped).

What the creators share (politiquepixels, pixels.stories, proteine.facile, lucdgain, daybyday1to30, zak.kho): big
heads, big expressive eyes, thick brows, thick black outlines, flat colours with one soft shadow, hair as a few
simple shapes with a few lines, one bright garment, dark sets.

Mistakes of v10-v17 and the rule each one gave:
- Procedural hair (17 then 7 computed clumps) made gaps, scallops, a feather crown, chevrons -> hair is drawn by hand
  as one designed silhouette, a few wave lines and a few highlight shapes, symmetric except the waves and the lock.
- Stacked effects (height maps, halftone, hatching, rim light, misregistration, sepia) made faces noisy and plastic
  -> flat colours, ONE shadow shape per form, a thin moonlight line, nothing else.
- Realistic proportions (small eyes, long necks) lost the expressions on a phone -> big heads, big eyes.
- Every version replaced the whole character -> identities are fixed now; change one thing at a time.
- Effects were judged at thumbnail size only -> every new face is checked at 1000 px with a centre line.

Dark fantasy, the only theme: shadows lean violet (`NIGHT`), a thin lavender moonlight line on the right edge
(`MOON`, 150 alpha, 3 px), the gold moon brooch, the double (grey-blue skin, glowing red slit eyes, black tears, a
crack, the grin, darker clothes). Kept from the creator's own requests: the dark-blue lock, the hybrid almond eyes,
the slicked-back wavy dark brown-black hair, the scar, the tired crescents under the eyes.

`bust5(who, look, brow, mouth_, wide, blink, sway, size)` -> RGBA; `python3 toon5.py out.jpg` writes the sheet in
about 25 s (toon4 needed 5 min).

## Animation and compositing, from two Grease Pencil tutorials (watched by Gemini, November 23)

1. "2D animation over 3D in Blender" (youtu.be/CljGkkmH-Z0): a base mesh rigged on Mixamo (check the licence of the
   motion library for commercial use) gives proportions and perspective; the Graph Editor changes a pose (move a
   rotation curve), the speed (scale keys on X) and the intensity (scale on Y, to exaggerate); trace the key poses
   first (walk: contact, down, passing, up), structure before detail; Grease Pencil Sculpt mode adjusts a drawing
   without redrawing it; clean-up on a new layer with closed lines so fills work.
2. "A 2D character in a 3D painted scene" (youtu.be/VmekmH0QJMs): collections and render layers because Grease
   Pencil ignores the camera's depth of field; Vector/linear keys for constant motion (falling snow); a Noise
   modifier for a living, trembling line; onion skin; straight-ahead or pose-to-pose; simple circles for structure;
   a fill layer with a palette sampled from the model sheet; render PNG RGBA with transparency and a Z pass; composite
   with Alpha Over, an animated blur on foreground objects, Hue/Saturation and Exposure for the mood; glow on magic
   objects; a vignette.

What our Python pipeline took (`toon5.py`, test `scripts/anim_test_v18.py`, 3 s):
- `line_boil(im, seed)`: the Noise modifier by hand, 1-2 px smooth displacement, a new seed per drawing.
- Animate on twos: 12 drawings a second, each held two frames.
- `bust5(..., light=-1..1)`: the one shadow shape moves to the side away from the light and widens as the light
  turns to the front (a moving candle moves the shadow).
- Horror timing: a long held pose, then a brutal pose with no in-between (the double is simply there, bigger).
- Compositing: characters on their own layer, a blurred foreground object for depth, a glow on magic objects (the
  moon brooch, the double's eyes), a vignette, a cold grade with crushed blacks.
- Mixamo motion would need the user to download it (the session cannot log in); not used.

## Model sheet (November 23): `python3 toon5.py out.jpg model`, `assets/persos_v18_fiche_modele.jpg`

Three-quarter left, front, three-quarter right for every character, from one drawing: `bust5(..., turn=-1..1)` draws
the body, the head, the features and the hair on separate layers and `turn_warp` slides each by its depth (features
60, hair 34, skull 18, body 0) while the far side narrows by 35 % at turn 1. Use turn 0.3-0.5; a full profile needs
its own drawing and does not exist yet. Look the eyes toward the turn (`look=(turn * 0.6, 0)`).

## v19 (November 23): a natural lock and hair, a double that frightens

- **The lock** was a glossy blue tube pasted on the forehead. Now it is a clump of his own hair: it leaves the hair
  mass at the hairline (the part over the hair is cut away, so it never sits on top of the hair), blue from the
  hairline (dyed), curves round the brow and hooks at the tip, a thinner strand splits off it, one soft highlight.
  A wide flat root read as a box: keep the root narrow and already blue where it shows.
- **The hair**: volume drawn as shapes (a dark groove under each swept-back clump, a light on top), not as stroked
  lines; the stick-like loose strand became two small wisps lifting at the hairline.
- **The double's teeth** sat on a straight line while the mouth curves, so they poked out at the corners. Teeth are
  now placed along the upper and lower lip curves, clipped inside the mouth, needles with two long fangs, an
  outline each, gums, a black throat.
- **The double was not frightening**: black sclera with a glowing red slit iris, hollow violet sockets with veins,
  the grin cut up into the cheeks, sharper rising brows, a colder skin. It keeps the hero's hair and clothes.

## v20 (November 23): hazel eyes for the hero

The creator wanted hazel eyes with a faint green. The iris is now an olive outer ring (`iris` 112,108,62) and an
amber-brown centre round the pupil (`iris_in` 140,94,46, 70 % of the iris, with a lighter lower crescent). A first
try with a green outer ring at full strength read as green eyes, not hazel: keep the green to the rim. The lock stays
the only blue on the hero. Close-up: `assets/yeux_noisette.jpg`.
