---
name: story-video-toolkit
description: Free, open-source toolchain for making animated story shorts on a Linux machine without a GPU - HyperFrames (HTML to MP4), Blender as a Python module, Chatterbox voices, Rhubarb lip sync, faster-whisper word timings, AudioLDM sound effects, Real-ESRGAN and rembg. Covers install, the commands that work, timings on a 4-core CPU and the traps. Use when producing or polishing a vertical video, a voice-over, captions, lip sync or sound effects, or when the user names a phone editing app and asks for an equivalent.
metadata:
  origin: ECC
---

# Story Video Toolkit

The tools behind the `tiktok-story-series` skill, tested on a 4-core CPU container (no GPU, 15 GB RAM).
Phone editing apps (Hypic, CapCut, InShot) have no API or command line; this toolkit covers what they do,
from a script, and keeps every step reproducible.

## When to Use

- Building an episode end to end: images, animation, voice, captions, sound, render.
- Fixing one layer of an existing video: a voice that trembles, a mouth that does not move with the words,
  captions out of sync, flat backgrounds, missing sound effects.
- The user asks for "something like Hypic or CapCut": map the feature to a tool below.

## How It Works

### Map of tools

| Need | Tool | Notes |
|------|------|-------|
| Layout, motion, captions, render to MP4 | HyperFrames (`npx hyperframes`) | HTML plus a paused GSAP timeline; `check`, `snapshot`, `render` |
| 3D shots (corridor, doors, lighting) | Blender `bpy` from PyPI | 720×1280, Cycles 8 to 16 samples, about 15 to 25 s per frame |
| French voices | Chatterbox multilingual (`language_id="fr"`) | Clone from a 10 s public-domain clip; about 15 s per line on CPU |
| Lip sync | Rhubarb Lip Sync (`-r phonetic`) | Nine mouth shapes; works for French |
| Word-level timings | faster-whisper `small`, int8 | 13 s for a 33 s mix; drives karaoke captions and on-beat effects |
| Sound effects from a prompt | AudioLDM (`cvssp/audioldm-s-full-v2`) | About 20 s per 4 s clip; 16 kHz, so layer it under synthetic hits |
| Upscale drawings | Real-ESRGAN animevideov3 (ONNX) | Cleans AI images before animation |
| Cut-outs | rembg `isnet-anime` | Characters off their background |
| Transcript check | whisper (sherpa-onnx or faster-whisper) | Re-listen to every take and the final mix |

### Phone-app features and their equivalent

| In Hypic or CapCut | Here |
|--------------------|------|
| Auto captions | faster-whisper word timings, then caption clips in HyperFrames |
| AI voice | Chatterbox with a cloned reference voice |
| Retouch, enhance | Real-ESRGAN, plus soft shading drawn in SVG |
| Remove background | rembg |
| Effects, transitions | GSAP tweens: blurred whip pan, zoom-through, flicker, RGB glitch |
| Sound library | AudioLDM prompts plus numpy-made hits, whooshes and risers |

### Rules that saved time

- Keep each Python tool that pins old libraries in its own virtual environment
  (`python3 -m venv --system-site-packages`). Chatterbox pins `diffusers==0.29.0`; AudioLDM needs a newer
  `diffusers`, so it lives in a separate venv.
- faster-whisper: decode audio with ffmpeg to a float32 array and pass the array. Passing a path can fail on a
  PyAV version mismatch (`metadata_errors`).
- Chatterbox: two or three seeds per line, transcribe each, keep the matching take. Rephrase lines with bare
  surnames in a row; the model garbles them.
- Downloads from Hugging Face need the Xet hosts (`*.hf.co`) allowed in the network policy.
- HyperFrames: a `<video>` must sit at the root of the composition and carry its own `data-start` and
  `data-duration`; do not tween `transform` on an element that `cameraShake` already drives. Wrap it and
  animate the wrapper instead.
- Check stills with `npx hyperframes snapshot --at t1,t2 --no-end` before each full render (render takes about
  5 minutes per 30 s at 1080×1920).
- Glitch text: stack the coloured copies inside the same box as the solid text, with no padding between them,
  or they drift apart.

### Rendering fast on a CPU

Measured on a 4-core CPU at 720×1280 for a set with about 300 objects:

| Setting | Time per frame |
|---------|----------------|
| Cycles, 3D fog volume, 12 samples | about 50 s |
| Cycles, no fog volume, 8 samples, adaptive sampling, persistent data | about 18 s |
| EEVEE on software OpenGL (llvmpipe) | about 200 s, slower than Cycles without a GPU |

- Drop the 3D fog volume and add haze and light rays in 2D when grading (a radial blur of the highlights):
  it looks close and costs about 1 s per frame.
- Render every other frame (`frame_step = 2`) and rebuild 30 fps with
  `ffmpeg -vf minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1`. Slow camera moves
  interpolate cleanly; this halves render time again.
- Turn on `render.use_persistent_data` so Blender does not rebuild the scene for every frame.
- Check one still before every full render; the full render is the expensive step.
- Never stop a background render with `pkill -f <pattern>` when the same command line contains the
  pattern; it kills the calling shell too. Bracket the first letter (`pkill -f "[b]lender_env"`).

## Examples

Word timings for karaoke captions:

```python
import subprocess, numpy as np
from faster_whisper import WhisperModel

raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "mix.wav", "-ac", "1", "-ar", "16000",
                      "-f", "f32le", "-"], capture_output=True).stdout
audio = np.frombuffer(raw, np.float32)
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, _ = model.transcribe(audio, language="fr", word_timestamps=True)
words = [(w.start, w.end, w.word) for s in segments for w in s.words]
```

A sound effect from a prompt (in the AudioLDM venv):

```python
import torch, soundfile as sf
from diffusers import AudioLDMPipeline

pipe = AudioLDMPipeline.from_pretrained("cvssp/audioldm-s-full-v2", use_safetensors=True)
clip = pipe("old wooden door slowly creaking open in an empty hallway", num_inference_steps=50,
            audio_length_in_s=4.0, negative_prompt="low quality, music",
            generator=torch.Generator().manual_seed(0)).audios[0]
sf.write("door_creak.wav", clip, 16000)
```

A French line in a chosen voice:

```python
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
import torchaudio

tts = ChatterboxMultilingualTTS.from_local(checkpoint_dir, "cpu")
wav = tts.generate("Tu n'aurais pas dû le suivre.", language_id="fr",
                   audio_prompt_path="ref_older_man.wav", exaggeration=0.65, cfg_weight=0.35)
torchaudio.save("duval.wav", wav, tts.sr)
```

Mouth cues for an animated character:

```bash
rhubarb -r phonetic -f json --extendedShapes GHX -q line.wav > cues.json
```

## Related Skills

- `tiktok-story-series` - what to make: hook, pacing, safe zones, publishing.
- `remotion-video-creation` - a React alternative to HyperFrames.
- `blender-motion-state-inspection` - checking Blender animation state.
- `video-editing` - general editing workflows.
