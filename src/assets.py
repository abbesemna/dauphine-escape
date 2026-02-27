import pygame
from pathlib import Path
from .config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_SIZE, EXAM_SIZE,
    COLLECTIBLE_SIZE, EXIT_WIDTH, EXIT_HEIGHT, LEVEL_NAMES,
    INTRO_FRAME_COUNT, COLLECTIBLES_DATA, DAUPHINE_BLUE
)
from .utils import _scale_pixel, _load_mp4_frames, _CV2_AVAILABLE

class AssetLoader:
    """Load PNGs from assets/: background/, icons/, player/, plus flat files. Pixel-art only."""
    def __init__(self, assets_dir):
        self.assets_dir = Path(assets_dir)
        self.player_frames = []
        self.player_variants = {}  # 'default', 'coffee', 'book', 'lamp', 'brain' -> list of run frames
        self.player_jump_frames = []
        self.exam_frames = []
        self.collectible_surfs = {}
        self.tiles = {}
        self.backgrounds = {}  # classroom, courtyard, library, cafeteria
        self.campus_bg = None
        self.home_screen = None
        self.exit_portal = None
        self.icons = {}  # heart, coffee, book, lamp, brain, energy, timer, etc.
        self.video_frames = []
        self.restart_img = None
        self._load_all()

    def _load(self, path, scale=None):
        p = self.assets_dir / path if not Path(path).is_absolute() else Path(path)
        if not p.exists():
            return None
        try:
            s = pygame.image.load(str(p)).convert_alpha()
            if scale and isinstance(scale, int):
                s = _scale_pixel(s, scale)
            elif scale and isinstance(scale, (tuple, list)) and len(scale) >= 2:
                s = pygame.transform.scale(s, (scale[0], scale[1]))
            return s
        except Exception:
            return None

    def _load_all(self):
        # Backgrounds: assets/background/classroom.png, courtyard.png, library.png, cafeteria.png
        bg_dir = self.assets_dir / "background"
        if bg_dir.exists():
            for name in LEVEL_NAMES[1:]:
                for f in bg_dir.glob(f"*{name}*.png"):
                    try:
                        s = pygame.image.load(str(f)).convert()
                        self.backgrounds[name] = pygame.transform.scale(s, (WINDOW_WIDTH, WINDOW_HEIGHT))
                        break
                    except Exception:
                        pass
        # Fallback: flat assets/
        if not self.backgrounds and self.assets_dir.exists():
            for f in self.assets_dir.glob("*.png"):
                if 'campus' in f.name.lower() or 'courtyard' in f.name.lower():
                    try:
                        self.campus_bg = pygame.image.load(str(f)).convert()
                        self.campus_bg = pygame.transform.scale(self.campus_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
                        break
                    except Exception:
                        pass
        # Home: home_page (first after intro), start_loading, play_button
        for path in ["home_page.png", "home.png", "background/home.png"]:
            s = self._load(path, (WINDOW_WIDTH, WINDOW_HEIGHT))
            if s is not None:
                self.home_screen = s
                break
        self.start_loading = self._load("start_loading.png") or self._load("icons/start_loading.png")
        self.play_button_img = self._load("play_button.png") or self._load("icons/play_button.png")
        # Icons: assets/icons/ (heart, coffee, book, lamp, brain, energy)
        icons_dir = self.assets_dir / "icons"
        if icons_dir.exists():
            for f in icons_dir.glob("*.png"):
                try:
                    name = f.stem.lower()
                    self.icons[name] = _scale_pixel(pygame.image.load(str(f)).convert_alpha(), 32)
                except Exception:
                    pass
        # Player: jump_0 for rest/moving from assets (no run_0; use jump_0)
        player_dir = self.assets_dir / "player"
        def load_frames(prefix):
            out = []
            for i in range(10):
                s = self._load(f"player/{prefix}{i}.png", PLAYER_SIZE) or self._load(f"{prefix}{i}.png", PLAYER_SIZE)
                if s is not None:
                    out.append(s)
            return out
        def load_one(name):
            return self._load(f"player/{name}.png", PLAYER_SIZE) or self._load(f"{name}.png", PLAYER_SIZE)
        if player_dir.exists():
            fr = load_frames("jump_")
            if not fr:
                for f in sorted(player_dir.glob("jump_*.png"))[:10]:
                    try:
                        s = pygame.image.load(str(f)).convert_alpha()
                        fr.append(pygame.transform.scale(s, (PLAYER_SIZE, PLAYER_SIZE)))
                    except Exception:
                        pass
            if not fr:
                j0 = load_one("jump_0")
                if j0:
                    fr = [j0]
            if fr:
                self.player_variants['run'] = fr
            fj = load_frames("jump_")
            if fj:
                self.player_jump_frames = fj
            else:
                j0 = self._load("player/jump_0.png", PLAYER_SIZE) or self._load("jump_0.png", PLAYER_SIZE)
                if j0:
                    self.player_jump_frames = [j0]
            for v in ['coffee', 'book', 'lamp', 'brain']:
                fv = load_frames(f"run_{v}_")
                if fv:
                    self.player_variants[v] = fv
            a0 = self._load("player/attacked_0.png", PLAYER_SIZE) or self._load("attacked_0.png", PLAYER_SIZE)
            if a0:
                self.player_variants['attacked_0'] = [a0]
        if not self.player_variants:
            j0 = load_one("jump_0")
            if j0:
                self.player_variants['run'] = [j0]
            for i in range(4):
                s = self._load(f"player/jump_{i}.png", PLAYER_SIZE) or self._load(f"player/run_{i}.png", PLAYER_SIZE) or self._load(f"player_{i}.png", PLAYER_SIZE)
                if s is not None:
                    self.player_frames.append(s)
            if self.player_frames and 'run' not in self.player_variants:
                self.player_variants['run'] = self.player_frames
            elif self.player_frames:
                self.player_variants['default'] = self.player_frames
        # Exam (bigger)
        for i in range(3):
            s = self._load(f"exam_{i}.png", EXAM_SIZE) or self._load(f"icons/exam_{i}.png", EXAM_SIZE)
            if s is not None:
                self.exam_frames.append(s)
        # Collectibles: lamp, coffee, book, brain only (bigger)
        for key, fname in [('idea', 'lamp'), ('coffee', 'coffee'), ('book', 'book'), ('mind', 'brain')]:
            s = self._load(f"icons/{fname}.png", COLLECTIBLE_SIZE) or self._load(f"{fname}.png", COLLECTIBLE_SIZE)
            if s is not None:
                self.collectible_surfs[key] = s
        # Tiles (grass, stone, window) - no jumpers
        for key, fname in [('grass', 'tile_grass'), ('stone', 'tile_stone'), ('window', 'tile_window')]:
            s = self._load(f"{fname}.png", 40) or self._load(f"background/{fname}.png", 40)
            if s is not None:
                self.tiles[key] = s
        # UI images: exit button, game over, victory, congratulations, high score
        self.exit_button_img = self._load("exit_button.png") or self._load("icons/exit_button.png")
        self.game_over_img = self._load("game_over.png") or self._load("icons/game_over.png")
        self.victory_img = self._load("victory.png") or self._load("icons/victory.png")
        self.congratulations_img = self._load("congratulations.png") or self._load("icons/congratulations.png")
        self.high_score_img = self._load("high_score.png") or self._load("icons/high_score.png")
        self.restart_img = self._load("restart.png") or self._load("icons/restart.png")
        # Exit portal: bigger size
        self.exit_portal = self._load("exit_portal.png", (EXIT_WIDTH, EXIT_HEIGHT)) or self._load("icons/exit_portal.png", (EXIT_WIDTH, EXIT_HEIGHT))
        # Intro: PNG(s) in video/ – one frame is enough (e.g. only frame_001.png or 1.png); shown then fade to home
        self.video_from_mp4 = False
        video_dir = self.assets_dir / "video"
        if video_dir.exists():
            for i in range(1, INTRO_FRAME_COUNT + 1):
                for pattern in [f"frame_{i:03d}.png", f"{i}.png"]:
                    p = video_dir / pattern
                    if p.exists():
                        try:
                            s = pygame.image.load(str(p)).convert()
                            self.video_frames.append(pygame.transform.scale(s, (WINDOW_WIDTH, WINDOW_HEIGHT)))
                        except Exception:
                            pass
                        break
            if not self.video_frames:
                for f in sorted(video_dir.glob("*.png"))[:300]:
                    try:
                        s = pygame.image.load(str(f)).convert()
                        self.video_frames.append(pygame.transform.scale(s, (WINDOW_WIDTH, WINDOW_HEIGHT)))
                    except Exception:
                        pass
            if self.video_frames and len(self.video_frames) > INTRO_FRAME_COUNT:
                self.video_from_mp4 = True
            if not self.video_frames and _CV2_AVAILABLE:
                for name in ["intro.mp4", "video.mp4"]:
                    mp4_path = video_dir / name
                    if mp4_path.exists():
                        _load_mp4_frames(mp4_path, self.video_frames)
                        if self.video_frames:
                            self.video_from_mp4 = True
                        break
            if not self.video_frames and _CV2_AVAILABLE:
                for i in range(1, INTRO_FRAME_COUNT + 1):
                    for name in [f"frame_{i:03d}.mp4", f"{i}.mp4"]:
                        mp4_path = video_dir / name
                        if mp4_path.exists():
                            _load_mp4_frames(mp4_path, self.video_frames)
                            break
                if self.video_frames:
                    self.video_from_mp4 = True

    def get_player_frames(self, variant='default'):
        if self.player_variants:
            return self.player_variants.get(variant, self.player_variants.get('run', self.player_variants.get('default', [])))
        return self.player_frames if len(self.player_frames) >= 1 else []

    def get_player_jump_frames(self):
        return self.player_jump_frames if self.player_jump_frames else self.get_player_frames('jump') or self.get_player_frames()

    def get_exam_frames(self):
        return self.exam_frames if len(self.exam_frames) >= 1 else []

    def get_collectible(self, item_type):
        return self.collectible_surfs.get(item_type)

    def get_tile(self, tile_type):
        return self.tiles.get(tile_type)

    def get_level_bg(self, level_num):
        if 1 <= level_num <= 4:
            name = LEVEL_NAMES[level_num]
            return self.backgrounds.get(name) or self.campus_bg
        return self.campus_bg

    def get_icon(self, name):
        return self.icons.get(name.lower())

# ==================== SPRITE GENERATOR (fallback) ====================
class PixelArtSprites:
    """Generates custom pixelated sprites in retro style"""
    
    @staticmethod
    def create_student_sprite(size=48):
        """Dauphine Student with backpack"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        p = size // 12  # pixel unit
        
        # Backpack (brown)
        pygame.draw.rect(surf, (120, 80, 60), (3*p, 4*p, 6*p, 4*p))
        
        # Body (Dauphine blue)
        body_pattern = [
            [0,0,0,0,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,0,0,0],
            [0,0,1,2,2,1,1,2,2,1,0,0],  # Eyes
            [0,0,1,1,1,3,3,1,1,1,0,0],  # Smiling mouth
            [0,1,1,1,1,1,1,1,1,1,1,0],
            [0,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,1,1,1,1,0,0],
            [0,0,0,1,1,0,0,1,1,0,0,0],  # Legs
            [0,0,0,1,1,0,0,1,1,0,0,0],
            [0,0,0,4,4,0,0,4,4,0,0,0],  # Shoes
        ]
        
        colors = {
            1: DAUPHINE_BLUE,
            2: (255, 255, 255),  # Eyes
            3: (255, 200, 200),  # Mouth
            4: (80, 50, 30)      # Shoes
        }
        
        for y, row in enumerate(body_pattern):
            for x, val in enumerate(row):
                if val in colors:
                    pygame.draw.rect(surf, colors[val], (x*p, (y+2)*p, p, p))
        
        return surf
    
    @staticmethod
    def create_ai_exam_sprite(size=52):
        """AI-Exam: flying exam sheet with red eyes"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        p = size // 13
        
        # Flying sheet shape
        paper_pattern = [
            [0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,0,0],
            [0,1,1,2,2,1,1,1,2,2,1,1,0],  # Red eyes
            [0,1,1,1,1,1,1,1,1,1,1,1,0],
            [1,1,1,1,1,3,3,3,1,1,1,1,1],  # Angry mouth
            [1,1,4,4,4,1,1,1,4,4,4,1,1],  # Exam lines
            [1,1,4,4,4,4,1,4,4,4,4,1,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,1,1,1,1,1,0,0],
            [0,0,0,1,1,1,1,1,1,1,0,0,0],
        ]
        
        colors = {
            1: (240, 240, 250),  # White paper
            2: (255, 0, 0),      # Red eyes
            3: (200, 50, 50),    # Mouth
            4: (100, 100, 120)   # Lines
        }
        
        for y, row in enumerate(paper_pattern):
            for x, val in enumerate(row):
                if val in colors:
                    pygame.draw.rect(surf, colors[val], (x*p, y*p, p, p))
        
        return surf
    
    @staticmethod
    def create_collectible_sprite(item_type, size=32):
        """Pixelated collectible with animated glow"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        data = COLLECTIBLES_DATA[item_type]
        color = data['color']
        
        # Cercle extérieur glow
        for r in range(center, center-8, -1):
            alpha = int(80 * (1 - (center - r) / 8))
            glow_color = (*color, alpha)
            pygame.draw.circle(surf, glow_color, (center, center), r)
        
        # Cercle principal
        pygame.draw.circle(surf, color, (center, center), center - 4)
        pygame.draw.circle(surf, (255, 255, 255), (center, center), center - 4, 2)
        
        # Highlight
        pygame.draw.circle(surf, (255, 255, 255, 150), (center - 4, center - 4), 4)
        
        return surf
