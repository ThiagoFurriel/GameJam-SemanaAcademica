from dataclasses import dataclass, field

from rhythm.judge import Grade

POINTS = {Grade.PERFECT: 300, Grade.GOOD: 100, Grade.MISS: 0}


@dataclass
class Score:
    points: int = 0
    combo: int = 0
    max_combo: int = 0
    counts: dict = field(default_factory=lambda: dict.fromkeys(Grade, 0))

    def register(self, grade):
        self.counts[grade] += 1
        self.points += POINTS[grade]
        if grade is Grade.MISS:
            self.combo = 0
        else:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
