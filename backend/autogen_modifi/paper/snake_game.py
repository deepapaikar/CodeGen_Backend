# filename: snake_game.py
import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Define the colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Define the game window, block size, and speed
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20
SPEED = 15

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

# Snake and Food data
snake_pos = [[100, 50], [90, 50], [80, 50]]
snake_food = [random.randrange(1, (SCREEN_WIDTH//BLOCK_SIZE)) * BLOCK_SIZE,
              random.randrange(1, (SCREEN_HEIGHT//BLOCK_SIZE)) * BLOCK_SIZE]
food_spawn = True
direction = 'RIGHT'
change_to = direction
score = 0

# Game Over function
def game_over():
    my_font = pygame.font.SysFont('times new roman', 50)
    game_over_surface = my_font.render('Your Score is: ' + str(score), True, RED)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (SCREEN_WIDTH/2, SCREEN_HEIGHT/4)
    screen.fill(BLACK)
    screen.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    quit()

# Main function
def main():
    global direction, change_to, score, snake_food, food_spawn

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_to = 'UP'
                elif event.key == pygame.K_DOWN:
                    change_to = 'DOWN'
                elif event.key == pygame.K_LEFT:
                    change_to = 'LEFT'
                elif event.key == pygame.K_RIGHT:
                    change_to = 'RIGHT'

        # Making sure the snake cannot move in the opposite direction instantaneously
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        # Moving the snake
        if direction == 'UP':
            snake_pos[0][1] -= BLOCK_SIZE
        if direction == 'DOWN':
            snake_pos[0][1] += BLOCK_SIZE
        if direction == 'LEFT':
            snake_pos[0][0] -= BLOCK_SIZE
        if direction == 'RIGHT':
            snake_pos[0][0] += BLOCK_SIZE

        # Snake body growing mechanism
        snake_pos.insert(0, list(snake_pos[0]))
        if snake_pos[0] == snake_food:
            score += 1
            food_spawn = False
        else:
            snake_pos.pop()

        # Spawning food on the screen
        if not food_spawn:
            snake_food = [random.randrange(1, (SCREEN_WIDTH//BLOCK_SIZE)) * BLOCK_SIZE,
                          random.randrange(1, (SCREEN_HEIGHT//BLOCK_SIZE)) * BLOCK_SIZE]
        food_spawn = True

        # GFX
        screen.fill(BLACK)
        for pos in snake_pos:
            pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(screen, RED, pygame.Rect(snake_food[0], snake_food[1], BLOCK_SIZE, BLOCK_SIZE))

        # Game Over conditions
        if snake_pos[0][0] < 0 or snake_pos[0][0] > SCREEN_WIDTH-BLOCK_SIZE:
            game_over()
        if snake_pos[0][1] < 0 or snake_pos[0][1] > SCREEN_HEIGHT-BLOCK_SIZE:
            game_over()
        for block in snake_pos[1:]:
            if snake_pos[0] == block:
                game_over()

        # Refresh game screen
        pygame.display.update()
        # Refresh rate
        clock.tick(SPEED)

# Run the game
main()