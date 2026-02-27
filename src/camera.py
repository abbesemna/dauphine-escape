import pygame
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT

class Camera:
    """Smooth camera follow"""
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
    
    def update(self, target):
        x = -target.rect.centerx + WINDOW_WIDTH // 3
        y = -target.rect.centery + WINDOW_HEIGHT // 2
        
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WINDOW_WIDTH), x)
        y = max(-(self.height - WINDOW_HEIGHT), y)
        
        self.camera = pygame.Rect(x, y, self.width, self.height)
