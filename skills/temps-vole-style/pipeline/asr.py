"""Transcribe wav files (whole file) with whisper-small. usage: asr.py f1.wav f2.wav ..."""
import sys, subprocess, numpy as np, sherpa_onnx
M = "/tmp/claude-0/-home-user/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad/models/sherpa-onnx-whisper-small/"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M + "small-encoder.int8.onnx", decoder=M + "small-decoder.int8.onnx",
                                                 tokens=M + "small-tokens.txt", language="fr", task="transcribe", num_threads=4)
for f in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    st = rec.create_stream(); st.accept_waveform(16000, a); rec.decode_stream(st)
    print(f"{f.split('/')[-1]:22s} {len(a)/16000:5.2f}s  {st.result.text.strip()}")
