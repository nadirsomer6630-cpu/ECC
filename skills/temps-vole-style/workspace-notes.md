# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this workspace is

`/home/user` is not a git repository. It is the working area of a French TikTok creator who produces vertical interactive thriller series (each episode ends on an A/B vote): **L'ASCENSEUR**, **BLACKOUT** and **EMPLOI INSTABLE**. Claude writes the scripts and produces the full episodes (3D sets, 2D characters, voices, sound, captions, HUD). The user speaks French; reply in plain, complete French sentences.

- `*.mp4` at the root are delivered episode versions. Never overwrite one: write a new `_vN` file.
- `ecc/` is the only repository Claude may push to for this work (`nadirsomer6630-cpu/ecc`, branch `feat/tiktok-story-series-skill`, never the default branch). It has its own `CLAUDE.md`; the reusable know-how lives in `ecc/skills/story-video-toolkit/` and `ecc/skills/tiktok-story-series/`.
- `studio/` is the user's Roblox Studio MCP config (pushable, unrelated to video).
- `pmndrs/`, `motion-canvas/`, `drona23/`, `nadirsomer6630-cpu/`, `affaan-m/`, `openai/` are read-only reference clones. Only `motion-canvas` is relevant to video (candidate for animated UI inserts, untested here).

## The pipeline lives in two scratchpads, and they are volatile

Scripts: `/tmp/claude-0/-home-user/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/` (called `$A` below).
Assets, voices, caches, temp frames: `/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/` (called `$B`).

Both disappear when the container is reclaimed, and nothing in them is committed. Before relying on them, check they exist. If they are gone, the episode `.mp4` files and the skills in `ecc/` are what survives; the scripts must be rebuilt from the skill.

Disk is a fixed allowance (about 2 GB free). A full episode render needs about 1 GB of temp JPEG frames in `$B/ei2tmp/`. Delete old `*tmp/f*.jpg` frames and unused clones before rendering.

## Commands (EMPLOI INSTABLE episode 2, the current work)

```bash
A=/tmp/claude-0/-home-user/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad
B=/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad
export HF_HOME=$B/hfcache          # faster-whisper model cache, required by every ei2.py run

cd $A
python3 ei2.py /home/user/emploi_instable_ep2_vN.mp4            # full render, about 22 min, Pool(4)
EI_SHOT=list python3 ei2.py /tmp/x.mp4                          # print the 16 named shots and their times
EI_SHOT=portique,vote python3 ei2.py /home/user/out.mp4         # re-render only those shots, about 6 min
EI_STEP=30 python3 ei2.py /tmp/x.mp4                            # every 30th frame, quick layout test, no encode
EI_AUDIO_ONLY=1 python3 ei2.py /home/user/out.mp4               # remix sound and re-encode from existing frames

python3 $B/ei2probe.py                                          # render a contact sheet of chosen timestamps to $B/qa/e3probe.jpg (edit the `ts` list)
python3 -I $B/asr.py file.wav [...]                             # transcribe to check a voice take or the final mix

# 3D sets (Blender as the bpy Python module, Cycles CPU)
python3 -I $A/blender_env.py valmont $B/ei2hd/gate_ 1 1 32 --fast --hires --evening --rich --cam=gate
#   cams: hall open desk chair door exit gate stairs stairdoor basement ; preview without --hires and with 8 samples

# 2D character sprites (SVG rendered by Playwright)
python3 $B/ei2sprsrc/make.py && node $B/ei2sprsrc/shoot.js $B/ei2sprsrc/ $B/ei2spr/

# Voices (ElevenLabs; the key is injected by the network proxy, code sends the literal "proxy-injected")
python3 $B/elv4_gen.py [line ids]                               # eleven_v3 with acting tags, 3 takes per line into $B/elv4/
```

`EI_SHOT` refuses to run if the timeline changed (any voice take or pause) or frames are missing; then a full render is the only option. Importing `ei2` (as the probe does) is safe: frames are only deleted at the start of a full render.

## Architecture of an episode script (`ei2.py`)

One file builds the whole episode in this order, and later stages depend on earlier ones:

1. **Voices to timeline.** `VO_A` loads the chosen takes from `$B/elv2/fin4/`. `align()` matches whisper word timings to the script text at letter level, so captions use the script's spelling with real timings. `at(key, gap)` appends each line to the timeline (`line_t`), and `wt(key, word)` gives the time of a spoken word. Every cut and effect is anchored on these (`T_NON`, `T_ROUGE`, `T_OUVRE`, ...), never on hard-coded seconds.
2. **Shots.** Each shot is a function returning a 1080x1920 PIL image for time `t`: 3D stills (`ST[...]`, rendered 1.2x oversize) moved by `view()` (sub-pixel crop, slow drift), or 2D inserts drawn in PIL (phone, rules poster, badge, drawing, HR screen, bracelet). Characters are 2D sprites composited into the still *before* `view()` so set and character move together. `view_xy()` maps a point of a still to screen coordinates for HUD callouts.
3. **`render(i, t)`** picks the shot from the timeline, applies the grade (`white_grade` for the clinical present, `night_grade` after 18:00), then overlays HUD (`hud`, `tag`, `hud_chip`, `callout`), handwritten thoughts (`THOUGHTS`), vote cards and captions (`grade.karaoke`). `frame(i)` adds the 0.3 s dissolves listed in `CUTS`.
4. **Sound** is synthesised in numpy at the end of `__main__` (hum, ticks, heartbeat, bells, keyboards, the shock), voices are mixed over it with ducking, then ffmpeg encodes (x264 crf 21, about -13 LUFS).

