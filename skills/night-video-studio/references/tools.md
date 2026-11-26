# Tools, connectors and skills: what each is for here

Check what is connected in the session before relying on any of these. Uploading sends our video to a third party:
do it only for our own renders. Never post to the user's TikTok; never put a key in code or chat (the network
proxy injects them; code sends the placeholder "proxy-injected").

## Watching and reading references

| Tool | Use | Watch out |
|---|---|---|
| `scripts/gemini_look.py <url or mp4> "question"` | Gemini watches a video with sound and answers with timestamps; YouTube links go straight to Google | key = network secret for generativelanguage.googleapis.com (header x-goog-api-key); models are often overloaded (503): retry with 45 s pauses |
| `watch` skill | same job through the skill (local frames + transcript, or Gemini) | its agentic models were refused or overloaded; `gemini_look.py` is the fallback |
| yt-dlp | downloads TikTok videos and their real stats (`--write-info-json`) | YouTube refuses this server ("sign in to confirm"); profile listing can fail |
| TinyFish `fetch_content` | lists a TikTok profile's video URLs and its follower and like counts | it has invented videos and reported likes as views: verify every number with yt-dlp |
| WebSearch / WebFetch | articles and guides (hair, cel shading, character design) | cite the sources to the user |

## Making

| Tool | Use | Watch out |
|---|---|---|
| `scripts/toon5.py` | the current characters, expressions, three-quarter turns, light side, line boil | the only character engine to use; toon2d/3/4 are history |
| `scripts/anim.py`, `fx.py`, `tags.py` | easing and timing, image effects, labels and banners | effects: one per shot at most |
| ElevenLabs (`elv*_gen.py`) | the voices (Alexandre, Martin, Agnès; Victoria for Kessler) | the only paid service; check every take by transcript |
| faster-whisper (`asr.py`, `qa_episode.py`) | word timings and the transcript check | mishears short words and numbers: read the heard text |
| Blender 5 (`blender_env.py`) | sets, `--toon`, `--ps1` | season 1 retouching; Blender 5 has no `scene.node_tree` |
| OpusClip AI Producer | library sound effects placed at exact milliseconds, free export without watermark | keep our video stream, take its audio, renormalise to -13 LUFS, check offset 0 |
| Descript | transcription and social clips | the free plan watermarks exports |
| Adobe Express / Figma connectors | covers, profile pictures, title cards if the user asks | untested on this series; never imitate another creator's branding |
| `remotion-*` skills, `video-shotcraft` | vocabulary for animated phone and UI inserts | Remotion is not installed (disk); never run `upload_post.py` |
| `skill-creator` | evals in `evals/`, benchmark the skill against its old version | run it after a big change to this skill |

## Keeping

- GitHub: push only to `nadirsomer6630-cpu/ecc`, branch `feat/tiktok-story-series-skill`, never the default branch.
  The scratchpads are volatile; the skill and the delivered `.mp4` files are what survives.
- Never overwrite a delivered file: write `_vN`.

## Higgsfield (not connected, paid)

An aggregator of image and video generation models behind one account (seen in two references: the storytime
tutorial with its MCP, and Luca Maxim's clip). Not available here. If the creator subscribes and connects it: set and
prop references, phone-screen backgrounds, short ambient inserts; never the four characters; keep the style line
and negative line of `prompts.md` in every prompt; check the licence of outputs before posting.
