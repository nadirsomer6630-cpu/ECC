---
name: night-video-studio
description: Writes, draws, animates, produces, checks and publishes advice for the French interactive horror TikToks of the night-job series ("Livreur de nuit", then caissier de nuit, gardien de piscine...) - the hero, Samir, the mother and the double drawn with toon5 in a flat 2D dark-fantasy style, scripts in short lines with the 6-beat blueprint, ElevenLabs voices checked by transcript, phone screens, in-video A/B choices, animation on twos, sound, quality gate, descriptions and stats follow-up; also learning from reference videos (YouTube, TikTok) with Gemini and folding the lessons into the kit. Use it whenever the user asks for a new episode or part, a fix on a delivered episode, a change to a character's look (hair, eyes, teeth, clothes), a description or hashtags, an analysis of TikTok Studio numbers, or sends a video or a creator to learn from, even if they only say "fais la suite", "corrige", "change mes cheveux", "apprends cette vidéo" or send screenshots.
metadata:
  origin: ECC
---

# Night video studio

The production kit of a French TikTok creator's interactive horror series: each night the viewer ("tu") does a
night job, a double wears the faces of the people he loves, and every choice tests one rule. Answer in plain,
complete French. The kit saves time: one script per episode, one command per step, checks before delivery.

## When to Use

- A new episode or part: script with the blueprint, then the pipeline below.
- A fix on a delivered episode: change the shot, re-render only the seconds that changed.
- A change to a character: see "Characters" - one change at a time, checked at 1000 px.
- A video, a YouTube tutorial or a TikTok creator to learn from: see "Learning from a reference".
- A description, a pinned comment or hashtags; TikTok Studio stats: read `references/account.md` first.

## How It Works

### 1. Decide what this episode tests

`references/account.md` holds the real numbers and the test log: one variable changes per video so the next stats
can say something. Name the variable before writing; keep the rest of the recipe.

### 2. Write the script (blueprint in `references/craft.md`, sources in `references/catalogue.md`)

The six beats, because they are what the top storytime and horror videos share:
1. **Hook, 0-5 s**: "Imagine." over an image that already shows the anomaly, a 3-4 word yellow banner with the
   stakes. Half the viewers leave at 0:01-0:02 and 93-98 % come from For You, so the episode must work alone: no
   recap, no title card.
2. **Context** in one or two lines, then **a promise with a time** ("Dans une minute, tu vas devoir ouvrir.").
3. **Escalation by three**: three signs, each worse (three knocks, three texts, three near-misses).
4. **The pivot**: the in-video A/B choice, with "A OU B ? ÉCRIS-LE" on screen (only 10-14 % reach the end card).
   Both outcomes are shown: the wrong one ends on a fair clue replayed ("TOUT À L'HEURE"), a red "RÈGLE N°x" card
   (the count continues across seasons; next is 10), a tape rewind.
5. **Payoff**: the consequence, shown.
6. **Landing**: a last line that calls back the opening or loops to frame 0, then "TU FERAIS QUOI ?" with two
   buttons and what each costs.

Lines of 3 to 7 words, one image each. Dialogue as shot / reverse shot, a new close-up per line, one or two funny
lines from Samir. Sounds the hero cannot see are said by the voice. One shock per video (one second of silence, a
smear, a negative flash). A part runs 60-65 s; cut every dead second.

Lines go in `voices/<episode>.json` as `[[id, voice, "[acting tags] text"], ...]`: `narr` (Alexandre), `samir`
(Martin), `mere` (Agnès); ids starting with `s` are phone audio. The double speaks with the voice it steals. Never
clone or imitate another creator's voice.

### 3. Characters (`scripts/toon5.py`, spec at the top of `references/style-bible.md`)

The current cast is v19: flat 2D like the creators the user follows (big heads, big eyes, thick outline, flat
colour, one shadow shape), dark fantasy as the only theme. Identities are fixed; the creator found wholesale
redesigns "too radical", so:
- Change one thing at a time, only what was asked, and show it next to the previous version.
- Draw hair by hand as a few shapes; never generate it procedurally (it made gaps, scallops and spikes before).
- No stacked rendering effects on faces (halftone, hatching, height maps made them noisy and plastic).
- Check every new face at 1000 px with a red centre line: stains, asymmetry, teeth or strands crossing outlines.
- `python3 toon5.py out.jpg` (expressions sheet, ~25 s), `python3 toon5.py out.jpg model` (three-quarter sheet).
`bust5(who, look, brow, mouth_, wide, blink, sway, size, light, boil, turn)`; the list of what went wrong and why is
in `references/learned.md`.

### 3b. The whole frame (`references/art-direction.md`)

The gap with the reference creators was never the faces: it was the frame. Every shot is a lit 3D set
(`scripts/supermarche.py` for the supermarket) with our characters standing in it (`scripts/scene5.py`:
`figure5` full body with poses, `back5` for over-the-shoulder, `place` tints them with the set's light and adds a
contact shadow), a fixed HUD (place + "NUIT 1 / 30" on the left, a label + the clock on the right), one caption line
in heavy white capitals with one orange word, a cold grade and a vignette. `scripts/frames_s2.py` builds three
test frames; `assets/comparaison_reference_vs_nous.jpg` is the side-by-side to beat.

