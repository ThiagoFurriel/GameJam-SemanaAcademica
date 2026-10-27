import json
from dataclasses import dataclass
from pathlib import Path

from settings import LANES


@dataclass(frozen=True)
class Note:
    beat: float
    lane: int


@dataclass(frozen=True)
class Chart:
    bpm: float
    offset: float
    notes: tuple

    # o chart é escrito em beats; segundos só aparecem na hora de julgar,
    # assim mudar o bpm não exige reescrever as notas.
    def time_of(self, beat):
        return beat * 60 / self.bpm

    def beat_at(self, time):
        return time * self.bpm / 60


def load_chart(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    notes = []
    for beat, lane in data["notes"]:
        if not 0 <= lane < len(LANES):
            raise ValueError(f"{path}: a corda {lane} não existe (beat {beat})")
        notes.append(Note(float(beat), int(lane)))
    notes.sort(key=lambda note: note.beat)
    return Chart(float(data["bpm"]), float(data.get("offset", 0.0)), tuple(notes))
