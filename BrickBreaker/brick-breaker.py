import sys
import math
import pygame
import random

from pygame.locals import *

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 14
BALL_SIZE = 10
BLOCK_WIDTH = 80
BLOCK_HEIGHT = 30

class Paddle(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, width, height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = pygame.Surface([width, height])
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = (screen_width - width) // 2
        self.rect.y = screen_height - height - 10
        self.speed = 7

    def update(self, move_left, move_right):
        if move_left and self.rect.x > 0:
            self.rect.x -= self.speed
        if move_right and self.rect.x < self.screen_width - self.rect.width:
            self.rect.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Ball(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, size):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.original_image = pygame.image.load("items/ball.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (size, size))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = (screen_width - size) // 2
        self.rect.y = screen_height - size - 30
        self.speed = 5
        self.direction = [1, -1]
        self.rotation_angle = 0

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        if self.rect.x <= 0 or self.rect.x >= self.screen_width - self.rect.width:
            self.direction[0] = -self.direction[0]
        if self.rect.y <= 0:
            self.direction[1] = -self.direction[1]
        if self.direction[0] > 0:
            self.rotation_angle += self.speed
        else:
            self.rotation_angle -= self.speed

    def draw(self, screen):
        self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        screen.blit(self.image, self.rect)



class Block(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill((0, 128, 255))
        self.rect = self.image.get_rect()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, size, color, effect):
        super().__init__()
        self.image = pygame.Surface([size, size])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2
        self.effect = effect

    def update(self):
        self.rect.y += self.speed

    def apply_effect(self, paddle, ball):
        soundpowerup.play()
        if self.effect == "increase_paddle_size":
            paddle.rect.width *= 2
            paddle.image = pygame.transform.scale(paddle.image, (paddle.rect.width, paddle.rect.height))  # Add this line
        elif self.effect == "increase_ball_speed":
            ball.speed = 10

class LaserPowerUp(PowerUp):
    def __init__(self, x, y, size, color, effect):
        super().__init__(x, y, size, color, effect)
        self.image = pygame.Surface([size, size])
        self.image.fill(color)
        pygame.draw.rect(self.image, (255, 255, 255), [size // 2 - 2, 0, 4, size])
        
    def apply_effect(self, paddle, ball):
        if self.effect == "increase_paddle_size":
            paddle.rect.width *= 2
        elif self.effect == "increase_ball_speed":
            ball.speed = 10
        elif self.effect == "laser":
            paddle.has_laser = True

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, num_frames, frame_size, frame_duration):
        super().__init__()
        self.x = x
        self.y = y
        self.num_frames = num_frames
        self.frame_size = frame_size
        self.frame_duration = frame_duration
        self.frames = self.create_spritesheet()
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.elapsed_time = 0

    def create_spritesheet(self):
        frames = []
        for i in range(self.num_frames):
            frame = pygame.Surface(self.frame_size)
            frame.fill((0, 0, 0))
            pygame.draw.circle(frame, (255, 0, 0), (self.frame_size[0] // 2, self.frame_size[1] // 2),
                               (i + 1) * self.frame_size[0] // (self.num_frames * 2))
            frames.append(frame)
        return frames

    def update(self, dt):
        self.elapsed_time += dt
        if self.elapsed_time >= self.frame_duration:
            self.elapsed_time = 0
            self.current_frame += 1
            if self.current_frame >= self.num_frames:
                self.kill()
            else:
                self.image = self.frames[self.current_frame]


paddle = Paddle(SCREEN_WIDTH, SCREEN_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT)
blocks = pygame.sprite.Group()
power_ups = pygame.sprite.Group()


for i in range(5):
    for j in range(8):
        block = Block(BLOCK_WIDTH, BLOCK_HEIGHT)
        block.rect.x = j * (BLOCK_WIDTH + 10) + 50
        block.rect.y = i * (BLOCK_HEIGHT + 10) + 50
        blocks.add(block)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Breakout')
clock = pygame.time.Clock()
ball = Ball(SCREEN_WIDTH, SCREEN_HEIGHT, 20)
explosions = pygame.sprite.Group()



running = True
move_left = False
move_right = False

soundmainmenu = pygame.mixer.Sound('sounds/MenuSound.mp3')
soundmaingame = pygame.mixer.Sound('sounds/MainGameSound.mp3')
soundmainmenumove = pygame.mixer.Sound('sounds/mainmenumovesound.wav')
soundbrickcollide = pygame.mixer.Sound('sounds/brickbreak.wav')
soundplankcollide = pygame.mixer.Sound('sounds/soundplankcollide.wav')
soundgameopener = pygame.mixer.Sound('sounds/gameopener.wav')
soundpowerup = pygame.mixer.Sound('sounds/soundpowerup.wav')
max_sound_duration1 = 400
max_sound_duration2 = 100

def create_level(level):
    bricks = pygame.sprite.Group()

    if level == 1:
        # Create level 1 bricks
        for i in range(8):
            for j in range(6):
                brick = Block(10 + i * 100, 50 + j * 30)
                bricks.add(brick)
    elif level == 2:
        # Create level 2 bricks
        for i in range(9):
            for j in range(7):
                brick = Block(10 + i * 90, 50 + j * 30)
                bricks.add(brick)

    return bricks

def main_menu(screen, clock):
    control = 'Keyboard'
    soundmainmenu.play()
    menu_items = ["Play Game", "Set Difficulty", "Settings", "Quit Game"]
    current_item = 0
    font = pygame.font.Font("font/PressStart2P-Regular.ttf", 24)
    menu_running = True

    def get_hovered_item(pos):
        for i, item in enumerate(menu_items):
            text = font.render(item, True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.center = (SCREEN_WIDTH // 2, 200 + 50 * i)
            if text_rect.collidepoint(pos):
                return i
        return None

    while menu_running:
        screen.fill((0, 0, 0))

        for i, item in enumerate(menu_items):
            color = (0, 0, 255) if i == current_item else (255, 255, 255)
            text = font.render(item, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + 50 * i))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEMOTION:
                hovered_item = get_hovered_item(event.pos)
                if hovered_item is not None:
                    current_item = hovered_item
            if event.type == MOUSEBUTTONDOWN:
                soundmainmenumove.play()
                if event.button == 1:
                    if current_item == 0:
                        return control
                    elif current_item == 1:
                        set_difficulty(screen, clock)
                    elif current_item == 2:
                        control = settings(screen, clock)
                    elif current_item == 3:
                        pygame.quit()
                        sys.exit()
            
            if event.type == KEYDOWN:
                if event.key == K_DOWN:
                    current_item = (current_item + 1) % len(menu_items)
                    soundmainmenumove.play()
                if event.key == K_UP:
                    current_item = (current_item - 1) % len(menu_items)
                    soundmainmenumove.play()
                if event.key == K_RETURN:
                    soundmainmenumove.play()
                    if current_item == 0:
                        return control
                    elif current_item == 1:
                        set_difficulty(screen, clock)
                    elif current_item == 2:
                        control = settings(screen, clock)
                    elif current_item == 3:
                        pygame.quit()
                        sys.exit()



        clock.tick(60)


def set_difficulty(screen, clock):
    difficulties = ["Easy", "Medium", "Hard"]
    current_difficulty = 0
    font = pygame.font.Font("font/PressStart2P-Regular.ttf", 24)
    setting_difficulty = True
    back_button = pygame.Rect(10, 10, 100, 40)

    while setting_difficulty:

        screen.fill((0, 0, 0))

        for i, difficulty in enumerate(difficulties):
            color = (0, 255, 0) if difficulty == "Easy" else (0, 0, 255) if difficulty == "Medium" else (255, 0, 0)
            if i != current_difficulty:
                color = (128, 128, 128)
            text = font.render(difficulty, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + 50 * i))
        mouse_x, mouse_y = pygame.mouse.get_pos()

        pygame.draw.rect(screen, (255, 255, 255), back_button, 1)
        back_text_color = (0, 0, 255) if back_button.collidepoint(mouse_x, mouse_y) else (255, 255, 255)
        back_text = font.render("<-", True, (255, 255, 255))
        screen.blit(back_text, (back_button.x + back_button.width // 2 - back_text.get_width() // 2,
                                back_button.y + back_button.height // 2 - back_text.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                for i, difficulty in enumerate(difficulties):
                    text = font.render(difficulty, True, (255, 255, 255))
                    text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
                    text_y = 200 + 50 * i
                    if text_x <= mouse_x <= text_x + text.get_width() and text_y <= mouse_y <= text_y + text.get_height():
                        current_difficulty = i
            if event.type == MOUSEBUTTONDOWN:
                soundmainmenumove.play()
                if event.button == 1:
                    if back_button.collidepoint(event.pos):
                        setting_difficulty = False
                    elif current_difficulty == 0:
                        ball.speed = 4
                        paddle.speed = 6
                        setting_difficulty = False
                    elif current_difficulty == 1:
                        ball.speed = 6
                        paddle.speed = 8
                        setting_difficulty = False
                    elif current_difficulty == 2:
                        ball.speed = 8
                        paddle.speed = 10
                        setting_difficulty = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    setting_difficulty = False
                if event.key == K_DOWN:
                    current_difficulty = (current_difficulty + 1) % len(difficulties)
                    soundmainmenumove.play()
                if event.key == K_UP:
                    current_difficulty = (current_difficulty - 1) % len(difficulties)
                    soundmainmenumove.play()
                if event.key == K_RETURN:
                    soundmainmenumove.play()
                    if current_difficulty == 0:
                        ball.speed = 4
                        paddle.speed = 6
                        setting_difficulty = False
                    elif current_difficulty == 1:
                        ball.speed = 6
                        paddle.speed = 8
                        setting_difficulty = False
                    elif current_difficulty == 2:
                        ball.speed = 8
                        paddle.speed = 10
                        setting_difficulty = False

        clock.tick(60)

def settings(screen, clock):
    control_methods = ["Keyboard", "Mouse"]
    current_controlmethod = 0
    font = pygame.font.Font("font/PressStart2P-Regular.ttf", 24)
    setting_control = True
    back_button = pygame.Rect(10, 10, 100, 40)

    while setting_control:

        screen.fill((0, 0, 0))

        for i, control in enumerate(control_methods):
            color = (0, 255, 0) if control == "Keyboard" else (0, 0, 255) if control == "Mouse" else (255, 0, 0)
            if i != current_controlmethod:
                color = (128, 128, 128)
            text = font.render(control, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + 50 * i))
        mouse_x, mouse_y = pygame.mouse.get_pos()

        pygame.draw.rect(screen, (255, 255, 255), back_button, 1)
        back_text_color = (0, 0, 255) if back_button.collidepoint(mouse_x, mouse_y) else (255, 255, 255)
        back_text = font.render("<-", True, (255, 255, 255))
        screen.blit(back_text, (back_button.x + back_button.width // 2 - back_text.get_width() // 2,
                                back_button.y + back_button.height // 2 - back_text.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                for i, control in enumerate(control_methods):
                    text = font.render(control, True, (255, 255, 255))
                    text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
                    text_y = 200 + 50 * i
                    if text_x <= mouse_x <= text_x + text.get_width() and text_y <= mouse_y <= text_y + text.get_height():
                        current_controlmethod = i
            if event.type == MOUSEBUTTONDOWN:
                soundmainmenumove.play()
                if event.button == 1:
                    if back_button.collidepoint(event.pos):
                        setting_control = False
                    elif current_controlmethod == 0:
                        print("Picked Keyboard")
                        return 'Keyboard'
                    elif current_controlmethod == 1:
                        print("Picked Mouse")
                        return 'Mouse'

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    setting_control = False
                if event.key == K_DOWN:
                    current_controlmethod = (current_controlmethod + 1) % len(control_methods)
                    soundmainmenumove.play()
                if event.key == K_UP:
                    current_controlmethod = (current_controlmethod - 1) % len(control_methods)
                    soundmainmenumove.play()
                if event.key == K_RETURN:
                    soundmainmenumove.play()
                    if current_controlmethod == 0:
                        print("Picked Keyboard")
                        return 'Keyboard'
                    elif current_controlmethod == 1:
                        print("Picked Mouse")
                        return 'Mouse'

        clock.tick(60)



def game_over(screen, clock):
    font = pygame.font.Font("font/PressStart2P-Regular.ttf", 24)
    text = font.render("Game Over", True, (0, 255, 0))
    text_rect = text.get_rect()
    text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    screen.blit(text, text_rect)
    pygame.display.flip()

    play_again = False
    while not play_again:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    play_again = True
                    return True
                if event.key == K_ESCAPE:
                    play_again = False
                    return False
        clock.tick(60)

control_method = main_menu(screen, clock)
soundmainmenu.stop()
soundgameopener.play()
pygame.time.wait(int(soundgameopener.get_length() * 1000))
soundmaingame.play()

dt = 60

level = 1
bricks = create_level(level)


while running:

    if control_method == "Keyboard":
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    move_left = True
                if event.key == K_RIGHT:
                    move_right = True
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    move_left = False
                if event.key == K_RIGHT:
                    move_right = False

    elif control_method == "Mouse":

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == MOUSEMOTION:
                new_x = event.pos[0] - paddle.rect.width // 2
                new_x = max(0, min(new_x, screen.get_width() - paddle.rect.width))
                paddle.rect.x = new_x


    paddle.update(move_left, move_right)
    ball.update()

    if pygame.sprite.collide_rect(ball, paddle) and ball.direction[1] > 0:
        ball.direction[1] = -ball.direction[1]
        soundplankcollide.play(maxtime=max_sound_duration2)
        relative_position = (ball.rect.x + ball.rect.width / 2) - (paddle.rect.x + paddle.rect.width / 2)
        normalized_position = relative_position / (paddle.rect.width / 2)
        ball.direction[0] += normalized_position * 0.5
        ball.direction[0] = max(min(ball.direction[0], 1), -1)

    block_collided = pygame.sprite.spritecollideany(ball, blocks)
    if block_collided:
        blocks.remove(block_collided)
        ball.direction[1] = -ball.direction[1]
        soundbrickcollide.play(maxtime=max_sound_duration1)

        explosion = Explosion(block_collided.rect.x, block_collided.rect.y, 8, (64, 64), 50)
        explosions.add(explosion)

        if random.random() < 0.25:
            effect = random.choice(["increase_paddle_size", "increase_ball_speed"])
            color = (0, 255, 0) if effect == "increase_paddle_size" else (255, 0, 0)
            power_up = PowerUp(block_collided.rect.x, block_collided.rect.y, 20, color, effect)
            power_ups.add(power_up)

    explosions.update(dt)
    power_ups.update()

    for power_up in power_ups:
        if pygame.sprite.collide_rect(paddle, power_up):
            paddle.rect.width = PADDLE_WIDTH
            ball.speed = 6
            power_up.apply_effect(paddle, ball)
            power_ups.remove(power_up)
            paddle.image = pygame.transform.scale(paddle.image, (paddle.rect.width, paddle.rect.height))


    if ball.rect.y >= screen.get_height():
        print("Game Over!")
        soundmaingame.stop()
        if game_over(screen, clock):
            level = 1
            bricks = create_level(level)
            ball.reset_position()
            paddle.reset_position()
            paddle.rect.width = PADDLE_WIDTH
            paddle.image = pygame.transform.scale(paddle.image, (paddle.rect.width, paddle.rect.height))
            ball.speed = 6
        else:
            running = False

    if len(bricks) == 0:
        level += 1
        bricks = create_level(level)

        ball.reset_position()
        paddle.reset_position()


    screen.fill((0, 0, 0))
    font = pygame.font.Font("font/PressStart2P-Regular.ttf", 24)
    level_text = font.render(f"Level: {level}", True, (255, 255, 255))
    screen.blit(level_text, (10, 10))

    paddle.draw(screen)
    ball.draw(screen)
    blocks.draw(screen)
    power_ups.draw(screen)
    explosions.draw(screen)
    explosions.update(dt)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
