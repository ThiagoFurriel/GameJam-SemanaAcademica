import pygame

BORDER = "#0c0912"


def present(canvas, window):
    # tudo é desenhado no canvas em resolução fixa e só aqui é escalado pra janela,
    # mantendo a proporção e preenchendo a sobra com borda.
    canvas_width, canvas_height = canvas.get_size()
    width, height = window.get_size()
    scale = min(width / canvas_width, height / canvas_height)
    target = (max(1, int(canvas_width * scale)), max(1, int(canvas_height * scale)))
    window.fill(BORDER)
    window.blit(
        pygame.transform.scale(canvas, target),
        ((width - target[0]) // 2, (height - target[1]) // 2),
    )
    pygame.display.flip()