Prompts (`references/prompts.md`): the fixed style line, the negative line, each character's identity anchors,
the seven-field shot spec (`scene5.render_shot(spec, sets)`, demo `scripts/shots_demo.py`) and the script prompt.
Every shot of an episode is written as a spec first; only the per-shot fields may vary.

### 4. Voices

Copy the newest generator (`scripts/elv11_gen.py`): eleven_v3 with acting tags, every take transcribed with
faster-whisper and scored, retries with other seeds then eleven_multilingual_v2, a take still loud in its last
0.15 s is rejected. The key is injected by the proxy ("proxy-injected" in code). Whisper mishears short words and
numbers: read the heard text.

### 5. Animate and build the episode module

Copy `scripts/nuit5.py`: voices and word timings (`at`, `wt(line, word)`), shot functions returning a 1080x1920
image for time `t`, `raw()`, `finish()` (grade, HUD, banners, notifications, buttons, captions), the numpy sound mix.
Anchor every cut on `wt`/`L_`, never on seconds. Animation rules (from the tutorials, `references/learned.md`):
12 drawings a second held two frames, `line_boil` with a new seed per drawing, key poses first, subtle motion
(blinks, small nods) over big moves, horror timing as a long hold then a brutal pose with no in-between, the shadow
follows the light (`light=`), characters on their own layer with a blurred foreground for depth, glow only on magic
objects, a vignette. Test: `scripts/anim_test_v18.py`. Acting (`rig5.py acting`): anticipation before a move, overshoot (`back_out`), hands and head
on springs (`Spring`), blinks in five drawings (`lid`), emotions through several face drawings, fear played by the
body (shoulders up, a tremor, a step back, a hand to the chest).

### 6. Look before rendering, then render

`probe6.py "0" "L_('s1')+1" ...` renders chosen moments to a contact sheet: frame 0, banners off faces, the monster
big enough, nothing black, captions in the safe zone. Free disk first (about 0.7 GB of frames per minute). Render in
four processes (`slices.py <module> k 4 0-<dur>`), count frames, `fill5.py` the missing ones, then
`EI_AUDIO_ONLY=1 python3 <module>.py OUT.mp4` (x264 CRF 24, maxrate 3.2 Mb/s, loudnorm -13 LUFS). A visual fix with
the same voices re-renders only those seconds; a changed take or pause needs a full render.

### 7. Quality gate (before saying it is done)

Transcribe the final audio passage by passage against the script; loudness about -13 LUFS; duration and frame
count; a contact sheet of every changed shot. Say plainly that acting and sound balance cannot be judged by
transcript. Never overwrite a delivered file: write `_vN`.

### 7b. Two posts a day (`references/publishing.md`)

One production per night, two videos: part 1 at midday (the dilemma, the riddle, the A/B choice, 55-62 s) and part
2 in the evening (the answer, the rule card, the loop, 28-35 s), posted as a video reply to the winning comment.
Keep the same two hours every day and compare after 7 days. If a night is not ready, post a short riddle (15-20 s)
cut from existing shots rather than a rushed episode.

### 8. Description and posting

`<Story name>... | <the choice as a question> ? #horreur #creepypasta #<test tag>` (no night or part number: every video stands alone, see `references/account.md`), or a quoted line the
viewer hears as the story name. Three hashtags only (#flippant is the strongest third seen; never
`#pourtoi`, `#pov`, `#animation` or `#livreur`). A pinned comment with the A/B question or the fair clue. The cover is the opening image, the
same posting hour, a new part as a video reply to the winning comment, an old version set to "Seulement moi".

### Learning from a reference

1. Get it: `scripts/gemini_look.py <youtube-url | file.mp4> "question"` (TikTok: yt-dlp first; profiles: TinyFish,
   then verify counts with yt-dlp). Ask for timestamps, techniques, mistakes, settings, and how to apply them to
   flat 2D characters. Retry with pauses when the models answer 503.
2. Separate method from identity: keep the method, never the characters, art, titles or voices.
3. Social watch and earning: `references/social.md` (`scripts/veille.py` ranks videos by their real rates; photo
   carousels through TinyFish image links; what each platform pays for and under which conditions; every video at
   least 61 s).
4. Apply one concrete lesson to the kit (code, rule, or script beat), show the result, and record source, lesson and
   where it went in `references/learned.md`. Tools and their pitfalls: `references/tools.md`.

## Examples

**Example 1**: "fais la partie 2, ils ont voté B" -> test log, a 60-65 s script on the six beats with the vote paid
off, voices checked, probe, render, gate, then the file and its description.

**Example 2**: "mes cheveux ne sont pas naturels et le monstre ne fait pas peur" -> render both at 1000 px, name
what is wrong, fix only those parts in `toon5.py`, show before/after, update the spec at the top of the style bible.

**Example 3**: the user sends four TikTok Studio screenshots -> % watched and full-view rate per video at equal age,
the test log updated, facts separated from hypotheses, one variable for the next video.

The scripts contain absolute scratch paths of the session that made them; set `A` (scripts) and `B` (assets) when
restoring them in a new session.
