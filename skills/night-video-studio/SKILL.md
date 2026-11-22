---
name: night-video-studio
description: Writes, produces, retouches and checks the French interactive horror TikToks of the night-job series ("Livreur de nuit", the courier, Samir, the mother, the double, and the next seasons such as caissier de nuit or gardien de piscine) - script in short lines, ElevenLabs voices checked by transcript, 2D characters in Blender sets, phone screens, in-video choices with both outcomes, one-command render and partial re-render, sound, quality gate, then the TikTok description and the stats follow-up. Use it whenever the user asks for a new episode or part, a fix on a delivered episode, a description or hashtags for one of these videos, or an analysis of their TikTok Studio numbers, even if they only say "fais la suite", "corrige", "je mets quoi en description" or send screenshots of their stats.
metadata:
  origin: ECC
---

# Night video studio

The production kit of a French TikTok creator's interactive horror series: each night the viewer ("tu") does a
night job, a double wears the faces of the people he loves, and every choice tests one rule. The user writes in
French; answer in plain, complete French. The kit exists to save time: one script per episode, one command per
step, and checks that run before anything is delivered.

## When to Use

- A new episode or part: start from `scripts/nuit5.py` (the latest) and a new lines file.
- A fix on a delivered episode: change the shot, then re-render only the seconds that changed.
- A description, a pinned comment or hashtags for a video.
- TikTok Studio screenshots or stats to analyse: read `references/account.md` first and update its test log.

## How It Works

### 1. Decide what this episode tests

Open `references/account.md`. It holds the account's real numbers and the test log: one variable changes per
video (the opening, the length, the hashtag...) so the next stats can say something. Name the variable before
writing, and keep the rest of the recipe as it was.

### 2. Write the script

These rules come from the account's own numbers and from videos of the niche at 0.2 to 2.8 M views. The details and
the sources are in `references/craft.md` and `references/catalogue.md`.

- **The episode must work for someone who never saw the others.** 93 to 98 % of views come from For You. The nights
  that opened on a self-contained premise held best (Nuit 1 "le client porte ton nom": 26 % watched, 10.9 % to the
  end); the ones that opened on context or a recap held worst (Nuit 3: 12 %, 1.9 %). So frame 0 shows the whole
  premise and its anomaly at once: the voice starts on "Imagine." and the image already shows what is wrong (the
  mother's text on top of Samir's call, a phone screen with a red tag), with a 3-4 word yellow banner stating the
  stakes ("IL EST À DEUX ENDROITS."). No title card, no "previously" in the first seconds: the episode number goes
  in the HUD line and the description.
- **Short lines**: 3 to 7 words, one image each, no connectors ("Elle ouvre. Sur le palier, Samir. Il sourit.").
  Sounds the hero cannot see are described by the voice.
- **Length**: a part runs 60 to 65 s; a single episode stays under 1:45. Viewers told the creator long episodes
  bore them, and every Studio curve loses most viewers in the first two seconds anyway.
- **One rule, tested**. An in-video choice shows both outcomes: the wrong one ends in a loss whose clue was visible
  before, the clue is replayed ("TOUT À L'HEURE"), a red "RÈGLE N°x" card is written by hand on the order slip
  (rules 1 to 9 exist; the next is 10), then a tape rewind and the right outcome.
- **The phone carries the story**: the mother's texts as notifications at the top, the video call with Samir (same
  frame every time), order and map apps with real detail. A HUD line stays on screen: night, place, clock.
- **Dialogue as shot / reverse shot**, a new close-up for every line, and one or two funny lines from Samir.
- **One shock per video**: one second of silence, then a smear and a negative flash on the monster's close-up.
- **The end** makes the next video necessary: a last line that reframes everything, then an end card "TU FERAIS
  QUOI ?" with two buttons, one line each on what the choice costs, "Écris A ou B en commentaire", "Abonne-toi".

Write the lines as `voices/<episode>.json`: `[[id, voice, "[acting tags] text"], ...]` with voices `narr`
(Alexandre), `samir` (Martin), `mere` (Agnès). Ids starting with `s` are filtered as phone audio by the mix.
Never clone or imitate another creator's voice.

### 3. Voices

