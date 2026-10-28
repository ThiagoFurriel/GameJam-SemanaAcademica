import pygame

import ui
from rhythm.judge import Grade
from settings import COLORS, LANES, SIZE

# centro do player, que é desenhado em x=179 com 24px de largura
HIT_X = 191
# velocidade em pixels por beat (não por frame): a nota chega na linha
# exatamente no beat dela, seja qual for o fps.
PIXELS_PER_BEAT = 96
FEEDBACK_DURATION = 0.4
GRADE_COLORS = {Grade.PERFECT: "#ffe046", Grade.GOOD: "#46b8dd", Grade.MISS: "#ed252e"}

RESULTS_SHADE = (8, 6, 12, 140)
RESULTS_PANEL = pygame.Rect(128, 29, 224, 196)
# coluna da tabela de estatísticas: rótulo encosta na esquerda, número na direita
STATS_LEFT = 160
STATS_RIGHT = 320
STATS_TOP = 126
STATS_ROW = 16
STATS = ((Grade.PERFECT, "PERFEITO"), (Grade.GOOD, "BOM"), (Grade.MISS, "ERROU"))
COMBO_ALPHA = 220

# abaixo desse valor de ressonância o mundo começa a perder a cor
GRAY_FROM = 0.7
RESONANCE_BAR = pygame.Rect(180, 19, 120, 7)
GAME_OVER_PANEL = pygame.Rect(128, 71, 224, 128)
GAME_OVER_COLOR = "#ed252e"


def note_x(chart, note, song_time):
    return HIT_X + (note.beat - chart.beat_at(song_time)) * PIXELS_PER_BEAT


class HighwayView:
    def __init__(self, note_sprites):
        self.note_sprites = note_sprites
        self.font = ui.font(8)
        self.big_font = ui.font(16)

    def draw_notes(self, canvas, highway, song_time):
        for lane, notes in enumerate(highway.lanes):
            y = LANES[lane]
            pygame.draw.line(canvas, COLORS[lane], (HIT_X, y - 6), (HIT_X, y), 1)
            sprite = self.note_sprites[lane]
            for note in notes:
                x = note_x(highway.chart, note, song_time)
                # as filas estão em ordem de beat: daqui pra frente tudo está fora da tela
                if x - sprite.get_width() > SIZE[0]:
                    break
                canvas.blit(sprite, sprite.get_rect(midbottom=(round(x), y)))

    def draw_resonance(self, canvas, resonance):
        """ressonância baixa tira a cor do mundo. vai entre o mundo e o hud, pra o hud seguir colorido."""
        gray = min(1.0, max(0.0, (GRAY_FROM - resonance) / GRAY_FROM))
        if gray > 0:
            faded = pygame.transform.grayscale(canvas)
            faded.set_alpha(round(255 * gray))
            canvas.blit(faded, (0, 0))

    def draw_hud(self, canvas, highway, song_time):
        self._draw_resonance_bar(canvas, highway.resonance.displayed)
        score = highway.score
        ui.draw_text(canvas, self.font, f"PONTOS {score.points}", ui.TEXT, topleft=(8, 8))
        if score.combo > 1:
            ui.draw_text(canvas, self.font, f"COMBO {score.combo}", ui.TEXT, topleft=(8, 20))
        age = song_time - highway.last_grade_time
        if highway.last_grade is not None and age < FEEDBACK_DURATION:
            alpha = round(255 * (1 - age / FEEDBACK_DURATION))
            ui.draw_text(
                canvas,
                self.font,
                highway.last_grade.value.upper(),
                GRADE_COLORS[highway.last_grade],
                alpha,
                midbottom=(HIT_X, LANES[0] - 30),
            )

    def draw_results(self, canvas, highway, time):
        ui.draw_shade(canvas, canvas.get_rect(), RESULTS_SHADE)
        ui.draw_panel(canvas, RESULTS_PANEL)
        center = RESULTS_PANEL.centerx
        score = highway.score

        ui.draw_text(canvas, self.font, "FIM DE FASE", ui.ACCENT, midtop=(center, 45))
        ui.draw_text(canvas, self.big_font, str(score.points), ui.TEXT, midtop=(center, 64))
        self._draw_centered_pair(
            canvas, ("COMBO MÁX ", ui.TEXT, COMBO_ALPHA), (f"{score.max_combo}x", ui.ACCENT, 255), 89
        )

        canvas.fill(ui.DIVIDER, (STATS_LEFT, 110, STATS_RIGHT - STATS_LEFT, 1))
        for row, (grade, label) in enumerate(STATS):
            y = STATS_TOP + row * STATS_ROW
            color = GRADE_COLORS[grade]
            ui.draw_text(canvas, self.font, label, color, topleft=(STATS_LEFT, y))
            ui.draw_text(canvas, self.font, str(score.counts[grade]), color, topright=(STATS_RIGHT, y))
        canvas.fill(ui.DIVIDER, (STATS_LEFT, 179, STATS_RIGHT - STATS_LEFT, 1))

        if ui.blink(time):
            self._draw_key_hint(canvas, "ENTER", "CONTINUAR", 196)

    def draw_game_over(self, canvas, time):
        ui.draw_shade(canvas, canvas.get_rect(), RESULTS_SHADE)
        ui.draw_panel(canvas, GAME_OVER_PANEL)
        center = GAME_OVER_PANEL.centerx
        ui.draw_text(canvas, self.big_font, "GAME OVER", GAME_OVER_COLOR, midtop=(center, 87))
        ui.draw_text(canvas, self.font, "O SILÊNCIO VENCEU", ui.TEXT, COMBO_ALPHA, midtop=(center, 111))
        canvas.fill(ui.DIVIDER, (STATS_LEFT, 129, STATS_RIGHT - STATS_LEFT, 1))
        if ui.blink(time):
            self._draw_key_hint(canvas, "ENTER", "TENTAR DE NOVO", 143)
        self._draw_key_hint(canvas, "ESC", "MENU", 165)

    def _draw_key_hint(self, canvas, key_label, hint, top):
        # tecla + o que ela faz, centralizados juntos na tela
        left = SIZE[0] // 2 - (ui.key_width(key_label) + 4 + self.font.size(hint)[0]) // 2
        key = ui.draw_key(canvas, (left, top), label=key_label)
        ui.draw_text(canvas, self.font, hint, ui.TEXT, topleft=(key.right + 4, top + 2))

    def _draw_resonance_bar(self, canvas, value):
        ui.draw_text(canvas, self.font, "RESSONÂNCIA", ui.TEXT, midtop=(RESONANCE_BAR.centerx, 8))
        canvas.fill(ui.BORDER, RESONANCE_BAR)
        inner = RESONANCE_BAR.inflate(-2, -2)
        canvas.fill(ui.SHADOW, inner)
        # a cor do preenchimento acompanha a lore: cinza quando vazia, amarela quando cheia
        color = pygame.Color(ui.OFF).lerp(ui.ACCENT, value)
        canvas.fill(color, (inner.left, inner.top, round(inner.width * value), inner.height))

    def _draw_centered_pair(self, canvas, first, second, top):
        # duas cores na mesma linha: mede o conjunto e centraliza no painel
        width = sum(self.font.size(text)[0] for text, _, _ in (first, second))
        x = RESULTS_PANEL.centerx - width // 2
        for text, color, alpha in (first, second):
            ui.draw_text(canvas, self.font, text, color, alpha, topleft=(x, top))
            x += self.font.size(text)[0]
