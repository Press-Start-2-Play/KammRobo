import pygame
import math
from config import PIXELS_PER_METER
from paths import find_closest_t

class Robot:
    def __init__(self, mass, start_pos):
        self.mass = mass
        self.pos = pygame.Vector2(start_pos)
        self.vel = pygame.Vector2(0, 0)

        # Physics Constants
        self.co_of_friction = 0.7
        self.g_pxps2 = 9.80665 * PIXELS_PER_METER
        self.max_frictional_force = self.mass * self.g_pxps2 * self.co_of_friction

        # PID Gains
        self.kp = 130 * self.mass   
        self.ki = 10 * self.mass
        self.kd = 40 * self.mass
        self.integral_sum = pygame.Vector2(0, 0)
        self.last_error   = pygame.Vector2(0, 0)
        self.last_R = 10000

    def update(self, dt, path_time, current_func):
        target, R = current_func(path_time)
        
        # Prevent division by zero on very first frame
        dR_dt = (R - self.last_R) / dt if dt > 0 else 0
        self.last_R = R

        # --- PID Force ---
        error = target - self.pos
        self.integral_sum += error * dt
        if self.integral_sum.length() > 10000:     
            self.integral_sum.scale_to_length(10000)
            
        derivative = (error - self.last_error) / dt if dt > 0 else pygame.Vector2(0, 0)
        desired_force = (self.kp * error) + (self.ki * self.integral_sum) + (self.kd * derivative)
        self.last_error = error

        # --- Friction Circle ---
        speed = self.vel.length()   # px/s
        f_centripetal = (self.mass * speed**2) / R if R > 0 else 0
        f_lat_actual   = min(f_centripetal, self.max_frictional_force)

        # Longitudinal budget (Pythagorean)
        f_long = math.sqrt(max(0, self.max_frictional_force**2 - f_lat_actual**2))

        # Pre-emptive braking 
        if dR_dt < 0 and speed > 380:    
            brake_strength = abs(dR_dt) * 0.2  
            if speed > 0: # Guard against normalizing a zero vector
                braking_force = -self.vel.normalize() * min(brake_strength, f_long)
                desired_force += braking_force

        # Clamp total force
        if desired_force.length() > self.max_frictional_force:
            desired_force.scale_to_length(self.max_frictional_force)

        # --- Drift check ---
        v_grip = math.sqrt(self.max_frictional_force * R / self.mass)
        is_drifting = speed > v_grip
        if is_drifting:
            path_time = find_closest_t(self.pos, path_time, current_func)

        # --- Physics Integration ---
        robot_acc  = desired_force / self.mass
        self.vel += robot_acc * dt
        self.pos += self.vel * dt

        return path_time, speed, is_drifting, target