from collections import deque

from rhythm.judge import Grade
from rhythm.resonance import Resonance
from rhythm.score import Score
from settings import LANES


class Highway:
    """Coleta notas automaticamente na corda ocupada pelo personagem."""

    def __init__(self, chart, on_judge=None):
        self.chart = chart
        # on_judge(note, grade, song_time) avisa quem quiser reagir ao julgamento
        # (efeitos, sons) sem a highway precisar saber que eles existem
        self.on_judge = on_judge
        # Uma fila global mantém os julgamentos em ordem cronológica.
        self.pending = deque(chart.notes)
        # As filas por corda são usadas no desenho das notas.
        self.lanes = [deque() for _ in LANES]
        for note in chart.notes:
            self.lanes[note.lane].append(note)
        self.end_time = chart.time_of(chart.notes[-1].beat) if chart.notes else 0.0
        self.score = Score()
        self.resonance = Resonance()
        self.last_grade = None
        self.last_grade_time = 0.0

    def update(self, song_time, occupied_lane):
        while self.pending and not self.resonance.depleted:
            note = self.pending[0]
            if self.chart.time_of(note.beat) > song_time:
                break
            self.pending.popleft()
            self.lanes[note.lane].popleft()
            grade = Grade.PERFECT if note.lane == occupied_lane else Grade.MISS
            self._register(note, grade, song_time)

    def _register(self, note, grade, song_time):
        self.score.register(grade)
        self.resonance.register(grade)
        self.last_grade = grade
        self.last_grade_time = song_time
        if self.on_judge is not None:
            self.on_judge(note, grade, song_time)
