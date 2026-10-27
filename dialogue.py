import random

import pygame

import ui
from assets import load_god_frames, load_god_portraits, load_image
from display import present
from figure import GodFigure
from settings import LANES, SIZE

BOX = pygame.Rect(16, 212, 448, 54)
PADDING = 10
LINE_HEIGHT = 12
MAX_LINES = 3
TEXT_WIDTH = BOX.width - 2 * PADDING
# o texto aparece por tempo, não por frame: a velocidade é a mesma em qualquer fps
CHARS_PER_SECOND = 45
NAME_TAG_HEIGHT = 15
CONTINUE_ARROW = (7, 5)
ADVANCE_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
GOD_TOPLEFT = (285, 9)
PLAYER_FPS = 9

# escurecimento leve do parque, pra o texto ter contraste
PARK_SHADE = (8, 6, 12, 60)
# os fundos das falas sobem esse tanto: o que importa neles (banco, postes, raio)
# fica perto do chão, e a caixa de diálogo cobriria. no topo só se perde céu vazio.
BACKGROUND_SHIFT = 32
# o raio: a tela clareia e apaga, e o zigue-zague some um pouco antes
FLASH_DURATION = 0.35
FLASH_ALPHA = 200
BOLT_DURATION = 0.2
BOLT_COLORS = ("#b98bd6", "#f4eefc")
BOLT_STEPS = 9
# retrato do deus nas falas fora das fases: da cintura pra cima, à direita, com a base
# um pouco atrás da borda de cima da caixa, pra o corte na cintura ficar escondido
PORTRAIT_SIZE = (144, 168)
PORTRAIT_TOPLEFT = (BOX.right - PORTRAIT_SIZE[0] - 8, BOX.top + 10 - PORTRAIT_SIZE[1])
# chegada de cada deus: desliza da direita com fade e para
SLIDE_DURATION = 0.35
SLIDE_DISTANCE = 160
# texto solto no fundo preto, sem caixa: largura da coluna centralizada
LOOSE_TEXT_WIDTH = 320


def _draw_background(canvas, image):
    canvas.blit(image, (0, -BACKGROUND_SHIFT))
    # a faixa que sobra embaixo repete o chão da própria imagem (quase toda atrás da caixa)
    height = image.get_height()
    floor = image.subsurface((0, height - BACKGROUND_SHIFT, image.get_width(), BACKGROUND_SHIFT))
    canvas.blit(floor, (0, height - BACKGROUND_SHIFT))


def _player_frames():
    sheet = load_image("player")
    return [sheet.subsurface((i * 24, 0, 24, 24)) for i in range(5)]


class BackdropScene:
    """um fundo fixo, com escurecimento opcional pra o texto ter contraste."""

    boxed = True

    def __init__(self, image, shade=None):
        self.background = load_image(image)
        self.shade = shade

    def begin(self, page, time):
        pass

    def draw(self, canvas, time):
        _draw_background(canvas, self.background)
        if self.shade:
            ui.draw_shade(canvas, canvas.get_rect(), self.shade)


class StormScene:
    """a dimensão dos deuses: céu tempestuoso, com raio quando a página pede."""

    boxed = True

    def __init__(self):
        self.background = load_image("tempestade")
        self.flash_start = None
        self.bolt = []
        self._random = random.Random()

    def begin(self, page, time):
        if page.flash:
            self.flash_start = time
            self.bolt = self._make_bolt()

    def draw(self, canvas, time):
        _draw_background(canvas, self.background)
        if self.flash_start is None:
            return
        age = time - self.flash_start
        if age < BOLT_DURATION:
            for width, color in zip((3, 1), BOLT_COLORS):
                pygame.draw.lines(canvas, color, False, self.bolt, width)
        if age < FLASH_DURATION:
            ui.draw_shade(canvas, canvas.get_rect(), (244, 238, 252, round(FLASH_ALPHA * (1 - age / FLASH_DURATION))))

    def _make_bolt(self):
        # zigue-zague sorteado a cada raio, descendo do topo até o horizonte
        x = self._random.randrange(140, 340)
        points = [(x, 0)]
        for step in range(1, BOLT_STEPS + 1):
            x += self._random.randrange(-18, 19)
            points.append((x, step * 20))
        return points


def _portrait(level):
    frames = load_god_portraits(level.god_sheet, PORTRAIT_SIZE[1])
    return GodFigure(frames, PORTRAIT_TOPLEFT, animated=False)


class GodScene:
    """retrato parado só do deus que está falando, sobre um céu; quem chega entra deslizando."""

    boxed = True

    def __init__(self, levels, gods, background):
        self.background = load_image(background)
        self.figures = {gods[level.slug].name: _portrait(level) for level in levels}
        self.speaker = None
        self.arrival = 0.0

    def begin(self, page, time):
        # se o mesmo deus fala de novo, ele fica parado; só quem chega desliza
        if page.speaker != self.speaker:
            self.speaker = page.speaker
            self.arrival = time

    def draw(self, canvas, time):
        _draw_background(canvas, self.background)
        progress = min(1.0, (time - self.arrival) / SLIDE_DURATION)
        # desacelera no fim (ease-out), como quem chega e para
        eased = 1 - (1 - progress) ** 3
        shift = round(SLIDE_DISTANCE * (1 - eased))
        self.figures[self.speaker].draw(canvas, time, shift, round(255 * eased))


