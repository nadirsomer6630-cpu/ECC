---
name: night-video-studio
description: Fast production of the French interactive horror TikToks ("Livreur de nuit" and the next night-job episodes) - 2D characters in Blender sets, ElevenLabs voices checked by transcript, phone screens, three in-video choices, then one-command render, partial re-render and quality gate. Use when writing, producing, retouching or checking one of these episodes, or when starting a new night-job episode from the existing one.
metadata:
  origin: ECC
---

# Night video studio

The production kit for the night-job series, built on what the best videos in the niche do and on our own
statistics. It exists to save time: one script per episode, one command per step, and checks that run before
anything is sent.

## When to Use

- A new night-job episode (courier, night watchman, baby-sitter...): copy `pipeline/nuit1.py` and its lines file.
- A retouch on a delivered episode: `make.sh fix` re-renders only the seconds that changed.
- Before any delivery: `make.sh qa`.

## How It Works

### What makes a video hold (measured)

| | Ep. 3 v2 (73 s, old format) | Livreur de nuit nuit 1 (2:48) |
|---|---|---|
| Average watch | 7.9 s | 41.8 s |
| Watched to the end | 5 % | 10.8 % |

Half the viewers of nuit 1 left within 2 s: the first image was a face doing nothing. Reference videos in the
niche (230 k to 2.8 M views) all do the following, so every episode does it too:

1. **Image 0 asks a question.** The voice starts on frame 0 with "Imagine." and the screen already shows the
   anomaly (a notification "Client : ???", a message from someone who never writes).
2. **The reveal lands before 5 s**, with a red tag on the phone screen saying what is wrong.
3. **One rule, tested three times.** Each wrong choice ends in a loss whose clue was visible before, a rule
   written by hand on the order slip, and a tape rewind.
4. **The phone carries the story** (order app, messages, counters). A HUD line stays on screen: clock, place,
   money for the night.
