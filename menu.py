import os
import sys
import math
import subprocess
import pygame

pygame.init()
W, H = 1000, 563
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("RageBait")
clock = pygame.time.Clock()
BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "img")

stand = pygame.image.load(os.path.join(IMG, "stand.png")).convert_alpha()
jump_img = pygame.image.load(os.path.join(IMG, "jump.png")).convert_alpha()
walk_frames = []
for i in range(1, 5):
    wf = pygame.image.load(os.path.join(IMG, f"walk_{i}.png")).convert_alpha()
    walk_frames.append(wf)

char_x = 50.0
char_y = 330.0
ground_y = 330.0
char_speed = 100.0
direction = 1
velocity_y = 0.0
gravity = 1000.0
jump_strength = -400.0
on_ground = True
next_jump = pygame.time.get_ticks() + 1200
frame_counter = 0

ground_color = (208, 79, 46)
ground_pos = [0, 425, W, 150]
button_width = 200
button_height = 65
button_gap = 20
play_base = pygame.Rect((W-button_width)//2, H//2-button_height-button_gap//2, button_width, button_height)
quit_base = pygame.Rect((W-button_width)//2, H//2+button_gap//2, button_width, button_height)
font = pygame.font.Font(None, 38)
title_font = pygame.font.Font(None, 72)
title_main = title_font.render("RAGEBAIT", True, (220, 100, 65))
title_sub = title_font.render("GAME", True, (220, 100, 65))
running = True
play_lift = 0.0
quit_lift = 0.0
play_grow = 0.0
quit_grow = 0.0
pressed = None


def start_game():
    subprocess.Popen([sys.executable, os.path.join(BASE, "core", "1.py")])


while running:
    dt = min(clock.tick(60)/1000.0, 0.05)
    frame_counter += 1
    now = pygame.time.get_ticks()
    mouse = pygame.mouse.get_pos()
    play_hover = play_base.collidepoint(mouse)
    quit_hover = quit_base.collidepoint(mouse)
    ease = min(1.0, dt * 14)
    play_lift += ((-4 if pressed == "play" else 7 if play_hover else 0) - play_lift) * ease
    quit_lift += ((-4 if pressed == "quit" else 7 if quit_hover else 0) - quit_lift) * ease
    play_goal = -8 if pressed == "play" else 14 if play_hover else math.sin(now / 350) * 3
    quit_goal = -8 if pressed == "quit" else 14 if quit_hover else 0
    play_grow += (play_goal - play_grow) * ease
    quit_grow += (quit_goal - quit_grow) * ease
    play = play_base.inflate(int(play_grow), int(play_grow * 0.4)).move(0, -int(play_lift))
    quit_button = quit_base.inflate(int(quit_grow), int(quit_grow * 0.4)).move(0, -int(quit_lift))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                start_game()
                running = False
            elif event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if play_base.collidepoint(event.pos):
                pressed = "play"
            elif quit_base.collidepoint(event.pos):
                pressed = "quit"
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if pressed == "play" and play_base.collidepoint(event.pos):
                start_game()
                running = False
            elif pressed == "quit" and quit_base.collidepoint(event.pos):
                running = False
            pressed = None

    char_x += direction * char_speed * dt
    if char_x <= 0:
        char_x, direction = 0, 1
    elif char_x + stand.get_width() >= W:
        char_x, direction = W-stand.get_width(), -1
    if on_ground and now >= next_jump:
        velocity_y = jump_strength
        on_ground = False
        next_jump = now + 1700
    if not on_ground:
        char_y += velocity_y * dt
        velocity_y += gravity * dt
        if char_y >= ground_y:
            char_y, velocity_y, on_ground = ground_y, 0, True

    screen.fill((248, 223, 8))
    pygame.draw.rect(screen, ground_color, ground_pos)

    if not on_ground and jump_img:
        current_sprite = jump_img
    elif walk_frames and on_ground:
        current_sprite = walk_frames[(frame_counter // 8) % len(walk_frames)]
    else:
        current_sprite = stand

    if direction < 0:
        current_sprite = pygame.transform.flip(current_sprite, True, False)

    screen.blit(current_sprite, (round(char_x), round(char_y)))

    pygame.draw.rect(screen, (196, 100, 65) if play_hover else (220, 100, 65), play, border_radius=12)
    pygame.draw.rect(screen, (196, 100, 65) if quit_hover else (220, 100, 65), quit_button, border_radius=12)
    play_text = font.render("Jouer", True, (248, 223, 8))
    quit_text = font.render("Quitter", True, (248, 223, 8))
    screen.blit(play_text, play_text.get_rect(center=play.center))
    screen.blit(quit_text, quit_text.get_rect(center=quit_button.center))
    screen.blit(title_main, title_main.get_rect(center=(W//2, play_base.top-75)))
    screen.blit(title_sub, title_sub.get_rect(center=(W//2, play_base.top-35)))
    pygame.display.flip()

pygame.quit()
sys.exit()
