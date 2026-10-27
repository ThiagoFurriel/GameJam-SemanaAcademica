"""Gera a música de cada fase a partir dos charts.

    python generate_music.py              # todas: charts/*.json -> music/<fase>.wav
    python generate_music.py folk metal   # só as fases pedidas

Precisa de numpy e scipy:  pip install numpy scipy
O estilo (folk, glam, punk, metal) vem do nome do JSON.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "music"))

import rock_theme  # noqa: E402


def main(slugs):
    paths = sorted((ROOT / "charts").glob("*.json"))
    if slugs:
        paths = [path for path in paths if path.stem in slugs]
    if not paths:
        print("nenhum chart encontrado")
        return 1

    for path in paths:
        try:
            style = rock_theme.style_from_path(path)
        except ValueError as error:
            print(f"pulando {path.name}: {error}")
            continue
        audio = rock_theme.chart_audio(str(path), style)
        out = ROOT / "music" / f"{path.stem}.wav"
        rock_theme.save_song(out, audio)
        print(f"{out.relative_to(ROOT)}  ({len(audio) / rock_theme.SAMPLE_RATE:.1f} s, estilo {style})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