Shared helpers: `grade.py` (voice loading, captions, tape look, `filmic`), `blender_env.py` (all 3D scenes for every series; Valmont views are selected with `--cam=`; `prop()` imports Poly Haven glTF models from `$B/models/`; the `basement` and `gate` views also export JSON with screen positions that `ei2.py` reads). `SD` in `ei2.py` is an ImageDraw proxy that draws at 2x for anti-aliased shapes; `spill`, `torch`, `rim_light` and `bloom` are the lighting helpers.

Older episodes follow the same shape: `ei1v2.py` (EMPLOI INSTABLE ep1), `ep4.py` (L'Ascenseur ep4), `bo3.py` (Blackout ep3).

## Rules the user has set

- Deliver only verified versions: transcribe the final audio passage by passage and compare with the script, check loudness, and look at frames of every changed shot. Whisper mishears short clips cut mid-word; re-check with a clip framed around the phrase before concluding. Say plainly that the acting of a voice cannot be judged by ear.
- Captions: at most 3 words per group, each word appears when it is spoken (never before), only the spoken word highlighted, 66 px, inside TikTok safe zones.
- Voice at natural speed with a short pause after sentences; never time-stretch it.
- One real scene per sentence, no gimmick transitions, no split screen. One smear + negative-flash shock per episode, preceded by 1 s of silence. "À SUIVRE" instead of dates.
- Characters keep the same look across episodes (2D characters in 3D sets). A 3D-character test is agreed for one shot of episode 3 only.
- EMPLOI INSTABLE signature: the episode opens on the exact time, the hero never speaks (his thoughts are handwritten on screen), red is reserved for "stolen time", the past is black-and-white CCTV tape, the last frame loops into the first.
- Voices: Alexandre (narrator), Victoria (Kessler), Martin (Samir), Agnès (the mother), on ElevenLabs. Never clone or imitate another creator's voice or mascot.
- Descriptions: one hook sentence, an explicit "A ou B" comment prompt, 4 hashtags. Be honest about what a description or a tool can and cannot do for reach.
- Group fixes into one render; use `EI_SHOT` for visual-only retouches. Free tools are preferred; ElevenLabs is the one paid service.
- Assets must be CC0 or clearly licensed. Reachable from this session: Poly Haven, ambientCG (API works). Kenney, Quaternius and Mixamo need the user to download and upload the packs.

# STUDIO 3D / VIDÉO

## Objectif
Créer un studio web 3D/2D de qualité professionnelle :
- Scènes 3D interactives avec Three.js / React Three Fiber.
- Import de modèles GLB/glTF depuis Blender.
- Vidéos génératives 2D avec Motion Canvas.
- Interface sombre premium, fluide et accessible.
- Export vidéo 1080p.

## Stack
- Vite + TypeScript + React.
- Three.js + React Three Fiber + drei.
- postprocessing pour le rendu cinématique.
- shadcn/ui + framer motion pour l’interface.
- Motion Canvas pour la vidéo 2D.
- glTF/GLB pour les assets Blender.
- Draco / Meshopt / KTX2 pour l’optimisation.

## Qualité
- Aucun placeholder, mock ou fonctionnalité simulée.
- Rendu fluide à 60 fps.
- Interface responsive et accessible.
- Aucun TODO, code mort ou dépendance inutilisée.
- Direction artistique forte : palette restreinte, typographie expressive, animations utiles.

## Définition de terminé
Le travail est terminé seulement si :
- Le projet démarre sans erreur.
- Les interactions fonctionnent.
- Le rendu est visuellement abouti.
- La performance est vérifiée.
- Tu indiques les fichiers modifiés et la commande de lancement.

# Episode method for the next episodes (added after studying scenar.app's public examples)

Only the public parts of scenar.app were read (style descriptions, the first lines of four prompts with their step lists, three example videos). The full prompts are paid and were not accessed; if the user buys and pastes them, adapt from the pasted text.

What their best-performing format does that ours did not, and what to apply from EMPLOI INSTABLE episode 4 on:

- **Pay off a choice inside the video.** Their horror example asks "A ou B ?" at about 15 s, then shows both outcomes in the same video ("Si tu as choisi de rentrer… tu es mort."). Ours asked one question at the very end and answered it days later. New structure: one early in-video choice with both outcomes shown (the wrong one ends in a short, clear loss), then the end-of-episode vote for the big decision.
- **Each loss teaches a rule.** After a wrong choice, a full-screen red card "RÈGLE N°x" states what the viewer just learned. It fits Valmont's rule poster; keep a running rule count across episodes.
- **A live clock on screen for the whole episode**, with a small location line above it ("NIVEAU -2 · ALLÉE C"). We already open on the exact time; keep it running at the top instead of showing it once.
- **Shorter sentences.** Their lines are 3 to 7 words ("Tu te retournes. La rue est vide."). Aim for that; cut every connector.
- **Process before production** (from their step lists): check tools, ask the user the open questions in one message, offer 3 pitches, write the script, then voice, animation, frame-by-frame check, render. For a "survival" beat use: hook in one sentence, the steps, the false good idea, the twist.
- **End on "Partie 2 ?"-style hunger**: the last line must make the next episode necessary, and subscribers' names or comments can appear in the set (rule poster signatures, HR screen names) to reward commenting.

Keep unchanged: 2D characters in 3D sets, the handwritten thoughts, red = stolen time, the user's voices, one shock per episode.
