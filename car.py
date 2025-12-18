import pygame
import math

class Car:
    def __init__(self, x, y, width, height):
        self.y = y
        self.width = width
        self.height = height
        
        # Car movement settings
        self.velocity = 0
        self.max_velocity = 6
        self.acceleration = 0.2
        self.friction = 0.15
        self.default_speed = 3  # Speed when not braking
        
        # Lane system
        self.angle = 0
        self.lane = 1   # Middle lane (0, 1, 2)
        self.target_lane = 1
        self.lane_width = 200
        self.lane_change_speed = 10
        
        # Set initial position in center lane (lane 1 = x position 300)
        self.x = self.lane * self.lane_width + self.lane_width // 2
        
        # Current state
        self.braking = False
        self.current_command = "CENTER"
        self.last_command = "NONE"  # Track previous command to prevent repeated lane changes
    
    def update_controls(self, model_action):
        """Update car controls based on model prediction"""
        self.current_command = model_action
        
        # Handle braking
        if model_action == "BRAKE":
            self.braking = True
        else:
            self.braking = False
            
            # Handle action input for single lane changes (only if command changed)
            if model_action != self.last_command:
                if model_action == "SWIPE_LEFT" and self.target_lane > 0:
                    self.target_lane = max(0, self.target_lane - 1)
                elif model_action == "SWIPE_RIGHT" and self.target_lane < 2: 
                    self.target_lane = min(2, self.target_lane + 1)
        
        # Update last command to prevent repeated actions
        self.last_command = model_action
    
    def update(self, dt):
        """Update car physics and position"""
        # Handle speed - always move forward unless braking
        if self.braking:
            # Actually stop the car when braking
            self.velocity = max(0, self.velocity - self.acceleration * 4)
            # Don't maintain default speed when braking
        else:
            # Maintain default speed when not braking
            if self.velocity < self.default_speed:
                self.velocity = min(self.default_speed, self.velocity + self.acceleration)
            else:
                self.velocity = self.default_speed
        
        # Handle lane changing
        target_x = self.target_lane * self.lane_width + self.lane_width // 2
        if abs(self.x - target_x) > 3:
            if self.x < target_x:
                self.x += self.lane_change_speed
            else:
                self.x -= self.lane_change_speed
        else:
            self.x = target_x
            self.lane = self.target_lane
        
        # Update forward movement - but keep car position fixed on screen
        # The car stays in the same screen position, road moves instead
        # Don't move the car's Y position
    
    def get_rect(self):
        """Get car rectangle for collision detection"""
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)
    
    def draw(self, screen):
        """Draw the car on screen with enhanced graphics"""
        import math
        
        # Car colors based on state
        if self.braking:
            car_color = (220, 50, 50)  # Red when braking
            outline_color = (150, 20, 20)  # Dark red outline
            glow_color = (255, 100, 100)  # Red glow
        else:
            car_color = (50, 120, 220)  # Blue car
            outline_color = (30, 80, 150)  # Dark blue outline
            glow_color = (100, 150, 255)  # Blue glow
        
        # Draw car glow/shadow effect
        for i in range(5, 0, -1):
            glow_alpha = 50 - i * 8
            shadow_surface = pygame.Surface((self.width + i*2, self.height + i*2), pygame.SRCALPHA)
            shadow_rect = pygame.Rect(0, 0, self.width + i*2, self.height + i*2)
            pygame.draw.rect(shadow_surface, (*glow_color, glow_alpha), shadow_rect, border_radius=12)
            screen.blit(shadow_surface, (self.x - self.width//2 - i, self.y - self.height//2 - i))
        
        # Main car body with gradient effect
        car_rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                              self.width, self.height)
        
        # Create gradient effect
        for i in range(self.height):
            alpha = 0.3 + 0.7 * (i / self.height)
            gradient_color = tuple(int(c * alpha) for c in car_color)
            pygame.draw.rect(screen, gradient_color, 
                           (car_rect.x, car_rect.y + i, car_rect.width, 1))
        
        # Car outline with rounded corners
        pygame.draw.rect(screen, outline_color, car_rect, 4, border_radius=12)
        
        # Car windows with reflection effect
        window_rect = pygame.Rect(self.x - self.width//3, self.y - self.height//3, 
                                 self.width*2//3, self.height//3)
        pygame.draw.rect(screen, (150, 200, 255), window_rect, border_radius=6)
        
        # Window reflection
        reflection_rect = pygame.Rect(self.x - self.width//4, self.y - self.height//3 + 2, 
                                    self.width//2, self.height//6)
        pygame.draw.rect(screen, (200, 230, 255), reflection_rect, border_radius=3)
        
        # Enhanced headlights with glow - at the FRONT (top) of car
        left_light_pos = (self.x - self.width//4, self.y - self.height//2 - 3)
        right_light_pos = (self.x + self.width//4, self.y - self.height//2 - 3)
        
        # Headlight glow
        for radius in range(8, 3, -1):
            alpha = 30 + radius * 5
            glow_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 200, alpha), (radius, radius), radius)
            screen.blit(glow_surface, (left_light_pos[0] - radius, left_light_pos[1] - radius))
            screen.blit(glow_surface, (right_light_pos[0] - radius, right_light_pos[1] - radius))
        
        # Actual headlights
        pygame.draw.circle(screen, (255, 255, 220), left_light_pos, 4)
        pygame.draw.circle(screen, (255, 255, 220), right_light_pos, 4)
        
        # Brake lights with animation - at the BACK (bottom) of car
        if self.braking:
            brake_intensity = int(200 + 55 * abs(math.sin(pygame.time.get_ticks() * 0.01)))
            left_brake = (self.x - self.width//4, self.y + self.height//2 + 3)
            right_brake = (self.x + self.width//4, self.y + self.height//2 + 3)
            
            # Brake light glow
            for radius in range(6, 2, -1):
                alpha = 40 + radius * 8
                glow_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (brake_intensity, 30, 30, alpha), (radius, radius), radius)
                screen.blit(glow_surface, (left_brake[0] - radius, left_brake[1] - radius))
                screen.blit(glow_surface, (right_brake[0] - radius, right_brake[1] - radius))
            
            pygame.draw.circle(screen, (brake_intensity, 50, 50), left_brake, 3)
            pygame.draw.circle(screen, (brake_intensity, 50, 50), right_brake, 3)
        
        # Car details (door handles, side mirrors)
        # Left door handle
        pygame.draw.rect(screen, (80, 80, 80), 
                        (self.x - self.width//2 - 2, self.y - 5, 4, 10), border_radius=2)
        # Right door handle  
        pygame.draw.rect(screen, (80, 80, 80), 
                        (self.x + self.width//2 - 2, self.y - 5, 4, 10), border_radius=2)
        
        # Speed lines when moving fast
        if self.velocity > 4:
            for i in range(5):
                line_y = self.y + self.height//2 + 10 + i * 8
                line_alpha = int(100 * (self.velocity / self.max_velocity))
                line_surface = pygame.Surface((20, 2), pygame.SRCALPHA)
                pygame.draw.rect(line_surface, (255, 255, 255, line_alpha), (0, 0, 20, 2))
                screen.blit(line_surface, (self.x - 10, line_y))
    
    def reset_position(self, x, y):
        """Reset car to starting position"""
        self.y = y
        self.velocity = 0
        self.lane = 1  # Start in middle lane
        self.target_lane = 1
        # Ensure car stays in correct lane position
        self.x = self.lane * self.lane_width + self.lane_width // 2
        self.last_command = "NONE"  # Reset command tracking
