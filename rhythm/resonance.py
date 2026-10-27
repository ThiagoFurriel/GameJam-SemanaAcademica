import math

from rhythm.judge import Grade

# começa baixa: o link já está amaldiçoado, e é tocando que o mundo recupera a cor
START = 0.4
GAINS = {Grade.PERFECT: 0.06, Grade.GOOD: 0.03, Grade.MISS: -0.12}
# rapidez com que o valor mostrado alcança o real; a mesma suavização do movimento do player
SMOOTHING = 6


class Resonance:
    """quanto do mundo do link ainda tem cor, de 0 a 1. chegando a zero, o silêncio vence."""

    def __init__(self):
        self.value = START
        # valor que a tela mostra: persegue o real aos poucos, sem degrau a cada nota
        self.displayed = START

    @property
    def depleted(self):
        return self.value <= 0

    def register(self, grade):
        self.value = min(1.0, max(0.0, self.value + GAINS[grade]))

    def update(self, dt):
        self.displayed += (self.value - self.displayed) * (1 - math.exp(-SMOOTHING * dt))
