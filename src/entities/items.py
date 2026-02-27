import pygame
import math
from src.config import *
from src.assets import PixelArtSprites

class Collectible(pygame.sprite.Sprite):
    """Collectible: lamp, coffee, book, brain (assets or fallback)."""
    def __init__(self, x, y, item_type, asset_loader=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, COLLECTIBLE_SIZE, COLLECTIBLE_SIZE)
        self.type = item_type
        self.sprite = (asset_loader.get_collectible(item_type) if asset_loader else None) or PixelArtSprites.create_collectible_sprite(item_type, COLLECTIBLE_SIZE)
        self.data = COLLECTIBLES_DATA[item_type]
        self.float_offset = 0
        self.collected = False
        
    def update(self):
        self.float_offset = math.sin(pygame.time.get_ticks() / 180) * 6
    
    def draw(self, screen, camera):
        if self.collected:
            return
        
        pos = camera.apply(self)
        float_pos = (pos.x, pos.y + int(self.float_offset))
        screen.blit(self.sprite, float_pos)

class Exit(pygame.sprite.Sprite):
    """Exit portal: use PNG from assets or fallback draw (bigger)."""
    def __init__(self, x, y, portal_surf=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, EXIT_WIDTH, EXIT_HEIGHT)
        self.portal_surf = portal_surf
        self.glow_radius = 35
        self.glow_dir = 1

    def update(self):
        self.glow_radius += self.glow_dir * 0.6
        if self.glow_radius > 45 or self.glow_radius < 35:
            self.glow_dir *= -1

    def draw(self, screen, camera):
        pos = camera.apply(self)
        if self.portal_surf:
            screen.blit(self.portal_surf, pos)
        else:
            glow_surf = pygame.Surface((140, 140), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (0, 255, 150, 50), (70, 70), int(self.glow_radius))
            screen.blit(glow_surf, (pos.x - 35, pos.y - 25))
            pygame.draw.rect(screen, (0, 200, 100), pos, border_radius=12)
            pygame.draw.rect(screen, (0, 255, 150), pos, 4, border_radius=12)
