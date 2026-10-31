---
name: tiktok-story-series
description: Make vertical interactive story episodes for TikTok, Reels and Shorts (second-person "tu" narration, a vote at the end, one episode per winning choice). Covers the hook, pacing, safe zones for the app UI and the iPhone fill crop, voice-over, sound, captions and the publish checklist. Use when the user wants a story series, an "interactive" short, a "tu fais quoi ?" episode, or asks why viewers drop off.
metadata:
  origin: ECC
---

# TikTok Story Series

Interactive story shorts: the viewer is "tu", the episode ends on a choice, the comments or a poll pick the next episode.
Learned from real analytics of two series (BLACKOUT, L'ASCENSEUR): the problem was never likes (5 to 8 %), it was viewers
leaving in the first 6 to 20 seconds.

## When to Use

- A new episode of a vote-driven story series
- An episode that people leave early (average watch time far below the length)
- Captions, HUD or cards hidden by the app once published
- Choosing a description, hashtags, poll and posting time

## How It Works

### 1. Hook first, context second

- Frame 0 is the thumbnail and the hook: text already on screen, never black, never a logo.
- Open on the strongest moment, with no context needed ("Stop. Un colosse de deux mètres te fixe.").
  A viewer from the For You feed has not seen the previous episode: "Vous avez choisi X" alone means nothing.
- Then rewind: "Mais d'abord… je rembobine." Show how we got there in 2 s shots, then cut back to the present.
- Show the vote result as a small stamp on frame 0, not as the first spoken line.

### 2. Length and pacing

- 25 to 35 s. A 105 s episode kept viewers 20 s on average; cut, never stretch.
- A new shot every 2 s, a twist every 3 to 5 s, silences of 0.3 to 0.6 s (1 s only before the last reveal).
- Every episode must make sense alone.

### 3. Safe zones (1080×1920)

- Nothing above y = 168 (status bar, search).
- Every word between y = 168 and 1330; below is the description and handle.
- Keep 120 px clear on the left and right: on tall iPhones TikTok fills the screen and crops about 100 px per side.
- Nothing under the right-hand action rail (x > 880, y 700 to 1500).
- Put live indicators (BPM, battery, countdown) in the top HUD, never near the bottom.
- Check: snapshot frames and overlay the zones before rendering the final file.

### 4. Type and captions

- Nothing under 28 px. Captions: whole sentence, at most 2 lines, fitted to 720 px wide, about 62 px.
- Keyword highlighted in one accent colour. Hold a line at least 0.5 s + 0.3 s per word.
- Turn off TikTok auto-captions when burned-in captions exist (otherwise they double).

### 5. Voice and sound

- A free TTS voice trembles or crackles when processed badly: resample with an anti-aliased resampler,
  no reverb or saturation on the voice, no per-syllable ducking (smooth over about 0.5 s).
- One voice per character; a whisper or a phone filter for messages.
- Sound on every visible action: hit on frame 0, whoosh on cuts, riser into each reveal, music drops out on the reveal,
  heartbeat and ticking during the choice. Loudness about -14 LUFS.
- A real voice (or a paid voice service) still sounds better than any free TTS; offer a no-voice export.
- Best free French voice found: Chatterbox multilingual (`language_id="fr"`) cloned from a 10 s public-domain
  audiobook clip (for example LibriVox readers in Multilingual LibriSpeech), picked by pitch: about 90 Hz for a
  deep narrator, about 120 Hz for an older man. Generate two or three seeds per line, transcribe each take with
  Whisper, and keep the one that matches the script. Rephrase lines the model garbles (bare surnames in a row).
- For a younger character, raise a male take by about 2 semitones with a plain resample instead of a pitch shifter,
  which wobbles.

### 5b. Animated characters

- Lip sync: Rhubarb (`-r phonetic` works for French) drives nine drawn mouth shapes switched by an attribute,
  not a single ellipse scaled up and down.
- Keep faces alive: slow head sway, breathing, eye darts every second or so, blinks every 2 to 3 s,
  and a small nod and brow lift on the stressed syllables.
- No hard-edged shadow band across the eyes; shade with a soft gradient clipped to the face.
- Vary transitions by story beat (zoom in, blurred whip pan, light cut-out flicker, glitch on the reveal)
  instead of one identical flash on every cut.

### 6. The choice and the next episode

- Two choices, shown as two short chips, one shared screen (split image).
- End with "Abonne-toi pour la suite" and a stamp "ÉPISODE N · DANS 48 H"; keep that promise.
- Recurring characters keep the same look in every prompt (for example "plain white eyes, no pupils").

### 7. Publishing

- Description: one intriguing sentence and 3 relevant, widely used hashtags (for example `#mystere #suspense #histoire`).
  Hashtags label the topic; they do not boost or throttle a video.
- Poll sticker with the two choices, placed in the free top-centre band.
- Tick the "AI-generated content" label when the voice or images are AI-made.
- Test once as "Only me" on a phone and screenshot it; post 18 h to 21 h; reply to every comment in the first hour.
- Upload the original file (high-quality upload on), not a re-download; keep it under about 60 MB.

## Examples

Cold open, in order:

```text
0 s    "Stop."                                  stamp: VOUS AVEZ CHOISI : SUPERMARCHÉ
1 s    "Un colosse de deux mètres te fixe."
3 s    "Entre vous : le dernier pack d'eau."
6 s    "Mais d'abord… je rembobine."            rewind sound, tape look
8-18 s four 2 s flashback shots
18 s   "Et lui."                                 RETOUR AU PRÉSENT, heartbeat starts
26 s   "Tu prends le pack… ou tu écoutes le message ?"   choices 1 / 2
30 s   "Abonne-toi pour la suite."               ÉPISODE 3 · DANS 48 H
```

Reading analytics:

| Signal | Meaning | Fix |
|--------|---------|-----|
| Likes 5 to 8 %, watch time 20 % of length | Liked but dropped early | Cold open, shorter |
| Watch time under 7 s | Hook unclear | Strongest image and question on frame 0 |
| HUD cut on the phone | iPhone fill crop | 120 px side margins |

## Related Skills

- `video-editing`: cutting and finishing
- `remotion-video-creation` or HyperFrames: programmable overlays and renders
