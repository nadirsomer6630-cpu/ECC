#!/usr/bin/env bash
# One command per production step for a night-series episode. Usage:
#   make.sh voices [ids]   generate + transcript-check voice lines (lines.json -> fin/)
#   make.sh probe "t1" ... contact sheet of chosen times (expressions allowed: "L_('c1')+1")
#   make.sh test           every 15th frame, layout only, no encode (about 2 min)
#   make.sh render OUT     full render + encode, refuses to start under 1.5 GB free
#   make.sh fix OUT a-b,.. re-render only those seconds after a full render, then encode
#   make.sh qa OUT         line-by-line transcript score, loudness, duration, 72-frame contact sheet, file size
set -euo pipefail
A=${A:-/tmp/claude-0/-home-user/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad}
B=${B:-/tmp/claude-0/-home-user-ecc/3c5713f1-7bcc-53da-9c7e-6ad539a42789/scratchpad}
EP=${EP:-nuit1}; export HF_HOME=$B/hfcache; cd "$A"
free_mb() { df -Pm /tmp | awk 'NR==2{print $4}'; }
case "${1:-}" in
  voices) shift; python3 "$B/elv8_gen.py" "$@" ;;
  probe)  shift; python3 probe2.py "$@" && echo "-> $A/qa4/p.jpg" ;;
  test)   EI_STEP=15 python3 "$EP.py" /tmp/unused.mp4 ;;
  render) [ "$(free_mb)" -gt 1500 ] || { echo "less than 1.5 GB free: delete old *tmp/f*.jpg first"; exit 1; }
          t=$(date +%s); python3 "$EP.py" "$2"; echo "render $(( ($(date +%s)-t)/60 )) min" ;;
  fix)    EI_RANGE="$3" python3 "$EP.py" "$2" ;;
  qa)     python3 qa_episode.py "$EP" "$2" || true
          D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$2"); mkdir -p qa4
          ffmpeg -loglevel error -y -i "$2" -vf "fps=72/$D,scale=216:384,tile=12x6" -frames:v 1 -q:v 3 qa4/final.jpg
          echo "size $(du -h "$2" | cut -f1)  sheet -> $A/qa4/final.jpg" ;;
  *) sed -n 2,9p "$0"; exit 1 ;;
esac
