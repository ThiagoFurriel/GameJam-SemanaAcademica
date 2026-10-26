import math
from pathlib import Path

import pygame

ASSETS = Path(__file__).resolve().parent / "sprites"
SIZE = (480, 270)
LANES = (145, 174, 203, 232, 261)
KEYS = (pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g)
COLORS = ("#99f634", "#ed252e", "#ffe046", "#46b8dd", "#f68b43")


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((960, 540), pygame.RESIZABLE)
        pygame.display.set_caption("teste 1")
        self.canvas = pygame.Surface(SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 12)
        self.images = {
            name: pygame.image.load(str(ASSETS / f"{name}.png")).convert_alpha()
            for name in ("metal", "nuvemmetal", "deusmetalsprite", "cordas", "player")
        }
        sheet = self.images["deusmetalsprite"]
        self.god = [
            pygame.transform.scale(sheet.subsurface((i * 144, 0, 144, 313)), (120, 261))
            for i in range(4)
        ]
        self.player = [self.images["player"].subsurface((i * 24, 0, 24, 24)) for i in range(5)]
        self.running = True
        self.animation = 0.0
        self.lane = 0
        self.player_y = float(LANES[0])

    def event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in KEYS:
                self.lane = KEYS.index(event.key)
            elif event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self, dt):
        self.animation += dt
        self.player_y += (LANES[self.lane] - self.player_y) * (1 - math.exp(-24 * dt))

    def draw(self):
        for name, speed in (("metal", 6), ("nuvemmetal", 12)):
            offset = int(self.animation * speed) % SIZE[0]
            for x in (-offset, SIZE[0] - offset):
                self.canvas.blit(self.images[name], (x, 0))
        self.canvas.blit(self.god[int(self.animation * 4) % 4], (285, 9))
        self.canvas.blit(self.images["cordas"], (0, 0))
        for i, y in enumerate(LANES):
            label = self.font.render("ASDFG"[i], False, COLORS[i])
            self.canvas.blit(label, label.get_rect(center=(17, y - 10)))
        frame = self.player[int(self.animation * 9) % len(self.player)]
        self.canvas.blit(frame, (179, round(self.player_y) - 24))

        width, height = self.window.get_size()
        scale = min(width / SIZE[0], height / SIZE[1])
        target = (max(1, int(SIZE[0] * scale)), max(1, int(SIZE[1] * scale)))
        self.window.fill("#0c0912")
        self.window.blit(
            pygame.transform.scale(self.canvas, target),
            ((width - target[0]) // 2, (height - target[1]) // 2),
        )
        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(60) / 1000, 0.1)
                for event in pygame.event.get():
                    self.event(event)
                self.update(dt)
                self.draw()
        finally:
            pygame.quit()


if __name__ == "__main__":
    Game().run()
