from enum import Enum

# janelas em segundos, contadas a partir do instante exato da nota.
# julgar por tempo (e não por distância em pixels) deixa a "hitbox"
# independente do fps e da velocidade de rolagem das notas.
PERFECT_WINDOW = 0.070
GOOD_WINDOW = 0.130
MISS_WINDOW = 0.200


class Grade(Enum):
    PERFECT = "perfeito!"
    GOOD = "bom"
    MISS = "errou"


def judge(delta):
    """delta = momento do toque - momento da nota (negativo = adiantado)."""
    distance = abs(delta)
    if distance <= PERFECT_WINDOW:
        return Grade.PERFECT
    if distance <= GOOD_WINDOW:
        return Grade.GOOD
    if distance <= MISS_WINDOW:
        return Grade.MISS
    # fora de qualquer janela o toque não conta pra nota nenhuma
    return None