class BlackScene:
    """fundo preto e só o texto, sem caixa: pausa antes de virar pro menu."""

    boxed = False

    def begin(self, page, time):
        pass

    def draw(self, canvas, time):
        canvas.fill(ui.SHADOW)


class LevelScene:
    """o cenário da fase com o deus dela, do jeito que aparece no jogo."""

    boxed = True

    def __init__(self, level):
        self.background = load_image(level.background)
        self.clouds = load_image(level.clouds)
        self.strings = load_image("cordas")
        self.player = _player_frames()
        self.figure = GodFigure(load_god_frames(level.god_sheet), GOD_TOPLEFT)

    def begin(self, page, time):
        pass

    def draw(self, canvas, time):
        canvas.blit(self.background, (0, 0))
        canvas.blit(self.clouds, (0, 0))
        self.figure.draw(canvas, time)
        canvas.blit(self.strings, (0, 0))
        frame = self.player[int(time * PLAYER_FPS) % len(self.player)]
        canvas.blit(frame, (179, LANES[0] - 24))


class Dialogue:
    """caixa de diálogo estilo rpg: personagem em cena, texto digitando embaixo."""

    def __init__(self, window):
        self.window = window
        self.canvas = pygame.Surface(SIZE)
        self.clock = pygame.time.Clock()
        self.font = ui.font(8)

    def run(self, pages, scenes):
        """mostra as páginas em ordem; devolve True se o jogador fechou a janela.

        scenes mapeia o page.scene pra cena de fundo (None é a cena padrão).
        """
        time = 0.0
        index = 0
        lines, start = self._begin(pages[index], scenes, time)
        while True:
            time += min(self.clock.tick(60) / 1000, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key not in ADVANCE_KEYS:
                    continue
                if self._typing(lines, time - start):
                    # primeiro toque completa a página, o segundo avança
                    start = time - self._length(lines) / CHARS_PER_SECOND
                else:
                    index += 1
                    if index == len(pages):
                        return False
                    lines, start = self._begin(pages[index], scenes, time)
            self._draw(pages[index], scenes, lines, time, time - start)

    def _begin(self, page, scenes, time):
        scene = scenes[page.scene]
        scene.begin(page, time)
        width = TEXT_WIDTH if scene.boxed else LOOSE_TEXT_WIDTH
        return ui.wrap_text(page.text, self.font, width), time

    @staticmethod
    def _length(lines):
        return sum(len(line) for line in lines)

    def _typing(self, lines, age):
        return int(age * CHARS_PER_SECOND) < self._length(lines)

    def _draw(self, page, scenes, lines, time, age):
        scene = scenes[page.scene]
        scene.draw(self.canvas, time)
        if scene.boxed:
            # caixa opaca: o cenário não pode aparecer atrás do texto
            self.canvas.fill(ui.SHADOW, BOX.inflate(-2, -2))
            ui.draw_panel(self.canvas, BOX)
            if page.speaker:
                self._draw_name_tag(page.speaker)
            top = BOX.top + PADDING
            arrow = (BOX.right - PADDING, BOX.bottom - PADDING // 2 - 2)
        else:
            # texto solto: bloco centralizado na tela, cada linha centralizada
            top = (SIZE[1] - len(lines) * LINE_HEIGHT) // 2
            arrow = (SIZE[0] // 2, top + len(lines) * LINE_HEIGHT + 10)

        remaining = int(age * CHARS_PER_SECOND)
        for row, line in enumerate(lines[:MAX_LINES]):
            visible = line[:max(0, remaining)]
            remaining -= len(line)
            if not visible:
                continue
            y = top + row * LINE_HEIGHT
            if scene.boxed:
                ui.draw_text(self.canvas, self.font, visible, ui.TEXT, topleft=(BOX.left + PADDING, y))
            else:
                # alinha pelo tamanho da linha inteira, pra o texto não "andar" enquanto digita
                left = (SIZE[0] - self.font.size(line)[0]) // 2
                ui.draw_text(self.canvas, self.font, visible, ui.TEXT, topleft=(left, y))

        if not self._typing(lines, age) and ui.blink(time):
            ui.draw_arrow(self.canvas, "down", arrow, CONTINUE_ARROW, ui.ACCENT)
        present(self.canvas, self.window)

    def _draw_name_tag(self, speaker):
        width = self.font.size(speaker)[0] + 12
        # a etiqueta fica presa na borda de cima da caixa, por cima dela
        tag = pygame.Rect(BOX.left + 8, BOX.top - NAME_TAG_HEIGHT // 2 - 2, width, NAME_TAG_HEIGHT)
        # fundo opaco antes do painel, pra a borda da caixa não aparecer atrás do nome
        self.canvas.fill(ui.SHADOW, tag.inflate(-2, -2))
        ui.draw_panel(self.canvas, tag)
        ui.draw_text(self.canvas, self.font, speaker, ui.ACCENT, center=(tag.centerx, tag.centery + 1))
