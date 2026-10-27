import math

import pygame

import story
from assets import load_god_frames, load_image
from dialogue import PARK_SHADE, BackdropScene, BlackScene, Dialogue, GodScene, LevelScene, StormScene
from display import present
from figure import GodFigure
from journey import Journey, approves
from levels import LEVELS
from menu import Menu
from rhythm.chart import load_chart
from rhythm.conductor import Conductor
from rhythm.effects import Effects
from rhythm.highway import Highway
from rhythm.view import HighwayView
from settings import COLORS, KEYS, LANES, NOTE_SPRITES, SIZE

# folga depois da última nota antes de mostrar o resultado, em segundos
END_DELAY = 1.5


class Game:
    def __init__(self, window, level):
        self.window = window
        self.canvas = pygame.Surface(SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 12)
        self.images = {
            name: load_image(name)
            for name in (level.background, level.clouds, "cordas", "player")
        }
        self.layers = ((level.background, 6), (level.clouds, 12))
        self.god = GodFigure(load_god_frames(level.god_sheet), (285, 9))
        self.player = [self.images["player"].subsurface((i * 24, 0, 24, 24)) for i in range(5)]
        self.running = True
        self.closed = False
        self.retry = False
        # instante em que a ressonância zerou; a fase congela nele
        self.failed_at = None
        self.animation = 0.0
        self.lane = 0
        self.player_y = float(LANES[0])

        chart = load_chart(level.chart)
        note_sprites = [load_image(name) for name in NOTE_SPRITES]
        self.effects = Effects(chart, note_sprites)
        self.highway = Highway(chart, on_judge=self.judged)
        self.highway_view = HighwayView(note_sprites)
        # a música começa por último, depois de todo o carregamento,
        # pra nenhum travamento de load cair dentro da contagem do tempo
        self.conductor = Conductor(chart.offset, level.music)
        self.conductor.start()

    @property
    def failed(self):
        return self.failed_at is not None

    @property
    def song_time(self):
        return self.failed_at if self.failed else self.conductor.song_time

    @property
    def finished(self):
        if self.failed:
            return False
        # sem música o fim é pelo chart; com música, espera ela acabar também
        song_over = self.conductor.song_time > self.highway.end_time + END_DELAY
        return song_over and not self.conductor.music_playing

    def judged(self, note, grade, song_time):
        self.effects.spawn(note, grade, song_time)
        if self.highway.resonance.depleted and not self.failed:
            # o silêncio venceu: congela a fase e para a música
            self.failed_at = song_time
            self.conductor.stop()

    def event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            self.closed = True
        elif event.type == pygame.KEYDOWN:
            if event.key in KEYS and not self.failed:
                self.lane = KEYS.index(event.key)
                self.highway.press(self.lane, self.conductor.song_time)
            elif event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_RETURN and (self.finished or self.failed):
                self.retry = self.failed
                self.running = False

    def update(self, dt):
        self.animation += dt
        self.player_y += (LANES[self.lane] - self.player_y) * (1 - math.exp(-24 * dt))
        # a barra continua animando até o zero mesmo com a fase congelada
        self.highway.resonance.update(dt)
        if self.failed:
            return
        self.conductor.update()
        # um único instante por frame, pra highway e efeitos concordarem sobre o tempo
        song_time = self.conductor.song_time
        self.highway.update(song_time)
        self.effects.update(song_time)

    def draw(self):
        song_time = self.song_time
        for name, speed in self.layers:
            offset = int(self.animation * speed) % SIZE[0]
            for x in (-offset, SIZE[0] - offset):
                self.canvas.blit(self.images[name], (x, 0))
        self.god.draw(self.canvas, self.animation)
        self.canvas.blit(self.images["cordas"], (0, 0))
        for i, y in enumerate(LANES):
            label = self.font.render("ASDFG"[i], False, COLORS[i])
            self.canvas.blit(label, label.get_rect(center=(17, y - 10)))
        self.highway_view.draw_notes(self.canvas, self.highway, song_time)
        frame = self.player[int(self.animation * 9) % len(self.player)]
        self.canvas.blit(frame, (179, round(self.player_y) - 24))
        self.effects.draw(self.canvas, song_time)
        self.highway_view.draw_resonance(self.canvas, self.highway.resonance.displayed)
        if self.failed:
            self.highway_view.draw_game_over(self.canvas, self.animation)
        elif self.finished:
            self.highway_view.draw_results(self.canvas, self.highway, self.animation)
        else:
            self.highway_view.draw_hud(self.canvas, self.highway, song_time)
        present(self.canvas, self.window)

    def run(self):
        """roda a fase; devolve True se o jogador fechou a janela."""
        try:
            while self.running:
                dt = min(self.clock.tick(60) / 1000, 0.1)
                for event in pygame.event.get():
                    self.event(event)
                self.update(dt)
                self.draw()
        finally:
            self.conductor.stop()
        return self.closed


def main():
    # 48khz é a taxa em que a maioria dos sistemas roda o áudio: casando com ela,
    # ninguém precisa converter no caminho. buffer pequeno = menos latência.
    # precisa vir antes do pygame.init(), e não deve mudar depois de calibrar
    # o offset, porque desloca toda a sincronia.
    pygame.mixer.pre_init(48000, -16, 2, 512)
    pygame.init()
    try:
        window = pygame.display.set_mode((960, 540), pygame.RESIZABLE)
        pygame.display.set_caption("Apenas um Input")
        play(window)
    finally:
        pygame.quit()


def play(window):
    """abertura → menu → fala do deus → fase (→ game over → de novo) → reação → (final) → menu.

    cada etapa devolve se o jogador fechou a janela; aí tudo encerra na hora.
    """
    journey = Journey(LEVELS)
    dialogue = Dialogue(window)
    story_scenes = {
        "park": BackdropScene("parque", PARK_SHADE),
        "storm": StormScene(),
        "god": GodScene(LEVELS, story.GODS, "tempestade"),
        "black": BlackScene(),
        # o final: a tempestade passou e a noite voltou a ser calma
        "night": BackdropScene("noite"),
        "farewell": GodScene(LEVELS, story.GODS, "noite"),
    }
    if dialogue.run(story.INTRO, story_scenes):
        return
    menu = Menu(window, journey)
    while (level := menu.run()) is not None:
        god = story.GODS[level.slug]
        level_scene = {None: LevelScene(level)}
        if dialogue.run(god.intro, level_scene):
            return
        game = Game(window, level)
        if game.run():
            return
        # no game over, tentar de novo recomeça a fase direto, sem repetir a fala do deus
        while game.retry:
            game = Game(window, level)
            if game.run():
                return
        # saiu com esc (no meio da fase ou no game over): volta pro menu sem reação do deus
        if not game.finished:
            continue
        approved = approves(game.highway.resonance)
        if dialogue.run(god.approve if approved else god.disapprove, level_scene):
            return
        if approved and not journey.finished:
            journey.complete(level)
            if journey.finished and dialogue.run(story.ENDING, story_scenes):
                return


if __name__ == "__main__":
    main()
