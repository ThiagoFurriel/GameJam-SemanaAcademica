import pygame

IDLE_FPS = 4


class GodFigure:
    """um deus em cena. animated=False deixa ele parado no primeiro quadro (retratos da abertura)."""

    def __init__(self, frames, topleft, animated=True):
        self.frames = frames
        self.topleft = topleft
        self.animated = animated

    def draw(self, canvas, time, shift=0, alpha=255):
        """shift e alpha servem pra entrada deslizando com fade."""
        frame = self.frames[int(time * IDLE_FPS) % len(self.frames)] if self.animated else self.frames[0]
        if alpha < 255:
            # multiplica o alpha de cada pixel numa cópia, em vez de set_alpha na imagem:
            # o resultado é o mesmo em qualquer driver de vídeo
            frame = frame.copy()
            frame.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        canvas.blit(frame, (self.topleft[0] + shift, self.topleft[1]))
