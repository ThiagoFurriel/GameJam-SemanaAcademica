from dataclasses import dataclass

from settings import CHARTS, MUSIC


@dataclass(frozen=True)
class Level:
    slug: str
    title: str
    god_sheet: str

    @property
    def background(self):
        return self.slug

    @property
    def clouds(self):
        return f"nuvem{self.slug}"

    @property
    def chart(self):
        return CHARTS / f"{self.slug}.json"

    @property
    def music(self):
        # .ogg tem prioridade; sem ele, usa o .wav gerado por generate_music.py
        for extension in (".ogg", ".wav"):
            path = MUSIC / f"{self.slug}{extension}"
            if path.exists():
                return path
        return MUSIC / f"{self.slug}.ogg"


# ordem da jornada: do deus mais calmo ao mais pesado
LEVELS = (
    Level("folk", "Folk", "deusafolksprite"),
    Level("glam", "Glam Rock", "deusaglamsprite"),
    Level("punk", "Punk", "deuspunksprite"),
    Level("metal", "Heavy Metal", "deusmetalsprite"),
)