Copy the newest generator (`scripts/elv11_gen.py`) with its folder path changed. It calls eleven_v3 with the acting
tags, transcribes every take with faster-whisper, scores it against the line, retries with other seeds then with
eleven_multilingual_v2, and rejects a take that is still loud in its last 0.15 s (a take cut mid-word once slipped
through). The API key is injected by the network proxy; the code sends the placeholder "proxy-injected". Whisper
mishears short words ("Clic" as "Clique", digits for numbers): read the heard text instead of trusting a low score.

### 4. Build the episode module

Copy `scripts/nuit5.py`. Its order matters, because later parts depend on earlier ones: voices and their word
timings (`at` builds the timeline, `wt(line, word)` gives the time of a spoken word), then shot functions that
return a 1080x1920 image for a time `t`, then `raw()` that picks the shot, `finish()` that adds grade, HUD,
banners, notifications, buttons and captions, then the numpy sound mix in `__main__`. Anchor every cut and effect
on `wt`/`L_`, never on hard-coded seconds, so a new voice take moves everything with it. Word anchors compare
lowercase words with their accents kept ("s'éteint" -> `"teint"`).

### 5. Look before rendering

`python3 probe6.py "0" "L_('s1')+1" ...` (copy it for the new module) renders chosen moments to a contact sheet in
a few minutes. Check every shot there: frame 0, banners not covering faces or bubbles, the monster big enough,
nothing black, captions inside the safe zone.

### 6. Render

- Free disk first: a 60 s episode needs about 0.7 GB of JPEG frames; delete old `*tmp/f*.jpg`.
- Render in four independent processes, `python3 slices.py <module> k 4 0-<duration>` for k = 0..3, because the
  multiprocessing pool hung several times. A slice can die silently: count frames, then `fill5.py` renders only
  the missing ones (run it once more if a few remain).
- Write `timeline.sig`, then `EI_AUDIO_ONLY=1 python3 <module>.py OUT.mp4` mixes the sound and encodes (x264 CRF 24,
  maxrate 3.2 Mb/s, loudnorm -13 LUFS).
- A visual fix with the same voices and pauses: re-render only those seconds with `slices.py <module> k 4 a-b`, then
  encode again. A changed voice take or pause changes the timeline, and only a full render is then valid.

### 7. Optional: library sound effects

OpusClip AI Producer can lay its library sounds (wood thuds for knocks, clicks, tape rewind, paper, sub impacts,
clock ticks) at exact milliseconds on an uploaded video, and exported without a watermark when tried (Descript's
free plan watermarks). Keep our video stream and take only the audio of its export, renormalised to -13 LUFS, then
check that the offset is zero. Uploading sends the video to a third party: do it for our own renders only.

### 8. Quality gate (before saying it is done)

- Transcribe the final audio passage by passage and compare with the script; re-check a doubtful line with a clip
  framed around it before concluding.
- Loudness about -13 LUFS, duration, frame count, a contact sheet of every changed shot.
- Say plainly that the acting of a voice and the balance of sound effects cannot be judged by transcript.
- Never overwrite a delivered file: write `_vN`.

### 9. Deliver the description

Format, from the account's hashtag study:
`« <a line of the monster or the hook> » 👁️ Nuit N, partie P : <the choice as a question> ? #horreur #creepypasta #<test tag>`

- Three hashtags only: `#horreur #creepypasta` and one rotating test tag from the test log. Never #pourtoi and its
  variants, #pov, #animation or #livreur (they bring the wrong audience or none).
- A pinned comment that asks the A/B question or points at the fair clue ("tu avais remarqué qu'il était sec ?").
- Posting advice: the cover is the opening image, the same posting hour every time, a new part posted as a video
  reply to the comment that won the vote, an older version set to "Seulement moi" rather than deleted.

## Examples

**Example 1**: "fais la partie 2, ils ont voté B" -> check the test log, write a cold-open script of about 60 s with
the vote paid off on screen, generate and check voices, probe, render, gate, then give the file and its
description.

**Example 2**: the user sends four TikTok Studio screenshots -> compute % watched and full-view rate for each video,
compare at equal age, update the test log in `references/account.md`, separate facts from hypotheses, and say what
the next video should change.

The scripts contain absolute scratch paths of the session that made them; set `A` (scripts) and `B` (assets) when
restoring them in a new session.
