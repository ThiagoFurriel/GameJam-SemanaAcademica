# ressonância mínima no fim da fase pra o deus aprovar e abrir a próxima.
# fica acima do valor inicial: passar é devolver ao mundo mais cor do que ele tinha.
APPROVAL_RESONANCE = 0.5


def approves(resonance):
    return resonance.value >= APPROVAL_RESONANCE


class Journey:
    """progresso da campanha: "link não escolhe o repertório", as fases abrem em ordem.

    o progresso vive só enquanto o jogo está aberto (sem save): decisão de jam,
    uma partida inteira cabe numa sessão.
    """

    def __init__(self, levels):
        self.levels = levels
        self.completed = set()

    def unlocked(self, level):
        index = self.levels.index(level)
        return index == 0 or self.levels[index - 1] in self.completed

    def complete(self, level):
        self.completed.add(level)

    @property
    def next_level(self):
        return next((level for level in self.levels if level not in self.completed), None)

    @property
    def finished(self):
        return self.next_level is None
