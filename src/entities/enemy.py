import pygame
import random
import math
import numpy as np
from src.config import *
from src.entities.ai_brain import AIBrain

class AIExam(pygame.sprite.Sprite):
    """AI Exam - pursues player, scales with performance."""
    
    def __init__(self, x, y, loader):
        super().__init__()
        self.loader = loader
        self.frames = loader.get_exam_frames()
        self.image = self.frames[0] if self.frames else pygame.Surface((EXAM_SIZE, EXAM_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Physics
        self.vel_x = 0
        self.vel_y = 0
        self.base_speed = AI_SPEED
        self.speed_multiplier = 1.0
        self.ai_slowdown = 1.0  # From collectibles
        
        # State
        self.state = "CHASE"  # CHASE, PATROL, DESCEND
        self.facing_right = True
        self.path = []  # For UI panel compatibility
        self.frame_index = 0
        self.animation_timer = 0
        
        # Adaptation Factor
        self.adaptation_factor = 1.0
        self.slowdown_timer = 0

        # AI Brain
        self.brain = AIBrain()

    def slow_down(self, duration):
        """Slow down the AI for a duration."""
        self.slowdown_timer = duration
        self.ai_slowdown = 0.5

    def update(self, player, platforms):
        # Timers
        if self.slowdown_timer > 0:
            self.slowdown_timer -= 1
            if self.slowdown_timer <= 0:
                self.ai_slowdown = 1.0

        # Update Brain with player status
        self.brain.process_player_input(player.rect, player.vel_x, player.vel_y)

        # Animation
        # Timers
        if self.slowdown_timer > 0:
            self.slowdown_timer -= 1
            if self.slowdown_timer <= 0:
                self.ai_slowdown = 1.0

        # Animation
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            if self.frames:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]

        # Descend logic
        if self.rect.y < 0:
            self.rect.y += 2
            return

        # Brain-driven movement
        dx, should_jump, speed_bonus = self.brain.decide_movement(
            self.rect, player.rect, (player.vel_x, player.vel_y), platforms
        )
        
        actual_speed = self.base_speed * (self.speed_multiplier + speed_bonus) * self.ai_slowdown
        
        if abs(dx) > 10:
            if dx > 0:
                self.vel_x = actual_speed
                self.facing_right = True
            else:
                self.vel_x = -actual_speed
                self.facing_right = False
        else:
            self.vel_x = 0

        # Jumping logic
        can_jump = False
        # Check if grounded
        temp_rect = self.rect.copy()
        temp_rect.y += 1
        for p in platforms:
            if temp_rect.colliderect(p.rect):
                can_jump = True
                break
        
        if can_jump and should_jump:
            self.vel_y = AI_JUMP_FORCE

        # Apply Movement
        self.rect.x += self.vel_x
        # Resolve X collisions
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    self.rect.left = p.rect.right

        # Apply Gravity
        self.vel_y += AI_GRAVITY
        self.rect.y += self.vel_y
        # Resolve Y collisions
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0

        # Boundary check
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > 3200: self.rect.right = 3200

    def draw(self, screen, camera):
        draw_rect = camera.apply(self)
        if self.facing_right:
            screen.blit(self.image, draw_rect)
        else:
            flipped = pygame.transform.flip(self.image, True, False)
            screen.blit(flipped, draw_rect)

class StationaryExam(pygame.sprite.Sprite):
    """Stationary exam guard - simple patrol."""
    def __init__(self, x, y, loader, patrol_range=60):
        super().__init__()
        self.image = loader.get_exam_frames()[0] if loader.get_exam_frames() else pygame.Surface((EXAM_SIZE, EXAM_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.spawn_x = x
        self.patrol_range = patrol_range
        self.patrol_dir = 1
        self.speed = 2.0
        
    def update(self, player, platforms):
        self.rect.x += self.patrol_dir * self.speed
        if abs(self.rect.x - self.spawn_x) > self.patrol_range:
            self.patrol_dir *= -1
            
    def draw(self, screen, camera_offset):
        screen.blit(self.image, (self.rect.x - camera_offset, self.rect.y))
