import pygame
import math

# --- INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 1000, 700 # Made it slightly larger for the UI
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('KammRobo: Telemetry Edition')

# Colors
CLR_BG = (10, 12, 15)
CLR_PATH = (40, 45, 50)
CLR_ROBOT = (0, 255, 200)
CLR_DRIFT = (255, 50, 50)
CLR_TEXT = (200, 210, 220)

center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
path_time = 0.0
PIXELS_PER_METER = 100.0

# --- ROBOT STATE ---
mass = 1.5  # Balanced mass
robot_pos = pygame.Vector2(center.x, center.y)
robot_vel = pygame.Vector2(0, 0)
trail = []  # List of (pos, is_drifting)

# Physics Constants
co_of_friction = 0.7
g_pxps2 = 9.80665 * PIXELS_PER_METER
max_frictional_force = mass * g_pxps2 * co_of_friction

# PID Tuning - Slightly higher D for high mass stability
kp = 35.0 * mass
ki = 1.2 * mass
kd = 18.0 * mass
integral_sum = pygame.Vector2(0, 0)
last_error = pygame.Vector2(0, 0)

font_small = pygame.font.SysFont("Consolas", 18)
font_large = pygame.font.SysFont("Consolas", 28, bold=True)

def get_path_info(t):
    x = center.x + 300 * math.cos(1.2 * t)
    y = center.y + 220 * math.sin(1.1 * t)
    dx = -300 * 1.2 * math.sin(1.2 * t)
    dy = 220 * 1.1 * math.cos(1.1 * t)
    ddx = -300 * (1.2**2) * math.cos(1.2 * t)
    ddy = -220 * (1.1**2) * math.sin(1.1 * t)
    
    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000
    return pygame.Vector2(x, y), R, pygame.Vector2(dx, dy)

def draw_glow_circle(surf, color, pos, radius):
    for i in range(3): # Simple layered glow
        alpha = 100 // (i + 1)
        s = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (radius * 2, radius * 2), radius + (i * 0.8))
        surf.blit(s, (pos[0] - radius * 2, pos[1] - radius * 2))

running = True
while running:
    dt = min(clock.tick(60) / 1000.0, 0.03)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    path_time += dt
    target, R, target_vel = get_path_info(path_time)

    # PID Calculation
    error = target - robot_pos
    integral_sum += error * dt
    if integral_sum.length() > 500: integral_sum.scale_to_length(500)
    derivative = (error - last_error) / dt
    desired_force = (kp * error) + (ki * integral_sum) + (kd * derivative)
    last_error = error

    # Friction Budget Logic
    speed = robot_vel.length()
    f_centripetal = (mass * speed**2) / R if R > 0 else 0
    f_lat_actual = min(f_centripetal, max_frictional_force)
    f_long_budget = math.sqrt(max(0, max_frictional_force**2 - f_lat_actual**2))

    if desired_force.length() > max_frictional_force:
        desired_force.scale_to_length(max_frictional_force)

    # Physics Update
    v_grip = math.sqrt(max_frictional_force * R / mass)
    is_drifting = speed > v_grip
    
    robot_acc = desired_force / mass
    robot_vel += robot_acc * dt
    robot_pos += robot_vel * dt

    # Add to trail
    trail.append((pygame.Vector2(robot_pos), is_drifting))
    if len(trail) > 100: trail.pop(0)

    # --- DRAWING ---
    screen.fill(CLR_BG)

    # 1. Draw Static Path
    for i in range(0, 500, 2):
        p, _, _ = get_path_info(path_time - 5 + i * 0.02)
        pygame.draw.circle(screen, CLR_PATH, (int(p.x), int(p.y)), 1)

    # 2. Draw Motion Trail
    if len(trail) > 2:
        for i in range(len(trail)-1):
            t_color = CLR_DRIFT if trail[i][1] else CLR_ROBOT
            alpha = int(255 * (i / len(trail)))
            pygame.draw.line(screen, (*t_color, alpha), trail[i][0], trail[i+1][0], 2)

    # 3. Draw Robot and Target
    color = CLR_DRIFT if is_drifting else CLR_ROBOT
    draw_glow_circle(screen, color, robot_pos, 8)
    pygame.draw.circle(screen, (255, 255, 255), target, 3, 1)

    # 4. TELEMETRY UI (The "Aesthetic" part)
    ui_bg = pygame.Surface((220, 160), pygame.SRCALPHA)
    ui_bg.fill((20, 25, 30, 180))
    screen.blit(ui_bg, (20, 20))
    
    txt_kamm = font_large.render("KAMM-ROBO OS", True, CLR_ROBOT)
    screen.blit(txt_kamm, (30, 30))
    
    vel_text = font_small.render(f"VELOCITY: {speed/PIXELS_PER_METER:.2f} m/s", True, CLR_TEXT)
    force_text = font_small.render(f"LAT FORCE: {f_lat_actual:.0f} N", True, CLR_TEXT)
    status_text = font_small.render("STATUS: DRIFTING" if is_drifting else "STATUS: GRIP", True, color)
    
    screen.blit(vel_text, (30, 70))
    screen.blit(force_text, (30, 95))
    screen.blit(status_text, (30, 120))

    # 5. Visual Friction Circle (Bottom Left)
    circle_center = pygame.Vector2(100, HEIGHT - 100)
    pygame.draw.circle(screen, CLR_PATH, circle_center, 60, 1)
    # Draw actual force vector inside the circle
    force_vec = desired_force / max_frictional_force * 60
    pygame.draw.line(screen, color, circle_center, circle_center + force_vec, 3)
    pygame.draw.circle(screen, color, circle_center + force_vec, 4)

    pygame.display.flip()

pygame.quit()