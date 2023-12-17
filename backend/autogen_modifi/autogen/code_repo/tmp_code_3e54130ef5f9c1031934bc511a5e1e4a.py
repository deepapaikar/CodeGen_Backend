import pygame
import random
import time

# Initialize pygame
pygame.init()

# Define the screen size
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Game')

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Define the snake and food block size
BLOCK_SIZE = 20

# Initialize variables
snake_pos = [[100, 50], [90, 50], [80, 50]]
snake_speed = [BLOCK_SIZE, 0]
food_pos = [random.randrange(1, (SCREEN_WIDTH // BLOCK_SIZE)) * BLOCK_SIZE,
            random.randrange(1, (SCREEN_HEIGHT // BLOCK_SIZE)) * BLOCK_SIZE]
food_spawn = True
score = 0

# Set the clock
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_speed[1] != BLOCK_SIZE:
                snake_speed = [0, -BLOCK_SIZE]
            elif event.key == pygame.K_DOWN and snake_speed[1] != -BLOCK_SIZE:
                snake_speed = [0, BLOCK_SIZE]
            elif event.key == pygame.K_LEFT and snake_speed[0] != BLOCK_SIZE:
                snake_speed = [-BLOCK_SIZE, 0]
            elif event.key == pygame.K_RIGHT and snake_speed[0] != -BLOCK_SIZE:
                snake_speed = [BLOCK_SIZE, 0]

    # Snake movement
    for i in range(len(snake_pos) - 1, 0, -1):
        snake_pos[i] = list(snake_pos[i - 1])
    snake_pos[0][0] += snake_speed[0]
    snake_pos[0][1] += snake_speed[1]

    # Snake collision with boundaries
    if snake_pos[0][0] >= SCREEN_WIDTH or snake_pos[0][0] < 0 or snake_pos[0][1] >= SCREEN_HEIGHT or snake_pos[0][1] < 0:
        running = False

    # Snake collision with itself
    for block in snake_pos[1:]:
        if snake_pos[0] == block:
            running = False

    # Spawn food
    if not food_spawn:
        food_pos = [random.randrange(1, (SCREEN_WIDTH // BLOCK_SIZE)) * BLOCK_SIZE,
                    random.randrange(1, (SCREEN_HEIGHT // BLOCK_SIZE)) * BLOCK_SIZE]
    food_spawn = False

    # Snake eating food
    if snake_pos[0] == food_pos:
        score += 1
        food_spawn = True
        snake_pos.append([0, 0])

    # Drawing everything
    screen.fill(BLACK)
    for pos in snake_pos:
        pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))

    # Display score
    font = pygame.font.SysFont(None, 35)
    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, [0, 0])

    # Update the display
    pygame.display.update()

    # Frame rate
    clock.tick(10)

# End the game
pygame.quit()