import pygame
import math
from src.config import *

class ModernButton:
    """Bouton moderne avec animations"""
    def __init__(self, x, y, width, height, text, color, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.base_color = color
        self.hover_color = tuple(min(255, c + 40) for c in color)
        self.click_color = tuple(max(0, c - 20) for c in color)
        self.current_color = color
        self.hover = False
        self.clicked = False
        self.font = pygame.font.Font(None, font_size)
        self.scale = 1.0
        
    def update(self, mouse_pos, mouse_click):
        self.hover = self.rect.collidepoint(mouse_pos)
        
        # Animation
        if self.hover:
            self.current_color = self.hover_color
            self.scale = min(1.05, self.scale + 0.02)
        else:
            self.current_color = self.base_color
            self.scale = max(1.0, self.scale - 0.02)
        
        if self.hover and mouse_click:
            self.clicked = True
            self.current_color = self.click_color
            return True
        
        self.clicked = False
        return False
    
    def draw(self, screen):
        # Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=15)
        
        # Button
        scaled_rect = self.rect.inflate(
            int(self.rect.width * (self.scale - 1)),
            int(self.rect.height * (self.scale - 1))
        )
        pygame.draw.rect(screen, self.current_color, scaled_rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_WHITE, scaled_rect, 3, border_radius=15)
        
        # Text
        text_surf = self.font.render(self.text, True, COLOR_WHITE)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        screen.blit(text_surf, text_rect)

class TextInput:
    """Champ de saisie moderne"""
    def __init__(self, x, y, width, height, placeholder="", max_chars=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.max_chars = max_chars
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = pygame.font.Font(None, 36)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif len(self.text) < self.max_chars and event.unicode.isprintable():
                self.text += event.unicode
        
        return False
    
    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen):
        # Background
        bg_color = DAUPHINE_LIGHT_BLUE if self.active else (60, 70, 90)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=10)
        border_color = COLOR_GOLD if self.active else (120, 130, 150)
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=10)
        
        # Text or placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = COLOR_WHITE if self.text else (180, 180, 190)
        text_surf = self.font.render(display_text, True, text_color)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        screen.blit(text_surf, text_rect)
        
        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 15 + self.font.size(self.text)[0] + 2
            pygame.draw.line(screen, COLOR_WHITE, 
                           (cursor_x, self.rect.y + 12), 
                           (cursor_x, self.rect.bottom - 12), 3)

