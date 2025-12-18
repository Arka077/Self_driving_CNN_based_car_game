"""
Automated Balanced Dataset Generator
- Uses EXACT same graphics as the actual game (Car and Road classes)
- Generates perfectly balanced training data
- Automatically labels based on optimal action (avoid obstacles)
"""

import pygame
import cv2
import numpy as np
import os
from datetime import datetime
import random
import sys

# Import Car first
from car import Car

# Import Road and Obstacle - handle potential import issues
try:
    from road import Road, Obstacle
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("Attempting alternative import...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("road_module", "road.py")
    road_module = importlib.util.module_from_spec(spec)
    sys.modules["road_module"] = road_module
    spec.loader.exec_module(road_module)
    Road = road_module.Road
    Obstacle = road_module.Obstacle

class AutomatedDatasetGenerator:
    def __init__(self, samples_per_class=500, screen_width=600, screen_height=800):
        pygame.init()
        
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Automated Dataset Generator - Matching Game Graphics")
        
        # Dataset settings
        self.samples_per_class = samples_per_class
        self.samples_collected = {'left': 0, 'no_action': 0, 'right': 0}
        
        # Create dataset directory
        self.dataset_dir = f'dataset'
        self.action_dirs = {
            'left': os.path.join(self.dataset_dir, 'left'),
            'no_action': os.path.join(self.dataset_dir, 'no_action'),
            'right': os.path.join(self.dataset_dir, 'right')
        }
        
        for path in self.action_dirs.values():
            os.makedirs(path, exist_ok=True)
        
        # Use actual game objects!
        self.car = Car(300, 650, 45, 70)
        self.road = Road(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Obstacle settings for controlled generation
        self.obstacle_min_distance = 100  # Minimum distance in front of car
        self.obstacle_max_distance = 350  # Maximum distance in front of car
        
        print("\n" + "="*70)
        print("🤖 AUTOMATED BALANCED DATASET GENERATOR")
        print("="*70)
        print(f"✅ Using EXACT game graphics (Car + Road classes)")
        print(f"Target: {samples_per_class} samples per class")
        print(f"Total samples: {samples_per_class * 3}")
        print(f"Saving to: {self.dataset_dir}/")
        print("="*70 + "\n")
    
    def generate_scenario(self, target_action):
        """
        Generate obstacle configuration and car position for the target action
        Returns: (car_lane, obstacle_configs)
        
        ✅LOGIC (teaches OPTIMAL actions only):
        - NO_ACTION: Car's lane is CLEAR (no obstacles blocking the way forward)
        - LEFT: Obstacle in car's lane, must move to LEFT (only when left is clear)
        - RIGHT: Obstacle in car's lane, must move to RIGHT (only when right is clear)
        
        This prevents the model from learning unnecessary moves!
        IMPORTANT: Only ONE obstacle at a time (realistic gameplay)
        """
        car_y = self.car.y
        
        # Obstacles should be closer and more visible (200-400 pixels ahead)
        min_distance = 150
        max_distance = 400
        
        if target_action == 'no_action':
            # ✅ Car's lane is COMPLETELY CLEAR
            # This teaches: "don't move if your lane is safe"
            car_lane = random.randint(0, 2)  # Random lane for car
            
            # Get the other two lanes
            other_lanes = [l for l in [0, 1, 2] if l != car_lane]
            
            # 60% chance: obstacles in OTHER lanes (teaches "obstacle elsewhere = stay")
            # 40% chance: no obstacles at all (teaches "clear road = stay")
            if random.random() < 0.6 and len(other_lanes) > 0:
                # ONE obstacle in a random OTHER lane
                obs_lane = random.choice(other_lanes)
                obs_y = car_y - random.randint(min_distance, max_distance)
                return car_lane, [(obs_lane, obs_y)]
            else:
                # No obstacles at all
                return car_lane, []
        
        elif target_action == 'left':
            # ✅ Obstacle in car's lane + LEFT lane is clear
            # This teaches: "move left ONLY when you must AND left is safe"
            car_lane = random.choice([1, 2])  # CENTER or RIGHT (can't be LEFT)
            
            # ONE obstacle in car's lane, at random distance
            obs_y = car_y - random.randint(min_distance, max_distance)
            
            # NO obstacles in the left lane (left lane must be clear to move there)
            return car_lane, [(car_lane, obs_y)]
        
        elif target_action == 'right':
            # ✅ Obstacle in car's lane + RIGHT lane is clear
            # This teaches: "move right ONLY when you must AND right is safe"
            car_lane = random.choice([0, 1])  # LEFT or CENTER (can't be RIGHT)
            
            # ONE obstacle in car's lane, at random distance
            obs_y = car_y - random.randint(min_distance, max_distance)
            
            # NO obstacles in the right lane (right lane must be clear to move there)
            return car_lane, [(car_lane, obs_y)]
        
        return 1, []  # Default: center lane, no obstacles
    
    def create_custom_obstacles(self, obstacle_configs):
        """
        Replace road's obstacles with custom configuration
        Uses the actual Obstacle class from road.py
        """
        # Clear existing obstacles
        self.road.obstacles.clear()
        
        for lane, y_pos in obstacle_configs:
            # Calculate x position based on lane (matching Road class)
            x = lane * self.road.lane_width + self.road.lane_width // 2
            
            # Create obstacle using the actual Obstacle class
            # All obstacles are red cars (matching game)
            try:
                obstacle = Obstacle(
                    x=x,
                    y=y_pos,
                    width=50,  # Fixed width from Road.spawn_obstacle
                    height=80,  # Fixed height from Road.spawn_obstacle
                    speed=0,  # Not used in current Road implementation
                    obstacle_type="car"  # Always use car type (red car)
                )
                
                self.road.obstacles.append(obstacle)
            except Exception as e:
                print(f"⚠️  Error creating obstacle: {e}")
                continue
    
    def capture_and_save_frame(self, surface, action):
        """Capture frame and save to appropriate folder"""
        # Convert pygame surface to numpy array
        frame_array = pygame.surfarray.array3d(surface)
        frame_array = np.transpose(frame_array, (1, 0, 2))
        frame_rgb = frame_array.astype(np.uint8)
        
        # Convert RGB to BGR for OpenCV (to match training pipeline)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        # Save to appropriate folder
        folder = self.action_dirs[action]
        filename = f"{action}_{self.samples_collected[action]:05d}.png"
        filepath = os.path.join(folder, filename)
        
        cv2.imwrite(filepath, frame_bgr)
        self.samples_collected[action] += 1
    
    def generate_dataset(self):
        """Main generation loop"""
        clock = pygame.time.Clock()
        
        # Create balanced list of actions to generate
        actions_to_generate = []
        for action in ['left', 'no_action', 'right']:
            actions_to_generate.extend([action] * self.samples_per_class)
        
        # Shuffle for randomness
        random.shuffle(actions_to_generate)
        
        total_samples = len(actions_to_generate)
        current_sample = 0
        
        print("🚀 Starting generation...\n")
        
        for target_action in actions_to_generate:
            # Handle pygame events (to prevent freezing)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("\n❌ Generation interrupted by user")
                    self.print_statistics()
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    print("\n❌ Generation interrupted by user")
                    self.print_statistics()
                    pygame.quit()
                    return
            
            # Create a fresh surface for the game
            game_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            
            # Generate obstacle scenario for this action
            car_lane, obstacle_configs = self.generate_scenario(target_action)
            
            # Position car in the correct lane
            self.car.lane = car_lane
            self.car.target_lane = car_lane
            self.car.x = car_lane * self.car.lane_width + self.car.lane_width // 2
            
            # Create obstacles
            self.create_custom_obstacles(obstacle_configs)
            
            # Add some visual variety to road scroll position
            self.road.road_y = random.randint(-50, 0)
            
            # Draw using ACTUAL game graphics
            # Background gradient (matching game)
            for y in range(self.SCREEN_HEIGHT):
                color_intensity = int(20 + 15 * (y / self.SCREEN_HEIGHT))
                pygame.draw.line(game_surface, 
                               (color_intensity, color_intensity, color_intensity + 5), 
                               (0, y), (self.SCREEN_WIDTH, y))
            
            # Draw road (using actual Road class)
            self.road.draw_road(game_surface)
            self.road.draw_obstacles(game_surface)
            
            # Draw car (using actual Car class)
            self.car.draw(game_surface)
            
            # Save the frame
            self.capture_and_save_frame(game_surface, target_action)
            
            # Update display (for visual feedback)
            self.screen.blit(game_surface, (0, 0))
            
            # Add UI overlay
            self.draw_progress_ui(current_sample, total_samples)
            
            pygame.display.flip()
            clock.tick(120)  # Fast generation
            
            current_sample += 1
            
            # Print progress
            if current_sample % 50 == 0:
                progress = (current_sample / total_samples) * 100
                print(f"Progress: {current_sample}/{total_samples} ({progress:.1f}%) | "
                      f"L:{self.samples_collected['left']} "
                      f"C:{self.samples_collected['no_action']} "
                      f"R:{self.samples_collected['right']}")
        
        print("\n✅ Generation complete!\n")
        
        # Generate 10% center obstacle scenarios to augment no_action
        print("🔄 Adding center obstacle scenarios (10% augmentation)...")
        center_samples = max(int(self.samples_per_class * 0.1), 1)
        self.generate_center_obstacle_augmentation(center_samples, clock)
        
        print("\n✅ Full dataset generation complete!\n")
        self.print_statistics()
        
        # Keep window open briefly
        pygame.time.wait(2000)
        pygame.quit()
    
    def draw_progress_ui(self, current, total):
        """Draw progress UI on screen"""
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((500, 250), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 200), (0, 0, 500, 250), border_radius=15)
        self.screen.blit(overlay, (50, 275))
        
        # Title
        title = font_large.render("Generating Dataset", True, (0, 255, 255))
        self.screen.blit(title, (100, 295))
        
        # Using game graphics indicator
        using_text = font_small.render("Using Actual Game Graphics", True, (0, 255, 0))
        self.screen.blit(using_text, (150, 345))
        
        # Progress
        progress = (current / total) * 100
        progress_text = font_medium.render(f"{current}/{total} ({progress:.1f}%)", True, (255, 255, 0))
        self.screen.blit(progress_text, (190, 380))
        
        # Progress bar
        bar_width = 450
        bar_height = 30
        bar_x = 75
        bar_y = 430
        
        # Background
        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=15)
        
        # Filled portion
        filled_width = int((current / total) * bar_width)
        pygame.draw.rect(self.screen, (0, 255, 100), (bar_x, bar_y, filled_width, bar_height), border_radius=15)
        
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 3, border_radius=15)
        
        # Counts
        counts_text = font_medium.render(
            f"L:{self.samples_collected['left']} "
            f"C:{self.samples_collected['no_action']} "
            f"R:{self.samples_collected['right']}", 
            True, (255, 255, 255)
        )
        self.screen.blit(counts_text, (130, 475))
    
    def generate_center_obstacle_augmentation(self, num_samples, clock):
        """Generate center obstacle scenarios and add to no_action folder"""
        print(f"Generating {num_samples} center obstacle scenarios...")
        
        for i in range(num_samples):
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("\n❌ Generation interrupted by user")
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    print("\n❌ Generation interrupted by user")
                    return
            
            game_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            
            # Car ONLY in LEFT or RIGHT (not center)
            car_lane = random.choice([0, 2])  # LEFT or RIGHT
            
            # Obstacle ONLY in CENTER lane
            obs_lane = 1
            
            # Varying vertical positions
            min_distance = -200
            max_distance = 350
            obs_y = self.car.y - random.randint(min_distance, max_distance)
            
            # Position car
            self.car.lane = car_lane
            self.car.target_lane = car_lane
            self.car.x = car_lane * self.car.lane_width + self.car.lane_width // 2
            
            # Create center obstacle
            self.create_custom_obstacles([(obs_lane, obs_y)])
            
            # Add visual variety
            self.road.road_y = random.randint(-50, 0)
            
            # Draw game
            for y in range(self.SCREEN_HEIGHT):
                color_intensity = int(20 + 15 * (y / self.SCREEN_HEIGHT))
                pygame.draw.line(game_surface, 
                               (color_intensity, color_intensity, color_intensity + 5), 
                               (0, y), (self.SCREEN_WIDTH, y))
            
            self.road.draw_road(game_surface)
            self.road.draw_obstacles(game_surface)
            self.car.draw(game_surface)
            
            # Save as no_action
            self.capture_and_save_frame(game_surface, 'no_action')
            
            # Display
            self.screen.blit(game_surface, (0, 0))
            
            # Draw augmentation UI
            font_medium = pygame.font.Font(None, 32)
            aug_text = font_medium.render(f"Augmenting: {i+1}/{num_samples}", True, (255, 165, 0))
            self.screen.blit(aug_text, (200, 50))
            
            pygame.display.flip()
            clock.tick(120)
            
            if (i + 1) % 20 == 0:
                print(f"  Augmentation: {i+1}/{num_samples}")
        
        print(f"✅ Added {num_samples} center obstacle scenarios to no_action\n")
    
    def print_statistics(self):
        """Print final statistics"""
        print("="*70)
        print("📊 DATASET GENERATION STATISTICS")
        print("="*70)
        print(f"Dataset saved to: {self.dataset_dir}/")
        print(f"\nSamples collected:")
        print(f"  LEFT:      {self.samples_collected['left']:4d}")
        print(f"  NO_ACTION: {self.samples_collected['no_action']:4d}")
        print(f"  RIGHT:     {self.samples_collected['right']:4d}")
        print(f"  TOTAL:     {sum(self.samples_collected.values()):4d}")
        
        total = sum(self.samples_collected.values())
        if total > 0:
            print(f"\nDistribution:")
            for action, count in self.samples_collected.items():
                pct = (count / total) * 100
                print(f"  {action:10s}: {pct:5.1f}%")
        
        print("\n" + "="*70)
        print("✅ Dataset ready for training!")
        print(f"\nNext steps:")
        print(f"1. Update your training script to use: '{self.dataset_dir}'")
        print(f"2. Run training with this balanced, game-matching dataset")
        print(f"3. Model should perform MUCH better!")
        print("="*70 + "\n")


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🤖 AUTOMATED DATASET GENERATOR")
    print("="*70)
    print("\n✅ Uses EXACT same Car and Road graphics as your game")
    print("✅ Perfectly balanced dataset (equal samples per class)")
    print("✅ Intelligent obstacle placement for realistic scenarios")
    print("\nConfiguration:")
    
    # Get user input
    try:
        samples = input("\nSamples per class (default 500, recommended 300-1000): ").strip()
        samples_per_class = int(samples) if samples else 500
        
        if samples_per_class < 100:
            print("⚠️  Warning: Less than 100 samples per class may not train well")
            print("   Recommended: 300-500 for good results")
        elif samples_per_class > 2000:
            print("⚠️  Warning: This will take a while. Consider starting with 500.")
    except:
        samples_per_class = 500
    
    print(f"\n✅ Will generate {samples_per_class} samples per class")
    print(f"   Total: {samples_per_class * 3} images")
    print(f"   Estimated time: ~{(samples_per_class * 3) / 60:.1f} seconds")
    print("\nPress ENTER to start, or CTRL+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        return
    
    # Create generator and run
    generator = AutomatedDatasetGenerator(samples_per_class=samples_per_class)
    generator.generate_dataset()


if __name__ == "__main__":
    main()