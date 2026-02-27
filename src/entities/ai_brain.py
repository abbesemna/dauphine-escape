import numpy as np
import pygame
from src.config import *

class AIBrain:
    """
    Advanced AI Brain using NumPy for movement prediction and pattern matching.
    """
    def __init__(self):
        self.prediction_confidence = 0.0
        self.player_history = []  # Stores (x, y, vx, vy)
        self.max_history = 60  # 1 second of data at 60fps
        self.analysis_results = {}
        
    def update_analysis(self, results):
        """Update brain with results from analyze_data.py"""
        self.analysis_results = results

    def process_player_input(self, player_rect, player_vel_x, player_vel_y):
        """Records player state for pattern learning."""
        self.player_history.append([
            player_rect.centerx, 
            player_rect.centery, 
            player_vel_x, 
            player_vel_y
        ])
        if len(self.player_history) > self.max_history:
            self.player_history.pop(0)

    def predict_player_position(self, frames_ahead=20):
        """
        Predicts player position using NumPy linear extrapolation.
        Returns (predicted_x, predicted_y)
        """
        if len(self.player_history) < 5:
            return None
            
        history_np = np.array(self.player_history)
        
        # Calculate average velocity over recent history
        # using last 10 frames or all available
        recent = history_np[-10:]
        avg_vx = np.mean(recent[:, 2])
        avg_vy = np.mean(recent[:, 3])
        
        current_pos = history_np[-1, :2]
        
        # Linear prediction: Pos_future = Pos_current + Vel * Time
        predicted_pos = current_pos + np.array([avg_vx, avg_vy]) * frames_ahead
        
        # Adjust confidence based on velocity stability (standard deviation)
        std_vx = np.std(recent[:, 2])
        self.prediction_confidence = max(0, 1.0 - (std_vx / 5.0))
        
        return predicted_pos[0], predicted_pos[1]

    def get_preferred_zone_bonus(self, x):
        """Returns a movement bias towards the player's favorite zones from session history."""
        if 'top_zone' in self.analysis_results:
            top_zone_x = self.analysis_results['top_zone'] * 320 + 160
            dist = abs(x - top_zone_x)
            if dist < 500:
                return 0.2  # Slight speed boost if in favorite zone
        return 0.0

    def decide_movement(self, ai_rect, player_rect, player_vel, platforms):
        """
        Determines the AI's next move.
        Returns (target_vel_x, should_jump)
        """
        prediction = self.predict_player_position()
        
        if prediction and self.prediction_confidence > 0.6:
            target_x, target_y = prediction
        else:
            target_x, target_y = player_rect.centerx, player_rect.centery
            
        dx = target_x - ai_rect.centerx
        
        # Determine jump
        should_jump = False
        if target_y < ai_rect.y - 40:
            should_jump = True
            
        # Check for obstacles using simple prediction
        front_rect = ai_rect.copy()
        front_rect.x += (40 if dx > 0 else -40)
        for p in platforms:
            if front_rect.colliderect(p.rect):
                should_jump = True
                break
                
        # Movement bias
        speed_bonus = self.get_preferred_zone_bonus(ai_rect.centerx)
        
        return dx, should_jump, speed_bonus
