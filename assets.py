import pygame

from settings import ASSETS


def load_image(name):
    # convert_alpha() deixa o blit bem mais rápido; exige o display já criado.
    return pygame.image.load(str(ASSETS / f"{name}.png")).convert_alpha()


def load_god_portraits(name, height):
    """os mesmos 4 quadros, cortados da cabeça até `height`, na escala original da arte.

    sem reescalar: os pixels ficam exatamente como a artista desenhou.
    """
    sheet = load_image(name)
    return [sheet.subsurface((i * 144, 0, 144, height)).copy() for i in range(4)]


def load_god_frames(name):
    # as folhas dos deuses têm 4 quadros de 144x313 lado a lado.
    sheet = load_image(name)
    return [
        pygame.transform.scale(sheet.subsurface((i * 144, 0, 144, 313)), (120, 261))
        for i in range(4)
    ]
