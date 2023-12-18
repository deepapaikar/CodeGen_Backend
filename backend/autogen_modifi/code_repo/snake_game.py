# filename: snake_game.py

import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Set game window dimensions
WIDTH, HEIGHT = 640, 480
game_window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')

# Define snake parameters
snake_block = 20
snake_speed = 15
snake_list = []
snake_length = 1

# Define food parameters
foodx = round(random.randrange(0, WIDTH - snake_block) / 20.0) * 20.0
foody = round(random.randrange(0, HEIGHT - snake_block) / 20.0) * 20.0

# Initialize game clock
clock = pygame.time.Clock()

# Define snake function
def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(game_window, GREEN, [x[0], x[1], snake_block, snake_block])

# Define game over function
def game_over():
    font_style = pygame.font.SysFont(None, 50)
    message = font_style.render('You Lost! Press Q-Quit or C-Play Again', True, RED)
    game_window.blit(message, [WIDTH / 6, HEIGHT / 3])
    pygame.display.update()
    time.sleep(2)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                quit()
            if event.key == pygame.K_c:
                game_loop()

# Define score function
def your_score(score):
    value = pygame.font.SysFont(None, 35).render("Your Score: " + str(score), True, BLACK)
    game_window.blit(value, [0, 0])

# Define game loop
def game_loop():
    game_over_flag = False
    game_close = False

    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    x1_change = 0
    y1_change = 0

    snake_list = []
    snake_length = 1

    foodx = round(random.randrange(0, WIDTH - snake_block) / 20.0) * 20.0
    foody = round(random.randrange(0, HEIGHT - snake_block) / 20.0) * 20.0

    while not game_over_flag:

        while game_close:
            game_window.fill(WHITE)
            game_over()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over_flag = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        game_window.fill(WHITE)
        pygame.draw.rect(game_window, RED, [foodx, foody, snake_block, snake_block])
        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        our_snake(snake_block, snake_list)
        your_score(snake_length - 1)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, WIDTH - snake_block) / 20.0) * 20.0
            foody = round(random.randrange(0, HEIGHT - snake_block) / 20.0) * 20.0
            snake_length += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

# Start the game loop
game_loop()