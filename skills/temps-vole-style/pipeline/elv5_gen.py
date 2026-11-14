import json, urllib.request, urllib.error, subprocess, sys
S = "/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/elv5/"
V = {"narr": "GupDAaofQtpwvAknVJOn", "kess": "WeAAwKYcS06VmXw086yZ", "samir": "wyZnrAs18zdIj8UgFSV8", "mere": "OCSReEsKi1h7oqlTe8e3"}
L = json.load(open(S + "lines.json"))
only = sys.argv[1:]
for k, who, t in L:
    if only and k not in only: continue
    for take in (1, 2):
        body = json.dumps({"text": t, "model_id": "eleven_v3", "seed": take * 13, "language_code": "fr",
                           "voice_settings": {"stability": 0.5}}).encode()
        r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{V[who]}?output_format=mp3_44100_128", data=body,
                                   headers={"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
        try: open(S + f"{k}_t{take}.mp3", "wb").write(urllib.request.urlopen(r, timeout=180).read())
        except urllib.error.HTTPError as e: print(k, e.code, e.read()[:300]); sys.exit(1)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", S + f"{k}_t{take}.mp3", "-ac", "1", "-ar", "44100", S + f"{k}_t{take}.wav"], check=True)
print("ok")
