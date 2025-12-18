import pygame
import random
import math

class Obstacle:
    def __init__(self, x, y, width, height, speed, obstacle_type="car"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.active = True
        self.obstacle_type = obstacle_type
        self.animation_offset = random.random() * 6.28  # Random animation start
        self.points_awarded = False
        
        # Points for different obstacle types
        self.point_values = {
            "car": 10,
            "truck": 20,
            "barrier": 5
        }
    
    def update(self, dt, camera_speed):
        """Update obstacle position - obstacles come from ahead (top) toward car (bottom)"""
        # Move obstacle down the screen (from top toward car at bottom)
        self.y += camera_speed * dt * 150  # Obstacles move toward car
        
        # Remove obstacle if it goes past the car (bottom of screen)
        if self.y > 800:  # Past bottom of screen
            self.active = False
    
    def get_rect(self):
        """Get obstacle rectangle for collision detection"""
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)
    
    def draw(self, screen):
        """Draw the obstacle on screen with enhanced graphics"""
        if not self.active:
            return
            
        obstacle_rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                                  self.width, self.height)
        
        # Draw all obstacles as red cars with the same design
        self.draw_car(screen, obstacle_rect)
    
    def draw_car(self, screen, rect):
        """Draw a realistic enemy car - always red"""
        # Car is always red
        car_color = (200, 0, 0)
        
        # Main car body
        pygame.draw.rect(screen, car_color, rect, border_radius=8)
        pygame.draw.rect(screen, (100, 0, 0), 
                        rect, 3, border_radius=8)
        
        # Car windows
        window_rect = pygame.Rect(rect.x + rect.width//4, rect.y + rect.height//4, 
                                 rect.width//2, rect.height//3)
        pygame.draw.rect(screen, (100, 150, 200), window_rect, border_radius=4)
        
        # Headlights (at the front/top since car faces down)
        pygame.draw.circle(screen, (255, 255, 200), 
                          (rect.x + rect.width//4, rect.y + 3), 3)
        pygame.draw.circle(screen, (255, 255, 200), 
                          (rect.x + 3*rect.width//4, rect.y + 3), 3)
    
    def draw_truck(self, screen, rect):
        """Draw a truck obstacle"""
        # Truck body
        pygame.draw.rect(screen, (80, 80, 80), rect, border_radius=6)
        pygame.draw.rect(screen, (50, 50, 50), rect, 4, border_radius=6)
        
        # Truck cabin (at front/top)
        cabin_rect = pygame.Rect(rect.x + rect.width//6, rect.y, 
                               rect.width*2//3, rect.height//3)
        pygame.draw.rect(screen, (120, 120, 120), cabin_rect, border_radius=4)
        
        # Truck windows
        window_rect = pygame.Rect(rect.x + rect.width//3, rect.y + 2, 
                                 rect.width//3, rect.height//6)
        pygame.draw.rect(screen, (150, 200, 255), window_rect, border_radius=2)
        
        # Side stripes
        pygame.draw.rect(screen, (255, 100, 100), 
                        (rect.x + 2, rect.y + rect.height//2, rect.width - 4, 4))
    
    def draw_barrier(self, screen, rect):
        """Draw an orange construction barrier"""
        # Barrier body
        pygame.draw.rect(screen, (255, 140, 0), rect, border_radius=4)
        pygame.draw.rect(screen, (200, 100, 0), rect, 3, border_radius=4)
        
        # Diagonal stripes
        for i in range(0, rect.width + rect.height, 8):
            start_x = rect.x + i
            start_y = rect.y
            end_x = rect.x + i - rect.height
            end_y = rect.y + rect.height
            
            if start_x < rect.x + rect.width and end_x > rect.x:
                pygame.draw.line(screen, (255, 255, 255), 
                               (max(start_x, rect.x), start_y), 
                               (max(end_x, rect.x), end_y), 2)
    
    def draw_bonus(self, screen, rect):
        """Draw an animated bonus collectible"""
        import time
        
        # Pulsing glow effect
        current_time = time.time()
        pulse = abs(math.sin(current_time * 5 + self.animation_offset))
        glow_radius = int(20 + pulse * 10)
        glow_alpha = int(50 + pulse * 100)
        
        # Draw glow
        glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 215, 0, glow_alpha), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (rect.centerx - glow_radius, rect.centery - glow_radius))
        
        # Main bonus coin
        pygame.draw.circle(screen, (255, 215, 0), rect.center, rect.width//2)
        pygame.draw.circle(screen, (255, 255, 100), rect.center, rect.width//2 - 2)
        pygame.draw.circle(screen, (200, 160, 0), rect.center, rect.width//2, 3)
        
        # Star shape inside
        star_points = []
        for i in range(10):
            angle = i * math.pi / 5
            radius = rect.width//3 if i % 2 == 0 else rect.width//6
            x = rect.centerx + radius * math.cos(angle)
            y = rect.centery + radius * math.sin(angle)
            star_points.append((x, y))
        
        if len(star_points) > 2:
            pygame.draw.polygon(screen, (255, 255, 255), star_points)

class Road:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.lane_width = 200  # Wider lanes to match car
        self.num_lanes = 3  # Reduced to 3 lanes
        
        # Road properties
        self.road_y_offset = 0
        self.line_spacing = 40
        
        # Obstacles
        self.obstacles = []
        self.obstacle_spawn_timer = 0
        self.obstacle_spawn_interval = 1500  # Reduced frequency - spawn every 1.5 seconds
        self.obstacle_speed = 0  # Not used anymore, movement handled in update
        
        # Points system
        self.score = 0
        self.distance_traveled = 0
        self.multiplier = 1
        self.bonus_spawn_chance = 0.1  # 10% chance for bonus items
        
        # Visual effects
        self.road_particles = []
        self.explosion_effects = []
    
    def update(self, dt, car_speed):
        """Update road scrolling and obstacles"""
        # Update road scrolling effect - road moves DOWN to simulate car moving UP
        self.road_y_offset += car_speed * dt * 100  # Increased for better visibility
        if self.road_y_offset > self.line_spacing:
            self.road_y_offset = 0
        
        # Update distance traveled and score
        distance_increment = car_speed * dt * 15  # Scale for reasonable numbers
        self.distance_traveled += distance_increment
        self.score += int(distance_increment * self.multiplier)  # Distance points
        
        # Spawn obstacles more frequently
        self.obstacle_spawn_timer += dt * 1000  # Convert to milliseconds
        if self.obstacle_spawn_timer >= self.obstacle_spawn_interval:
            self.spawn_obstacle()
            self.obstacle_spawn_timer = 0
        
        # Update existing obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(dt, car_speed)
            if not obstacle.active:
                self.obstacles.remove(obstacle)
        
        # Update particle effects
        self.update_particles(dt)
    
    def update_particles(self, dt):
        """Update road particle effects"""
        # Add road particles for speed effect - particles move DOWN (toward car)
        if random.random() < 0.4:
            x = random.randint(0, self.num_lanes * self.lane_width)
            y = -10  # Start from top
            self.road_particles.append({
                'x': x, 'y': y, 'speed': random.uniform(200, 400),  # Move down
                'life': random.uniform(3, 5), 'max_life': 5
            })
        
        # Update particles - move them down the screen
        for particle in self.road_particles[:]:
            particle['y'] += particle['speed'] * dt  # Move DOWN
            particle['life'] -= dt
            
            if particle['life'] <= 0 or particle['y'] > self.height:
                self.road_particles.remove(particle)
    
    def award_points(self, obstacle):
        """Award points for avoiding an obstacle"""
        if not obstacle.points_awarded:
            points = obstacle.point_values[obstacle.obstacle_type] * self.multiplier
            self.score += points
            obstacle.points_awarded = True
            return points
        return 0
    
    def spawn_obstacle(self):
        """Spawn a new obstacle in a random lane with better distribution"""
        # Randomly select lane with equal probability
        lane = random.randint(0, self.num_lanes - 1)  # 0, 1, or 2 for 3 lanes
        x = lane * self.lane_width + self.lane_width // 2
        y = -100  # Start well above screen
        
        # All obstacles are the same size - fixed dimensions
        width = 50
        height = 80
        
        # Determine obstacle type based on weighted random chance
        rand = random.random()
        if rand < 0.33:  # 33% chance for truck
            obstacle_type = "truck"
        elif rand < 0.67:  # 34% chance for barrier
            obstacle_type = "barrier"
        else:  # 33% chance for regular car
            obstacle_type = "car"
        
        obstacle = Obstacle(x, y, width, height, self.obstacle_speed, obstacle_type)
        self.obstacles.append(obstacle)
    
    def draw_road(self, screen):
        """Draw the road lanes and markings with enhanced graphics"""
        # Fill road background with realistic asphalt
        road_rect = pygame.Rect(0, 0, self.num_lanes * self.lane_width, self.height)
        
        # Create asphalt gradient
        for y in range(self.height):
            color_variation = 40 + int(10 * math.sin(y * 0.1))
            road_color = (color_variation, color_variation, color_variation)
            pygame.draw.line(screen, road_color, (0, y), (road_rect.width, y))
        
        # Add road texture and wear marks
        for i in range(0, road_rect.width, 15):
            for j in range(0, self.height, 15):
                if random.random() < 0.05:
                    spot_size = random.randint(1, 3)
                    spot_color = random.randint(25, 35)
                    pygame.draw.circle(screen, (spot_color, spot_color, spot_color), (i, j), spot_size)
        
        # Draw lane dividers with enhanced dashed lines
        for i in range(1, self.num_lanes):
            x = i * self.lane_width
            for y in range(int(-self.road_y_offset), self.height + 50, self.line_spacing):
                # Main dashed line
                line_rect = pygame.Rect(x - 4, y, 8, 30)
                pygame.draw.rect(screen, (255, 255, 150), line_rect, border_radius=3)
                
                # Reflective coating effect
                highlight_rect = pygame.Rect(x - 2, y + 2, 4, 26)
                pygame.draw.rect(screen, (255, 255, 200), highlight_rect, border_radius=2)
        
        # Draw road edges with double lines
        edge_color = (255, 255, 100)
        # Left edge
        pygame.draw.rect(screen, edge_color, (0, 0, 8, self.height))
        pygame.draw.rect(screen, (200, 200, 80), (2, 0, 4, self.height))
        
        # Right edge
        right_edge = self.num_lanes * self.lane_width
        pygame.draw.rect(screen, edge_color, (right_edge - 8, 0, 8, self.height))
        pygame.draw.rect(screen, (200, 200, 80), (right_edge - 6, 0, 4, self.height))
        
        # Draw speed particles
        self.draw_particles(screen)
    
    def draw_particles(self, screen):
        """Draw road particle effects"""
        for particle in self.road_particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            if alpha > 0:
                size = int(2 * (particle['life'] / particle['max_life']))
                if size > 0:
                    particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surface, (255, 255, 255, alpha), (size, size), size)
                    screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
    
    def draw_obstacles(self, screen):
        """Draw all active obstacles"""
        for obstacle in self.obstacles:
            obstacle.draw(screen)
    
    def check_collisions(self, car_rect):
        """Check if car collides with any obstacles or collects bonuses"""
        for obstacle in self.obstacles:
            if obstacle.active and car_rect.colliderect(obstacle.get_rect()):
                # Collision with obstacle
                return True, 0
        return False, 0
    
    def get_score(self):
        """Get the current score"""
        return self.score
    
    def get_multiplier(self):
        """Get the current score multiplier"""
        return self.multiplier
    
    def get_distance(self):
        """Get the distance traveled"""
        return int(self.distance_traveled)
    
    def reset(self):
        """Reset road state"""
        self.obstacles.clear()
        self.distance_traveled = 0
        self.obstacle_spawn_timer = 0
        self.score = 0
        self.multiplier = 1.0
        self.road_particles.clear()
        self.explosion_effects.clear()