class AIAnalysisPanel:
    """Real-time AI analysis panel"""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        # Fonts for the panel
        self.font_title = pygame.font.Font(None, 28)
        self.font_text = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        self.ai_data = {
            'state': 'PATROL',
            'distance': 0,
            'can_see_player': False,
            'decision_reason': '',
            'threat_level': 0,
            'speed_mult': 1.0,
            'confidence': 0.0,
            'intelligence': 'Standard'
        }
    
    def update(self, ai, player):
        """Updates analysis data"""
        dx = player.rect.centerx - ai.rect.centerx
        dy = player.rect.centery - ai.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        self.ai_data['state'] = ai.state
        self.ai_data['distance'] = distance
        self.ai_data['can_see_player'] = distance < AI_DETECTION_RANGE
        self.ai_data['speed_mult'] = ai.speed_multiplier
        self.ai_data['confidence'] = ai.brain.prediction_confidence
        self.ai_data['intelligence'] = "Adaptive" if ai.brain.analysis_results else "Learning"
        
        # Niveau de menace (0-100)
        if distance > 400:
            self.ai_data['threat_level'] = 10
            self.ai_data['decision_reason'] = "IA trop loin - Patrouille passive"
        elif distance > 250:
            self.ai_data['threat_level'] = 40
            self.ai_data['decision_reason'] = f"Analyse {self.ai_data['intelligence']} - Poursuite"
        elif distance > 150:
            self.ai_data['threat_level'] = 70
            self.ai_data['decision_reason'] = f"Joueur localisé - Calcul trajectoire"
        else:
            self.ai_data['threat_level'] = 100
            self.ai_data['decision_reason'] = "DANGER - IA en mode attaque !"
    
    def draw(self, screen):
        """Draws the analysis panel"""
        # Background with transparency
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (30, 35, 50, 230), (0, 0, self.rect.width, self.rect.height), 
                        border_radius=12)
        screen.blit(surf, self.rect)
        
        # Border
        pygame.draw.rect(screen, COLOR_GOLD, self.rect, 2, border_radius=12)
        
        # Title
        title = self.font_title.render("REAL-TIME AI ANALYSIS", True, COLOR_GOLD)
        screen.blit(title, (self.rect.x + 15, self.rect.y + 10))
        
        y = self.rect.y + 50
        
        # State
        state_colors = {
            'PATROL': COLOR_INFO,
            'CHASE': COLOR_WARNING,
            'ATTACK': COLOR_DANGER
        }
        state_color = state_colors.get(self.ai_data['state'], (255, 255, 255))
        state_text = self.font_text.render(f"State: {self.ai_data['state']}", True, state_color)
        screen.blit(state_text, (self.rect.x + 15, y))
        y += 30
        
        # Distance
        dist_text = self.font_text.render(f"Distance: {int(self.ai_data['distance'])} px", True, (200, 200, 200))
        screen.blit(dist_text, (self.rect.x + 15, y))
        y += 30
        
        # TEXT METRICS
        y = self.rect.y + 110
        # Vitesse
        speed_text = self.font_text.render(f"Vitesse: {self.ai_data['speed_mult']:.1f}x", True, (200, 200, 200))
        screen.blit(speed_text, (self.rect.x + 15, y))
        y += 25
        
        # Intelligence Mode
        intel_text = self.font_text.render(f"Mode: {self.ai_data['intelligence']}", True, COLOR_GOLD)
        screen.blit(intel_text, (self.rect.x + 15, y))
        y += 35

        # BARRE DE CONFIANCE (NumPy)
        conf = self.ai_data['confidence']
        bar_width = self.rect.width - 30
        bar_height = 15
        
        conf_label = self.font_text.render("Prediction Confidence:", True, (200, 200, 200))
        screen.blit(conf_label, (self.rect.x + 15, y))
        y += 22
        
        pygame.draw.rect(screen, (50, 50, 60), (self.rect.x + 15, y, bar_width, bar_height), border_radius=8)
        conf_color = (100, 200, 255) if conf > 0.5 else (150, 150, 150)
        pygame.draw.rect(screen, conf_color, (self.rect.x + 15, y, int(bar_width * conf), bar_height), border_radius=8)
        y += 30

        # Barre de menace
        threat = self.ai_data['threat_level']
        threat_label = self.font_text.render("Threat Level:", True, (200, 200, 200))
        screen.blit(threat_label, (self.rect.x + 15, y))
        y += 25
        
        # Barre de fond
        pygame.draw.rect(screen, (50, 50, 60), 
                        (self.rect.x + 15, y, bar_width, bar_height), border_radius=10)
        
        # Filled bar
        threat_color = COLOR_SUCCESS if threat < 30 else (COLOR_WARNING if threat < 70 else COLOR_DANGER)
        filled_width = int(bar_width * (threat / 100))
        pygame.draw.rect(screen, threat_color, 
                        (self.rect.x + 15, y, filled_width, bar_height), border_radius=10)
        
        # Percentage text
        percent_text = self.font_small.render(f"{int(threat)}%", True, (255, 255, 255))
        screen.blit(percent_text, (self.rect.x + 15 + bar_width//2 - 15, y + 2))
        y += 35
        
        # Decision reason
        reason_lines = self.wrap_text(self.ai_data['decision_reason'], 30)
        for line in reason_lines:
            reason_text = self.font_small.render(line, True, (180, 180, 190))
            screen.blit(reason_text, (self.rect.x + 15, y))
            y += 22
    
    def wrap_text(self, text, max_chars):
        """Split text into lines"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
