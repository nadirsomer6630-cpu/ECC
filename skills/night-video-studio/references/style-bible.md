# Style bible: the series' own DNA (from season 2 on)

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
