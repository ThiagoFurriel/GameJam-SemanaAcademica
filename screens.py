import random

import pygame

import ui
from assets import load_god_frames, load_image
from dialogue import BOLT_COLORS, BOLT_DURATION, FLASH_ALPHA, FLASH_DURATION
from display import present
from menu import BAR, BAR_SHADE
from settings import COLORS, SIZE

CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
GOD_FPS = 4

# os quatro deuses sobem do horizonte lado a lado (4 x 120px = a tela inteira),
# um de cada vez, e o título aparece depois por cima
GOD_WIDTH = 120
GOD_TOP = 92
GOD_DROP = 60
GOD_RISE = 0.6
GOD_STAGGER = 0.25
TITLE_AT = 1.4
TITLE_FADE = 0.5
TITLE_Y = 28
TITLE_DROP = 6
SUBTITLE_ALPHA = 190
# névoa escura subindo da barra até a cintura dos deuses
FOG_TOP = 190
FOG_ALPHA = 230
# o primeiro raio cai logo depois que os deuses chegam; os outros, em intervalos sorteados
FIRST_FLASH = 1.9
FLASH_GAP = (2.5, 5.5)
BOLT_STEPS = 5
BOLT_STEP = 18
HINT_GAP = 6

# créditos: cada linha é (tipo, texto); "gap" só dá espaço
CREDITS = (
    ("title", "LINK: Ressonância Maldita"),
    ("small", "uma maldição"),
    ("small", "quatro deuses"),
    ("small", "nenhuma nota errada"),
    ("gap", None),
    ("head", "EQUIPE"),
    ("name", "ANA BEATRIZ COSENZA"),
    ("name", "BEATRIZ DOS SANTOS CUNHA"),
    ("name", "BRENO CHRISOSTOMO PINNA"),
    ("name", "THIAGO FURRIEL DE CASTRO"),
    ("gap", None),
    ("head", "ARTE"),
    ("name", "SPRITES E CENÁRIOS"),
    ("small", "produzidos pela equipe"),
    ("gap", None),
    ("head", "MUSICAS"),
    ("small", "produzidas pela equipe"),
    ("gap", None),
    ("head", "ENGINE"),
    ("name", "PYTHON + PYGAME"),
    ("gap", None),
    ("head", "FONTE"),
    ("name", "PRESS START 2P"),
    ("gap", None),
    ("head", "FEITO PARA"),
    ("name", "GAMEJAM DA XII SEMANA"),
    ("name", "DA COMPUTAÇÃO - UFF"),
    # espaço grande pra o agradecimento parar sozinho na tela
    *(("gap", None),) * 8,
    ("title", "OBRIGADO POR JOGAR!"),
    ("small", "o show continua."),
)
# altura de cada tipo de linha, tamanho da fonte, cor e deslocamento vertical do texto
STYLES = {
    "title": (34, 16, ui.ACCENT, 0),
    "head": (18, 8, ui.ACCENT, 4),
    "name": (14, 8, ui.TEXT, 0),
    "small": (13, 8, "#b98bd6", 0),
    "gap": (16, None, None, 0),
}
SCROLL_SPEED = 16
# a rolagem para quando o agradecimento chega nessa altura
STOP_Y = 120
# distância das bordas em que cada linha some aos poucos
EDGE_FADE = 24
CREDITS_HINT_Y = SIZE[1] - 30


def _ease_out(progress):
    progress = min(1.0, max(0.0, progress))
    return 1 - (1 - progress) ** 3


def _with_alpha(image, alpha):
    # mesmo truque do GodFigure: multiplica o alpha numa cópia
    if alpha >= 255:
        return image
    image = image.copy()
    image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    return image


def _draw_strings_underline(canvas, centerx, top, alpha=255):
    """as cinco cordas viram um sublinhado colorido do título."""
    for index, color in enumerate(COLORS):
        ui.draw_shade(canvas, (centerx - 60 + index * 24, top, 22, 2), (*pygame.Color(color)[:3], alpha))


