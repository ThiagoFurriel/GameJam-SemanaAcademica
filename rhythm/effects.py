import math
import random
from dataclasses import dataclass

import pygame

from rhythm.judge import Grade
from rhythm.view import note_x
from settings import LANES

# as animações são calculadas pelo tempo da música, não por frame,
# então duram o mesmo em qualquer fps.
FALL_DURATION = 0.4
# em pixels do canvas por segundo²
GRAVITY = 700
NOTE_SIZE = 16
# quantas partículas de fogo sobem por grade de acerto
FLAME_PARTICLES = {Grade.PERFECT: 28, Grade.GOOD: 16}
# o fogo sai em fluxo durante esse tempo, não tudo de uma vez: forma uma coluna
FLAME_EMIT = 0.12
FLAME_LIFE = (0.2, 0.38)
FLAME_RISE = (50, 110)
# metade da largura da base da chama, em pixels
FLAME_SPREAD = 5
# quanto a partícula fecha em direção ao centro até o fim da vida: faz a ponta
FLAME_TAPER = 0.8
FLAME_WOBBLE = 1.5
# tamanho em pixels conforme a vida passa: grosso na base, fino na ponta
FLAME_SIZES = ((0.3, 3), (0.65, 2), (1.0, 1))
# do mais quente pro mais frio: a partícula percorre a paleta enquanto vive.
# os tons são contidos de propósito: onde as partículas se sobrepõem a soma
# já chega no branco, então só o miolo da chama fica branco-quente.
FLAME_PALETTE = (
    (210, 180, 90),
    (200, 140, 40),
    (180, 90, 25),
    (140, 45, 15),
    (70, 20, 8),
)
# multiplica o rgb da nota perdida: escurece mantendo um resto do tom da corda
MISS_TINT = (90, 90, 100)


@dataclass
class Particle:
    x: float
    offset: float
    y: float
    rise: float
    life: float
    phase: float
    start: float


@dataclass
class Fall:
    x: float
    y: float
    lane: int
    start: float


def _fade(age, duration):
    return round(255 * max(0.0, 1 - age / duration))


class Effects:
    """acerto solta fogo, erro cai da corda."""

    def __init__(self, chart, note_sprites):
        self.chart = chart
        self.missed_sprites = [self._darken(sprite) for sprite in note_sprites]
        self.particles = []
        self.falls = []
        self._random = random.Random()

    def spawn(self, note, grade, song_time):
        x = note_x(self.chart, note, song_time)
        y = LANES[note.lane]
        if grade is Grade.MISS:
            self.falls.append(Fall(x, y, note.lane, song_time))
            return
        base_y = y - NOTE_SIZE / 4
        for _ in range(FLAME_PARTICLES[grade]):
            self.particles.append(
                Particle(
                    x,
                    self._random.uniform(-FLAME_SPREAD, FLAME_SPREAD),
                    base_y,
                    self._random.uniform(*FLAME_RISE),
                    self._random.uniform(*FLAME_LIFE),
                    self._random.uniform(0, math.tau),
                    song_time + self._random.uniform(0, FLAME_EMIT),
                )
            )

    def update(self, song_time):
        self.particles = [p for p in self.particles if song_time - p.start < p.life]
        self.falls = [f for f in self.falls if song_time - f.start < FALL_DURATION]

    def draw(self, canvas, song_time):
        for fall in self.falls:
            self._draw_fall(canvas, fall, song_time - fall.start)
        for particle in self.particles:
            age = song_time - particle.start
            # pula a que ainda não saiu do fluxo de emissão e a que já apagou
            # entre o update e o draw deste frame
            if 0 <= age < particle.life:
                self._draw_particle(canvas, particle, age)

    def _draw_particle(self, canvas, particle, age):
        progress = age / particle.life
        color = FLAME_PALETTE[min(int(progress * len(FLAME_PALETTE)), len(FLAME_PALETTE) - 1)]
        size = next(size for limit, size in FLAME_SIZES if progress < limit)
        offset = particle.offset * (1 - FLAME_TAPER * progress)
        x = particle.x + offset + math.sin(particle.phase + age * 30) * FLAME_WOBBLE
        y = particle.y - particle.rise * age
        rect = pygame.Rect(round(x), round(y), size, size)
        canvas.fill(color, rect, special_flags=pygame.BLEND_RGB_ADD)

    def _draw_fall(self, canvas, fall, age):
        # a nota para de acompanhar a corda e só despenca
        sprite = self.missed_sprites[fall.lane]
        sprite.set_alpha(_fade(age, FALL_DURATION))
        y = fall.y + GRAVITY * age * age / 2
        canvas.blit(sprite, sprite.get_rect(midbottom=(round(fall.x), round(y))))

    @staticmethod
    def _darken(sprite):
        dark = sprite.copy()
        dark.fill(MISS_TINT, special_flags=pygame.BLEND_RGB_MULT)
        return dark
