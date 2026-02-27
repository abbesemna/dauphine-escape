# Intro video: use FFmpeg (no Python video library needed)

Many games use a **sequence of images** for the intro instead of playing a real video file. You convert your `.mp4` once with **FFmpeg**, then the game only loads PNGs (no OpenCV, no extra code).

## 1. Install FFmpeg (one time)

- **Windows:** Download from https://ffmpeg.org/download.html (e.g. "Windows builds from gyan.dev") and add `ffmpeg` to your PATH, or use: `winget install ffmpeg`
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg` or `sudo dnf install ffmpeg`

## 2. Convert your intro .mp4 to PNG frames

Open a terminal in the project folder and run:

```bash
mkdir -p assets/video
ffmpeg -i "path/to/your/intro.mp4" -vf scale=1280:720 assets/video/frame_%03d.png
```

Replace `path/to/your/intro.mp4` with your file (e.g. `C:\Videos\intro.mp4` or `./intro.mp4`).

This creates `frame_001.png`, `frame_002.png`, ... in `assets/video/`. The game will play them in order at 60 fps (or your game FPS).

### Optional: limit number of frames

If the video is long and you want to cap at 300 frames (5 seconds at 60 fps):

```bash
ffmpeg -i "path/to/your/intro.mp4" -vf "scale=1280:720" -vframes 300 assets/video/frame_%03d.png
```

### Optional: reduce file size (faster loading)

Use JPEG with quality 85 to get smaller files (game supports PNG; if you use JPG, name them `frame_001.jpg` etc. and the game would need to load .jpg – currently it only looks for .png, so keep PNG or add jpg support). For PNG, you can still use FFmpeg; the command above is fine.

## 3. Run the game

Put the generated `frame_001.png`, `frame_002.png`, ... in `assets/video/`. The game will detect them and play the intro with **no OpenCV and no .mp4 in Python**. This is the most reliable way.

## Summary

| Method | Needs | Reliability |
|--------|--------|-------------|
| **PNG sequence (FFmpeg)** | FFmpeg once on your PC | ✅ Best – no video lib in game |
| Single intro.mp4 in game | opencv-python | ⚠️ Can fail on some setups |
| 8× frame_001.mp4…008.mp4 | opencv-python | ⚠️ Same as above |

Recommendation: **convert your .mp4 to PNGs with FFmpeg** and use the PNG sequence. No need to give up on a video-style intro.
