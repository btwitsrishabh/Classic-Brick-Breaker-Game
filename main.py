import pygame
import random
import time
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 960
HEIGHT = 720
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BALL_RADIUS = 20
BALL_SPEED = 5
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_SPEED = 10
BRICK_WIDTH = 80
BRICK_HEIGHT = 30
BRICK_GAP = 10


# Load resources
def load_resources():
    background_image = pygame.image.load("17520.jpg")
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    bounce_sound = pygame.mixer.Sound("bounce.mp3")
    break_sound = pygame.mixer.Sound("blast.mp3")
    gameover_sound = pygame.mixer.Sound("game over.mp3")

    return background_image, bounce_sound, break_sound, gameover_sound


# Initialize the game
def initialize_game():
    ball = {
        "x": (WIDTH - BALL_RADIUS) // 2,
        "y": HEIGHT - 2 * BALL_RADIUS,
        "dx": random.choice([-1, 1]) * BALL_SPEED,
        "dy": -BALL_SPEED,
    }

    paddle = {
        "width": PADDLE_WIDTH,
        "height": PADDLE_HEIGHT,
        "x": (WIDTH - PADDLE_WIDTH) // 2,
        "y": HEIGHT - PADDLE_HEIGHT - 10,
        "speed": PADDLE_SPEED,
    }

    # Set up levels and brick configurations (defined globally)
    levels = [
        [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        [
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        ],
        [
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        ],
    ]

    current_level = 0
    bricks = generate_bricks(levels[current_level])

    power_ups = []
    score = 0

    game_started = False
    game_over = False
    paused = False
    paused_time = 0
    start_time = 0

    bounce_sound = pygame.mixer.Sound("bounce.mp3")
    break_sound = pygame.mixer.Sound("blast.mp3")
    game_over_sound = pygame.mixer.Sound("game over.mp3")

    # Set the current_level key in game_data
    game_data = {
        "ball": ball,
        "paddle": paddle,
        "bricks": bricks,
        "power_ups": power_ups,
        "score": score,
        "current_level": current_level,
        "game_started": game_started,
        "game_over": game_over,
        "paused": paused,
        "paused_time": paused_time,
        "start_time": start_time,
        "bounce_sound": bounce_sound,
        "break_sound": break_sound,
        "game_over_sound": game_over_sound,
        "levels": levels,
    }

    return game_data


# Generate power-ups
def generate_power_up(brick_rect):
    power_up_x = brick_rect.x + brick_rect.width // 2
    power_up_y = brick_rect.y + brick_rect.height // 2
    power_up_type = random.choice(["expand", "shrink", "speed_up"])
    power_up_rect = pygame.Rect(power_up_x - 10, power_up_y - 10, 20, 20)
    power_up = {"rect": power_up_rect, "type": power_up_type}
    return power_up


# Generate bricks based on the level configuration
def generate_bricks(level):
    bricks = []
    for row in range(len(level)):
        for col in range(len(level[row])):
            if level[row][col] == 1:
                brick_x = BRICK_GAP + (BRICK_WIDTH + BRICK_GAP) * col
                brick_y = BRICK_GAP + (BRICK_HEIGHT + BRICK_GAP) * row
                bricks.append(pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT))
    return bricks


# Update power-ups
def update_power_ups(power_ups, paddle):
    new_power_ups = []
    for power_up in power_ups:
        power_up["y"] += 3
        if power_up["rect"].colliderect(paddle):
            apply_power_up(power_up, paddle)
        else:
            new_power_ups.append(power_up)
    return new_power_ups


# Apply power-up effects
def apply_power_up(power_up, paddle):
    if power_up["type"] == "expand":
        paddle["width"] += 20
    elif power_up["type"] == "shrink":
        paddle["width"] -= 20
        if paddle["width"] < 20:
            paddle["width"] = 20
    elif power_up["type"] == "speed_up":
        paddle["speed"] += 2


