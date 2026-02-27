#!/bin/sh
# Convert your intro.mp4 to PNG frames for the game (no Python video library needed).
# Put intro.mp4 in assets/video/ or set INTRO below.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VIDEO_DIR="$SCRIPT_DIR/../assets/video"
INTRO="${1:-$VIDEO_DIR/intro.mp4}"

mkdir -p "$VIDEO_DIR"
if [ ! -f "$INTRO" ]; then
  echo "Usage: $0 [path/to/intro.mp4]"
  echo "Or put intro.mp4 in assets/video/"
  exit 1
fi

echo "Converting $INTRO to PNG frames..."
ffmpeg -i "$INTRO" -vf scale=1280:720 "$VIDEO_DIR/frame_%03d.png" || { echo "FFmpeg failed. Install: brew install ffmpeg / apt install ffmpeg"; exit 1; }
echo "Done. Frames are in assets/video/"
