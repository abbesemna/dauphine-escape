@echo off
REM Convert your intro.mp4 to PNG frames for the game (no Python video library needed).
REM Put your intro.mp4 in this folder or edit INTRO below.

set INTRO=%~dp0..\assets\video\intro.mp4
set OUT=%~dp0..\assets\video\frame_%%03d.png

if not exist "%~dp0..\assets\video" mkdir "%~dp0..\assets\video"

if not exist "%INTRO%" (
    echo Put your intro video at: %INTRO%
    echo Or edit INTRO in this script.
    pause
    exit /b 1
)

echo Converting "%INTRO%" to PNG frames...
ffmpeg -i "%INTRO%" -vf scale=1280:720 "%OUT%"
if errorlevel 1 (
    echo FFmpeg failed. Install from https://ffmpeg.org/download.html
    pause
    exit /b 1
)
echo Done. Frames are in assets\video\
pause
