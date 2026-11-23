# Craft: what each reference taught, and the kit that applies it

Read the section that matches the scene you are writing. SKILL.md has the rules that apply to every episode;
this file has the why and the details. Method only: never reuse another creator's characters, art, voices,
worlds or titles.

## Contents
- One-second readability (animated-series method page)
- Emotion (2.4 M-view non-horror "what if")
- Series rhythm (2.1 M-view survival account)
- Dialogue and humour (893 k-view family sketch)
- Labels kit (1.6 M-view recap format)
- Continuity
- Assets of the existing episodes

## One-second readability

A wide shot with a tiny hero and no text loses the viewer; a close-up, one exaggerated emotion and one phrase read
in a second.
- A yellow banner (`tags.banner`, 3 or 4 words in caps) states what the image *means*, not what the voice says:
  "IL EST SEC.", "CE N'EST PAS SAMIR.", "LEQUEL EST LE VRAI ?". One per shot, at y 700 (under the clock and the
  notifications, clear of the video call's self-view); at y 470 over a phone held in POV.
- Exaggerated emotions: wavy mouth and sweat for fear, shock lines (`tags.burst`) in the character's colour on the
  reaction line, fading in 1.5 s.
- The monster ends in close-up, never small in a doorway: push in until the face fills the frame.
- No black frame: darkness keeps one thing to look at (a blade of light in a door gap, two red eyes).
- No shot longer than about 3 s without a change: wide, then close, then a final gesture.
- Three beats per scene: hook, action, punchline.

## Emotion

- Arc: funny, then embarrassing, then sad, then a flip of point of view (the other person was suffering too).
- After a scene, a short cut-away to whoever waits (the mother): her reaction carries the emotion.
- Warm, bright memories against the dark present: a palette change says "this is the past".
- Story objects as cards (a ticket, a bubble) state a fact faster than a sentence.
- Shares and saves come from family emotion; fear alone brings views but fewer shares.

## Series rhythm

- Parts of about 60-65 s, posted a few days apart; the post title is the choice or a line of the monster.
- First person: your hand and a real-size phone (iPhone 13 proportions, about 1 : 2.16) at the bottom of the frame;
  a companion talks with you on a video call.
- Clue cards on objects; a small "Abonné · la partie 2 arrive" chip half-way.
- End card: "TU FERAIS QUOI ?", two buttons with one line each on what the choice costs, "Écris-le en commentaire",
  "Abonne-toi pour la partie 2".

## Dialogue and humour

- Shot / reverse shot: a close-up on whoever speaks, a new shot for every line.
- One or two funny lines per part from the companion (Samir) relieve the fear and raise likes.
- A caring habit of the mother (food, the plate she keeps) works as a running gag, then as a clue.

## Labels kit (`scripts/tags.py`)

A word stuck on a person or object states a fact in half a second. Our own drawings: `stamp_tag` (red rubber
stamp), `label` (strip, any colour), `name_plate` (gold, for a first appearance or the villain), `live_bug`, `note`
(handwritten, typed in with the voice), `poster` ("DISPARU"), `tape` (crime-scene tape), `rec_frame`, `grin` (the
double's painted grin, the series motif), `subscribe`, `banner`, `burst`. Call `tags.setup(E.MONT, E.HAND)` first.
Clue tags on people work well in a comparison: "TREMPÉ" on the real one, "SEC" on the double.

## Continuity

Abrupt changes between characters confuse viewers (the creator's note).
- One colour per character, worn by nobody else: courier purple (cap with a moon), Samir green (knitted beanie with
  a pompom, never the courier's cap), mother pink (bob and bun), the double black or with white/red eyes.
- A character appearing for the first time in a video gets a name plate.
- The video call keeps the same frame every time: call UI, your face inset, the green "SAMIR" pill.
- Never cut face to face at the same size without a cue (scale change, the phone, the name on screen).
- The double wearing someone's face differs by one constant sign (eyes, grin) and is shown in another place.

## Assets of the existing episodes

- `nuit1.py`: the complete reference episode (timeline from voice timings `at`/`wt`, phone screens, facade with the
  scooter rider, stairs with lamps going out behind him, a door whose light follows its opening, rewinds, numpy
  sound mix).
- `nuit2.py`: `handheld` camera, `rain`, `motes`, `steam`, `reveal` (torch cone over a dark render), `seated`,
  `call_screen`; Blender views `--cam=home_entry|home_kitchen --home=dark|lit`.
- `nuit4.py`: POV phone (`iphone`, `pov` with push-in to read), `samir_cam`, `peephole` (fisheye), `notif`
  (mother's texts), `map_screen`, `clue_card`, `receipt` (rules slip), `end_card`, `dark_gap`, `hook_face`.
- `nuit5.py`: season finale; two outcomes in one video, `landing` with real and fake Samir, `grin_close`, `ticket`,
  loop to Nuit 1's first frame.
- `toon2d.py`: `char(h, **pose)` for the courier, Samir (`samir=True`), the mother (`mum=True`), the double
  (`dark=True`), `monster_face`; `n2motion.py`: perspective doors, one-piece hands, sleeves.
- Set stills (Blender, Poly Haven CC0): street, landing lit/dark/with bag, closed door, stairs, entry and kitchen
  lit/dark, bedroom.

## Storytime blueprint (youtu.be/NZ596meuUK8, AI storytime with Claude Code + Higgsfield, watched by Gemini Nov 23)

The tool there generates the images with a paid AI video service; our pipeline draws them, so only the method is
kept. The story shape, checked against our episodes:
1. Hook, 0-5 s, a shock sentence with no intro (ours: "Imagine." over the anomaly already on screen).
2. Context in one or two sentences.
3. Escalation by the rule of three: three attempts or signs, each worse than the last (three knocks, three texts,
   three times the double is almost caught).
4. The pivot: one absurd or desperate decision (the in-video A/B choice sits here).
5. Climax and payoff: its consequence, shown, not told.
6. Landing: a last line that calls back the opening (our loop to frame 0, or the reframing line).
Production rules from the same video: a model sheet so the characters never drift between scenes (an inconsistent
character makes the video read fake); a breakdown per scene (description, narration line, image, motion); subtle
motion (blinks, small nods) rather than big moves; 60-65 s of voice; an edit that removes every dead second.

## Constraints and riddles (November 23, the creator's condition for season 2)

Every night has a visible constraint and a fair riddle, because a viewer who can solve the episode before the choice
comments and watches again:
- **Constraint on screen**: a countdown in the HUD ("FERMETURE DANS 00:60") down to the choice, and the job's rules
  on screen (the sheet taped under the till). Rules of the job can conflict at the choice (rule 2 vs rule 3).
- **A riddle with a pause**: a decodable clue (initials of the items on a receipt spell FERME, a number, an object
  that comes back) with a banner "⏸ METS PAUSE : ...". At most two clues, both lead to the right answer; the answer
  episode replays them ("TOUT À L'HEURE", the initials lighting up one by one).
- Ask for the vote AND the riddle during the choice ("Le mot caché, tu l'as trouvé ? Écris-le").
