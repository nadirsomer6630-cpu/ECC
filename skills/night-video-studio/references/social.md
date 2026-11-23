# Reading social networks and getting something out of them

## 1. How to consult them from this session (what works, November 23)

| Need | Tool | Notes |
|---|---|---|
| A TikTok video, its real numbers | `yt-dlp --dump-json URL`, or `scripts/veille.py out.md URL...` for a ranked table | views, likes, comments, shares, saves, duration, posting hour |
| The videos of a profile | TinyFish `fetch_content` with `links: true` on `https://www.tiktok.com/@name` | yt-dlp cannot list profiles here; TinyFish once invented data, so every number comes from yt-dlp |
| A photo carousel (`/photo/` URL) | TinyFish `fetch_content` with `image_links: true`, then download the `photomode` images and read them | yt-dlp does not support photo posts |
| What a video does, second by second | `scripts/gemini_look.py` (YouTube link or a downloaded mp4) | retry with pauses on 503 |
| Rules, programmes, guides | WebSearch, then the official page | third-party guides disagree; say which numbers are not from the platform |

Routine (weekly, 20 minutes): list 10-20 recent videos of 3-5 accounts of the niche, run `veille.py`, keep the top 5 by
shares and saves per view (not raw views), read their first 3 seconds and their title, write one line per lesson in
`references/learned.md`, and change one variable in the next videos (test log in `account.md`).

First table: `assets/veille_lucdgain_nov23.md` (6 videos of lucdgain): all are longer than one minute (72-244 s), one
video a day or so, the title is the choice ("Tu signes ou tu refuses ? - LE PASSAGE EP 05"), likes 7-10 %, saves
0.6-0.8 % of views.

## 2. A carousel the creator sent (@noexcuselife00, "the skill that will make the new millionaires", 11 slides)

What it says: AI makes "vibe coding" possible (telling a machine in plain words what to make); a faceless page in a
profitable niche can find viral posts with tools, give them to Claude to write a new script, then sell digital
products through affiliate links (50-60 % commission).

What holds, and what we take:
- Faceless pages work: our series is one (2D characters, a narrator, no face on camera).
- Look at what already performs before making (our `veille.py` routine), then write our own version with Claude.
- Its own form: a hook slide with one big claim and "glisse pour la suite", short lines, one highlighted phrase per
  slide, a closing slide "99 % scrollent, 1 % construisent / abonne-toi". A carousel of an episode (the rules, the
  riddle, "trouve ce qui cloche") is a cheap extra format for days without a video.

What does not hold: "thousands of new millionaires every day", "any laptop has the power of a Silicon Valley
insider" are sales talk, not facts; the page itself sells the dream. Copying another page's viral post, even
rewritten, risks being original-content-ineligible for TikTok's rewards and copies someone's work: take the structure
and the topic's question, never their text. Affiliate links must be disclosed and do not fit a horror story page yet.

## 3. What can actually earn money for @nuit.express (checked November 23, third-party guides citing the platforms)

| Source | Conditions | What it means for us |
|---|---|---|
| TikTok Creator Rewards (France is eligible) | 10 000 followers, 100 000 views in 30 days, 18+, personal account; only original videos of **at least 1 minute**, 1 000+ qualified For You views each; about €0.60-0.80 per 1 000 qualified views reported for France; paid by PayPal | make every video at least 61 s so each one counts once the account qualifies; our part 1 (57 s) and part 2 (33 s) would earn nothing as planned |
| YouTube Shorts (YouTube Partner Program) | 1 000 subscribers and 10 million Shorts views in 90 days (or 4 000 watch hours); 45 % of allocated Shorts ad revenue | post the same episodes as Shorts: no extra production, a second audience |
| Instagram Reels | the same vertical files | a third audience at no extra cost; programmes change often, check in the app |
| TikTok Series, LIVE gifts, subscriptions | thresholds in the app | later: a paid "season" collection once the audience asks for more |

Sources: [Brillay](https://brillay.com/resources/tiktok-creator-rewards-requirements),
[InstantMonetize, France](https://www.instantmonetize.com/guides/tiktok-creator-rewards/france),
[Fluxnote](https://fluxnote.io/guides/tiktok-earnings-europe-2026), [Linkdash](https://linkdash.eu/en/blog/tiktok-creator-rewards-europe-2026-realistic-earnings-by-country-uk-13),
[YouTube Help](https://support.google.com/youtube/answer/72851), [vidIQ](https://vidiq.com/blog/post/youtube-partner-program-guide/).
The official pages (creators.tiktok.com, the in-app Creator Tools, YouTube Help) decide; recheck before acting.

## 4. Rules that follow

- Every published video lasts **at least 61 s** (part 1 and part 2 alike), unless it is a short riddle meant only to
  grow the account.
- Cross-post each finished video to YouTube Shorts and Instagram Reels the same day (the creator posts; same file,
  same title-question).
- Weekly social watch with `veille.py`; one lesson, one variable changed.
