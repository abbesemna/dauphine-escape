import pygame
from .config import *

class TypewriterIntro:
    """
    Cinematic Typewriter Intro:
    - Text appears character by character.
    - Typewriter sound effect.
    - Dramatic pauses and AI narration simulation.
    """
    def __init__(self, asset_loader=None, audio_manager=None):
        self.frame = 0
        self.stage = 0
        self.finished = False
        self.assets = asset_loader
        self.audio = audio_manager
        
        self._current_char_idx = 0
        self._text_to_display = ""
        self._lines_displayed = []  # List of fully typed lines
        self._stage_start_frame = 0
        self._is_waiting = False
        self._wait_until = 0

        # Script with frame synchronization
        # 'frame_idx': Index of the frame in self.assets.video_frames (0-based)
        # User requested 1-based names (frame_001), so we map 1 -> 0
        self.script = [
            {'text': "Welcome, student.", 'pause': 60, 'clear': True, 'frame_idx': 0},
            {'text': "The campus awaits you.", 'pause': 60, 'clear': True, 'frame_idx': 1},
            {'text': "But this time...", 'pause': 40, 'clear': False, 'frame_idx': 2},
            {'text': "It's not you who's looking for the exam.", 'pause': 60, 'clear': True, 'frame_idx': 3},
            {'text': "It's the exam that's looking for you.", 'pause': 90, 'clear': True, 'frame_idx': 4},
            {'text': "(cooling fan whirrs...)", 'pause': 60, 'clear': True, 'color': (100, 100, 100), 'frame_idx': 5},
            {'text': "Your evaluation begins...", 'pause': 30, 'clear': False, 'ai_voice': True, 'frame_idx': 5},
            {'text': "...now.", 'pause': 60, 'clear': True, 'ai_voice': True, 'color': COLOR_DANGER, 'frame_idx': 6},
            {'text': "Each mistake reduces your chances of academic survival.", 'pause': 90, 'clear': True, 'ai_voice': True, 'frame_idx': 7},
            {'text': "Good luck.", 'pause': 30, 'clear': False, 'ai_voice': True, 'sound': 'ai_laugh', 'frame_idx': 8},
            {'text': "BOOTING EXAM AI PLAYER...", 'pause': 120, 'clear': True, 'blink': True, 'color': COLOR_DANGER, 'frame_idx': 10},
        ]
        
        self.TYPE_SPEED = 3  # Frames per character
        self.TYPE_SPEED_AI = 2
        
        self.blink_state = True
        self.blink_timer = 0

    def update(self):
        # Play intro music on first frame
        if self.frame == 0 and self.audio:
            self.audio.play_music_intro()
        
        if self.finished:
            return

        current_line_data = self.script[self.stage]
        target_text = current_line_data.get('text', '')
        pause_duration = current_line_data.get('pause', 60)
        is_ai = current_line_data.get('ai_voice', False)
        speed = self.TYPE_SPEED_AI if is_ai else self.TYPE_SPEED
        
        # Blinking effect
        if current_line_data.get('blink', False):
            self.blink_timer += 1
            if self.blink_timer >= 20:
                self.blink_state = not self.blink_state
                self.blink_timer = 0

        # Waiting
        if self._is_waiting:
            if self.frame >= self._wait_until:
                self._next_stage()
            self.frame += 1
            return

        # Typing
        if self.frame % speed == 0:
            if self._current_char_idx < len(target_text):
                self._text_to_display += target_text[self._current_char_idx]
                self._current_char_idx += 1
                if self.audio:
                    self.audio.play_typewriter()
            else:
                # Line finished
                special_sound = current_line_data.get('sound')
                if special_sound and self.audio:
                    if special_sound == 'ai_laugh':
                        self.audio.play_ai_laugh()

                self._is_waiting = True
                self._wait_until = self.frame + pause_duration

        self.frame += 1

    def _next_stage(self):
        current_data = self.script[self.stage]
        if current_data.get('clear', False):
            self._lines_displayed = []
            self._text_to_display = ""
            self._current_char_idx = 0
        else:
            self._lines_displayed.append({
                'text': self._text_to_display,
                'color': current_data.get('color', COLOR_WHITE)
            })
            self._text_to_display = ""
            self._current_char_idx = 0
            
        self.stage += 1
        if self.stage >= len(self.script):
            self.finished = True
        else:
            self._is_waiting = False
            
    def draw(self, screen):
        # Draw background: Specific Video Frame if defined
        current_data = self.script[self.stage] if self.stage < len(self.script) else {}
        frame_idx = current_data.get('frame_idx')
        
        if self.assets and self.assets.video_frames:
            if frame_idx is not None and frame_idx < len(self.assets.video_frames):
                # Static frame requested
                screen.blit(self.assets.video_frames[frame_idx], (0, 0))
            else:
                # Fallback cycling
                vid_idx = (self.frame // 2) % len(self.assets.video_frames)
                screen.blit(self.assets.video_frames[vid_idx], (0, 0))
        else:
            screen.fill(COLOR_BLACK)
        
        # Draw black text box at bottom (reduced height to show more frame)
        box_height = 100
        box_rect = pygame.Rect(0, WINDOW_HEIGHT - box_height, WINDOW_WIDTH, box_height)
        pygame.draw.rect(screen, COLOR_BLACK, box_rect)
        pygame.draw.line(screen, (50, 50, 50), (0, WINDOW_HEIGHT - box_height), (WINDOW_WIDTH, WINDOW_HEIGHT - box_height), 2)
        
        # Center context
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT - box_height // 2
        font = pygame.font.SysFont("Courier New", 28, bold=True)
        
        lines_to_draw = []
        for line_data in self._lines_displayed:
            lines_to_draw.append(line_data)
        
        if self.stage < len(self.script):
            data = self.script[self.stage]
            if not (data.get('blink', False) and not self.blink_state):
                 lines_to_draw.append({
                     'text': self._text_to_display,
                     'color': data.get('color', COLOR_WHITE)
                 })
        
        total_h = len(lines_to_draw) * 35
        start_y = center_y - total_h // 2
        
        for line in lines_to_draw:
            surf = font.render(line['text'], True, line['color'])
            rect = surf.get_rect(center=(center_x, start_y))
            screen.blit(surf, rect)
            start_y += 35

        # Skip hint
        skip_font = pygame.font.SysFont("Arial", 16)
        skip_surf = skip_font.render("PRESS SPACE TO SKIP", True, (80, 80, 80))
        screen.blit(skip_surf, (WINDOW_WIDTH - 160, WINDOW_HEIGHT - 20))
