import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Screen setup - will adapt to device
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake Game")

# Colors
BACKGROUND = (20, 30, 40)
GRID_COLOR = (40, 50, 60)
SNAKE_COLOR = (50, 200, 100)
SNAKE_HEAD_COLOR = (70, 220, 120)
FOOD_COLOR = (220, 80, 80)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (70, 140, 200)
BUTTON_HOVER = (90, 160, 220)

# Game constants
CELL_SIZE = 25
GRID_WIDTH = screen_width // CELL_SIZE
GRID_HEIGHT = screen_height // CELL_SIZE
GAME_SPEED = 10  # FPS for snake movement

# Font setup
font_small = pygame.font.SysFont(None, 28)
font_medium = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 48)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.score = 0
        self.grow_to = 3
        self.speed = GAME_SPEED
        self.last_move_time = 0
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self, current_time):
        # Move snake at appropriate speed
        if current_time - self.last_move_time < 1000 // self.speed:
            return False
            
        self.last_move_time = current_time
        
        head = self.get_head_position()
        x, y = self.direction
        new_position = (((head[0] + x) % GRID_WIDTH), ((head[1] + y) % GRID_HEIGHT))
        
        # Check for collision with self
        if new_position in self.positions[1:]:
            return True  # Game over
            
        self.positions.insert(0, new_position)
        
        # Grow snake if needed
        if len(self.positions) > self.grow_to:
            self.positions.pop()
            
        return False  # Game continues
            
    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def grow(self):
        self.grow_to += 1
        self.score += 10
        # Gradually increase speed
        if self.score % 50 == 0:
            self.speed = min(self.speed + 1, 20)
    
    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_COLOR
            rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (30, 40, 30), rect, 1)
            
            # Draw eyes on head
            if i == 0:
                eye_size = CELL_SIZE // 5
                # Determine eye positions based on direction
                dx, dy = self.direction
                if dx == 1:  # Right
                    left_eye = (pos[0] * CELL_SIZE + CELL_SIZE - eye_size*2, pos[1] * CELL_SIZE + eye_size*2)
                    right_eye = (pos[0] * CELL_SIZE + CELL_SIZE - eye_size*2, pos[1] * CELL_SIZE + CELL_SIZE - eye_size*3)
                elif dx == -1:  # Left
                    left_eye = (pos[0] * CELL_SIZE + eye_size, pos[1] * CELL_SIZE + eye_size*2)
                    right_eye = (pos[0] * CELL_SIZE + eye_size, pos[1] * CELL_SIZE + CELL_SIZE - eye_size*3)
                elif dy == 1:  # Down
                    left_eye = (pos[0] * CELL_SIZE + eye_size*2, pos[1] * CELL_SIZE + CELL_SIZE - eye_size*2)
                    right_eye = (pos[0] * CELL_SIZE + CELL_SIZE - eye_size*3, pos[1] * CELL_SIZE + CELL_SIZE - eye_size*2)
                else:  # Up
                    left_eye = (pos[0] * CELL_SIZE + eye_size*2, pos[1] * CELL_SIZE + eye_size)
                    right_eye = (pos[0] * CELL_SIZE + CELL_SIZE - eye_size*3, pos[1] * CELL_SIZE + eye_size)
                
                pygame.draw.circle(surface, (20, 20, 40), left_eye, eye_size)
                pygame.draw.circle(surface, (20, 20, 40), right_eye, eye_size)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
        
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        
    def draw(self, surface):
        rect = pygame.Rect(self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, FOOD_COLOR, rect)
        pygame.draw.rect(surface, (180, 50, 50), rect, 2)
        
        # Draw shine effect
        shine_rect = pygame.Rect(
            self.position[0] * CELL_SIZE + CELL_SIZE//4,
            self.position[1] * CELL_SIZE + CELL_SIZE//4,
            CELL_SIZE//4, CELL_SIZE//4
        )
        pygame.draw.ellipse(surface, (255, 220, 220), shine_rect)

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (40, 60, 100), self.rect, 3, border_radius=10)
        
        text_surf = font_medium.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def check_click(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

def draw_grid(surface):
    for y in range(0, screen_height, CELL_SIZE):
        for x in range(0, screen_width, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)

def draw_score(surface, score, high_score):
    score_text = font_medium.render(f"Score: {score}", True, TEXT_COLOR)
    surface.blit(score_text, (20, 20))
    
    high_score_text = font_medium.render(f"High Score: {high_score}", True, TEXT_COLOR)
    surface.blit(high_score_text, (screen_width - high_score_text.get_width() - 20, 20))

def draw_game_over(surface, score, high_score):
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))
    
    game_over_text = font_large.render("GAME OVER", True, (220, 80, 80))
    surface.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, screen_height//3))
    
    score_text = font_medium.render(f"Score: {score}", True, TEXT_COLOR)
    surface.blit(score_text, (screen_width//2 - score_text.get_width()//2, screen_height//2))
    
    if score == high_score:
        high_score_text = font_small.render("New High Score!", True, (255, 215, 0))
        surface.blit(high_score_text, (screen_width//2 - high_score_text.get_width()//2, screen_height//2 + 50))

def draw_directional_buttons(surface):
    # Only show on mobile or when touch input is detected
    if pygame.display.get_surface().get_width() < 800 or touch_controls:
        center_x, center_y = screen_width // 2, screen_height - 120
        button_size = 60
        
        # Up button
        pygame.draw.circle(surface, BUTTON_COLOR, (center_x, center_y - 70), button_size)
        pygame.draw.polygon(surface, TEXT_COLOR, [
            (center_x, center_y - 90),
            (center_x - 20, center_y - 50),
            (center_x + 20, center_y - 50)
        ])
        
        # Down button
        pygame.draw.circle(surface, BUTTON_COLOR, (center_x, center_y + 70), button_size)
        pygame.draw.polygon(surface, TEXT_COLOR, [
            (center_x, center_y + 90),
            (center_x - 20, center_y + 50),
            (center_x + 20, center_y + 50)
        ])
        
        # Left button
        pygame.draw.circle(surface, BUTTON_COLOR, (center_x - 70, center_y), button_size)
        pygame.draw.polygon(surface, TEXT_COLOR, [
            (center_x - 90, center_y),
            (center_x - 50, center_y - 20),
            (center_x - 50, center_y + 20)
        ])
        
        # Right button
        pygame.draw.circle(surface, BUTTON_COLOR, (center_x + 70, center_y), button_size)
        pygame.draw.polygon(surface, TEXT_COLOR, [
            (center_x + 90, center_y),
            (center_x + 50, center_y - 20),
            (center_x + 50, center_y + 20)
        ])

def check_directional_button_click(pos):
    center_x, center_y = screen_width // 2, screen_height - 120
    button_radius = 60
    
    # Calculate distance to each button
    dist_up = math.hypot(pos[0] - center_x, pos[1] - (center_y - 70))
    dist_down = math.hypot(pos[0] - center_x, pos[1] - (center_y + 70))
    dist_left = math.hypot(pos[0] - (center_x - 70), pos[1] - center_y)
    dist_right = math.hypot(pos[0] - (center_x + 70), pos[1] - center_y)
    
    if dist_up < button_radius:
        return (0, -1)
    if dist_down < button_radius:
        return (0, 1)
    if dist_left < button_radius:
        return (-1, 0)
    if dist_right < button_radius:
        return (1, 0)
    return None

# Initialize game objects
snake = Snake()
food = Food()
restart_button = Button(screen_width//2 - 100, screen_height//2 + 100, 200, 50, "Play Again")

# Game state
game_over = False
high_score = 0
touch_controls = False  # Flag to indicate touch input

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Keyboard input (for laptops)
        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))
            else:
                if event.key == pygame.K_SPACE:
                    snake.reset()
                    food.randomize_position()
                    game_over = False
                    
        # Mouse and touch input
        if event.type == pygame.MOUSEMOTION:
            restart_button.check_hover(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            touch_controls = True
            if game_over:
                if restart_button.check_click(event.pos, event):
                    snake.reset()
                    food.randomize_position()
                    game_over = False
            else:
                # Check if directional button was pressed
                direction = check_directional_button_click(event.pos)
                if direction:
                    snake.change_direction(direction)
    
    # Game logic
    if not game_over:
        game_over = snake.update(current_time)
        
        # Check if snake ate food
        if snake.get_head_position() == food.position:
            snake.grow()
            food.randomize_position()
            # Make sure food doesn't appear on snake
            while food.position in snake.positions:
                food.randomize_position()
    
    # Update high score
    if snake.score > high_score:
        high_score = snake.score
    
    # Drawing
    screen.fill(BACKGROUND)
    draw_grid(screen)
    snake.draw(screen)
    food.draw(screen)
    draw_score(screen, snake.score, high_score)
    
    # Draw directional buttons for mobile
    draw_directional_buttons(screen)
    
    if game_over:
        draw_game_over(screen, snake.score, high_score)
        restart_button.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()