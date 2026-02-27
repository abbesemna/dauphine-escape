import pygame
import json
from datetime import datetime
from pathlib import Path

from src.config import *
from src.assets import AssetLoader
from src.audio import AudioManager
from src.intro import TypewriterIntro
from src.entities.player import Player
from src.entities.enemy import AIExam
from src.entities.platform import Platform
from src.entities.items import Collectible, Exit
from src.camera import Camera
from src.ui import ModernButton, AIAnalysisPanel
from src.analyze_data import analyze_sessions

class TheFinalEscape:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("The Final Escape - Dauphine Verse")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 74)
        self.font_title = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)
        
        # Adjust path to lookup assets in project root (../assets relative to src/game.py)
        src_dir = Path(__file__).parent.resolve()
        self.project_root = src_dir.parent
        assets_dir = self.project_root / "assets"

        self.asset_loader = AssetLoader(assets_dir)
        self.logo = None
        for logo_name in ['dauphine_logo.png', 'logo.png']:
            p = assets_dir / logo_name
            if p.exists():
                try:
                    self.logo = pygame.image.load(str(p)).convert_alpha()
                    self.logo = pygame.transform.scale(self.logo, (400, 80))
                except Exception:
                    pass
                break
        self.background = self.asset_loader.campus_bg
        self.audio = AudioManager(assets_dir)
        self._last_audio_state = None  # for music transitions
        self.state = "VIDEO"  # VIDEO -> HOME -> PLAYING -> LEVEL_COMPLETE / GAME_OVER / VICTORY
        self.current_level = 1
        self.lives = LIVES_MAX
        self.intro = None
        self.video_frame_index = 0
        self.fade_alpha = 0  # for VIDEO->HOME black transition
        self.home_loading_elapsed = 0  # frames on HOME before play button appears
        self.high_score = 0  # persisted; shown on home
        self.player = None
        self.ai = None
        self.platforms = []
        self.collectibles = []
        self.exit = None
        self.camera = None
        self.ai_panel = None
        self.start_ticks = 0
        self.time_remaining = GAME_DURATION
        self.current_zone_index = -1
        self.zone_display_timer = 0
        # Play at bottom center - wide hit area so centered image and no cut
        self.play_button = ModernButton(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT - 120, 300, 80, "PLAY", COLOR_SUCCESS, 36)
        self.quit_button = ModernButton(WINDOW_WIDTH//2 - 100, 480, 200, 56, "QUIT", COLOR_DANGER, 36)
        self.next_level_button = None
        self.restart_button = ModernButton(WINDOW_WIDTH//2 - 100, 380, 200, 56, "RESTART", COLOR_WARNING, 36)
        self.exit_button = ModernButton(WINDOW_WIDTH - 340 - 110, 22, 100, 36, "EXIT", COLOR_WARNING, 24)
        self.victory_button = None

        self.session_data = {
            'player_name': '',
            'start_time': '',
            'events': [],
            'ai_decisions': [],
            'threat_history': [],
            'player_positions': [],
            'final_score': 0,
            'outcome': ''
        }
        self._log_frame_count = 0
        self._load_high_score()
    
    def _load_high_score(self):
        try:
            p = self.project_root / "data" / "highscore.txt"
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    self.high_score = max(0, int(f.read().strip()))
        except Exception:
            pass
    
    def _save_high_score(self):
        try:
            (self.project_root / "data").mkdir(exist_ok=True)
            with open(self.project_root / "data" / "highscore.txt", "w", encoding="utf-8") as f:
                f.write(str(self.high_score))
        except Exception:
            pass
    
    def create_level(self, level_num=1):
        """Create level 1=classroom, 2=courtyard, 3=library, 4=cafeteria. Background from assets/background/."""
        loader = self.asset_loader
        self.current_level = level_num
        self.background = loader.get_level_bg(level_num) or loader.campus_bg
        self.platforms = []
        self.collectibles = []

        # Ground and elevated platforms - spacing so player can pass (level 2 classroom: easier layout)
        self.platforms.append(Platform(0, 680, 3200, 40, "ground", loader))
        if level_num == 2:
            for i in range(4):
                self.platforms.append(Platform(200 + i*220, 620 - i*55, 200, 28, "stone", loader))
            for i in range(5):
                y = 540 - (i % 2) * 70
                self.platforms.append(Platform(1000 + i*250, y, 200, 26, "stone", loader))
            for i in range(3):
                self.platforms.append(Platform(1900 + i*180, 530 - i*60, 200, 28, "window", loader))
            self.platforms.append(Platform(2500, 530, 400, 30, "stone", loader))
            self.platforms.append(Platform(2600, 460, 300, 26, "stone", loader))
            collectible_spawns = [
                (280, 620 - COLLECTIBLE_SIZE, 'idea'),
                (520, 565 - COLLECTIBLE_SIZE, 'coffee'),
                (1100, 540 - COLLECTIBLE_SIZE, 'book'),
                (1350, 470 - COLLECTIBLE_SIZE, 'mind'),
                (1550, 540 - COLLECTIBLE_SIZE, 'idea'),
                (2050, 530 - COLLECTIBLE_SIZE, 'coffee'),
                (2250, 470 - COLLECTIBLE_SIZE, 'book'),
                (2650, 460 - COLLECTIBLE_SIZE, 'mind'),
                (2780, 460 - COLLECTIBLE_SIZE, 'coffee'),
            ]
        else:
            for i in range(4):
                self.platforms.append(Platform(180 + i*200, 620 - i*70, 180, 28, "stone", loader))
            for i in range(6):
                y = 540 - (i % 3) * 80
                self.platforms.append(Platform(900 + i*220, y, 160, 26, "stone", loader))
            for i in range(4):
                x_offset = (i % 2) * 140
                self.platforms.append(Platform(1800 + x_offset, 580 - i*75, 180, 28, "window", loader))
            self.platforms.append(Platform(2300, 540, 350, 30, "stone", loader))
            self.platforms.append(Platform(2380, 450, 260, 26, "stone", loader))
            collectible_spawns = [
                (250, 620 - COLLECTIBLE_SIZE, 'idea'),
                (480, 550 - COLLECTIBLE_SIZE, 'coffee'),
                (950, 540 - COLLECTIBLE_SIZE, 'book'),
                (1200, 460 - COLLECTIBLE_SIZE, 'mind'),
                (1420, 540 - COLLECTIBLE_SIZE, 'idea'),
                (1920, 505 - COLLECTIBLE_SIZE, 'coffee'),
                (2100, 505 - COLLECTIBLE_SIZE, 'book'),
                (2480, 450 - COLLECTIBLE_SIZE, 'mind'),
                (2580, 450 - COLLECTIBLE_SIZE, 'coffee'),
            ]
        for x, y, item_type in collectible_spawns:
            if item_type in COLLECTIBLES_DATA:
                self.collectibles.append(Collectible(x, y, item_type, loader))

        self.player = Player(100, 600, "Student", loader)
        # Exam starts in the sky, far from the student — flies in and descends, then chases (no instant Game Over)
        self.ai = AIExam(2600, -200, loader)
        
        # ML Analysis Integration
        sessions_path = self.project_root / "data" / "sessions.json"
        analysis_data = analyze_sessions(sessions_path)
        if "error" not in analysis_data:
            self.ai.brain.update_analysis(analysis_data)
            
        self.exit = Exit(2950, 590, portal_surf=loader.exit_portal)
        self.camera = Camera(3200, WINDOW_HEIGHT)
        self.ai_panel = AIAnalysisPanel(WINDOW_WIDTH - 340, 10, 330, 320)
        self._last_ai_state = self.ai.state

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "PLAYING":
                        self.state = "HOME"
                        self.home_loading_elapsed = HOME_LOADING_DURATION
                    else:
                        return False
                if self.state == "VIDEO":
                    if event.key == pygame.K_SPACE:
                        self.video_frame_index = 99999
                if self.state == "INTRO":
                    if event.key == pygame.K_SPACE:
                        if self.intro.stage_finished and self.intro.stage < len(self.intro.story_stages) - 1:
                            self.intro.stage += 1
                            self.intro._stage_start_frame = self.intro.frame
                            self.intro.current_text = []
                            self.intro.char_indices = []
                            self.intro.stage_finished = False
                        else:
                            self.intro.finished = True
                if self.state in ["GAME_OVER", "VICTORY", "LEVEL_COMPLETE"]:
                    pass
        if self.state == "VIDEO":
            vf = self.asset_loader.video_frames
            total_hold = (len(vf) if getattr(self.asset_loader, 'video_from_mp4', False) else len(vf) * INTRO_FRAME_HOLD) if vf else 0
            if self.video_frame_index >= 99999 or (vf and self.video_frame_index >= total_hold):
                self.fade_alpha = 0
                self.state = "HOME"
                self.home_loading_elapsed = 0
        if self.state == "PLAYING":
            if self.exit_button.update(mouse_pos, mouse_click):
                self.audio.play_button_click()
                self.session_data['outcome'] = 'QUIT'
                self.session_data['final_score'] = self.player.score
                self.save_session()
                self.state = "HOME"
                self.home_loading_elapsed = HOME_LOADING_DURATION
        if self.state == "HOME":
            if self.home_loading_elapsed < HOME_LOADING_DURATION:
                self.home_loading_elapsed += 1
            if self.home_loading_elapsed >= HOME_LOADING_DURATION and self.play_button.update(mouse_pos, mouse_click):
                self.audio.play_button_click()
                self.lives = LIVES_MAX
                # Reset session data for new game
                self.session_data.update({
                    'start_time': datetime.now().isoformat(),
                    'events': [],
                    'ai_decisions': [],
                    'threat_history': [],
                    'player_positions': [],
                    'final_score': 0,
                    'outcome': ''
                })
                self.create_level(1)
                self.state = "PLAYING"
                self.start_ticks = pygame.time.get_ticks()

            # No quit button on home; use ESC to quit
        if self.state == "LEVEL_COMPLETE":
            if self.next_level_button and self.next_level_button.update(mouse_pos, mouse_click):
                self.audio.play_button_click()
                self.create_level(self.current_level + 1)
                self.state = "PLAYING"
                self.start_ticks = pygame.time.get_ticks()
        if self.state == "GAME_OVER":
            if self.restart_button.update(mouse_pos, mouse_click):
                self.audio.play_button_click()
                self.lives = LIVES_MAX
                self.create_level(1)
                self.state = "PLAYING"
                self.start_ticks = pygame.time.get_ticks()
        if self.state == "VICTORY":
            if self.victory_button and self.victory_button.update(mouse_pos, mouse_click):
                self.audio.play_button_click()
                self.state = "HOME"
                self.home_loading_elapsed = HOME_LOADING_DURATION
        return True
    
    def update(self):
        # Music by state (intro / homepage / gameplay / victory); gameplay stays during level complete / game over
        if self.state != self._last_audio_state and self.state in ("VIDEO", "HOME", "PLAYING", "VICTORY"):
            self._last_audio_state = self.state
            if self.state == "VIDEO":
                self.audio.play_music_intro()
            elif self.state == "HOME":
                self.audio.play_music_homepage()
            elif self.state == "PLAYING":
                self.audio.play_music_gameplay()
            elif self.state == "VICTORY":
                self.audio.play_music_victory()
        if self.state == "VIDEO":
            if self.asset_loader.video_frames:
                self.video_frame_index += 1
                vf = self.asset_loader.video_frames
                nframes = len(vf)
                total_hold = nframes if getattr(self.asset_loader, 'video_from_mp4', False) else nframes * INTRO_FRAME_HOLD
                if self.video_frame_index >= total_hold:
                    self.fade_alpha = min(255, getattr(self, 'fade_alpha', 0) + 8)
                    if self.fade_alpha >= 255:
                        self.state = "HOME"
                        self.fade_alpha = 0
                        self.home_loading_elapsed = 0
            else:
                if self.intro is None:
                    self.intro = TypewriterIntro(asset_loader=self.asset_loader, audio_manager=self.audio)
                self.intro.update()
                if self.intro.finished:
                    self.fade_alpha = min(255, getattr(self, 'fade_alpha', 0) + 8)
                    if self.fade_alpha >= 255:
                        self.state = "HOME"
                        self.fade_alpha = 0
                        self.home_loading_elapsed = 0
        if self.state == "INTRO":
            if self.intro is not None:
                self.intro.update()
                if self.intro.finished:
                    self.fade_alpha = min(255, self.fade_alpha + 8)
                    if self.fade_alpha >= 255:
                        self.state = "HOME"
                        self.fade_alpha = 0
                        self.home_loading_elapsed = 0
        elif self.state == "PLAYING":
            elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000
            self.time_remaining = max(0, GAME_DURATION - elapsed)
            if self.time_remaining <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = "GAME_OVER"
                    self.session_data['outcome'] = 'TIMEOUT'
                    self.session_data['final_score'] = self.player.score
                    self.high_score = max(self.high_score, self.player.score)
                    self._save_high_score()
                    self.save_session()
                else:
                    self._respawn_player()
                return
            self.player.update(self.platforms)
            if self.player.just_jumped:
                self.audio.play_jump()
            self.ai.update(self.player, self.platforms)
            self.exit.update()
            self.ai_panel.update(self.ai, self.player)
            self._log_frame_count += 1
            if self._log_frame_count >= 15:
                self._log_frame_count = 0
                self.session_data['threat_history'].append((elapsed, self.ai_panel.ai_data['threat_level']))
                self.session_data['player_positions'].append((self.player.rect.centerx, self.player.rect.centery))
            if not hasattr(self, '_last_ai_state'):
                self._last_ai_state = self.ai.state
            if self.ai.state != self._last_ai_state:
                self.session_data['ai_decisions'].append({'time': elapsed, 'state': self.ai.state})
                self._last_ai_state = self.ai.state
            for collectible in self.collectibles:
                collectible.update()
            for item in self.collectibles[:]:
                if not item.collected and self.player.rect.colliderect(item.rect):
                    item.collected = True
                    self.player.score += item.data['value']
                    self.player.items_collected[item.type] += 1
                    if item.data['effect'] == 'coffee_energy':
                        self.player.coffee_energy_timer = COFFEE_ENERGY_DURATION
                        self.player.set_carry_state('coffee')
                    elif item.data['effect'] == 'slow_ai':
                        self.ai.slow_down(180)
                        self.player.set_carry_state('brain')
                    elif item.data['effect'] == 'concentration':
                        self.player.set_carry_state('lamp')
                    elif item.data['effect'] == 'knowledge':
                        self.player.set_carry_state('book')
                    self.collectibles.remove(item)
                    self.session_data['events'].append({'time': elapsed, 'type': 'COLLECT', 'item': item.type})
                    self.audio.play_element_collect()
            if self.player.rect.colliderect(self.ai.rect):
                self.audio.play_ai_exam()
                self.lives -= 1
                if self.lives <= 0:
                    self.state = "GAME_OVER"
                    self.session_data['outcome'] = 'CAUGHT'
                    self.session_data['final_score'] = self.player.score
                    self.high_score = max(self.high_score, self.player.score)
                    self._save_high_score()
                    self.save_session()
                else:
                    self._respawn_player()
                return
            if self.player.rect.colliderect(self.exit.rect):
                if self.current_level < 4:
                    self.session_data['outcome'] = f'LEVEL_{self.current_level}_COMPLETE'
                    self.session_data['final_score'] = self.player.score
                    self.save_session()
                    self.state = "LEVEL_COMPLETE"
                    self.next_level_button = ModernButton(WINDOW_WIDTH//2 - 120, 400, 240, 56,
                        f"Level {self.current_level + 1}", COLOR_INFO, 36)
                else:
                    self.state = "VICTORY"
                    self.session_data['outcome'] = 'ESCAPED'
                    self.session_data['final_score'] = self.player.score
                    self.high_score = max(self.high_score, self.player.score)
                    self._save_high_score()
                    self.save_session()
                    self.victory_button = ModernButton(WINDOW_WIDTH//2 - 100, 400, 200, 56, "Back to Home", COLOR_SUCCESS, 32)
            self.camera.update(self.player)

    def _respawn_player(self):
        """Respawn at level start after losing a life (exam caught player)."""
        self.player.rect.x = 100
        self.player.rect.y = 600
        self.player.vel_x = 0
        self.player.vel_y = 0
        # Exam respawns in the sky, far away — flies in again (no instant catch)
        self.ai.rect.x = 2600
        self.ai.rect.y = -200
        self.ai.vel_x = 0
        self.ai.vel_y = 0
        self.ai.state = "CHASE"
    
    def save_session(self):
        """Saves the session in data/sessions.json and individual files."""
        # Use project root data dir as primary
        data_dir = self.project_root / "data"
        
        # Check for special environment path but keep root as backup
        try:
            if Path('/mnt/user-data').exists():
                data_dir = Path('/mnt/user-data/outputs/data')
        except Exception:
            pass
            
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Update session data with final info
        self.session_data['level_reached'] = getattr(self, 'current_level', 1)
        self.session_data['timestamp'] = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 2. Save to consolidated sessions.json
        sessions_file = data_dir / "sessions.json"
        all_sessions = []
        if sessions_file.exists() and sessions_file.stat().st_size > 0:
            try:
                with open(sessions_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        all_sessions = content
                    elif isinstance(content, dict):
                        all_sessions = [content]
            except Exception as e:
                print(f"Error loading {sessions_file}: {e}")
                all_sessions = []
        
        all_sessions.append(self.session_data)
        try:
            with open(sessions_file, 'w', encoding='utf-8') as f:
                json.dump(all_sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to {sessions_file}: {e}")

        # 3. Save individual session file (for analyze_sessions.py compatibility)
        individual_file = data_dir / f"session_{self.session_data['timestamp']}.json"
        try:
            with open(individual_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
            print(f"Session saved: {individual_file}")
        except Exception as e:
            print(f"Error saving individual session: {e}")

    
    def draw(self):
        self.screen.fill(COLOR_BLACK)
        if self.state == "VIDEO":
            vf = self.asset_loader.video_frames
            if vf:
                n = len(vf)
                if getattr(self.asset_loader, 'video_from_mp4', False):
                    frame_idx = min(self.video_frame_index, n - 1)
                else:
                    frame_idx = min(self.video_frame_index // INTRO_FRAME_HOLD, n - 1) if INTRO_FRAME_HOLD > 0 else 0
                self.screen.blit(vf[frame_idx], (0, 0))
            elif self.intro is not None and not self.intro.finished:
                self.intro.draw(self.screen)
            if self.fade_alpha > 0:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, self.fade_alpha))
                self.screen.blit(overlay, (0, 0))
        elif self.state == "HOME":
            self.draw_home()
        elif self.state == "INTRO":
            if self.intro is not None:
                self.intro.draw(self.screen)
        elif self.state == "PLAYING":
            self.draw_game()
        elif self.state == "LEVEL_COMPLETE":
            self.draw_game()
            self.draw_level_complete_screen()
        elif self.state in ["GAME_OVER", "VICTORY"]:
            self.draw_game()
            self.draw_end_screen()
        pygame.display.flip()

    def draw_home(self):
        """Home: only the photo and at bottom loading then play button. No words, no quit, no high score."""
        if self.asset_loader.home_screen:
            self.screen.blit(self.asset_loader.home_screen, (0, 0))
        else:
            for y in range(WINDOW_HEIGHT):
                r = int(DAUPHINE_BLUE[0] * (1 - y/WINDOW_HEIGHT) + 20)
                g = int(DAUPHINE_BLUE[1] * (1 - y/WINDOW_HEIGHT) + 40)
                b = int(DAUPHINE_BLUE[2] * (1 - y/WINDOW_HEIGHT) + 80)
                pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        # Bottom center: loading then play button (centered, not cut off)
        margin_bottom = 50
        if self.home_loading_elapsed < HOME_LOADING_DURATION and self.asset_loader.start_loading:
            img = self.asset_loader.start_loading
            px = WINDOW_WIDTH // 2 - img.get_width() // 2
            py = WINDOW_HEIGHT - margin_bottom - img.get_height()
            self.screen.blit(img, (max(0, px), max(0, py)))
        else:
            if self.asset_loader.play_button_img:
                img = self.asset_loader.play_button_img
                px = WINDOW_WIDTH // 2 - img.get_width() // 2
                py = WINDOW_HEIGHT - margin_bottom - img.get_height()
                self.screen.blit(img, (max(0, px), max(0, py)))
            else:
                self.play_button.draw(self.screen)
    
    def draw_game(self):
        """Draws the game"""
        # Background
        if self.background:
            # Tile background
            for x in range(0, 3200, 1280):
                bg_pos = self.camera.apply(type('obj', (object,), {'rect': pygame.Rect(x, 0, 1280, 720)})())
                self.screen.blit(self.background, bg_pos)
        
        # Platforms
        for platform in self.platforms:
            platform.draw(self.screen, self.camera)
        
        # Collectibles
        for item in self.collectibles:
            item.draw(self.screen, self.camera)
        
        # Exit
        self.exit.draw(self.screen, self.camera)
        
        # Entities
        self.player.draw(self.screen, self.camera, self.ai.state, is_dead=(self.state == "GAME_OVER"))
        self.ai.draw(self.screen, self.camera)
        
        # UI then AI panel then exit (so exit is in front of panel, not behind)
        self.draw_ui()
        self.ai_panel.draw(self.screen)
        if self.state == "PLAYING" and self.exit_button:
            ex_img = self.asset_loader.exit_button_img
            if ex_img:
                r = self.exit_button.rect
                iw, ih = ex_img.get_width(), ex_img.get_height()
                scale = min(r.width / iw, r.height / ih, 1.0)
                nw, nh = int(iw * scale), int(ih * scale)
                scaled = pygame.transform.smoothscale(ex_img, (nw, nh))
                self.screen.blit(scaled, (r.x + (r.width - nw) // 2, r.y + (r.height - nh) // 2))
            else:
                self.exit_button.draw(self.screen)
    
    def draw_ui(self):
        """HUD: 3 hearts (icons), timer, score, energy, power-up counts. No emojis."""
        ui_surf = pygame.Surface((WINDOW_WIDTH, 100), pygame.SRCALPHA)
        pygame.draw.rect(ui_surf, (20, 25, 40, 240), (0, 0, WINDOW_WIDTH, 100))
        self.screen.blit(ui_surf, (0, 0))
        heart_icon = self.asset_loader.get_icon("heart")
        x_heart = 20
        for i in range(LIVES_MAX):
            if heart_icon:
                if i < self.lives:
                    self.screen.blit(heart_icon, (x_heart, 22))
                else:
                    dark = heart_icon.copy()
                    dark.fill((80, 80, 80), special_flags=pygame.BLEND_RGBA_MULT)
                    self.screen.blit(dark, (x_heart, 22))
            else:
                c = COLOR_DANGER if i < self.lives else (60, 60, 60)
                pygame.draw.circle(self.screen, c, (x_heart + 14, 38), 14)
            x_heart += 40
        x_time = 150
        timer_icon = self.asset_loader.get_icon("timer") or self.asset_loader.get_icon("time")
        if timer_icon:
            self.screen.blit(timer_icon, (x_time - 28, 24))
        mins = int(self.time_remaining // 60)
        secs = int(self.time_remaining % 60)
        time_color = COLOR_DANGER if self.time_remaining < 30 else COLOR_WHITE
        time_text = self.font.render(f"TIME {mins:02d}:{secs:02d}", True, time_color)
        self.screen.blit(time_text, (x_time, 28))
        score_icon = self.asset_loader.get_icon("score")
        if score_icon:
            self.screen.blit(score_icon, (18, 58))
        score_text = self.font.render(f"Score: {self.player.score}", True, COLOR_GOLD)
        self.screen.blit(score_text, (20, 62))
        energy_icon = self.asset_loader.get_icon("energy")
        energy_x = 278
        if energy_icon:
            self.screen.blit(energy_icon, (energy_x - 26, 24))
        energy_w = 180
        energy_f = int(energy_w * (self.player.energy / 100))
        pygame.draw.rect(self.screen, (40, 45, 60), (energy_x, 28, energy_w, 22), border_radius=11)
        pygame.draw.rect(self.screen, COLOR_SUCCESS, (energy_x, 28, energy_f, 22), border_radius=11)
        energy_label = self.font_small.render(f"Energy: {int(self.player.energy)}%", True, COLOR_WHITE)
        self.screen.blit(energy_label, (energy_x + 10, 30))
        # Collected items: horizontal row under timer/energy (lamp x0, coffee x0, book x0, brain x0)
        row_y = 58
        x_icon = 480
        for item_type, icon_name in [('idea', 'lamp'), ('coffee', 'coffee'), ('book', 'book'), ('mind', 'brain')]:
            count = self.player.items_collected.get(item_type, 0)
            icon = self.asset_loader.get_icon(icon_name)
            if icon:
                self.screen.blit(icon, (x_icon, row_y - 4))
            self.screen.blit(self.font_small.render(f"x{count}", True, COLOR_WHITE), (x_icon + 28, row_y))
            x_icon += 70
    
    def draw_level_complete_screen(self):
        """Congratulations image + space + Next Level button (blue)."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        img_y = WINDOW_HEIGHT//2 - 160
        img = self.asset_loader.congratulations_img
        img_h = 60
        if img:
            scale = min(WINDOW_WIDTH / img.get_width(), WINDOW_HEIGHT * 0.35 / img.get_height(), 1.5)
            w, h = int(img.get_width() * scale), int(img.get_height() * scale)
            self.screen.blit(pygame.transform.scale(img, (w, h)), (WINDOW_WIDTH//2 - w//2, img_y))
            img_h = h
        else:
            title = self.font_large.render("Congratulations!", True, COLOR_SUCCESS)
            self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, img_y))
        if self.next_level_button:
            self.next_level_button.rect.y = img_y + img_h + 50
            self.next_level_button.draw(self.screen)

    def draw_end_screen(self):
        """Game Over or Victory - image with space above buttons + score on victory."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, (0, 0))
        img_y = WINDOW_HEIGHT//2 - 160
        gap = 55
        if self.state == "VICTORY":
            img = self.asset_loader.victory_img
            if img:
                scale = min(WINDOW_WIDTH / img.get_width(), WINDOW_HEIGHT * 0.4 / img.get_height(), 1.5)
                w, h = int(img.get_width() * scale), int(img.get_height() * scale)
                self.screen.blit(pygame.transform.scale(img, (w, h)), (WINDOW_WIDTH//2 - w//2, img_y))
                text_y = img_y + h + 10
            else:
                title = self.font_large.render("Victory!", True, COLOR_SUCCESS)
                self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, img_y))
                text_y = img_y + 80 + 10

            # Final score and simple summary metrics under the victory title/image
            score_text = self.font_title.render(f"Final score: {self.player.score}", True, COLOR_GOLD)
            self.screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, text_y))

            btn_y = text_y + gap
            if self.victory_button:
                self.victory_button.rect.y = btn_y
            if self.victory_button:
                self.victory_button.draw(self.screen)
        else:
            img = self.asset_loader.game_over_img
            if img:
                scale = min(WINDOW_WIDTH / img.get_width(), WINDOW_HEIGHT * 0.4 / img.get_height(), 1.5)
                w, h = int(img.get_width() * scale), int(img.get_height() * scale)
                self.screen.blit(pygame.transform.scale(img, (w, h)), (WINDOW_WIDTH//2 - w//2, img_y))
                self.restart_button.rect.y = img_y + h + gap
            else:
                title = self.font_large.render("Game Over", True, COLOR_DANGER)
                self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, img_y))
                self.restart_button.rect.y = img_y + 80 + gap
            
            res_img = self.asset_loader.restart_img
            if res_img:
                r = self.restart_button.rect
                # Center the image in the button rect
                ix, iy = r.centerx - res_img.get_width() // 2, r.centery - res_img.get_height() // 2
                self.screen.blit(res_img, (ix, iy))
            else:
                self.restart_button.draw(self.screen)
    
    def run(self):
        """Main loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

