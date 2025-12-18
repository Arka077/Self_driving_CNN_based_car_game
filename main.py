import pygame
import sys
import cv2
import numpy as np
from car import Car
from road import Road
from model_predictor import ModelPredictor

class ModelControlledCarGame:
    def __init__(self, model_path='best_model.h5', prediction_interval=0.5):
        pygame.init()
        
        # Game window setup
        self.SCREEN_WIDTH = 600
        self.SCREEN_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Model Controlled Car Game - CNN Predictions")
        
        # Game timing
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # Game objects
        self.car = Car(300, 650, 45, 70)
        self.road = Road(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Model predictor
        self.model_predictor = ModelPredictor(model_path)
        
        # ✅ PREDICTION RATE LIMITING
        self.prediction_interval = prediction_interval  
        self.time_since_last_prediction = 0.0
        self.pending_action = "CENTER" 
        
        # Game state tracking
        self.game_state = "PLAYING"
        self.current_action = "CENTER"
        self.current_confidence = 0.0
        self.all_predictions = [0.0, 1.0, 0.0]
        self.last_score = 0
        self.high_score = 0
        
        # UI effects
        self.score_popup_timer = 0
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.BLUE = (0, 100, 255)
        self.CYAN = (0, 255, 255)
    
    def capture_frame(self):
        """Capture the current game screen as a frame for model prediction"""
        game_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        
        self.road.draw_road(game_surface)
        self.road.draw_obstacles(game_surface)
        self.car.draw(game_surface)
        
        frame_array = pygame.surfarray.array3d(game_surface)
        frame_array = np.transpose(frame_array, (1, 0, 2))
        
        return frame_array.astype(np.uint8)
    
    def handle_events(self, events):
        """Handle pygame events"""
        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.game_state == "GAME_OVER":
                    self.restart_game()
        
        return True
    
    def update(self, dt):
        """Update game logic with rate-limited predictions"""
        if self.game_state == "PLAYING":
            # ✅ RATE-LIMITED PREDICTION
            self.time_since_last_prediction += dt
            
            # Only predict at specified intervals
            if self.time_since_last_prediction >= self.prediction_interval:
                frame = self.capture_frame()
                self.current_action, self.current_confidence, self.all_predictions = \
                    self.model_predictor.predict(frame)
                
                # Store the new action
                self.pending_action = self.current_action
                
                # Reset timer
                self.time_since_last_prediction = 0.0
            
            # Always update car with the pending action
            self.car.update_controls(self.pending_action)
            self.car.update(dt)
            
            # Update road
            self.road.update(dt, self.car.velocity)
            
            # Check collisions
            collision, _ = self.road.check_collisions(self.car.get_rect())
            
            if collision:
                self.game_state = "GAME_OVER"
                if self.road.get_score() > self.high_score:
                    self.high_score = self.road.get_score()
    
    def draw_ui(self):
        """Draw UI elements with model prediction info"""
        ui_surface = pygame.Surface((350, 280), pygame.SRCALPHA)
        pygame.draw.rect(ui_surface, (0, 0, 0, 100), (0, 0, 350, 280), border_radius=10)
        self.screen.blit(ui_surface, (10, 10))
        
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        y_offset = 25
        
        # Score display
        score_text = f"Score: {self.road.get_score()}"
        for offset in [(2, 2), (1, 1), (0, 0)]:
            color = (50, 50, 50) if offset != (0, 0) else self.YELLOW
            score_surface = font_large.render(score_text, True, color)
            self.screen.blit(score_surface, (25 + offset[0], y_offset + offset[1]))
        y_offset += 45
        
        # Multiplier display
        multiplier = self.road.get_multiplier()
        if multiplier > 1.0:
            mult_text = f"Multiplier: {multiplier:.1f}x"
            mult_color = self.GREEN if multiplier < 2.0 else self.RED
            mult_surface = font_medium.render(mult_text, True, mult_color)
            self.screen.blit(mult_surface, (25, y_offset))
            y_offset += 35
        
        # Current action with color coding
        if self.current_action == "SWIPE_LEFT":
            command_color = self.BLUE
            command_text = "⬅️ LEFT"
        elif self.current_action == "SWIPE_RIGHT":
            command_color = self.BLUE
            command_text = "➡️ RIGHT"
        else:
            command_color = self.GREEN
            command_text = "⬆️ CENTER"
        
        command_surface = font_medium.render(command_text, True, command_color)
        self.screen.blit(command_surface, (25, y_offset))
        y_offset += 35
        
        # Speed and lane info
        speed_text = f"Speed: {int(self.car.velocity)}"
        speed_surface = font_small.render(speed_text, True, self.WHITE)
        self.screen.blit(speed_surface, (25, y_offset))
        y_offset += 25
        
        # Lane indicator
        lane_names = ["LEFT", "CENTER", "RIGHT"]
        lane_text = f"Lane: {lane_names[self.car.lane]}"
        lane_surface = font_small.render(lane_text, True, self.WHITE)
        self.screen.blit(lane_surface, (25, y_offset))
        
        # Visual lane indicator
        lane_indicator_y = y_offset + 25
        for i in range(3):
            lane_rect = pygame.Rect(25 + i * 30, lane_indicator_y, 25, 15)
            if i == self.car.lane:
                pygame.draw.rect(self.screen, self.GREEN, lane_rect, border_radius=3)
            else:
                pygame.draw.rect(self.screen, (100, 100, 100), lane_rect, 2, border_radius=3)
        
        # High score display
        if self.high_score > 0:
            high_score_text = f"High Score: {self.high_score}"
            high_score_surface = font_small.render(high_score_text, True, self.YELLOW)
            self.screen.blit(high_score_surface, (25, lane_indicator_y + 35))
        
        # Model prediction info panel
        model_info_y = self.SCREEN_HEIGHT - 160
        model_bg = pygame.Surface((280, 150), pygame.SRCALPHA)
        pygame.draw.rect(model_bg, (0, 0, 0, 140), (0, 0, 280, 150), border_radius=8)
        self.screen.blit(model_bg, (10, model_info_y))
        
        # Prediction rate indicator
        prediction_hz = 1.0 / self.prediction_interval if self.prediction_interval > 0 else 60
        
        model_texts = [
            "MODEL PREDICTIONS:",
            f"Action: {self.current_action} ({self.current_confidence:.1%})",
            f"Rate: {prediction_hz:.1f} Hz",
            f"Left:   {self.all_predictions[0]:.1%}",
            f"Center: {self.all_predictions[1]:.1%}",
            f"Right:  {self.all_predictions[2]:.1%}"
        ]
        
        for i, text in enumerate(model_texts):
            if i == 0:
                color = self.CYAN
                font = font_medium
            else:
                color = (220, 220, 220)
                font = font_small
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, (20, model_info_y + 10 + i * 24))
    
    def draw_game_over(self):
        """Draw enhanced game over screen"""
        font_title = pygame.font.Font(None, 84)
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 36)
        
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(self.SCREEN_HEIGHT):
            alpha = int(150 * (y / self.SCREEN_HEIGHT))
            pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (self.SCREEN_WIDTH, y))
        self.screen.blit(overlay, (0, 0))
        
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2
        
        # Game over text with glow
        for offset in [(3, 3), (2, 2), (1, 1), (0, 0)]:
            glow_color = (100, 0, 0) if offset != (0, 0) else self.RED
            text_surface = font_title.render("GAME OVER", True, glow_color)
            text_rect = text_surface.get_rect(center=(center_x + offset[0], center_y - 120 + offset[1]))
            self.screen.blit(text_surface, text_rect)
        
        # Final score
        final_score = self.road.get_score()
        score_text = f"Final Score: {final_score}"
        score_surface = font_large.render(score_text, True, self.YELLOW)
        score_rect = score_surface.get_rect(center=(center_x, center_y - 50))
        self.screen.blit(score_surface, score_rect)
        
        # High score notification
        if final_score >= self.high_score and final_score > 0:
            new_high_text = "NEW HIGH SCORE!"
            high_surface = font_medium.render(new_high_text, True, self.GREEN)
            high_rect = high_surface.get_rect(center=(center_x, center_y - 10))
            self.screen.blit(high_surface, high_rect)
        elif self.high_score > 0:
            high_text = f"High Score: {self.high_score}"
            high_surface = font_medium.render(high_text, True, (200, 200, 200))
            high_rect = high_surface.get_rect(center=(center_x, center_y - 10))
            self.screen.blit(high_surface, high_rect)
        
        # Distance traveled
        distance_text = f"Distance: {int(self.road.distance_traveled)}m"
        distance_surface = font_medium.render(distance_text, True, self.WHITE)
        distance_rect = distance_surface.get_rect(center=(center_x, center_y + 30))
        self.screen.blit(distance_surface, distance_rect)
        
        # Restart instructions
        restart_bg = pygame.Surface((400, 80), pygame.SRCALPHA)
        pygame.draw.rect(restart_bg, (0, 0, 0, 150), (0, 0, 400, 80), border_radius=10)
        self.screen.blit(restart_bg, (center_x - 200, center_y + 70))
        
        restart_text = "Press R to Restart or ESC to Quit"
        restart_surface = font_medium.render(restart_text, True, self.WHITE)
        restart_rect = restart_surface.get_rect(center=(center_x, center_y + 110))
        self.screen.blit(restart_surface, restart_rect)
    
    def restart_game(self):
        """Restart the game"""
        self.car.reset_position(300, 650)
        self.road.reset()
        self.game_state = "PLAYING"
        self.time_since_last_prediction = 0.0  # Reset prediction timer
        self.pending_action = "CENTER"
    
    def run(self):
        """Main game loop with rate-limited predictions"""
        running = True
        
        while running:
            dt = self.clock.tick(self.FPS) / 1000.0
            
            events = pygame.event.get()
            running = self.handle_events(events)
            
            self.update(dt)
            
            # Draw background gradient
            for y in range(self.SCREEN_HEIGHT):
                color_intensity = int(20 + 15 * (y / self.SCREEN_HEIGHT))
                pygame.draw.line(self.screen, (color_intensity, color_intensity, color_intensity + 5), 
                               (0, y), (self.SCREEN_WIDTH, y))
            
            # Draw game elements
            self.road.draw_road(self.screen)
            self.road.draw_obstacles(self.screen)
            self.car.draw(self.screen)
            
            if self.game_state == "GAME_OVER":
                self.draw_game_over()
            
            self.draw_ui()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":    
    game = ModelControlledCarGame(
        model_path='best_model.h5', 
        prediction_interval=0.6  
    )
    game.run()