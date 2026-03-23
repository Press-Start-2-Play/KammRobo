import pygame
import math
import time

# --- INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 1266, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('KammRobo')

center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
path_time = 0.0
dt = 0.016


# --- SCALE ---
PIXELS_PER_METER = 100.0

# Robot State
mass = 2
robot_pos = pygame.Vector2(center.x , center.y)
robot_vel = pygame.Vector2(0, 0)

# Physics Constants
co_of_friction = 0.7
g_mps2 = 9.80665  # m/s²
g_pxps2 = g_mps2 * PIXELS_PER_METER   # px/s²  →  980.665 px/s²
max_frictional_force = mass * g_pxps2 * co_of_friction   #686 px-force

# PID Gains — Dynamically tuned for response to diifferent masses
kp = 130 * mass   
ki = 10 *mass
kd = 40* mass
integral_sum = pygame.Vector2(0, 0)
last_error   = pygame.Vector2(0, 0)
last_R = 10000

# # --- PATH LOGIC ---
def Lissajous(time_val):
    #Returns position (px) and radius of curvature R (px) for the Lissajous path.
    x   =  center.x + 250 * math.cos(1.2 * time_val)#250
    y   =  center.y + 210 * math.sin(1.1 * time_val)#180
    dx  = -250 * 1.2 * math.sin(1.2 * time_val)
    dy  =  210 * 1.1 * math.cos(1.1 * time_val)
    ddx = -250 * (1.2**2) * math.cos(1.2 * time_val)
    ddy = -210 * (1.1**2) * math.sin(1.1 * time_val)

    # R in pixels
    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000
    return pygame.Vector2(x, y), R

def Hypotrochoid(time_val):
    # R=200, r=65, d=100 (Adjust these for different spiro-effects)
    # x = (R - r) * cos(t) + d * cos(((R - r) / r) * t)
    
    k = (200 - 65) / 65
    x   = center.x + 135 * math.cos(time_val) + 100 * math.cos(k * time_val)
    y   = center.y + 135 * math.sin(time_val) - 100 * math.sin(k * time_val)
    
    dx  = -135 * math.sin(time_val) - 100 * k * math.sin(k * time_val)
    dy  =  135 * math.cos(time_val) - 100 * k * math.cos(k * time_val)
    
    ddx = -135 * math.cos(time_val) - 100 * (k**2) * math.cos(k * time_val)
    ddy = -135 * math.sin(time_val) + 100 * (k**2) * math.sin(k * time_val)

    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000
    return pygame.Vector2(x, y), R

def Figure_Eight(time_val):
    # Simple and clean figure-eight
    scale = 250
    x   = center.x + scale * math.sin(time_val)
    y   = center.y + scale * math.sin(time_val) * math.cos(time_val)
    
    dx  = scale * math.cos(time_val)
    dy  = scale * (math.cos(time_val)**2 - math.sin(time_val)**2) # cos(2t)
    
    ddx = -scale * math.sin(time_val)
    ddy = -scale * 2 * math.sin(2 * time_val)

    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000
    return pygame.Vector2(x, y), R

def Epitrochoid(time_val):
    t = time_val * 0.67  # slow it down (adjust 0.3 → smaller = more clustering)

    x   = center.x + 120 * math.cos(t) - 80 * math.cos(4 * t)
    y   = center.y + 120 * math.sin(t) - 80 * math.sin(4 * t)

    dx  = -120 * math.sin(t) + 320 * math.sin(4 * t)
    dy  =  120 * math.cos(t) - 320 * math.cos(4 * t)

    ddx = -120 * math.cos(t) + 1280 * math.cos(4 * t)
    ddy = -120 * math.sin(t) + 1280 * math.sin(4 * t)

    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000

    return pygame.Vector2(x, y), R

def find_closest_t(current_pos, current_t, func): #
    best_t, min_dist = current_t, 999999
    for i in range(50):
        test_t = current_t - 0.5 + (i * 0.02)
        pos_on_path, _ = func(test_t)
        dist = current_pos.distance_to(pos_on_path)
        if dist < min_dist:
            min_dist = dist
            best_t = test_t
    return best_t

#Aesthetics


# Colors
CLR_BG = (10, 12, 15)
CLR_PATH = (40, 45, 50)
CLR_TRACK = (0, 255, 200)
CLR_DRIFT = (255, 50, 50)
CLR_TEXT = (200, 210, 220)
CYAN = (0, 220, 220)
CYAN_DIM = (0, 180, 180)

# Font
font = pygame.font.SysFont("Segoe UI", 18)
font_header = pygame.font.SysFont("Segoe UI Semibold", 25)

# AI UI Buttons 
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


# BUTTON SETUP

BUTTON_W = 200
BUTTON_H = 42
PADDING = 18

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

# Active function
current_func = Hypotrochoid
func = current_func

# HEADER FUNCTION

