from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "sprites"
CHARTS = ROOT / "charts"
FONTS = ROOT / "fonts"
MUSIC = ROOT / "music"

SIZE = (480, 270)
LANES = (145, 174, 203, 232, 261)
KEYS = (pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g)
COLORS = ("#99f634", "#ed252e", "#ffe046", "#46b8dd", "#f68b43")
# sprite da nota de cada corda, na mesma ordem de COLORS
NOTE_SPRITES = ("greenpoint", "redpoint", "yellowpoint", "bluepoint", "orangepoint")
