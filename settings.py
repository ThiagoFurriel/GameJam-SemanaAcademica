from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "sprites"
CHARTS = ROOT / "charts"
FONTS = ROOT / "fonts"
MUSIC = ROOT / "music"

SIZE = (480, 270)
LANES = (145, 174, 203, 232, 261)
MOVE_UP_KEYS = (pygame.K_UP, pygame.K_w)
MOVE_DOWN_KEYS = (pygame.K_DOWN, pygame.K_s)
COLORS = ("#99f634", "#ed252e", "#ffe046", "#46b8dd", "#f68b43")
# sprite da nota de cada corda, na mesma ordem de COLORS
NOTE_SPRITES = ("greenpoint", "redpoint", "yellowpoint", "bluepoint", "orangepoint")
