import copy
import math
import os
import random
import subprocess
import sys

import pygame

WIDTH, HEIGHT = 1000, 563
GROUND = 425
SKY = (248, 223, 8)
ROCK = (208, 79, 46)
RED = (220, 100, 65)
DARK = (140, 50, 30)
GRAVITY = 1800.0
JUMP = 640.0
SPEED = 260.0

core_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(core_dir)
img_dir = os.path.join(root_dir, "img")
audio_dir = os.path.join(root_dir, "audio")
res = {}


def block(x, y, w, h, kind="solid", name=None, visible=True, solid=None, deadly=None, flee=None):
    if solid is None:
        solid = kind == "solid"
    if deadly is None:
        deadly = kind in ("spike", "spike_down", "fake_door")
    return {"x": float(x), "y": float(y), "w": w, "h": h, "kind": kind, "name": name,
            "visible": visible, "solid": solid, "deadly": deadly, "flee": flee,
            "goal": None, "speed": 0.0}


def trap(zone, actions, delay=0.0):
    return {"zone": zone, "actions": actions, "delay": delay, "timer": None, "done": False}


def floor(x1, x2, **kw):
    return block(x1, GROUND, x2 - x1, HEIGHT - GROUND, "solid", **kw)


def spikes(x, w, **kw):
    return block(x, GROUND - 30, w, 30, "spike", **kw)


def ceiling_spikes(x, w, **kw):
    return block(x, 0, w, 40, "spike_down", **kw)


def door(x, **kw):
    return block(x, GROUND - 80, 52, 80, "door", **kw)


def fake_door(x, **kw):
    return block(x, GROUND - 80, 52, 80, "fake_door", **kw)


def can(x, **kw):
    return block(x, GROUND - 56, 30, 56, "can", **kw)


def sodebo(x, **kw):
    return block(x, GROUND - 36, 56, 36, "sodebo", **kw)


def rect(b):
    return pygame.Rect(round(b["x"]), round(b["y"]), b["w"], b["h"])


def lethal(b):
    return b["visible"] and b["deadly"]


def step_block(b, dt, box):
    if b["goal"] is not None:
        gx, gy = b["goal"]
        dx, dy = gx - b["x"], gy - b["y"]
        dist = math.hypot(dx, dy)
        run = b["speed"] * dt
        if dist <= run:
            b["x"], b["y"] = gx, gy
            b["goal"] = None
        else:
            b["x"] += dx / dist * run
            b["y"] += dy / dist * run
    if b["flee"]:
        near, speed, xmin, xmax, jump = b["flee"]
        gap = b["x"] + b["w"] / 2 - box.centerx
        if abs(gap) < near:
            way = 1 if gap >= 0 else -1
            nx = b["x"] + way * speed * dt
            if nx < xmin or nx + b["w"] > xmax:
                if jump:
                    left_c = xmin + b["w"] / 2
                    right_c = xmax - b["w"] / 2
                    if abs(left_c - box.centerx) > abs(right_c - box.centerx):
                        nx = xmin
                    else:
                        nx = xmax - b["w"]
                else:
                    nx = min(max(nx, xmin), xmax - b["w"])
            b["x"] = nx


