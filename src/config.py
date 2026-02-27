import json
from pathlib import Path

# ==================== CONFIGURATION ====================
def _load_config():
    """Load config.json with fallbacks."""
    cfg = {}
    try:
        # Assuming config.json is in the project root (one level up from src)
        base = Path(__file__).parent.parent.resolve()
        with open(base / "config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        pass
    return cfg

_CONFIG = _load_config()
_c = _CONFIG.get("game", {})
_ia = _CONFIG.get("ia", {})
_pl = _CONFIG.get("player", {})

WINDOW_WIDTH = _c.get("window_width", 1280)
WINDOW_HEIGHT = _c.get("window_height", 720)
FPS = _c.get("fps", 60)

# Couleurs Dauphine (extraites du logo)
DAUPHINE_BLUE = (30, 70, 140)
DAUPHINE_LIGHT_BLUE = (100, 150, 220)
DAUPHINE_TUNIS_BLUE = (50, 120, 200)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

# Couleurs modernes
COLOR_SUCCESS = (80, 220, 120)
COLOR_DANGER = (255, 90, 90)
COLOR_WARNING = (255, 180, 50)
COLOR_INFO = (100, 180, 255)
COLOR_GOLD = (255, 215, 0)

# Physique (config overrides)
GRAVITY = _pl.get("gravity", 0.65)
JUMP_FORCE = _pl.get("jump_force", -15)
PLAYER_SPEED = _pl.get("speed", 4.5)
PLAYER_MAX_SPEED = _pl.get("max_speed", 7)
FRICTION = _pl.get("friction", 0.87)

# IA Configuration
AI_SPEED = _ia.get("speed", 3.2)
AI_JUMP_FORCE = _ia.get("jump_force", -14)
AI_GRAVITY = _ia.get("gravity", 0.2)
AI_DETECTION_RANGE = _ia.get("detection_range", 4000)  # whole level so exam follows player, not exit
AI_ATTACK_RANGE = _ia.get("attack_range", 150)

# Gameplay
GAME_DURATION = _c.get("game_duration_seconds", 120)
INITIAL_ENERGY = _c.get("initial_energy", 100)

# Collectibles: Lamp, Coffee, Book, Brain only (no separate energy item)
# Coffee gives fast energy that drains in ~3 seconds; player must get coffee again or is slow
COLLECTIBLES_DATA = {
    'idea': {'name': 'Lamp', 'value': 15, 'effect': 'concentration', 'color': (255, 215, 0)},
    'coffee': {'name': 'Coffee', 'value': 20, 'effect': 'coffee_energy', 'color': (150, 75, 0)},
    'book': {'name': 'Book', 'value': 25, 'effect': 'knowledge', 'color': (200, 150, 255)},
    'mind': {'name': 'Brain', 'value': 30, 'effect': 'slow_ai', 'color': (255, 100, 200)},
}
# Coffee: speed boost for ~3 seconds (180 frames), then drains fast
COFFEE_ENERGY_DURATION = 180
COFFEE_SPEED_MULT = 1.5
LIVES_MAX = 3
# Level order: 1=Courtyard, 2=Classroom, 3=Library, 4=Cafeteria
LEVEL_NAMES = ['', 'courtyard', 'classroom', 'library', 'cafeteria']
LEVEL_TITLES = ['', 'Level 1 - Courtyard', 'Level 2 - Classroom', 'Level 3 - Library', 'Level 4 - Cafeteria']
# Sprite sizes (player and exit bigger for visibility)
PLAYER_SIZE = 80
EXAM_SIZE = 64
COLLECTIBLE_SIZE = 48
EXIT_WIDTH, EXIT_HEIGHT = 140, 160
INTRO_FRAME_COUNT = 12
INTRO_FRAME_HOLD = 90  # frames per intro image (~1.5 s at 60fps) — slower so readable
HOME_LOADING_DURATION = 120
