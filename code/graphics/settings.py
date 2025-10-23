import settings
import pygame

pygame.init()

info = pygame.display.Info()


WINDOW_WIDTH = (info.current_w - (info.current_w * 0.00))
WINDOW_HEIGHT = (info.current_h - (info.current_h * 0.05))
# WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720 (320, 180) -> (80, 45)
TILE_SIZE = 64



