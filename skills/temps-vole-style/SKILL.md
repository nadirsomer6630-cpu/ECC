---
name: temps-vole-style
description: The house style and production method of the EMPLOI INSTABLE interactive thriller series ("Temps volé") - 2D paper characters in lit 3D sets, a clock that is part of the plot, handwritten thoughts, rules that pile up on one poster, wrong choices that rewind like a CCTV tape. Includes the master prompt to start an episode in a fresh session, the episode structure, the quality gate and the working pipeline (Python, Blender, ElevenLabs). Use when writing or producing an episode of this series, or a new series in the same style.
metadata:
  origin: ECC
---

# Temps volé

The style built for the French TikTok series EMPLOI INSTABLE: a temp worker replaces a man who vanished in a
company where nobody leaves after 18:00. Every episode ends on an A/B vote and the audience decides what follows.

## When to Use

- Starting a new episode of EMPLOI INSTABLE, or retouching one.
- Starting another series that should be recognisable as coming from the same author.
- Opening a fresh session: paste the master prompt below instead of replaying a long conversation.

## How It Works

### The grammar of the style

Each element carries meaning. Keep all of them; do not add decoration that carries none.

| Element | Rule | Why |
|---|---|---|
| Characters | Flat 2D sprites (SVG), composited into rendered 3D sets before the camera move | The look viewers recognise; the audience rejected a 3D character test |
| Time | The exact time opens the episode and a clock stays top-right for its whole length | The series is about time taken from people; the clock can freeze, run, or be turned back by the hero |
| Red | Only on what a character is losing: the clock, the stamp, the pocket square, a child's drawing | Red means stolen time; everything else stays white (day) or cold blue (after 18:00) |
| The hero | Never speaks. What he does not say is handwritten on screen, shaky, 2 to 4 words | Second-person narration plus an inner voice, without a second narrator |
| Rules | Valmont's framed poster; each loss adds one handwritten line to the same poster | Rules pile up across episodes and reward returning viewers |
| Wrong choice | Shown in full, stamped, then the image rewinds as black-and-white CCTV tape to the moment of choice | Immediate payoff inside the video, in the series' own vocabulary |
| Shock | One per episode: 1 s of silence, 3 smear frames, a negative flash | Scarcity keeps it effective |
| Captions | 3 words at most, each word appears when spoken, the spoken word in red, 66 px | Never ahead of the voice |
| Ending | An A/B vote whose cards point at things in the scene; last frame dissolves into the first | Vote, then loop |

### Episode structure (60 to 75 s)

1. The time, and one sentence a stranger understands (0 to 5 s).
2. Escalation in short sentences, 3 to 7 words, one real scene per sentence.
3. In-video choice at 12 to 20 s: two cards, a bar that runs out in about 1 s.
4. Outcome A in full (the loss), the stamp, the new rule written on the poster.
5. Tape rewind, outcome B, then the silence and the shock.
6. The emotional beat: a detail from someone's life (a drawing, a voicemail, a bracelet).
7. The idea of the episode: the hero uses a rule against the company.
8. The stake, stated by the antagonist in one line.
9. The vote. Both options must cost something.

### Method, in order

1. Check the tools exist (see `pipeline/`), ask every open question in one message, offer 3 pitches.
2. Write the script as lines with a speaker; keep the wording of a line stable once voiced.
3. Voices: ElevenLabs `eleven_v3` with acting tags in brackets, 2 takes per line; transcribe every take; fall
   back to `eleven_multilingual_v2` for a line whose names come out wrong.
4. Sets in Blender (`blender_env.py valmont ... --cam=<view>`), preview at 8 samples before the HD still.
5. Sprites: edit the SVG source, re-render with Playwright; poses are rotations of arm, leg and head groups.
6. Assemble (`ei3.py`): every cut is anchored on a spoken word through `wt(line, word)`, never on seconds.
7. Probe key frames, then full render; later retouches use the partial render.
8. Quality gate: `qa_episode.py` scores every line against the script on its own audio window; look at frames
   of each changed shot; state plainly what could not be judged (the acting of a voice).

### Pipeline files

`pipeline/` holds the working sources as they ran for episodes 2 and 3. They contain absolute paths to a
session scratch directory (`NEW`, `HD1`, `HD2`): set those first. The ElevenLabs key is never in a file; the
session's network proxy injects it and the code sends a placeholder.

| File | Role |
|---|---|
| `ei2.py` | Episode 2 and the shared engine: camera, sprites, lights, HUD, inserts, sound |
| `ei3.py` | Episode 3: loads the engine from `ei2.py`, defines its own timeline, shots and sound |
| `grade.py` | Voice loading, captions, tape look |
| `blender_env.py` | Every 3D set, selected by `--cam=` |
| `qa_episode.py` | Line-by-line voice check, duration, loudness, frame count |
| `elv5_gen.py`, `asr.py` | Voice generation and transcription |
| `sprites/` | Character sources and the two Playwright renderers |

## Examples

### Master prompt for a fresh session (paste as the first message, in French)

```text
Tu réalises l'épisode N de ma série TikTok EMPLOI INSTABLE dans le style « Temps volé ».
Lis d'abord skills/temps-vole-style/SKILL.md et applique sa grammaire sans exception.

Étape 0. Vérifie en silence que tu as Python, Blender (module bpy), ffmpeg, Playwright et l'accès à
ElevenLabs, puis dis-moi en quatre lignes ce qui manque.
Étape 1. Pose-moi toutes tes questions en un seul message : résultat du dernier vote, durée visée,
ce que je veux garder ou changer.
Étape 2. Propose trois pitchs d'une phrase chacun. J'en choisis un.
Étape 3. Écris le script : l'heure exacte en ouverture, des phrases de 3 à 7 mots, un choix dans la
vidéo avec ses deux issues, une règle ajoutée à l'affiche, un seul choc, un détail de vie réelle,
un vote final où les deux options coûtent quelque chose.
Étape 4. Voix, décors, personnages, montage, puis contrôle réplique par réplique.

Tu n'avances pas sans mon « ok », sauf si j'écris « enchaîne ». Tu ne livres que des versions
vérifiées et tu me dis ce que tu n'as pas pu vérifier.
```

### Commands

```bash
export HF_HOME=<cache dir>
python3 ei3.py out.mp4                          # full render
EI_STEP=30 python3 ei3.py /tmp/x.mp4            # one frame per second, layout test
EI_RANGE=5.7-9.4 python3 ei3.py out.mp4         # re-render one time range, same timeline only
python3 qa_episode.py ei3 out.mp4               # the quality gate
```

### What a wrong-choice block looks like (episode 3)

Question "Tu te retournes… ou tu cours ?" (cards, bar) then outcome A: her eyes fill the frame, the hero is
seated with a headset, the stamp PERMANENT lands, the poster gains "6. Ne la regarde jamais dans les yeux."
Then the tape rewinds with "TU RECOMMENCES." and outcome B plays.
