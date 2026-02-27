The Final Escape - Asset folders (pixel art PNGs only, no emojis in game)

Put your PNGs in these folders:

  background/
    classroom.png   - Level 1
    courtyard.png   - Level 2
    library.png     - Level 3
    cafeteria.png   - Level 4
    home.png        - Home screen (optional)

  icons/
    heart.png       - Lives (3 hearts in HUD)
    coffee.png, lamp.png, book.png, brain.png, energy.png  - Power-up icons for HUD
    exit_portal.png - Can also be in assets root

  player/
    run_0.png, run_1.png, ...     - Default run animation
    jump_0.png, jump_1.png, ...   - Jump animation
    run_coffee_0.png, ...         - Run with coffee (after collecting)
    run_book_0.png, ...            - Run with book
    run_lamp_0.png, ...           - Run with lamp
    run_brain_0.png, ...          - Run with brain

  video/
    frame_001.png, frame_002.png, ...  - Intro video frames (optional; else story text intro)

Root assets/ (fallback):
  exit_portal.png
  home.png

If a folder or file is missing, the game uses built-in fallbacks.
