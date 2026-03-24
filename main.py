import pygame
from config import WIDTH, HEIGHT, CENTER_X, CENTER_Y, CLR_BG, CLR_TRACK
from paths import Hypotrochoid, Figure_Eight, Epitrochoid, Lissajous
from ui_elements import CyberButton, draw_header, draw_status_panel, init_fonts
from robot import Robot

# --- INITIALIZATION ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('KammRobo')
init_fonts() 

# --- BUTTON SETUP ---
BUTTON_W, BUTTON_H, PADDING = 200, 42, 18
start_x = WIDTH - BUTTON_W - 30
start_y = 40

button_data = [
    ("Hypotrochoid", Hypotrochoid),
    ("Figure Eight", Figure_Eight),
    ("Epitrochoid", Epitrochoid),
    ("Lissajous", Lissajous),
]

buttons = []
for i, (label, func_ref) in enumerate(button_data):
    x = start_x
    y = start_y + i * (BUTTON_H + PADDING)
    buttons.append(CyberButton(label, x, y, BUTTON_W, BUTTON_H, func_ref))

# --- INSTANCE SETUP ---
current_func = Hypotrochoid
path_time = 0.0
robot = Robot(mass=2, start_pos=(CENTER_X, CENTER_Y))

# --- MAIN LOOP ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    raw_dt = clock.tick(60) / 1000.0
    dt = min(raw_dt, 0.02)

    # 1. Input Validation
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in buttons:
                if btn.base_rect.collidepoint(mouse_pos):
                    current_func = btn.func

    # 2. Logic Updates
    path_time += dt
    path_time, speed, is_drifting, target = robot.update(dt, path_time, current_func)

    for btn in buttons:
        btn.update(mouse_pos)

    # 3. Drawing
    screen.fill(CLR_BG)
    draw_header(screen)
    draw_status_panel(screen, current_func, speed, is_drifting)
    
    # Notice we can pass `active` to the button now to show which path is selected
    for btn in buttons:
        btn.draw(screen, active=(btn.func == current_func))

    # Draw path preview
    for i in range(500):
        p, _ = current_func(path_time - 2 + i * 0.02)
        pygame.draw.circle(screen, CLR_TRACK, (int(p.x), int(p.y)), 1)

    # Draw Target and Robot
    pygame.draw.circle(screen, (120, 120, 120), (int(target.x), int(target.y)), 4)
    
    color = (255, 255, 0) if is_drifting else (0, 255, 100)
    pygame.draw.circle(screen, color, (int(robot.pos.x), int(robot.pos.y)), 10)

    pygame.display.flip()

pygame.quit()