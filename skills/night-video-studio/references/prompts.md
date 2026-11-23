# Prompts: what we analysed, what we keep, and our own master prompts

The creator asked for every prompt worth studying to reach an art of our own. We do not generate images with an AI
model: our pipeline draws them in code. So a prompt here is a specification that the code and the writer follow,
written so it would also work in an image or video model if the creator ever uses one.

## 1. Sources analysed (November 23)

| Source | What it is | Kept | Dropped |
|---|---|---|---|
| OpenCreator `sun-style-writing` (cloned repo, MIT-style community template) | short-sentence non-fiction narration rules | short lines; concrete objects and numbers instead of adjectives; one ordinary object as a clue that comes back without being explained; turning points carried by a silence, a change of address, an action, a broken repetition; open on a contrast in three sentences; end on a concrete image that echoes the opening, never a moral | its fact-only constraint (we write fiction) |
| scenar.app (public parts, read earlier) | paid episode prompts for TikTok stories | check tools, ask open questions in one message, offer 3 pitches, then script; "hook, steps, false good idea, twist" for survival beats | the paid prompts (never accessed) |
| Storytime video (Claude Code + Higgsfield) | AI storytime pipeline | hook 0-5 s, context, escalation by three, pivot, payoff, landing; a "master prompt" locking the character's look; a breakdown per scene (description, narration, image, motion) | the paid video model |
| [Loova prompt pack](https://loova.ai/blog/ai-animation-character-consistency-prompt-pack) | character consistency template | an identity block (face, hair, eyes, skin, outfit, accessories, distinctive marks, style), then scene / action / expression / camera / lighting, then a lock: "preserve the exact identity... only change what this shot specifies"; a turnaround (front, 3/4, side, 3/4 back, back) | - |
| [Neolemon character DNA](https://www.neolemon.com/blog/best-ai-cartoon-prompts-copy-paste-ready/), [art-style list](https://www.neolemon.com/blog/list-of-art-styles-for-ai-prompts/) | worksheet and style tokens | "MUST NEVER CHANGE: 3 to 5 identity anchors"; a 1-2 line style line pasted unchanged into every prompt; drift starts with eye shape, hair silhouette and line weight, so lock those three | generic style lists |
| [Elser.ai video lock](https://www.elser.ai/blog/best-character-consistency-prompts-for-ai-video) | negative lock | "do not make the character realistic, 3D, older, younger, or visually different" | - |
| [Cartoon-show master style](https://cartoon-show-site.vercel.app/) | show bible workflow | study the references, write ONE coherent original style with rules for characters, locations, props and scenes, then reference it in every prompt | - |
| [Promptmake cartoon tokens](https://promptmake.net/blog/cartoon-styles-ai-prompt-keywords), [PromptHero cel shading](https://prompthero.com/search?q=cel+shading) | style vocabulary | name the medium, the outline thickness and the shading family: "2D cel animation still, bold black contours, flat color fills, two-tone cel shading (one hard shadow step), thin rim light" | heavy "volumetric fog" and photo-lens tokens: they pull a flat look toward 3D |
| [MakeAIPrompt dark fantasy reveal](https://makeaiprompt.com/blog/cinematic-dark-fantasy-storytelling-character-reveal-prompt/) | dark fantasy mood words | hard moonlight, high-contrast shadows, a glowing violet rim | stained glass and medieval props (not our world) |
| [Questas](https://blog.questas.co/the-new-visual-writers-room-building-a-shared-prompt-style-and), [MindStudio](https://www.mindstudio.ai/blog/ai-short-film-under-200-production-workflow), [Alici](https://alici.ai/formulas/media/fluently.jess/3e37498a-d2dc-5783-9644-4f9e251abf8f-fluently-ambassador-get-paid-for-views-ai-video), [storysnap](https://github.com/yavor-yankov/storysnap/issues/26) | shot prompt structure | [subject] + [action] + [environment] + [camera] + [lighting] + [grade] + [motion], timecoded; an invariants list (identity, wardrobe, style, grade) separate from a variables list (action, framing); a shot list with type, purpose and duration | - |
| video-shotcraft shot cards (installed skill) | motion vocabulary | hidden cut (a foreground object sweeping past hides a hard cut: a shelf, a passer-by), light-leak burn (a warm flare peaks and the cut hides in it), versus slam (two halves collide: the A/B choice), outline word fill (a hollow word snaps solid: "RÈGLE N°10") | product-film framing |

## 2. What this changes for us

- One **style line** never changes and opens every shot spec (below).
- Every character has **identity anchors that must never change**; everything else is a per-shot variable.
- Every shot is written in the same **seven fields**; the code renders from those fields (`scene5.render_shot`).
- Scripts follow the six beats plus the sun-style rules: the clue is an **object** that comes back, the turn is a
  **silence or a broken repetition**, the end is a **concrete image**, never a moral.

## 3. Our master prompts

### Style line (paste unchanged)

> Flat 2D cel animation, big-headed characters with bold black contours and flat colour fills, one hard shadow step
> leaning violet, a thin lavender moonlight rim; standing in a dark cinematic 3D night set with pools of cold light
> and deep black; dark fantasy, quiet and uncanny; vertical 9:16, heavy white captions with one orange word.

### Negative line

> Not realistic, not 3D characters, no soft airbrushed gradients, no halftone or hatching on faces, no photo lens
> blur on characters, no bright daylight, no extra characters, no change to anyone's face, hair, eyes or clothes.

### Identity anchors (must never change)

| Character | Anchors |
|---|---|
| Toi | slicked-back wavy dark brown-black hair; the dark-blue dyed lock over the left brow; hazel eyes with a faint green rim; the scar through the left brow; purple track jacket with white stripes and the gold moon brooch |
| Samir | green beanie with a cream pompom; short beard and moustache; green quilted puffer; gold stud in the left ear |
| Maman | grey bun with a gold pin; round gold glasses; pink cardigan over a cream turtleneck; pearl earrings |
| Le double | the hero's hair and clothes, darker; black eyes with a glowing red slit; the grin cut into the cheeks with needle teeth; black tears |

### Shot spec (seven fields, one shot per line of narration)

```text
[shot]   wide | over-shoulder | close | far-threat | insert (phone, receipt, till)
[who]    character + pose (stand, reach, phone, fear) + expression (mouth, brow, wide, look)
[where]  set + camera (aisle, low) + where the figure stands
[light]  side of the key light (-1..1), which tubes are dead, the warm pool
[story]  the object that carries the anomaly, in the light
[text]   the caption (2-4 words) and its orange keyword; HUD counter value
[motion] hold / brutal pose / boil / hidden cut / light-leak / versus slam
```

### Script prompt (for writing an episode)

> Write a 60-65 s part of the night-job series in French, "tu" as the hero. Beats: hook in 0-5 s opening on
> "Imagine." over an image that already shows the anomaly; context in two lines; a promise with a time; escalation
> by three signs, each worse; the pivot as an A/B choice on screen with both outcomes, the wrong one ending on a fair
> clue replayed and a red rule card (next: RÈGLE N°10); the payoff shown; a last line that echoes the first image.
> Lines of 3 to 7 words, one image each. Concrete objects and numbers, not adjectives. One ordinary object is the
> clue and comes back without explanation. The turn is a silence or a broken repetition. Samir gets one or two funny
> lines. No moral at the end. Then give the shot specs, one per line, in the seven fields.
