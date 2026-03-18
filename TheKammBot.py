import pygame
import math

# --- INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
path_time = 0.0
dt = 0.016

# --- SCALE ---
# 1 meter = 100 pixels. All physics constants are converted into pixel-space.
PIXELS_PER_METER = 100.0  # tune this to make the robot feel faster/slower

robot_pos = pygame.Vector2(center.x, center.y)
robot_vel = pygame.Vector2(0, 0)

mass = 1.0                    # kg (dimensionless here; cancels out)
co_of_friction = 0.7
g_mps2 = 9.80665              # m/s²
g_pxps2 = g_mps2 * PIXELS_PER_METER   # px/s²  →  980.665 px/s²

# Max friction force in pixel units: F = m * g_px * mu  (px/s² * kg = px-force)
max_frictional_force = mass * g_pxps2 * co_of_friction   # ≈ 686 px-force

# PID Gains — tuned for pixel distances (errors are now 0-300 px, not 0-3 m)
kp = 8.0    # was 0.15 in SI; pixel errors are ~100x larger so gain scales down
ki = 0.5
kd = 1.5

integral_sum = pygame.Vector2(0, 0)
last_error   = pygame.Vector2(0, 0)
last_R = 10000

# --- PATH LOGIC ---
def get_path_info(time_val):
    """
    Returns position (px) and radius of curvature R (px) for the Lissajous path.
    All coordinates are already in pixels — no conversion needed here.
    """
    x   =  center.x + 250 * math.cos(1.2 * time_val)
    y   =  center.y + 180 * math.sin(1.1 * time_val)
    dx  = -250 * 1.2 * math.sin(1.2 * time_val)
    dy  =  180 * 1.1 * math.cos(1.1 * time_val)
    ddx = -250 * (1.2**2) * math.cos(1.2 * time_val)
    ddy = -180 * (1.1**2) * math.sin(1.1 * time_val)

    # R in pixels
    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000
    return pygame.Vector2(x, y), R


def find_closest_t(current_pos, current_t):
    best_t, min_dist = current_t, 999999
    for i in range(50):
        test_t = current_t - 0.5 + (i * 0.02)
        pos_on_path, _ = get_path_info(test_t)
        dist = current_pos.distance_to(pos_on_path)
        if dist < min_dist:
            min_dist = dist
            best_t = test_t
    return best_t


running = True
while running:
    raw_dt = clock.tick(60) / 1000.0
    dt = min(raw_dt, 0.02)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Geometry
    path_time += dt
    target, R = get_path_info(path_time)
    dR_dt = (R - last_R) / dt
    last_R = R

    # 2. PID Force  (pixel-space error → pixel-force)
    error = target - robot_pos
    integral_sum += error * dt
    if integral_sum.length() > 500:           # clamp in px (was 10 in SI)
        integral_sum.scale_to_length(500)
    derivative = (error - last_error) / dt
    desired_force = (kp * error) + (ki * integral_sum) + (kd * derivative)
    last_error = error

    # 3. Friction Circle  (all values in pixel-force units)
    speed = robot_vel.length()                # px/s
    # Centripetal: F = m * v² / R  — v in px/s, R in px → force in px-force
    f_lat_required = (mass * speed**2) / R if R > 0 else 0
    f_lat_actual   = min(f_lat_required, max_frictional_force)

    # Longitudinal budget (Pythagorean)
    long_budget = math.sqrt(max(0, max_frictional_force**2 - f_lat_actual**2))

    # 4. Pre-emptive braking  (pixel-space)
    if dR_dt < 0 and speed > 50:             # speed threshold in px/s (was 10)
        brake_strength = abs(dR_dt) * 0.2
        if speed > 0.1:
            braking_force = -robot_vel.normalize() * min(brake_strength, long_budget)
            desired_force += braking_force

    # 5. Clamp total force to friction circle
    if desired_force.length() > max_frictional_force:
        desired_force.scale_to_length(max_frictional_force)

    # 6. Drift check  (speed threshold in px/s)
    #    v_grip = sqrt(F_max * R / m)  — already in pixel units
    v_grip = math.sqrt(max_frictional_force * R / mass) + 50   # +50 px/s margin
    is_drifting = speed > v_grip
    if is_drifting:
        path_time = find_closest_t(robot_pos, path_time)

    # 7. Physics Integration  (F/m = px/s²,  standard Euler)
    robot_acc  = desired_force / mass
    robot_vel += robot_acc * dt
    robot_pos += robot_vel * dt

    # --- DRAW ---
    screen.fill((30, 30, 30))

    for i in range(200):
        p, _ = get_path_info(path_time - 2 + i * 0.02)
        pygame.draw.circle(screen, (60, 60, 60), (int(p.x), int(p.y)), 1)

    color = (255, 255, 0) if is_drifting else (0, 255, 100)
    pygame.draw.circle(screen, color, (int(robot_pos.x), int(robot_pos.y)), 10)
    pygame.draw.circle(screen, (255, 0, 0), (int(target.x), int(target.y)), 4)

    pygame.display.flip()

pygame.quit()