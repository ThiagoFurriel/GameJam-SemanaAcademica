import functools

import pygame

from settings import FONTS

TEXT = "#f4eefc"
SHADOW = "#0c0912"
ACCENT = "#ffe046"
BORDER = "#f4eefc"
DIVIDER = "#4b4553"
OFF = "#6e6676"
PANEL = (8, 6, 12, 184)
KEY_FACE = "#f4eefc"
KEY_SHADE = "#8a6fa0"
KEY_TEXT = "#1a0a22"
BLINK_PERIOD = 1.0
BLINK_ON = 0.7


@functools.cache
def font(size):
    # a press start 2p é desenhada numa grade de 8px: só 8 e 16 ficam nítidos,
    # outros tamanhos distorcem os pixels das letras
    return pygame.font.Font(str(FONTS / "PressStart2P-Regular.ttf"), size)


def draw_text(canvas, typeface, text, color, alpha=255, **position):
    # sombra de 1px pra o texto não sumir em cima dos cenários claros
    rect = None
    for offset, fill in (((1, 1), SHADOW), ((0, 0), color)):
        label = typeface.render(text, False, fill)
        label.set_alpha(alpha)
        rect = label.get_rect(**position).move(offset)
        canvas.blit(label, rect)
    return rect


def draw_shade(canvas, rect, rgba):
    # pygame.draw ignora alpha direto no canvas, então a cor translúcida vai numa superfície própria
    shade = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    shade.fill(rgba)
    canvas.blit(shade, rect)


def draw_panel(canvas, rect):
    rect = pygame.Rect(rect)
    width, height = rect.size
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.fill(PANEL, panel.get_rect().inflate(-2, -2))
    # as bordas param 1px antes de cada canto: é o chanfro que deixa o painel com cara de pixel art
    for start, end in (
        ((1, 0), (width - 2, 0)),
        ((1, height - 1), (width - 2, height - 1)),
        ((0, 1), (0, height - 2)),
        ((width - 1, 1), (width - 1, height - 2)),
    ):
        pygame.draw.line(panel, BORDER, start, end)
    canvas.blit(panel, rect)


def wrap_text(text, typeface, width):
    """quebra o texto em linhas que cabem na largura, sem cortar palavras."""
    lines = []
    for word in text.split():
        candidate = f"{lines[-1]} {word}" if lines else word
        if lines and typeface.size(candidate)[0] <= width:
            lines[-1] = candidate
        else:
            lines.append(word)
    return lines


def draw_arrow(canvas, direction, center, size, color, shadow=False):
    """triângulo desenhado, em vez de glifo, pra alinhar certinho com o texto."""
    x, y = center
    half_width, half_height = size[0] // 2, size[1] // 2
    if direction == "down":
        points = [(x, y + half_height), (x - half_width, y - half_height), (x + half_width, y - half_height)]
    else:
        tip = -half_width if direction == "left" else half_width
        points = [(x + tip, y), (x - tip, y - half_height), (x - tip, y + half_height)]
    if shadow:
        pygame.draw.polygon(canvas, SHADOW, [(px + 1, py + 1) for px, py in points])
    pygame.draw.polygon(canvas, color, points)


def key_width(label=None):
    # teclas de seta são quadradas; as com texto crescem com o rótulo
    return font(8).size(label)[0] + 6 if label else 11


def draw_key(canvas, topleft, label=None, arrow=None):
    """tecla clara com sombra embaixo; devolve o retângulo pra posicionar o que vem depois."""
    rect = pygame.Rect(topleft, (key_width(label), 11))
    canvas.fill(KEY_SHADE, rect.move(0, 2))
    canvas.fill(KEY_FACE, rect)
    if label:
        text = font(8).render(label, False, KEY_TEXT)
        canvas.blit(text, text.get_rect(center=(rect.centerx, rect.centery + 1)))
    else:
        draw_arrow(canvas, arrow, rect.center, (4, 6), KEY_TEXT)
    return rect


def blink(time):
    # pisca pelo relógio, não por frame, então o ritmo não muda com o fps
    return time % BLINK_PERIOD < BLINK_ON * BLINK_PERIOD
