'''
Test Code For KammRobo
'''

import pygame
import math

# --- INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('KammRobo')

center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
path_time = 0.0

# --- SCALE ---
PIXELS_PER_METER = 100.0

# Robot State
mass = 1
robot_pos = pygame.Vector2(center.x, center.y)
robot_vel = pygame.Vector2(0, 0)

# Physics Constants
co_of_friction = 0.7
g_mps2 = 9.80665
g_pxps2 = g_mps2 * PIXELS_PER_METER
max_frictional_force = mass * g_pxps2 * co_of_friction

# PID Gains
kp = 130 * mass
ki = 10 * mass
kd = 40 * mass

integral_sum = pygame.Vector2(0, 0)
last_error = pygame.Vector2(0, 0)
last_R = 10000

# Colors
CLR_BG = (10, 12, 15)
CLR_TRACK = (0, 255, 200)
CYAN = (0, 220, 220)
CYAN_DIM = (0, 180, 180)

font = pygame.font.SysFont("Segoe UI", 18)

# =========================
# PATH FUNCTIONS
# =========================
def Hypotrochoid(t):
    k = (200 - 65) / 65
    x = center.x + 135 * math.cos(t) + 100 * math.cos(k * t)
    y = center.y + 135 * math.sin(t) - 100 * math.sin(k * t)

    dx = -135 * math.sin(t) - 100 * k * math.sin(k * t)
    dy = 135 * math.cos(t) - 100 * k * math.cos(k * t)

    ddx = -135 * math.cos(t) - 100 * (k**2) * math.cos(k * t)
    ddy = -135 * math.sin(t) + 100 * (k**2) * math.sin(k * t)

    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000

    return pygame.Vector2(x, y), R


def Figure_Eight(t):
    scale = 250
    x = center.x + scale * math.sin(t)
    y = center.y + scale * math.sin(t) * math.cos(t)

    dx = scale * math.cos(t)
    dy = scale * (math.cos(t)**2 - math.sin(t)**2)

    ddx = -scale * math.sin(t)
    ddy = -scale * 2 * math.sin(2 * t)

    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000

    return pygame.Vector2(x, y), R


def Epitrochoid(t):
    x = center.x + 120 * math.cos(t) - 80 * math.cos(6 * t)
    y = center.y + 120 * math.sin(t) - 80 * math.sin(6 * t)

    dx = -120 * math.sin(t) + 480 * math.sin(6 * t)
    dy = 120 * math.cos(t) - 480 * math.cos(6 * t)

    ddx = -120 * math.cos(t) + 2880 * math.cos(6 * t)
    ddy = -120 * math.sin(t) + 2880 * math.sin(6 * t)

    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000

    return pygame.Vector2(x, y), R


def Flower(t):
    r = 180 + 60 * math.sin(5 * t)
    x = r * math.cos(t)
    y = r * math.sin(t)

    dx = (60 * 5 * math.cos(5*t)) * math.cos(t) - r * math.sin(t)
    dy = (60 * 5 * math.cos(5*t)) * math.sin(t) + r * math.cos(t)

    ddx = -r * math.cos(t)
    ddy = -r * math.sin(t)

    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000

    return pygame.Vector2(center.x + x, center.y + y), R


# =========================
# BUTTON CLASS
# =========================
class CyberButton:
    def __init__(self, text, x, y, w, h, func):
        self.text = text
        self.func = func

        self.base_rect = pygame.Rect(x, y, w, h)
        self.rect = self.base_rect.copy()

        self.scale = 1.0
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.base_rect.collidepoint(mouse_pos)

        target_scale = 1.06 if self.hovered else 1.0
        self.scale += (target_scale - self.scale) * 0.2

        center = self.base_rect.center
        self.rect.width = int(self.base_rect.width * self.scale)
        self.rect.height = int(self.base_rect.height * self.scale)
        self.rect.center = center

    def draw(self, surface, active=False):
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        if active:
            alpha = 140
        else:
            alpha = 110 if self.hovered else 70

        pygame.draw.rect(surf, (*CYAN, alpha), surf.get_rect(), border_radius=8)
        pygame.draw.rect(surf, CYAN_DIM, surf.get_rect(), 1, border_radius=8)

        text_surf = font.render(self.text, True, CYAN)
        text_rect = text_surf.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        surf.blit(text_surf, text_rect)

        surface.blit(surf, self.rect.topleft)


# =========================
# BUTTON SETUP
# =========================
BUTTON_W = 200
BUTTON_H = 42
PADDING = 18

start_x = WIDTH - BUTTON_W - 30
start_y = 40

button_data = [
    ("Hypotrochoid", Hypotrochoid),
    ("Figure_Eight", Figure_Eight),
    ("Epitrochoid", Epitrochoid),
    ("Flower", Flower),
]

buttons = []
for i, (label, func_ref) in enumerate(button_data):
    x = start_x
    y = start_y + i * (BUTTON_H + PADDING)
    buttons.append(CyberButton(label, x, y, BUTTON_W, BUTTON_H, func_ref))

# Active function
current_func = Hypotrochoid
func = current_func

# =========================
# MAIN LOOP
# =========================
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    dt = min(clock.tick(60) / 1000.0, 0.02)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in buttons:
                if btn.base_rect.collidepoint(mouse_pos):
                    current_func = btn.func
                    func = current_func
                    path_time = 0

    path_time += dt
    target, R = func(path_time)

    # Simple movement (keeping your physics intact)
    direction = (target - robot_pos)
    if direction.length() > 1:
        robot_vel += direction.normalize() * 200 * dt

    robot_pos += robot_vel * dt
    robot_vel *= 0.95  # damping

    # --- DRAW ---
    screen.fill(CLR_BG)

    for btn in buttons:
        btn.draw(screen, active=(btn.func == current_func))

    # Draw path
    for i in range(400):
        p, _ = func(path_time - 2 + i * 0.02)
        pygame.draw.circle(screen, CLR_TRACK, (int(p.x), int(p.y)), 1)

    pygame.draw.circle(screen, (0, 255, 100), (int(robot_pos.x), int(robot_pos.y)), 10)
    pygame.draw.circle(screen, (255, 255, 255), (int(target.x), int(target.y)), 4)

    pygame.display.flip()

pygame.quit()