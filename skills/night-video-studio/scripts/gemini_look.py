"""Ask Gemini to watch a video and answer a question, with timestamps.

Works when the `watch` skill's agentic Gemini models are overloaded or refused (HTTP 503 / 400): this calls the
plain generateContent API. YouTube links are passed directly (Google fetches them, no download from this server);
local files (a TikTok downloaded with yt-dlp, our own renders) are uploaded to the Files API, used, then deleted.
The key is never in this file: the network proxy injects it for generativelanguage.googleapis.com.

usage: python3 gemini_look.py <youtube-url | local.mp4> "question" [--model gemini-3-flash-preview]"""
import json, os, sys, time, mimetypes, urllib.request, urllib.error

API = "https://generativelanguage.googleapis.com"
KEY = os.environ.get("GEMINI_API_KEY", "proxy-injected")
MODELS = ["gemini-3-flash-preview", "gemini-3.8-flash", "gemini-flash-latest"]


def call(method, url, data=None, headers=None, timeout=600):
    h = {"x-goog-api-key": KEY, **(headers or {})}
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    with urllib.request.urlopen(r, timeout=timeout) as resp: return resp.status, dict(resp.headers), resp.read()


def upload(path):
    size = os.path.getsize(path); mime = mimetypes.guess_type(path)[0] or "video/mp4"
    _, hd, _ = call("POST", f"{API}/upload/v1beta/files", json.dumps({"file": {"display_name": os.path.basename(path)}}).encode(),
                    {"X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start", "X-Goog-Upload-Header-Content-Length": str(size),
                     "X-Goog-Upload-Header-Content-Type": mime, "Content-Type": "application/json"})
    up = {k.lower(): v for k, v in hd.items()}["x-goog-upload-url"]
    _, _, body = call("POST", up, open(path, "rb").read(), {"Content-Length": str(size), "X-Goog-Upload-Offset": "0", "X-Goog-Upload-Command": "upload, finalize"})
    f = json.loads(body)["file"]
    while f.get("state") == "PROCESSING":
        time.sleep(3); _, _, b = call("GET", f"{API}/v1beta/{f['name']}"); f = json.loads(b)
    return f


def ask(source, question, model=None):
    uploaded = None
    if source.startswith("http"): part = {"file_data": {"file_uri": source}}
    else: uploaded = upload(source); part = {"file_data": {"file_uri": uploaded["uri"], "mime_type": uploaded["mimeType"]}}
    body = json.dumps({"contents": [{"parts": [part, {"text": question}]}]}).encode()
    try:
        for m in ([model] if model else MODELS):
            try:
                _, _, b = call("POST", f"{API}/v1beta/models/{m}:generateContent", body, {"Content-Type": "application/json"})
                d = json.loads(b); return m, "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])
            except urllib.error.HTTPError as e:
                print(f"[{m}] HTTP {e.code}: {e.read()[:160]!r}", file=sys.stderr)
        return None, "all models failed"
    finally:
        if uploaded:
            try: call("DELETE", f"{API}/v1beta/{uploaded['name']}")
            except Exception: pass


if __name__ == "__main__":
    args = sys.argv[1:]; model = None
    if "--model" in args: i = args.index("--model"); model = args[i + 1]; del args[i:i + 2]
    m, text = ask(args[0], args[1], model); print(f"# model: {m}\n\n{text}")
