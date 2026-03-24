import math
import pygame
from config import CENTER_X, CENTER_Y

center = pygame.Vector2(CENTER_X, CENTER_Y)

def Lissajous(time_val):
    x   =  center.x + 250 * math.cos(1.2 * time_val)
    y   =  center.y + 210 * math.sin(1.1 * time_val)
    dx  = -250 * 1.2 * math.sin(1.2 * time_val)
    dy  =  210 * 1.1 * math.cos(1.1 * time_val)
    ddx = -250 * (1.2**2) * math.cos(1.2 * time_val)
    ddy = -210 * (1.1**2) * math.sin(1.1 * time_val)

    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000
    return pygame.Vector2(x, y), R

def Hypotrochoid(time_val):
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
    scale = 250
    x   = center.x + scale * math.sin(time_val)
    y   = center.y + scale * math.sin(time_val) * math.cos(time_val)
    dx  = scale * math.cos(time_val)
    dy  = scale * (math.cos(time_val)**2 - math.sin(time_val)**2) 
    ddx = -scale * math.sin(time_val)
    ddy = -scale * 2 * math.sin(2 * time_val)

    num = (dx**2 + dy**2)**1.5
    den = abs(dx * ddy - dy * ddx)
    R = num / den if den > 0.1 else 10000
    return pygame.Vector2(x, y), R

def Epitrochoid(time_val):
    t = time_val * 0.67 
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

def find_closest_t(current_pos, current_t, func): 
    best_t, min_dist = current_t, 999999
    for i in range(50):
        test_t = current_t - 0.5 + (i * 0.02)
        pos_on_path, _ = func(test_t)
        dist = current_pos.distance_to(pos_on_path)
        if dist < min_dist:
            min_dist = dist
            best_t = test_t
    return best_t