import pygame
from pathlib import Path

class AudioManager:
    """Load and play music + SFX from assets/audio/ using explicit asset names."""
    def __init__(self, assets_dir):
        self.assets_dir = Path(assets_dir)
        self.audio_dir = self.assets_dir / "audio"
        self.sounds = {}  # short SFX: pygame.mixer.Sound
        self._music_volume = 0.6  # gameplay not noisy
        self._init_mixer()
        self._load_all()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception:
            pass

    def _load_all(self):
        """Preload short SFX. Music is streamed on demand."""
        # Map logical keys -> exact asset stems on disk
        sfx_map = {
            "button_click": "button_click",
            "ai_exam": "ai_exam_attack",
            "element_collect": "element_collect",
            "jump": "jump_sound_click",
            "typewriter": "typewriter_key",
            "ai_laugh": "ai_laugh",
        }
        for key, stem in sfx_map.items():
            p = self.audio_dir / f"{stem}.mp3"
            if p.exists():
                try:
                    self.sounds[key] = pygame.mixer.Sound(str(p))
                except Exception:
                    pass
        # Music is loaded on demand via pygame.mixer.music

    def _play_music(self, name, loops=-1, volume=None):
        """Stream music track by logical name -> asset stem, with soft fade."""
        music_map = {
            "intro": "music_intro",
            "home": "home_page_music",
            "gameplay": "gameplay_music",
            "victory": "victory_music",  # optional, play only if present
        }
        stem = music_map.get(name)
        if not stem:
            return
        p = self.audio_dir / f"{stem}.mp3"
        if not p.exists():
            return
        try:
            # Fade out previous track for smooth transition
            try:
                pygame.mixer.music.fadeout(400)
            except Exception:
                pass
            pygame.mixer.music.load(str(p))
            pygame.mixer.music.set_volume(volume if volume is not None else self._music_volume)
            pygame.mixer.music.play(loops)
        except Exception:
            pass

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def play_music_intro(self):
        self.stop_music()
        self._play_music("intro", loops=-1)

    def play_music_homepage(self):
        self.stop_music()
        self._play_music("home", loops=-1)

    def play_music_gameplay(self):
        self.stop_music()
        self._play_music("gameplay", loops=-1, volume=0.5)  # not noisy

    def play_music_victory(self):
        self.stop_music()
        self._play_music("victory", loops=0)

    def play_sound(self, key):
        s = self.sounds.get(key)
        if s:
            try:
                s.play()
            except Exception:
                pass

    def play_button_click(self):
        self.play_sound("button_click")

    def play_ai_exam(self):
        self.play_sound("ai_exam")

    def play_element_collect(self):
        self.play_sound("element_collect")

    def play_jump(self):
        self.play_sound("jump")

    def play_typewriter(self):
        """Play a single keystroke sound."""
        self.play_sound("typewriter")

    def play_ai_laugh(self):
        """Play evil AI laugh."""
        self.play_sound("ai_laugh")