# Update power-ups
def update_power_ups(power_ups, paddle):
    new_power_ups = []
    for power_up in power_ups:
        # Update the 'y' coordinate of the power-up 's rect
        power_up["rect"].y += 3

        # Check for collision with the paddle
        if (
            power_up["rect"].colliderect(
                (paddle["x"], paddle["y"], paddle["width"], paddle["height"])
            )
        ):
            apply_power_up(power_up, paddle)
        else:
            new_power_ups.append(power_up)
    return new_power_ups


def update_game_logic(game_data):
    ball = game_data["ball"]
    paddle = game_data["paddle"]
    bricks = game_data["bricks"]
    power_ups = game_data["power_ups"]
    current_level = game_data["current_level"]
    levels = game_data["levels"]

    # Move the paddle
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle["x"] -= paddle["speed"]
    if keys[pygame.K_RIGHT]:
        paddle["x"] += paddle["speed"]

    # Update ball position
    ball["x"] += ball["dx"]
    ball["y"] += ball["dy"]

    # Check for ball collision with the window edges
    if ball["x"] - BALL_RADIUS <= 0 or ball["x"] + BALL_RADIUS >= WIDTH:
        ball["dx"] = -ball["dx"]
        game_data["bounce_sound"].play()

    if ball["y"] - BALL_RADIUS <= 0:
        ball["dy"] = -ball["dy"]
        game_data["bounce_sound"].play()

    elif ball["y"] + BALL_RADIUS >= HEIGHT:
        game_data["game_over"] = True
        game_data["end_time"] = time.time()
        game_data["game_over_sound"].play()

    # Check for ball collision with the paddle
    if (
            ball["y"] + BALL_RADIUS >= paddle["y"]
            and paddle["x"] <= ball["x"] <= paddle["x"] + paddle["width"]
    ):
        # Calculate the angle of bounce based on where the ball hit the paddle
        relative_intersect_x = (paddle["x"] + paddle["width"] / 2) - ball["x"]
        normalized_relative_intersect_x = relative_intersect_x / (paddle["width"] / 2)
        bounce_angle = normalized_relative_intersect_x * (math.pi / 4)  # Adjust the bounce angle as needed

        # Update ball direction based on the bounce angle
        ball_speed = math.sqrt(ball["dx"] ** 2 + ball["dy"] ** 2)
        ball["dx"] = ball_speed * math.sin(bounce_angle)
        ball["dy"] = -ball_speed * math.cos(bounce_angle)

        game_data["bounce_sound"].play()

    # Check for ball collision with the bricks
    for brick in bricks:
        if brick.colliderect(
                pygame.Rect(
                    ball["x"] - BALL_RADIUS,
                    ball["y"] - BALL_RADIUS,
                    BALL_RADIUS * 2,
                    BALL_RADIUS * 2,
                )
        ):
            bricks.remove(brick)
            ball["dy"] = -ball["dy"]
            game_data["score"] += 1
            game_data["break_sound"].play()

            # Randomly generate power-ups
            if random.random() < 0.1:
                power_up_x = brick.x + brick.width // 2
                power_up_y = brick.y + brick.height // 2
                power_up_type = random.choice(["expand", "shrink", "speed_up"])
                power_up_rect = pygame.Rect(
                    power_up_x - 10, power_up_y - 10, 20, 20)
                power_up = {"rect": power_up_rect, "type": power_up_type}
                power_ups.append(power_up)

    # Handle power-up collision
    game_data["power_ups"] = update_power_ups(power_ups, paddle)

    # Check if all bricks are destroyed
    if len(bricks) == 0:
        if current_level < len(levels) - 1:
            # Move to the next level
            current_level += 1
            bricks = generate_bricks(levels[current_level])  # Generate bricks for the next level
            paddle["x"] = (WIDTH - paddle["width"]) // 2
            ball["x"] = paddle["x"] + paddle["width"] // 2
            ball["y"] = HEIGHT - 2 * BALL_RADIUS
            ball["dx"] = random.choice([-1, 1]) * BALL_SPEED
            ball["dy"] = -BALL_SPEED
            game_data["bounce_sound"].play()
        else:
            # Game is won
            game_data["game_over"] = True
            game_data["end_time"] = time.time()
            game_data["game_over_sound"].play()

    # Update game_data with the new current_level and bricks
    game_data["current_level"] = current_level
    game_data["bricks"] = bricks


