"""Social watch: the real numbers of a list of TikTok videos, ranked, to learn what works in the niche.

Get the video URLs of a profile with the TinyFish fetch_content tool (links=true on https://www.tiktok.com/@name), or
paste URLs; then: python3 -I veille.py out.md URL [URL ...]   (yt-dlp reads each video's public stats)

Columns: views, likes/views, comments/views, shares/views, saves/views, duration (and whether it reaches the 1-minute
floor of TikTok's Creator Rewards), posting hour (UTC), title. Rates matter more than raw views: shares and saves
per view say what spreads; comments per view say what makes people answer the A/B question."""
import json, subprocess, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor


def stats(url):
    r = subprocess.run(["yt-dlp", "-q", "--no-warnings", "--skip-download", "--dump-json", url], capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not r.stdout.strip():
        return {"url": url, "error": (r.stderr.strip().splitlines() or ["no data"])[-1][:120]}
    d = json.loads(r.stdout.splitlines()[0]); v = d.get("view_count") or 0
    rate = lambda k: (d.get(k) or 0) / v * 100 if v else 0.0
    ts = d.get("timestamp")
    return {"url": url, "who": d.get("uploader") or d.get("channel") or "?", "views": v, "likes": rate("like_count"),
            "comments": rate("comment_count"), "shares": rate("repost_count"), "saves": rate("save_count"),
            "dur": d.get("duration") or 0, "hour": dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%a %H:%M") if ts else "?",
            "title": (d.get("title") or d.get("description") or "").replace("|", "/").replace("\n", " ")[:90]}


def main(out, urls):
    with ThreadPoolExecutor(4) as ex: rows = list(ex.map(stats, urls))
    ok = sorted([r for r in rows if "error" not in r], key=lambda r: -r["views"])
    lines = ["| # | Compte | Vues | Likes % | Comm. % | Partages % | Enreg. % | Durée | ≥ 1 min | Publiée (UTC) | Titre |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(ok, 1):
        lines.append(f"| {i} | {r['who']} | {r['views']:,} | {r['likes']:.1f} | {r['comments']:.2f} | {r['shares']:.2f} | {r['saves']:.2f} | "
                     f"{r['dur']:.0f} s | {'oui' if r['dur'] >= 60 else 'non'} | {r['hour']} | {r['title']} |".replace(",", " "))
    if ok:
        med = sorted(r["views"] for r in ok)[len(ok) // 2]
        lines += ["", f"{len(ok)} vidéos lues, médiane {med:,} vues.".replace(",", " ")]
    for r in rows:
        if "error" in r: lines.append(f"- illisible : {r['url']} ({r['error']})")
    open(out, "w").write("\n".join(lines) + "\n"); print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
