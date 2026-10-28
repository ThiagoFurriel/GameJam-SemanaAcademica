from collections import deque

from rhythm.judge import MISS_WINDOW, Grade, judge
from rhythm.resonance import Resonance
from rhythm.score import Score
from settings import LANES


class Highway:
    """notas pendentes de cada corda e o julgamento dos toques."""

    def __init__(self, chart, on_judge=None):
        self.chart = chart
        # on_judge(note, grade, song_time) avisa quem quiser reagir ao julgamento
        # (efeitos, sons) sem a highway precisar saber que eles existem
        self.on_judge = on_judge
        # uma fila por corda, em ordem de beat: a próxima nota a julgar é sempre
        # a da frente, então cada toque custa O(1) em vez de varrer o chart.
        self.lanes = [deque() for _ in LANES]
        for note in chart.notes:
            self.lanes[note.lane].append(note)
        self.end_time = chart.time_of(chart.notes[-1].beat) if chart.notes else 0.0
        self.score = Score()
        self.resonance = Resonance()
        self.last_grade = None
        self.last_grade_time = 0.0

    def press(self, lane, song_time):
        # o toque é lido no frame em que o evento chega (até ~16ms de atraso a 60fps);
        # as janelas de julgamento já absorvem essa diferença.
        notes = self.lanes[lane]
        self._expire(notes, song_time)
        if not notes:
            return None
        grade = judge(song_time - self.chart.time_of(notes[0].beat))
        if grade is not None:
            self._register(notes.popleft(), grade, song_time)
        return grade

    def update(self, song_time):
        for notes in self.lanes:
            self._expire(notes, song_time)

    def _expire(self, notes, song_time):
        # nota que já passou da última janela não pode mais ser acertada
        while notes and song_time - self.chart.time_of(notes[0].beat) > MISS_WINDOW:
            self._register(notes.popleft(), Grade.MISS, song_time)

    def _register(self, note, grade, song_time):
        self.score.register(grade)
        self.resonance.register(grade)
        self.last_grade = grade
        self.last_grade_time = song_time
        if self.on_judge is not None:
            self.on_judge(note, grade, song_time)
