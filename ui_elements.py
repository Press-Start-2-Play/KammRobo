import pygame
from config import CYAN, CYAN_DIM

font = None
font_header = None

def init_fonts():
    global font, font_header
    font = pygame.font.SysFont("Segoe UI", 18)
    font_header = pygame.font.SysFont("Segoe UI Semibold", 25)

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
        alpha = 140 if active else (110 if self.hovered else 70)

        pygame.draw.rect(surf, (*CYAN, alpha), surf.get_rect(), border_radius=8)
        pygame.draw.rect(surf, CYAN_DIM, surf.get_rect(), 1, border_radius=8)

        text_surf = font.render(self.text, True, CYAN)
        text_rect = text_surf.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        surf.blit(text_surf, text_rect)
        surface.blit(surf, self.rect.topleft)

def draw_header(surface):
    header_text = "KammRobo"
    text_surf = font_header.render(header_text, True, (255,255,255))
    text_rect = text_surf.get_rect()

    padding_x = 30
    padding_y = 25
    text_rect.topleft = ((padding_x + 15), (padding_y + 60))

    panel_width = text_rect.width + 30
    panel_height = text_rect.height + 20
    panel_rect = pygame.Rect(padding_x, padding_y, panel_width, panel_height)
    panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)

    pygame.draw.rect(panel_surf, (*CYAN, 60), panel_surf.get_rect(), border_radius=8)
    pygame.draw.rect(panel_surf, CYAN_DIM, panel_surf.get_rect(), 1, border_radius=8)
    panel_surf.blit(text_surf, (15, 10))
    surface.blit(panel_surf, panel_rect.topleft)

def draw_status_panel(surface, current_func, speed, is_drifting):
    path_name = current_func.__name__
    drift_text = "DRIFT" if is_drifting else "GRIP"
    speed_mps = speed / 100

    lines = [
        f"PATH   : {path_name}",
        f"SPEED  : {int(speed)} px/s",
        f"VEL    : {speed_mps:.2f} m/s",
        f"STATE  : {drift_text}"
    ]

    text_surfs = [font.render(line, True, CYAN) for line in lines]
    width = max(s.get_width() for s in text_surfs) + 30
    height = sum(s.get_height() for s in text_surfs) + 25

    x, y = 30, 90 
    panel_rect = pygame.Rect(x, y, width, height)
    panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    pygame.draw.rect(panel_surf, (*CYAN, 50), panel_surf.get_rect(), border_radius=8)
    pygame.draw.rect(panel_surf, CYAN_DIM, panel_surf.get_rect(), 1, border_radius=8)

    y_offset = 10
    for surf in text_surfs:
        panel_surf.blit(surf, (15, y_offset))
        y_offset += surf.get_height() + 5

    surface.blit(panel_surf, panel_rect.topleft)