# Draw screen
def draw_screen(screen, background_image, game_data):
    # Draw the background image
    screen.blit(background_image, (0, 0))

    if not game_data["game_started"]:
        # Display start game text
        font = pygame.font.Font(None, 36)
        start_text = font.render("Press SPACE to start the game", True, RED)
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(start_text, start_rect)
    elif not game_data["game_over"] and not game_data["paused"]:
        # Draw the bricks
        for brick in game_data["bricks"]:
            pygame.draw.rect(screen, RED, brick)

        # Draw the paddle
        pygame.draw.rect(
            screen, BLACK, (game_data["paddle"]["x"], game_data["paddle"]["y"], game_data["paddle"]["width"],
                            game_data["paddle"]["height"])
        )

        # Draw the ball
        pygame.draw.circle(
            screen,
            RED,
            (int(game_data["ball"]["x"]), int(game_data["ball"]["y"])),
            BALL_RADIUS
        )

        # Draw the score, timer, and level number
        font = pygame.font.Font(None, 36)
        score_text = font.render("Score: {}".format(game_data["score"]), True, WHITE)
        score_rect = score_text.get_rect(topleft=(10, 10))
        screen.blit(score_text, score_rect)

        current_time = time.time() - game_data["start_time"]
        timer_text = font.render(
            "Time: {:.2f} seconds".format(current_time), True, WHITE)
        timer_rect = timer_text.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(timer_text, timer_rect)

        level_text = font.render(
            "Level: {}".format(game_data["current_level"] + 1), True, RED)
        level_rect = level_text.get_rect(center=(WIDTH // 2, 30))
        screen.blit(level_text, level_rect)
    else:
        if not game_data["paused"]:
            # Display game over text
            font = pygame.font.Font(None, 36)
            if game_data["current_level"] < len(game_data["levels"]) - 1:
                game_over_text = font.render("Level Complete!", True, RED)
            else:
                game_over_text = font.render("You Win!", True, RED)
            game_over_rect = game_over_text.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(game_over_text, game_over_rect)

            if game_data["current_level"] < len(game_data["levels"]) - 1:
                next_level_text = font.render(
                    "Press SPACE to continue", True, RED)
                next_level_rect = next_level_text.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(next_level_text, next_level_rect)
            else:
                time_taken = game_data["end_time"] - game_data["start_time"]
                time_taken_text = font.render(
                    "Time Taken: {:.2f} seconds".format(time_taken), True, RED)
                time_taken_rect = time_taken_text.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(time_taken_text, time_taken_rect)

            restart_text = font.render("Press R to restart", True, RED)
            restart_rect = restart_text.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(restart_text, restart_rect)
        else:
            # Display pause text
            font = pygame.font.Font(None, 36)
            pause_text = font.render("PAUSED", True, RED)
            pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(pause_text, pause_rect)

    # Draw power-ups
    for power_up in game_data["power_ups"]:
        pygame.draw.rect(screen, WHITE, power_up["rect"])


# Main game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Ball Game")
    clock = pygame.time.Clock()

    background_image, bounce_sound, break_sound, game_over_sound = load_resources()
    game_data = initialize_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_data["game_started"] and not game_data["game_over"]:
                        game_data["paused"] = not game_data["paused"]
                        if game_data["paused"]:
                            game_data["paused_time"] = time.time() - game_data["start_time"]
                        else:
                            game_data["start_time"] = time.time() - game_data["paused_time"]
                elif not game_data["game_started"] and event.key == pygame.K_SPACE:
                    game_data["game_started"] = True
                    game_data["start_time"] = time.time()
                elif game_data["game_over"] and event.key == pygame.K_SPACE:
                    game_data = initialize_game()

        if game_data["game_started"] and not game_data["game_over"] and not game_data["paused"]:
            # Update game logic
            update_game_logic(game_data)

        # Draw everything
        draw_screen(screen, background_image, game_data)
        pygame.display.flip()
        clock.tick(FPS)


# Main game entry point
if __name__ == "__main__":
    main()