5. **Comments are asked for at each choice**, not only at the end: few viewers reach the end.
6. **1:00 to 1:45** is where the references sit; 2:45 is the upper limit.
7. **Simple 2D characters** (round head, one bright colour) in dark sets. Detailed 3D characters did not pay.
8. **Description**: hook sentence, "Nuit N", 2 or 3 hashtags (#horreur #creepypasta #survie).

### What the top videos do that we now apply everywhere

- Frame 0 shows the anomaly with a red tag on the phone screen ("TU N'ES PAS ENCORE RENTRÉ.").
- One sentence, one framing: in a dialogue scene, wide shot, then the face of whoever speaks.
- The previous vote is paid off inside the next episode: both outcomes are shown.
- The final A/B can be solved only by returning viewers (a detail from the previous night): it feeds comments.
- "À SUIVRE · NUIT N" on the last seconds; description "Abonne-toi pour la nuit N".
- The camera moves to what the voice names (each rule as it is written, each hand as it is named).

### Emotion, from a 2.4 M-view non-horror reference

- Arc: funny, then embarrassing, then sad, then a flip of point of view (the other person was suffering too).
- After each scene, a short cut-away to whoever watches or waits (the mother): her reaction carries the emotion.
- Warm, bright memories against the dark present: a change of palette tells the viewer "this is the past".
- Story objects as cards (a ticket, a bubble with an icon) say a fact faster than a sentence.
- The last card names the next episode precisely ("NUIT 3 : LA NUIT DE TA MÈRE"), not a generic "à suivre".
- Shares and saves come from family emotion; fear alone brings views but fewer shares.

### Series rhythm, from a 2.1 M-view account (median 243 k over 21 videos)

- Parts of about 65 s, posted a few days apart; the post title is the choice: "Partie 1 | Tu ... ou tu ... ?".
- First person: your hands and your phone at the bottom of a wide-lens frame; a companion talks with you.
- Frame 0 is a title card: time, day, who you are, the situation, the dilemma.
- Clue cards on objects; a small "Abonné · la partie 2 arrive" chip half-way.
- End card: "TU FERAIS QUOI ?", two buttons with one line each on what it costs, "Écris-le en commentaire",
  "Abonne-toi pour la partie 2".

### Dialogue and humour, from an 893 k-view family sketch (15 % likes)

- Dialogue scenes as shot / reverse shot: a close-up on whoever speaks, a new shot for every line.
- One or two funny lines per part from the companion relieve the fear and raise likes and shares.
- A caring habit of the mother (food, texts) works as a running gag, then as a clue.

### Labels kit (`pipeline/tags.py`), from a 1.6 M-view recap format (22 k saves)

A word stuck on a person or object states a fact in half a second; scenes change every 2 to 3 s. Our own drawings,
no third-party art: `stamp_tag` (red rubber stamp), `label` (red strip), `name_plate` (gold), `live_bug`, `note`
(handwritten note typed in with the voice), `poster` ("DISPARU" with a photo), `tape` (crime-scene tape),
`rec_frame` (camcorder), `grin` (the double's grin painted on a wall: the series motif), `subscribe` (end card: the
button turns to ABONNÉ, then "NUIT N" and two open questions). Call `tags.setup(E.MONT, E.HAND)` first.
The hook sentence tells the whole premise as cause and consequence in one breath ("... et le soir même, il a trouvé
un mot collé sur sa porte").

### One-second readability, from an animated-series method page (1.28 M views in 6 days, Nov 2026)

Only the public page was read (the paid guide was not). Its before/after images make one point: a wide shot with
a tiny hero and no text loses the viewer; a close-up, one exaggerated emotion and one phrase read in a second.
- **Frame 0 on "Imagine": the hero's face, very close**, eyes wide, sweat drop, shock lines (`tags.burst`) behind,
  and the dilemma as a question on a yellow strip (`tags.banner`, 3 or 4 words in caps: "QUI SONNE CHEZ TOI ?").
  A face doing nothing lost half of nuit 1's viewers in 2 s; a face with an emotion and a question is the opposite.
- **A yellow banner on the key shots** that states what the image means, not what the voice says ("IL EST SEC.",
  "CE N'EST PAS SAMIR.", "IL ÉTAIT DÉJÀ EN BAS."). At most one banner per shot, placed at y 700, under the clock
  and notifications and clear of the call's self-view.
- **Exaggerated emotions**: wavy mouth and sweat for fear, a burst of shock lines in the character's colour on the
  reaction line (the mother's pink, the courier's purple), then it fades in 1.5 s.
- **The monster always ends in close-up**, never small in a doorway: push in until the face fills the frame.
- **No black frame**: the second of silence before the shock shows a blade of light growing in a door gap
  (`dark_gap` in `nuit4.py`).
- **No shot longer than about 3 s without a change**: split a long beat into wide, close, and a final gesture
  (the double lifts his head and looks into the peephole).
- **After a loss, replay the clue** before the rule card (the façade shot again, "TOUT À L'HEURE").
- Three beats for every scene: hook, action, punchline.

### Episode 2 assets

`nuit2.py` adds: `handheld` (noise-driven camera, tremor grows with tension), `rain`, `motes` (dust in a beam),
`steam`, `reveal` (phone torch: a lit render shows through a cone over a dark render of the same set),
`seated` (characters behind a table), `key_shot`, `call_screen`, `black_hands`, `bedroom_door`. Blender views
`--cam=home_entry|home_kitchen --home=dark|lit` (the mother's flat, Poly Haven CC0 furniture). `toon2d.char(mum=True)`
draws the mother (no bracelet: the red bracelet identifies the double). `opensimplex` is required (`pip install opensimplex`).

### Steps and commands

`pipeline/make.sh` wraps every step (paths `A` scripts, `B` assets; `EP` = episode module, default `nuit1`):

```bash
make.sh voices [ids]        # eleven_v3 with acting tags; each take transcribed and scored, fallback multilingual_v2
make.sh probe "0.0" "L_('c1')+1" "T_ECH"   # contact sheet of chosen moments before any render
make.sh test                # every 15th frame, layout only
make.sh render OUT.mp4      # full render (about 25 min for 2:45) and encode; refuses under 1.5 GB free disk
make.sh fix OUT.mp4 12-18   # redo only those seconds (same timeline), re-encode
make.sh qa OUT.mp4          # per-line transcript score, LUFS, duration, frame count, 72-frame sheet, file size
```

### Format and speed settings

- Encode x264 CRF 24, maxrate 3.2 Mb/s, AAC 192k, loudnorm -13 LUFS: 45 MB for 2:48, no visible loss.
- Colour grade is a 3D lookup table (`fast_grade`), lit sprites are cached: 0.4 to 1.2 s per frame on 4 cores.
- `oxipng -o 2 --strip safe` halves the PNG set renders.
- A changed voice line or pause changes the timeline: then only a full render is valid.

### Quality rules

- Captions: at most 3 words, each word appears when spoken, spoken word in red.
- Voices at natural speed, never time-stretched; the acting of a voice cannot be judged by ear, say so.
- Whisper writes numbers as digits ("2h51"): a low score on such a line is not a voice error; read the heard text.
- One shock per episode (smear + negative flash after 1 s of silence).
- Never overwrite a delivered file: write `_vN`.

## Examples

`pipeline/nuit1.py` is the complete reference episode: timeline from voice timings (`at`, `wt`), shots
(`lock_screen`, `order_screen`, `facade` with the scooter rider, `entry_shot`, `stairs_shot` with lamps going
out behind him, `door_mix` for a door whose light follows its opening, `hand_shot`, `swap_shot`, `receipt`),
overlays (`hud`, `buttons`, `stamp`, `callout`), the three rewinds, and the numpy sound mix.
`pipeline/toon2d.py` draws the courier and his dark double in any pose (`char`), the seated `rider` and the
arm through the door (`hand_out`). `voices/nuit1-lines.json` is the script with acting tags.

The pipeline files contain absolute scratch paths of the session that made them; set `A` and `B` (and `NEW` in
`ei2.py`) when restoring them in a new session. The ElevenLabs key is never in a file: the network proxy injects
it and the code sends a placeholder.
