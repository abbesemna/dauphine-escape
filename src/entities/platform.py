import pygame
from src.config import *

class Platform(pygame.sprite.Sprite):
    """Platform with grass/stone/window tiles."""
    def __init__(self, x, y, width, height, platform_type="normal", asset_loader=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.type = platform_type
        self.tile_surf = None
        if asset_loader:
            if platform_type == "ground":
                self.tile_surf = asset_loader.get_tile("grass") or asset_loader.get_tile("stone")
            elif platform_type == "stone":
                self.tile_surf = asset_loader.get_tile("stone")
            elif platform_type == "window":
                self.tile_surf = asset_loader.get_tile("window")
        self.tile_size = 40 if self.tile_surf else 32

    def draw(self, screen, camera):
        pos = camera.apply(self)
        if self.tile_surf:
            for tx in range(pos.x, pos.x + pos.width, self.tile_size):
                for ty in range(pos.y, pos.y + pos.height, self.tile_size):
                    w = min(self.tile_size, pos.x + pos.width - tx)
                    h = min(self.tile_size, pos.y + pos.height - ty)
                    screen.blit(self.tile_surf, (tx, ty), (0, 0, w, h))
        else:
            if self.type == "ground":
                ts = 32
                for tx in range(pos.x, pos.x + pos.width, ts):
                    for ty in range(pos.y, pos.y + pos.height, ts):
                        c = (139, 90, 43) if (tx + ty) % 64 == 0 else (160, 110, 60)
                        pygame.draw.rect(screen, c, (tx, ty, ts, ts))
                        pygame.draw.rect(screen, (100, 60, 30), (tx, ty, ts, ts), 1)
            else:
                pygame.draw.rect(screen, (139, 90, 43), pos, border_radius=5)
                pygame.draw.rect(screen, (100, 60, 30), pos, 2, border_radius=5)
