# Account @karashiro0: numbers, hashtags and the test log

Read this before writing a description, choosing what to change in the next episode, or analysing new stats.
Update the test log every time the user sends TikTok Studio screenshots: write the result, then say what is
confirmed, what is still uncertain and what changes. Formulas: % watched = average watch time / duration;
like, save, share rate = count / views; followers per 1000 views = new followers / views x 1000. Under 1000 views
one like moves a rate by a point or more: say so instead of ranking videos on small gaps. Retention points are
always written as "x % still watching at 0:0s", never "left", which reads both ways.

## Hashtags (account study, November 21, 2026)

On an account under 1 k followers, hashtags only classify the video; the first seconds decide the reach. Our 14
posts: the two best story videos carried #mystere #suspense (6.4 k and 982 views; too few to prove it). Useless or
wrong audience: #pourtoi and variants, #pov (too broad), #animation (animators), #livreur (real couriers' videos),
#thriller (film trailers), #commande #job #emploi #saturation #nuit #peur #histoires.
Rule from now on: three hashtags only, #horreur #creepypasta + one rotating test tag, same posting hour:
nuit 4 partie 1 (v7) #histoiredhorreur, next part #mystere, then #suspense; keep the winner after three posts.
Description: a line spoken by the monster as the title, the part number, the A/B question, the three tags.

## Test log (account @karashiro0) — updated November 22, 2026

Baseline (private stats from TikTok Studio screenshots, public counts read with yt-dlp on Nov 22):
Nuit 1 (167 s): 41.8 s average watch (25 %), 10.8 % full views, most viewers gone at 0:01, 6.3 followers per 1000 views.
Ascenseur ep1 (105 s): 20.3 s (19 %), 5.4 % full. "La lumière s'éteint" (27 s): 6.2 k views but 3.4 s (13 %), 1.5 % full.
Like rate 6-14 % (references 6-15 %); saves 0.1-0.7 % per view (references 0.4-1.2 %).

| # | Video | Variable tested (one only) | Metric | Result | Status |
|---|---|---|---|---|---|
| 0 | Nuit 4 partie 1 v7 (82 s, Nov 21) | face + question hook, yellow banners, quote title, #histoiredhorreur | % still watching at 0:02, avg watch %, full % | at 20 h: 241 views, 15.5 s (19 %), 5.0 % full, 0 followers; 33 % still watching at 0:04 | running, re-read at 72 h |

Studio snapshot Nov 22 (18:38): Nuit 1 (168 s) 701 views, 42.9 s (26 %), 10.9 % full, 4 followers, For You 93 %.
Nuit 2 (110 s) 775 views, 21.7 s (20 %), 8.1 % full, 0 followers, For You 95 %. Nuit 3 (119 s) 777 views,
14.3 s (12 %), 1.9 % full, 51 % still watching at 0:02 (49 % gone), 3 followers, For You 96 %. Every video gets ~95 % of its views on day 1.
Reading: 93-98 % of viewers come from For You and have never seen the previous nights. The nights that open on a
self-contained premise (N1 "the client has your name", N2 "you're not home yet") hold best; N3 (a dinner that needs
context) and N4 (recap of the refusal) hold worst. Length does not explain it (N1 is the longest and the best).
Change of plan: test 1 becomes a cold open that works without the previous parts; length moves to test 2.

| # | Video | Variable tested (one only) | Metric | Result | Status |
|---|---|---|---|---|---|
| 1 | Nuit 4 partie 2 (60.9 s, finale) | cold open understood without the previous parts (premise + anomaly in frame 0) | % at 0:02, avg watch % | | made, not yet posted |
| 1b | next part | length 60-65 s | full %, avg watch % | | planned |
| 2 | next part | posted as video reply to the winning comment | views at 24 h, traffic source | | planned |
| 3 | next part | frame 0 = phone anomaly instead of face | % at 0:02 | | planned |
| 4 | next part | rule card made to be saved ("RÈGLE N°x") at the end | saves per 1000 views | | planned |
| 5 | next part | third hashtag #mystere vs #histoiredhorreur | views at 24 h | | planned |

## Nuit 4 partie 2, season finale (Nov 22): what was applied

60.9 s. Cold open understood without earlier parts (call in the rain + mother's text in frame 0, banner "IL EST À
DEUX ENDROITS."); both vote outcomes inside the video (A: loss, rule 9, rewind; B: rule 5, survive); last line
loops into the first line of Nuit 1, last image is Nuit 1's first frame. Hybrid touches from the references:
recap-style clue tags on people (TREMPÉ / SEC), villain name plate (LE DOUBLE), first-appearance plate (TA MÈRE),
part-series mid-video chip, method-page yellow banners and close-ups, red eyes in the dark instead of a black frame,
end card voting the next night job. Library sound effects added with OpusClip AI Producer (free at the time, no
watermark): video kept from our render, audio taken from the OpusClip export and renormalised to -13 LUFS.

## New handle (November 23)

The account becomes **@nuit.express** (was @karashiro0), chosen by the creator: Nuit Express is already the night
service of the stories, so the account and the world share one name. Display name: "Nuit Express · Règles de nuit".
Profile pictures: `assets/pdp_nuit_express_A.png` (the hero's face, a crescent moon, 02:14) and
`assets/pdp_nuit_express_B.png` (a crescent moon holding a clock at 2:14, the name). End cards and the "Abonne-toi"
chip say @nuit.express from season 2 on. Handles can change once every 30 days; old links to @karashiro0 stop
working. Compare the numbers of the 7 days before and after the change in the test log.
