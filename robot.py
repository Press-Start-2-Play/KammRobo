import pygame
import math
from config import PIXELS_PER_METER
from paths import find_closest_t, Lissajous, Hypotrochoid, Epitrochoid, Figure_Eight

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
        self.integral_sum_mag = 0
        self.last_error   = pygame.Vector2(0, 0)
        self.last_R = 10000
        self.heading = 0
        self.stanley_gain = 4.0*mass
        self.wheelbase = 50

    def Heading_update(self):
        if self.vel.length() > 0:
            self.heading = math.atan2(self.vel.y, self.vel.x)

    def PID_update(self, dt, path_time, current_func):
        target, R = current_func(path_time)
        
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

        # Prevent division by zero on very first frame
        dR_dt = (R - self.last_R) / dt if dt > 0 else 0
        self.last_R = R
        
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

        #Update heading
        self.Heading_update()

        return path_time, speed, is_drifting, target
    
    def Stanley_steering_angle(self, path_time, current_func):
        # --- Get closest point ---
        path_time = find_closest_t(self.pos, path_time, current_func)
        p1, _ = current_func(path_time)
        
        # --- Lookahead for tangent ---
        Ld = 0.01
        p2, _ = current_func(path_time + Ld)

        # --- Path direction & Tangent angle ---
        path_vec = p2 - p1
        tangent_angle = math.atan2(path_vec.y, path_vec.x)

        # --- Heading error ---
        heading_error = tangent_angle - self.heading
        # Wrap to pi (-pi to pi)
        heading_error = (heading_error + math.pi) % (2 * math.pi) - math.pi

        # --- Cross-track error ---
        # error_vec is from robot to path
        error_vec = p1 - self.pos 
        
        # In a 2D plane, cross product of path vector and error vector gives perpendicular distance.
        # Note: Pygame's y-axis is inverted. This math assumes standard atan2 logic.
        path_dir = path_vec.normalize() if path_vec.length() > 0 else pygame.Vector2(1, 0)
        
        # e is the perpendicular distance (cross product of path direction and error vector)
        e = (error_vec.y * path_dir.x) - (error_vec.x * path_dir.y)

        # --- Stanley term ---
        # Prevent division by zero
        v = max(self.vel.length(), 1.0) 

        # The correction angle
        correction = math.atan2(self.stanley_gain * e, v)

        # Final steering angle (bounded to realistic steering limits, e.g., +/- 30 degrees)
        max_steer = math.radians(30)
        steering_angle = heading_error + correction
        steering_angle = max(-max_steer, min(steering_angle, max_steer))

        return steering_angle, path_time

    def Stanley_Controller(self, dt, path_time, current_func):
        target, _ = current_func(path_time) 
        
        # --- Get steering ---
        steering_angle, path_time = self.Stanley_steering_angle(path_time, current_func)

        # --- Speed control (Longitudinal) ---
        desired_speed = 200  
        speed = self.vel.length()
        speed_error = desired_speed - speed
        
        # Simple longitudinal acceleration
        accel = 5.0 * speed_error 
        
        # --- Kinematic Bicycle Model Update ---
        # 1. Update speed based on acceleration
        new_speed = speed + (accel * dt)
        new_speed = max(0, new_speed) # Prevent going backwards for basic Stanley
        
        # 2. Update heading based on steering angle and wheelbase
        # Rate of heading change: (v / L) * tan(delta)
        # Assuming you add `self.wheelbase = 50` (or appropriate pixel size) in __init__
        wheelbase = getattr(self, 'wheelbase', 50) 
        heading_rate = (new_speed / wheelbase) * math.tan(steering_angle)
        self.heading += heading_rate * dt
        
        # 3. Update velocity vector based on new heading and speed
        self.vel.x = new_speed * math.cos(self.heading)
        self.vel.y = new_speed * math.sin(self.heading)
        
        # 4. Update position
        self.pos += self.vel * dt

        return path_time, new_speed, False, target