def draw_header(surface):
    header_text = "KammRobo"

    # Render text
    text_surf = font_header.render(header_text, True, (255,255,255))
    text_rect = text_surf.get_rect()

    # Position (top-left, aligned nicely)
    padding_x = 30
    padding_y = 25
    text_rect.topleft = ((padding_x + 15), (padding_y + 60))

    # Background panel (glass effect)
    panel_width = text_rect.width + 30
    panel_height = text_rect.height + 20

    panel_rect = pygame.Rect(padding_x, padding_y, panel_width, panel_height)

    panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)

    # Subtle transparent background
    pygame.draw.rect(panel_surf, (*CYAN, 60), panel_surf.get_rect(), border_radius=8)

    # Thin border
    pygame.draw.rect(panel_surf, CYAN_DIM, panel_surf.get_rect(), 1, border_radius=8)

    # Blit text onto panel
    panel_surf.blit(text_surf, (15, 10))

    # Draw to screen
    surface.blit(panel_surf, panel_rect.topleft)


# TELEMETRY PANEL FUNCTION

def draw_status_panel(surface, current_func, speed, is_drifting):
    # --- TEXT CONTENT ---
    path_name = current_func.__name__
    drift_text = "DRIFT" if is_drifting else "GRIP"

    speed_mps = speed / 100

    lines = [
    f"PATH   : {path_name}",
    f"SPEED  : {int(speed)} px/s",
    f"VEL    : {speed_mps:.2f} m/s",
    f"STATE  : {drift_text}"
    ]

    # --- RENDER TEXT ---
    text_surfs = [font.render(line, True, CYAN) for line in lines]

    # --- PANEL SIZE ---
    width = max(s.get_width() for s in text_surfs) + 30
    height = sum(s.get_height() for s in text_surfs) + 25

    # Position: just below header
    x = 30
    y = 90   # sits nicely under header

    panel_rect = pygame.Rect(x, y, width, height)
    panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    # --- BACKGROUND (slightly lighter than header) ---
    pygame.draw.rect(panel_surf, (*CYAN, 50), panel_surf.get_rect(), border_radius=8)

    # --- BORDER ---
    pygame.draw.rect(panel_surf, CYAN_DIM, panel_surf.get_rect(), 1, border_radius=8)

    # --- TEXT PLACEMENT ---
    y_offset = 10
    for surf in text_surfs:
        panel_surf.blit(surf, (15, y_offset))
        y_offset += surf.get_height() + 5

    # --- DRAW ---
    surface.blit(panel_surf, panel_rect.topleft)



'''

MAIN LOOOOPPPPP !!!!!

'''

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    raw_dt = clock.tick(60) / 1000.0
    dt = min(raw_dt, 0.02)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Click detection
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in buttons:
                if btn.base_rect.collidepoint(mouse_pos):
                    current_func = btn.func
                    func = current_func

    path_time += dt
    target, R = func(path_time)
    dR_dt = (R - last_R) / dt
    last_R = R

    # PID Force  
    error = target - robot_pos
    integral_sum += error * dt
    if integral_sum.length() > 10000:     
        integral_sum.scale_to_length(10000)
    derivative = (error - last_error) / dt
    desired_force = (kp * error) + (ki * integral_sum) + (kd * derivative)
    last_error = error

    # Friction Circle
    speed = robot_vel.length()   # px/s
    # Centripetal: F = m * v² / R  — v in px/s, R in px → force in px-force
    f_centripetal = (mass * speed**2) / R if R > 0 else 0
    f_lat_actual   = min(f_centripetal, max_frictional_force)

    # Longitudinal budget (Pythagorean)
    f_long = math.sqrt(max(0, max_frictional_force**2 - f_lat_actual**2))

    # Pre-emptive braking 
    if dR_dt < 0 and speed > 380:     # should experiment with the speed
        brake_strength = abs(dR_dt) * 0.2  
        braking_force = -robot_vel.normalize() * min(brake_strength, f_long)
        desired_force += braking_force

    # Clamp total force
    if desired_force.length() > max_frictional_force:
        desired_force.scale_to_length(max_frictional_force)

    # Drift check  (speed threshold)
    #    v_grip = sqrt(F_max * R / m)  — already in pixel units
    v_grip = math.sqrt(max_frictional_force * R / mass)
    is_drifting = speed > v_grip
    if is_drifting:
        path_time = find_closest_t(robot_pos, path_time, func)

    # Physics Integration  (F/m = px/s²,  standard Euler)
    robot_acc  = desired_force / mass
    robot_vel += robot_acc * dt
    robot_pos += robot_vel * dt

     # Update
    for btn in buttons:
        btn.update(mouse_pos)

    # --- DRAW ---
    
    screen.fill(CLR_BG)
    draw_header(screen)
    draw_status_panel(
        screen,
        current_func,
        speed,
        is_drifting
    )
    
    for btn in buttons:
        btn.draw(screen)

    for i in range(500):
        p, _ = func(path_time - 2 + i * 0.02)
        pygame.draw.circle(screen, (CLR_TRACK), (int(p.x), int(p.y)), 1)

    color = (255, 255, 0) if is_drifting else (0, 255, 100)
    pygame.draw.circle(screen, color, (int(robot_pos.x), int(robot_pos.y)), 10)
    pygame.draw.circle(screen, (120, 120, 120), (int(target.x), int(target.y)), 4)
    

    pygame.display.flip()


pygame.quit()