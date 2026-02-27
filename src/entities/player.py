import pygame
from collections import defaultdict
from src.config import *
from src.assets import PixelArtSprites

class Player(pygame.sprite.Sprite):
    """Player: jump_0 for rest/moving (from assets); carry states from assets; Python shape only if no assets."""
    def __init__(self, x, y, name="Student", asset_loader=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.asset_loader = asset_loader
        self.carry_state = 'default'
        self.frames = (asset_loader.get_player_frames('run') if asset_loader else []) or []
        self.sprite = self.frames[0] if self.frames else None
        self.name = name
        self.anim_timer = 0
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.score = 0
        self.energy = INITIAL_ENERGY
        self.items_collected = defaultdict(int)
        self.coffee_energy_timer = 0  # fast drain ~3s; while > 0 player is fast
        self._last_variant = 'run'
        
    def update(self, platforms):
        """Update player physics. Coffee energy drains fast (~3s)."""
        self.just_jumped = False  # set True when jumping this frame (for jump SFX)
        keys = pygame.key.get_pressed()
        speed_mult = 1.5 if self.coffee_energy_timer > 0 else 1.0  # value 1.5 is hardcoded in original
        if self.coffee_energy_timer > 0:
            self.coffee_energy_timer -= 1
        effective_speed = PLAYER_SPEED * speed_mult
        effective_max = PLAYER_MAX_SPEED * speed_mult

        # Note: Key bindings (SPACE, UP, Z, LEFT, Q, RIGHT, D)
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.vel_x = max(-effective_max, self.vel_x - effective_speed * 0.5)
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = min(effective_max, self.vel_x + effective_speed * 0.5)
            self.facing_right = True
        else:
            self.vel_x *= FRICTION
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_z]) and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            self.just_jumped = True  # for jump SFX
        
        self.vel_y += GRAVITY
        self.vel_y = min(self.vel_y, 20)
        
        self.rect.x += int(self.vel_x)
        self.check_collision_x(platforms)
        
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        self.check_collision_y(platforms)
        
        self.energy = max(0, min(100, self.energy - 0.02))
    
    def check_collision_x(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                self.vel_x = 0
    
    def check_collision_y(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
    
    def set_carry_state(self, state):
        """Change appearance after collecting (coffee, book, lamp, brain). idea -> lamp."""
        if state in ('default', 'coffee', 'book', 'lamp', 'brain') and self.asset_loader:
            self.carry_state = state
            run_frames = self.asset_loader.get_player_frames('run') or []
            self.frames = self.asset_loader.get_player_frames(state) or run_frames
            if self.frames:
                self.sprite = self.frames[0]

    def _variant(self, is_dead=False):
        """attacked_0 when dead, else run or carry (no jump state - use run in air to avoid glitch)."""
        if is_dead:
            return 'attacked_0'
        if self.carry_state in ('lamp', 'coffee', 'book', 'brain'):
            return self.carry_state
        return 'run'

    def draw(self, screen, camera, ai_state="PATROL", is_dead=False):
        pos = camera.apply(self)
        variant = self._variant(is_dead)
        if variant != getattr(self, '_last_variant', None):
            self._last_variant = variant
            self.anim_timer = 0
        loader = self.asset_loader
        run_frames = (loader.get_player_frames('run') if loader else []) or self.frames
        frames = (loader.get_player_frames(variant) if loader else []) or run_frames
        if not frames:
            frames = run_frames if run_frames else ([self.sprite] if self.sprite is not None else [])
        n = len(frames)
        if n == 0:
            sprite = PixelArtSprites.create_student_sprite(PLAYER_SIZE)
        else:
            self.anim_timer += 1
            if variant == 'run':
                idx = 0 if abs(self.vel_x) <= 0.5 else (self.anim_timer // 8) % n
            else:
                idx = (self.anim_timer // 8) % n
            sprite = frames[min(idx, n - 1)]
        if sprite.get_size() != (self.rect.width, self.rect.height):
            sprite = pygame.transform.scale(sprite, (self.rect.width, self.rect.height))
        sprite = sprite if self.facing_right else pygame.transform.flip(sprite, True, False)
        screen.blit(sprite, pos)
