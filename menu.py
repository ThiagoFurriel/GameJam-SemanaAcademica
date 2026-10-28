import pygame

import ui
from assets import load_god_frames, load_image
from display import present
from settings import SIZE

PREVIOUS_KEYS = (pygame.K_LEFT, pygame.K_UP)
NEXT_KEYS = (pygame.K_RIGHT, pygame.K_DOWN)
CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)

PANEL = pygame.Rect(16, 20, 264, 180)
PADDING = 12
SELECTOR_Y = 120
# espaço entre cada seta e o nome do deus, igual dos dois lados
ARROW_GAP = 12
ARROW_SIZE = (7, 12)
DOT_SIZE = 6
DOT_GAP = 5
DOT_LOCKED = "#3a3442"
MUTED_ALPHA = 190
LOCKED_ALPHA = 110
# multiplica o rgb do deus bloqueado: vira silhueta, mantendo o contorno
SILHOUETTE = (24, 20, 32)
BAR = pygame.Rect(0, SIZE[1] - 32, SIZE[0], 32)
BAR_SHADE = (8, 6, 12, 217)
HINT_GAP = 14
# cada dica: as teclas (argumentos de ui.draw_key) e o que elas fazem
HINTS = (
    (({"arrow": "left"}, {"arrow": "right"}), "ESCOLHER"),
    (({"label": "ENTER"},), "JOGAR"),
    (({"label": "ESC"},), "SAIR"),
)


def _silhouette(frame):
    dark = frame.copy()
    dark.fill(SILHOUETTE, special_flags=pygame.BLEND_RGB_MULT)
    return dark


class Menu:
    """seleção de fase da jornada: dá pra ver todas, mas só jogar as já liberadas."""

    def __init__(self, window, journey):
        self.window = window
        self.journey = journey
        self.levels = journey.levels
        self.selected = 0
        self.canvas = pygame.Surface(SIZE)
        self.clock = pygame.time.Clock()
        # carrega tudo de uma vez: são poucas imagens e trocar de fase fica instantâneo
        self.scenes = []
        for level in self.levels:
            frames = load_god_frames(level.god_sheet)
            self.scenes.append(
                (
                    load_image(level.background),
                    load_image(level.clouds),
                    frames,
                    [_silhouette(frame) for frame in frames],
                )
            )
        self.animation = 0.0

    def run(self):
        """devolve a fase escolhida, ou None se o jogador quiser sair."""
        # volta sempre apontando pro próximo desafio da jornada
        if self.journey.next_level is not None:
            self.selected = self.levels.index(self.journey.next_level)
        while True:
            dt = min(self.clock.tick(60) / 1000, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key in CONFIRM_KEYS and self.journey.unlocked(self.levels[self.selected]):
                    return self.levels[self.selected]
                if event.key in PREVIOUS_KEYS:
                    self.selected = (self.selected - 1) % len(self.levels)
                elif event.key in NEXT_KEYS:
                    self.selected = (self.selected + 1) % len(self.levels)
            self.animation += dt
            self.draw()

    def draw(self):
        level = self.levels[self.selected]
        unlocked = self.journey.unlocked(level)
        background, clouds, frames, silhouettes = self.scenes[self.selected]
        god = frames if unlocked else silhouettes
        self.canvas.blit(background, (0, 0))
        self.canvas.blit(clouds, (0, 0))
        self.canvas.blit(god[int(self.animation * 4) % len(god)], (285, 9))

        ui.draw_panel(self.canvas, PANEL)
        left = PANEL.left + PADDING
        ui.draw_text(self.canvas, ui.font(8), "LINK: Ressonância Maldita", ui.ACCENT, topleft=(left, 42))
        ui.draw_text(
            self.canvas, ui.font(8), self._status(level), ui.TEXT, MUTED_ALPHA, topleft=(left, 86)
        )
        self._draw_selector(unlocked)
        self._draw_dots(left, 150)
        ui.draw_text(
            self.canvas,
            ui.font(8),
            f"FASE {self.selected + 1}/{len(self.levels)}",
            ui.TEXT,
            MUTED_ALPHA,
            topleft=(left, 167),
        )
        self._draw_hints()
        present(self.canvas, self.window)

    def _status(self, level):
        if level in self.journey.completed:
            return "VENCIDO"
        if self.journey.unlocked(level):
            return "PRÓXIMO DESAFIO"
        return "BLOQUEADO"

    def _draw_selector(self, unlocked):
        # nome centralizado no painel e as setas presas a ele, não às bordas:
        # assim o espaço fica igual dos dois lados pra qualquer tamanho de nome
        name = ui.draw_text(
            self.canvas,
            ui.font(16),
            self.levels[self.selected].title.upper(),
            ui.TEXT,
            255 if unlocked else LOCKED_ALPHA,
            center=(PANEL.centerx, SELECTOR_Y),
        )
        offset = ARROW_GAP + ARROW_SIZE[0] // 2
        for direction, x in (("left", name.left - offset), ("right", name.right + offset)):
            ui.draw_arrow(self.canvas, direction, (x, SELECTOR_Y), ARROW_SIZE, ui.ACCENT, shadow=True)

    def _draw_dots(self, left, top):
        for index, level in enumerate(self.levels):
            if index == self.selected:
                color = ui.ACCENT
            elif self.journey.unlocked(level):
                color = ui.OFF
            else:
                color = DOT_LOCKED
            x = left + 1 + index * (DOT_SIZE + DOT_GAP)
            self.canvas.fill(color, (x, top, DOT_SIZE, DOT_SIZE))

    def _draw_hints(self):
        ui.draw_shade(self.canvas, BAR, BAR_SHADE)
        self.canvas.fill(ui.DIVIDER, (BAR.left, BAR.top, BAR.width, 1))
        x, y = PANEL.left, BAR.top + 10
        for keys, hint in HINTS:
            for key in keys:
                x = ui.draw_key(self.canvas, (x, y), **key).right + 4
            label = ui.draw_text(self.canvas, ui.font(8), hint, ui.TEXT, topleft=(x, y + 2))
            x = label.right + HINT_GAP