def draw_block(screen, b):
    if not b["visible"]:
        return
    r = rect(b)
    kind = b["kind"]
    if kind == "solid":
        pygame.draw.rect(screen, ROCK, r)
    elif kind in ("spike", "spike_down"):
        count = max(1, r.w // 20)
        tooth = r.w / count
        for i in range(count):
            left = r.x + i * tooth
            if kind == "spike":
                pts = [(left, r.bottom), (left + tooth / 2, r.top), (left + tooth, r.bottom)]
            else:
                pts = [(left, r.top), (left + tooth / 2, r.bottom), (left + tooth, r.top)]
            pygame.draw.polygon(screen, RED, pts)
            pygame.draw.polygon(screen, DARK, pts, 2)
    elif kind in ("door", "fake_door"):
        screen.blit(res["door"], r)
    elif kind == "can":
        body = pygame.Rect(r.x, r.y + 4, r.w, r.h - 8)
        pygame.draw.rect(screen, (88, 150, 52), body, border_radius=5)
        pygame.draw.rect(screen, (200, 202, 206), (r.x + 3, r.y, r.w - 6, 5), border_radius=2)
        pygame.draw.rect(screen, (200, 202, 206), (r.x + 3, r.bottom - 5, r.w - 6, 5), border_radius=2)
        pygame.draw.ellipse(screen, (244, 236, 90), (r.x + 5, r.y + 18, r.w - 10, 20))
        pygame.draw.ellipse(screen, (60, 110, 36), (r.x + 5, r.y + 18, r.w - 10, 20), 2)
    elif kind == "sodebo":
        pygame.draw.rect(screen, (32, 78, 150), r, border_radius=4)
        pygame.draw.rect(screen, (238, 240, 244), (r.x + 4, r.y + 4, r.w - 8, r.h // 2 - 2), border_radius=3)
        pygame.draw.ellipse(screen, (250, 128, 98), (r.x + 6, r.y + r.h // 2 + 1, 20, 12))
        pygame.draw.ellipse(screen, (250, 128, 98), (r.x + 30, r.y + r.h // 2 + 1, 20, 12))


def load_image(name):
    return pygame.image.load(os.path.join(img_dir, name)).convert_alpha()


def load_sound(name):
    try:
        return pygame.mixer.Sound(os.path.join(audio_dir, name))
    except (pygame.error, FileNotFoundError):
        return None


def reset(g):
    g["blocks"], g["traps"] = copy.deepcopy(g["model"])
    g["box"].midbottom = g["start"]
    g["px"] = float(g["box"].x)
    g["py"] = float(g["box"].y)
    g["vy"] = 0.0
    g["facing"] = 1
    g["moving"] = False
    g["grounded"] = True
    g["flipped"] = False
    g["jump_mult"] = 1.0
    g["time"] = 0.0
    g["dead"] = 0.0
    g["won"] = 0.0
    g["bits"] = []


def die(g):
    if g["dead"] > 0 or g["won"] > 0:
        return
    g["dead"] = 0.45
    if res["die"]:
        res["die"].play()
    cx, cy = g["box"].center
    g["bits"] = [[cx, cy, random.uniform(-260, 260), random.uniform(-520, -80)] for _ in range(14)]


def zone_rect(g, z):
    if isinstance(z, str):
        for b in g["blocks"]:
            if b["name"] == z:
                return rect(b).inflate(4, 4)
        return pygame.Rect(0, 0, 0, 0)
    return pygame.Rect(z)


def apply(g, action):
    kind = action[0]
    if kind == "flip":
        g["flipped"] = not g["flipped"]
    elif kind == "jump":
        g["jump_mult"] = action[1]
    elif kind == "kill":
        die(g)
    elif kind == "tp":
        g["box"].midbottom = (action[1], action[2])
        g["px"] = float(g["box"].x)
        g["py"] = float(g["box"].y)
        g["vy"] = 0.0
    else:
        for b in g["blocks"]:
            if b["name"] != action[1]:
                continue
            if kind == "show":
                b["visible"] = True
            elif kind == "hide":
                b["visible"] = False
            elif kind == "solid":
                b["solid"] = action[2]
            elif kind == "deadly":
                b["deadly"] = action[2]
            elif kind == "move":
                b["goal"] = (b["x"] + action[2], b["y"] + action[3])
                b["speed"] = action[4]


def move(g, dt):
    box = g["box"]
    keys = pygame.key.get_pressed()
    left = keys[pygame.K_LEFT] or keys[pygame.K_q] or keys[pygame.K_a]
    right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    up = keys[pygame.K_UP] or keys[pygame.K_z] or keys[pygame.K_w] or keys[pygame.K_SPACE]
    direction = int(bool(right)) - int(bool(left))
    if g["flipped"]:
        direction = -direction
    g["moving"] = direction != 0
    if direction:
        g["facing"] = direction
    solids = [rect(b) for b in g["blocks"] if b["solid"]]
    g["px"] += direction * SPEED * dt
    g["px"] = max(0.0, min(g["px"], WIDTH - box.w))
    box.x = round(g["px"])
    if direction:
        for r in solids:
            if box.colliderect(r):
                if direction > 0:
                    box.right = r.left
                else:
                    box.left = r.right
                g["px"] = float(box.x)
    on_floor = any(box.move(0, 1).colliderect(r) for r in solids)
    if up and on_floor:
        g["vy"] = -JUMP * g["jump_mult"]
    g["vy"] += GRAVITY * dt
    g["py"] += g["vy"] * dt
    box.y = round(g["py"])
    for r in solids:
        if box.colliderect(r):
            if g["vy"] > 0:
                box.bottom = r.top
            else:
                box.top = r.bottom
            g["vy"] = 0.0
            g["py"] = float(box.y)
    g["grounded"] = any(box.move(0, 1).colliderect(r) for r in solids)


def next_path(number):
    path = os.path.join(core_dir, f"{number + 1}.py")
    if os.path.isfile(path):
        return path
    return os.path.join(root_dir, "menu.py")


def leave(path):
    subprocess.Popen([sys.executable, path])
    pygame.quit()
    sys.exit()


def update(g, dt):
    box = g["box"]
    if g["won"] > 0:
        g["won"] -= dt
        if g["won"] <= 0:
            leave(next_path(g["number"]))
        return
    if g["dead"] > 0:
        g["dead"] -= dt
        for bit in g["bits"]:
            bit[0] += bit[2] * dt
            bit[1] += bit[3] * dt
            bit[3] += GRAVITY * dt
        if g["dead"] <= 0:
            reset(g)
        return
    g["time"] += dt
    for b in g["blocks"]:
        step_block(b, dt, box)
    for b in g["blocks"]:
        if b["solid"] and box.colliderect(rect(b)):
            die(g)
            return
    move(g, dt)
    if box.top > HEIGHT + 60:
        die(g)
        return
    hit = box.inflate(-6, -6)
    for b in g["blocks"]:
        if lethal(b) and hit.colliderect(rect(b).inflate(-6, -4)):
            die(g)
            return
    for t in g["traps"]:
        if t["done"]:
            continue
        if t["timer"] is None and box.colliderect(zone_rect(g, t["zone"])):
            t["timer"] = g["time"] + t["delay"]
        if t["timer"] is not None and g["time"] >= t["timer"]:
            t["done"] = True
            for action in t["actions"]:
                apply(g, action)
    if g["dead"] > 0:
        return
    for b in g["blocks"]:
        if b["kind"] == "door" and b["visible"] and box.colliderect(rect(b).inflate(-16, -8)):
            g["won"] = 0.7
            if res["win"]:
                res["win"].play()
            return


def sprite(g):
    if not g["grounded"]:
        img = res["jump"]
    elif g["moving"]:
        img = res["walk"][int(g["time"] * 10) % len(res["walk"])]
    else:
        img = res["stand"]
    if g["facing"] < 0:
        img = pygame.transform.flip(img, True, False)
    return img


def draw(screen, g):
    screen.fill(SKY)
    for b in g["blocks"]:
        draw_block(screen, b)
    box = g["box"]
    if g["dead"] <= 0:
        screen.blit(sprite(g), (box.centerx - 50, box.bottom - 94))
    else:
        for bit in g["bits"]:
            pygame.draw.rect(screen, DARK, (int(bit[0]), int(bit[1]), 8, 8))
        veil = pygame.Surface((WIDTH, HEIGHT))
        veil.fill(DARK)
        veil.set_alpha(int(110 * g["dead"] / 0.45))
        screen.blit(veil, (0, 0))


def setup(number, start, blocks, traps):
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("RageBait")
    res["screen"] = screen
    res["stand"] = load_image("stand.png")
    res["jump"] = load_image("jump.png")
    res["walk"] = [load_image(f"walk_{i}.png") for i in range(1, 5)]
    res["door"] = pygame.transform.scale(load_image("door.png"), (52, 80))
    res["die"] = load_sound("Assets_Audio_Die Sound.wav")
    res["win"] = load_sound("Assets_Audio_Win Sound Effect 1.wav")
    g = {"number": number, "start": start, "model": (blocks, traps), "box": pygame.Rect(0, 0, 26, 58)}
    reset(g)
    return g


def play(number, start, blocks, traps):
    g = setup(number, start, blocks, traps)
    clock = pygame.time.Clock()
    while True:
        dt = min(clock.tick(60) / 1000.0, 0.033)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    leave(os.path.join(root_dir, "menu.py"))
                if event.key == pygame.K_r:
                    die(g)
        update(g, dt)
        draw(res["screen"], g)
        pygame.display.flip()