def _fog():
    height = BAR.top - FOG_TOP
    fog = pygame.Surface((SIZE[0], height), pygame.SRCALPHA)
    for row in range(height):
        fog.fill((*pygame.Color(ui.SHADOW)[:3], FOG_ALPHA * row // height), (0, row, SIZE[0], 1))
    return fog


class TitleScreen:
    """tela inicial: os quatro deuses na tempestade e o nome do jogo."""

    def __init__(self, window, levels):
        self.window = window
        self.canvas = pygame.Surface(SIZE)
        self.clock = pygame.time.Clock()
        self.background = load_image("tempestade")
        self.gods = [load_god_frames(level.god_sheet) for level in levels]
        self.fog = _fog()
        self._random = random.Random()

    def run(self):
        """devolve True se o jogador quiser sair (esc ou fechar a janela)."""
        time = 0.0
        flash_at = None
        next_flash = FIRST_FLASH
        bolt = []
        while True:
            time += min(self.clock.tick(60) / 1000, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key == pygame.K_ESCAPE:
                    return True
                if event.key in CONFIRM_KEYS:
                    return False
            if time >= next_flash:
                flash_at, bolt = time, self._make_bolt()
                next_flash = time + self._random.uniform(*FLASH_GAP)
            self.draw(time, None if flash_at is None else time - flash_at, bolt)

    def draw(self, time, flash_age, bolt):
        canvas = self.canvas
        canvas.blit(self.background, (0, 0))
        # o raio cai atrás dos deuses, no céu
        if flash_age is not None and flash_age < BOLT_DURATION:
            for width, color in zip((3, 1), BOLT_COLORS):
                pygame.draw.lines(canvas, color, False, bolt, width)
        frame = int(time * GOD_FPS)
        for index, frames in enumerate(self.gods):
            progress = _ease_out((time - index * GOD_STAGGER) / GOD_RISE)
            if progress <= 0:
                continue
            image = _with_alpha(frames[frame % len(frames)], round(255 * progress))
            canvas.blit(image, (index * GOD_WIDTH, GOD_TOP + round(GOD_DROP * (1 - progress))))
        canvas.blit(self.fog, (0, FOG_TOP))
        if flash_age is not None and flash_age < FLASH_DURATION:
            ui.draw_shade(canvas, canvas.get_rect(), (244, 238, 252, round(FLASH_ALPHA * (1 - flash_age / FLASH_DURATION))))

        appear = (time - TITLE_AT) / TITLE_FADE
        if appear > 0:
            alpha = round(255 * min(1.0, appear))
            top = TITLE_Y + round(TITLE_DROP * (1 - _ease_out(appear)))
            centerx = SIZE[0] // 2
            ui.draw_text(canvas, ui.font(16), "LINK: Ressonância Maldita", ui.ACCENT, alpha, midtop=(centerx, top))
            ui.draw_text(
                canvas,
                ui.font(8),
                "GAMEJAM - XII SEMANA DA COMPUTAÇÃO UFF",
                ui.TEXT,
                alpha * SUBTITLE_ALPHA // 255,
                midtop=(centerx, top + 26),
            )
            _draw_strings_underline(canvas, centerx, top + 42, alpha)

        ui.draw_shade(canvas, BAR, BAR_SHADE)
        canvas.fill(ui.DIVIDER, (BAR.left, BAR.top, BAR.width, 1))
        if appear >= 1:
            self._draw_hints(time)
        present(canvas, self.window)

    def _draw_hints(self, time):
        y = BAR.top + 10
        if ui.blink(time):
            label = "APERTE"
            width = ui.font(8).size(label)[0] + HINT_GAP + ui.key_width("ENTER")
            left = (SIZE[0] - width) // 2
            text = ui.draw_text(self.canvas, ui.font(8), label, ui.TEXT, topleft=(left, y + 2))
            ui.draw_key(self.canvas, (text.right + HINT_GAP, y), label="ENTER")
        # "ESC SAIR" encostado na direita, com a mesma margem do menu
        label = "SAIR"
        right = SIZE[0] - 16
        left = right - ui.font(8).size(label)[0] - 4 - ui.key_width("ESC")
        key = ui.draw_key(self.canvas, (left, y), label="ESC")
        ui.draw_text(self.canvas, ui.font(8), label, ui.TEXT, topleft=(key.right + 4, y + 2))

    def _make_bolt(self):
        # zigue-zague curto no céu, por trás dos deuses
        x = self._random.randrange(60, 420)
        points = [(x, 0)]
        for step in range(1, BOLT_STEPS + 1):
            x += self._random.randrange(-18, 19)
            points.append((x, step * BOLT_STEP))
        return points


class CreditsScreen:
    """créditos subindo numa tela preta, depois do final da história."""

    def __init__(self, window):
        self.window = window
        self.canvas = pygame.Surface(SIZE)
        self.clock = pygame.time.Clock()
        heights = [STYLES[kind][0] for kind, _ in CREDITS]
        # a rolagem para com a penúltima linha (o agradecimento) no STOP_Y
        self.scroll_end = SIZE[1] - STOP_Y + sum(heights[:-2])

    def run(self):
        """enter no fim (ou esc a qualquer momento) volta pro menu; devolve True se fechou a janela."""
        time = 0.0
        while True:
            time += min(self.clock.tick(60) / 1000, 0.1)
            offset = min(time * SCROLL_SPEED, self.scroll_end)
            done = offset >= self.scroll_end
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key == pygame.K_ESCAPE or (done and event.key in CONFIRM_KEYS):
                    return False
            self.draw(time, offset, done)

    def draw(self, time, offset, done):
        canvas = self.canvas
        canvas.fill(ui.SHADOW)
        centerx = SIZE[0] // 2
        y = SIZE[1] - round(offset)
        for index, (kind, text) in enumerate(CREDITS):
            height, size, color, shift = STYLES[kind]
            if text and -height < y < SIZE[1]:
                # some suave perto do topo e da base
                fade = min(1.0, max(0.0, (y - 4) / EDGE_FADE), max(0.0, (SIZE[1] - 12 - y) / EDGE_FADE))
                alpha = round(255 * fade)
                ui.draw_text(canvas, ui.font(size), text, color, alpha, midtop=(centerx, y + shift))
                if index == 0:
                    _draw_strings_underline(canvas, centerx, y + 20, alpha)
            y += height
        if done and ui.blink(time):
            label = "VOLTAR AO MENU"
            width = ui.key_width("ENTER") + 4 + ui.font(8).size(label)[0]
            key = ui.draw_key(canvas, ((SIZE[0] - width) // 2, CREDITS_HINT_Y), label="ENTER")
            ui.draw_text(canvas, ui.font(8), label, ui.TEXT, topleft=(key.right + 4, CREDITS_HINT_Y + 2))
        present(canvas, self.window)
