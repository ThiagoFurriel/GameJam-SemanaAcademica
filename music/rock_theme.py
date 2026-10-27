"""Trilhas de rock originais feitas com numpy, sem alterar a classe Music.

1) Tema original (guitarra + voz, Mi menor, 140 BPM):
       python rock_theme.py

2) Músicas das fases, a partir dos JSONs (folk, glam, metal, punk):
       python rock_theme.py folk.json glam.json metal.json punk.json

   Formato do JSON:
       bpm    -> batidas por minuto
       offset -> atraso (em segundos) antes de começar
       notes  -> [[tempo_em_batidas, corda], ...]   (corda de 0 a 4)

   Cada nota do JSON toca uma nota da escala do estilo (corda 0 = mais grave,
   corda 4 = mais aguda), em cima de um acompanhamento (baixo, guitarra base
   e bateria) com a cara de cada estilo.

O Music só é usado na hora de tocar (mixer e canal).
"""

import json
import math
import os
import sys

import numpy as np
from scipy.io.wavfile import write

SAMPLE_RATE = 44100
BPM = 140
BEAT = 60 / BPM  # duração de 1 tempo do tema original, em segundos

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# ---------- notas e frequências ----------

def note_to_freq(note):
    """'E2' -> 82.41 Hz (temperamento igual, A4 = 440 Hz)."""
    name, octave = note[:-1], int(note[-1])
    midi = 12 * (octave + 1) + NOTE_NAMES.index(name)
    return 440.0 * 2 ** ((midi - 69) / 12)


def power_chord(f):
    """Tônica + quinta + oitava."""
    return [f, f * 2 ** (7 / 12), f * 2]


def triad(f):
    """Acorde maior: tônica + terça + quinta."""
    return [f, f * 2 ** (4 / 12), f * 2 ** (7 / 12)]


def _fit(wave):
    peak = np.max(np.abs(wave))
    return wave / peak if peak > 0 else wave


def _envelope(n, attack=0.004, release=0.015, decay_tau=None):
    """Ataque rápido, decaimento exponencial opcional e release curto (evita cliques)."""
    t = np.arange(n) / SAMPLE_RATE
    env = np.ones(n)
    if decay_tau:
        env *= np.exp(-t / decay_tau)
    a = min(n, int(attack * SAMPLE_RATE))
    r = min(n, int(release * SAMPLE_RATE))
    if a:
        env[:a] *= np.linspace(0, 1, a)
    if r:
        env[-r:] *= np.linspace(1, 0, r)
    return env


# ---------- instrumentos (sempre em segundos) ----------

def distorted_tone(freqs, dur, gain=5, tau=0.6, harmonics=6):
    """Guitarra distorcida: harmônicos tipo serra + saturação (tanh)."""
    n = max(1, int(dur * SAMPLE_RATE))
    t = np.arange(n) / SAMPLE_RATE
    wave = np.zeros(n)
    for f in freqs:
        for k in range(1, harmonics + 1):
            if f * k < SAMPLE_RATE / 2:
                wave += np.sin(2 * np.pi * f * k * t) / k
    wave = np.tanh(gain * _fit(wave))
    return _fit(wave) * _envelope(n, decay_tau=tau)


def pluck_tone(freqs, dur, tau=0.7):
    """Violão/banjo sintético: harmônicos agudos somem mais rápido."""
    n = max(1, int(dur * SAMPLE_RATE))
    t = np.arange(n) / SAMPLE_RATE
    wave = np.zeros(n)
    for f in freqs:
        for k in range(1, 9):
            if f * k < SAMPLE_RATE / 2:
                wave += np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (1 + 0.8 * k) / tau)
    return _fit(wave) * _envelope(n, attack=0.002, release=0.02)


def lead_tone(f, dur, gain=4, vibrato=0.0, odd_only=False, tau=None):
    """Solo/lead: serra (ou quadrada, só harmônicos ímpares) saturada, com vibrato opcional."""
    n = max(1, int(dur * SAMPLE_RATE))
    t = np.arange(n) / SAMPLE_RATE
    phase = 2 * np.pi * f * t + vibrato * np.clip(t / 0.2, 0, 1) * np.sin(2 * np.pi * 5.5 * t)
    ks = range(1, 9, 2) if odd_only else range(1, 9)
    wave = sum(np.sin(k * phase) / k for k in ks)
    wave = np.tanh(gain * _fit(wave))
    return _fit(wave) * _envelope(n, attack=0.005, release=0.03, decay_tau=tau)


def bass_tone(f, dur):
    n = max(1, int(dur * SAMPLE_RATE))
    t = np.arange(n) / SAMPLE_RATE
    wave = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t)
    return _fit(wave) * _envelope(n, attack=0.003, release=0.02, decay_tau=0.35)


def voice_tone(f, dur):
    """Voz sintética: fundamental + harmônicos, com vibrato que entra aos poucos."""
    n = max(1, int(dur * SAMPLE_RATE))
    t = np.arange(n) / SAMPLE_RATE
    vibrato_depth = 0.6 * np.clip(t / 0.25, 0, 1)
    phase = 2 * np.pi * f * t + vibrato_depth * np.sin(2 * np.pi * 5.5 * t)
    wave = (np.sin(phase) + 0.45 * np.sin(2 * phase)
            + 0.25 * np.sin(3 * phase) + 0.10 * np.sin(4 * phase))
    return _fit(wave) * _envelope(n, attack=0.03, release=0.06)


# ---------- bateria ----------

def _drum_kick():
    n = int(0.25 * SAMPLE_RATE)
    t = np.arange(n) / SAMPLE_RATE
    freq = 45 + 90 * np.exp(-t / 0.035)  # "pancada" que desce de agudo para grave
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    return _fit(np.sin(phase) * np.exp(-t / 0.09))


def _drum_snare():
    rng = np.random.default_rng(1)
    n = int(0.2 * SAMPLE_RATE)
    t = np.arange(n) / SAMPLE_RATE
    noise = rng.standard_normal(n)
    return _fit(0.7 * noise * np.exp(-t / 0.05) + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.06))


def _drum_hat():
    rng = np.random.default_rng(2)
    n = int(0.07 * SAMPLE_RATE)
    t = np.arange(n) / SAMPLE_RATE
    noise = np.diff(rng.standard_normal(n), prepend=0)  # ruído filtrado (só agudos)
    return _fit(noise * np.exp(-t / 0.018))


DRUM_SOUNDS = {"kick": _drum_kick(), "snare": _drum_snare(), "hat": _drum_hat()}


# ====================================================================
# 1) Tema original (guitarra + voz)
# ====================================================================

def guitar(note, beats):
    """Power chord distorcido; notas curtas = palm mute."""
    tau = 0.10 if beats <= 0.5 else 0.60
    return distorted_tone(power_chord(note_to_freq(note)), beats * BEAT, gain=5, tau=tau)


def voice(note, beats):
    return voice_tone(note_to_freq(note), beats * BEAT)


GUITAR_RIFF = [  # 2 compassos, tocados 2x
    ("E2", .5), ("E2", .5), ("G2", .5), ("E2", .5), ("A2", .5), ("E2", .5), ("B2", .5), ("E2", .5),
    ("E2", .5), ("E2", .5), ("G2", .5), ("A2", .5), ("B2", 1), (None, 1),
]
GUITAR_CHORUS = [
    ("C3", 2), ("D3", 2),
    ("E3", 4),
    ("C3", 2), ("D3", 2),
    ("E3", 3), (None, 1),
]
GUITAR = GUITAR_RIFF * 2 + GUITAR_CHORUS

VOICE = [
    (None, 8),                                                       # compassos 1-2: só guitarra
    ("B4", 1), ("B4", .5), ("D5", .5), ("E5", 1), ("D5", 1),         # compasso 3
    ("B4", 1.5), ("A4", .5), ("G4", 2),                              # compasso 4
    ("E5", 2), ("D5", 2),                                            # compasso 5
    ("B4", 2), ("G4", 1), ("A4", 1),                                 # compasso 6
    ("E5", 2), ("G5", 1), ("E5", 1),                                 # compasso 7
    ("E5", 3), (None, 1),                                            # compasso 8
]


def render_track(events, instrument):
    """Coloca cada nota no seu tempo e soma tudo numa faixa float."""
    total_beats = sum(beats for _, beats in events)
    track = np.zeros(int(total_beats * BEAT * SAMPLE_RATE) + SAMPLE_RATE // 10)
    pos = 0.0
    for note, beats in events:
        if note is not None:
            wave = instrument(note, beats)
            start = int(pos * BEAT * SAMPLE_RATE)
            track[start:start + len(wave)] += wave
        pos += beats
    return track


def _to_int16(mix):
    mix = mix * (0.9 / np.max(np.abs(mix)))  # normaliza com folga
    return (mix * 32767).astype(np.int16)


def build_song(guitar_volume=0.6, voice_volume=0.4):
    """Tema original como array int16 (mono)."""
    g = render_track(GUITAR, guitar)
    v = render_track(VOICE, voice)
    mix = np.zeros(max(len(g), len(v)))
    mix[:len(g)] += g * guitar_volume
    mix[:len(v)] += v * voice_volume
    return _to_int16(mix)


# ====================================================================
# 2) Músicas das fases (JSON -> áudio)
# ====================================================================
#
# Para cada estilo:
#   lanes        -> nota de cada corda (0..4), sempre numa escala que combina com os acordes
#   progression  -> raiz do baixo em cada compasso (repete em loop)
#   chord        -> "power" (tônica+quinta) ou "triad" (acorde maior)
#   guitar_kind  -> "pluck" (violão) ou "dist" (guitarra distorcida)
#   guitar_up    -> sobe a guitarra N oitavas em relação ao baixo
#   guitar/bass  -> padrão de um compasso: (posição em tempos, duração em tempos[, intervalo em semitons])
#   drums        -> posições (em tempos) de cada peça da bateria em um compasso
#   lead         -> timbre da melodia (as notas do JSON)

STYLES = {
    # Folk: acústico, tríades maiores, baixo "boom" e violão "chick", sem peso na bateria.
    "folk": dict(
        lanes=["G4", "A4", "B4", "D5", "E5"],            # G maior pentatônica
        progression=["G2", "C3", "D3", "G2"],            # I - IV - V - I
        chord="triad", guitar_kind="pluck", guitar_up=1,
        guitar=[(0, .9), (1, .45), (1.5, .45), (2.5, .45), (3, .9)],
        bass=[(0, .9, 0), (2, .9, 7)],                   # tônica e quinta alternadas
        drums={"kick": [0, 2], "hat": [.5, 1.5, 2.5, 3.5]},
        drum_vol={"kick": .35, "snare": .3, "hat": .15},
        lead=dict(kind="pluck", tau=.5, max_beats=1.0),
        mix=dict(lead=.6, guitar=.35, bass=.45, drums=1.0),
    ),
    # Glam: power chords brilhantes, pisada forte (bumbo 1 e 3, caixa 2 e 4), lead com vibrato.
    "glam": dict(
        lanes=["A4", "B4", "C#5", "E5", "F#5"],          # Lá maior pentatônica
        progression=["A2", "D3", "E3", "A2"],            # I - IV - V - I
        chord="power", guitar_kind="dist", guitar_up=1, gain=3,
        guitar=[(0, 1.4), (1.5, .45), (2, 1.4), (3.5, .45)],
        bass=[(0, .9, 0), (1.5, .4, 0), (2, .9, 0), (3.5, .4, 0)],
        drums={"kick": [0, 2], "snare": [1, 3]},
        drum_vol={"kick": .8, "snare": .6, "hat": .25},
        lead=dict(kind="lead", gain=3, vibrato=.9, max_beats=1.5),
        mix=dict(lead=.55, guitar=.5, bass=.4, drums=.9),
    ),
    # Metal: afinação grave, "galope" em semicolcheias, bumbo duplo, lead bem saturado, escala frígia.
    "metal": dict(
        lanes=["E4", "F4", "G4", "A4", "B4"],            # Mi frígio (a segunda menor dá o peso)
        progression=["E2", "E2", "G2", "F2"],
        chord="power", guitar_kind="dist", guitar_up=0, gain=9,
        guitar=[(p, .2) for p in (0, .5, .75, 1, 1.5, 1.75, 2, 2.5, 2.75, 3, 3.5, 3.75)],
        bass=[(0, .5, 0), (1, .5, 0), (2, .5, 0), (3, .5, 0)],
        drums={"kick": [0, .5, .75, 1, 1.5, 1.75, 2, 2.5, 2.75, 3, 3.5, 3.75],
               "snare": [1, 3], "hat": [0, .5, 1, 1.5, 2, 2.5, 3, 3.5]},
        drum_vol={"kick": .8, "snare": .6, "hat": .2},
        lead=dict(kind="lead", gain=9, vibrato=.0, max_beats=.9, tau=1.2),
        mix=dict(lead=.5, guitar=.55, bass=.35, drums=.9),
    ),
    # Punk: power chords em colcheias seguidas (palhetada para baixo), bateria seca e reta, lead cru.
    "punk": dict(
        lanes=["D4", "E4", "F#4", "A4", "B4"],           # Ré maior pentatônica
        progression=["D2", "G2", "A2", "A2"],            # I - IV - V - V
        chord="power", guitar_kind="dist", guitar_up=1, gain=6,
        guitar=[(p, .45) for p in (0, .5, 1, 1.5, 2, 2.5, 3, 3.5)],
        bass=[(p, .45, 0) for p in (0, .5, 1, 1.5, 2, 2.5, 3, 3.5)],
        drums={"kick": [0, 2, 2.5], "snare": [1, 3], "hat": [0, .5, 1, 1.5, 2, 2.5, 3, 3.5]},
        drum_vol={"kick": .8, "snare": .7, "hat": .25},
        lead=dict(kind="lead", gain=6, vibrato=.0, odd_only=True, max_beats=.8),
        mix=dict(lead=.5, guitar=.5, bass=.35, drums=.9),
    ),
}


def load_chart(path):
    """Lê o JSON da fase: {'bpm', 'offset', 'notes': [[tempo, corda], ...]}."""
    with open(path, encoding="utf-8") as f:
        chart = json.load(f)
    chart.setdefault("offset", 0.0)
    chart["notes"] = sorted(chart["notes"])
    return chart


def style_from_path(path):
    """'fases/folk.json' -> 'folk' (aceita também prefixos como 'abc-folk.json')."""
    stem = os.path.splitext(os.path.basename(path))[0].lower()
    for candidate in (stem, stem.split("-")[-1], stem.split("_")[-1]):
        if candidate in STYLES:
            return candidate
    raise ValueError(f"Estilo desconhecido em '{path}'. Use um de: {', '.join(STYLES)}")


def _lead_wave(style, freq, dur):
    cfg = style["lead"]
    if cfg["kind"] == "pluck":
        return pluck_tone([freq], dur, tau=cfg["tau"])
    return lead_tone(freq, dur, gain=cfg["gain"], vibrato=cfg.get("vibrato", 0.0),
                     odd_only=cfg.get("odd_only", False), tau=cfg.get("tau"))


def _guitar_wave(style, freqs, dur, dur_beats):
    if style["guitar_kind"] == "pluck":
        return pluck_tone(freqs, dur, tau=0.6)
    tau = 0.08 if dur_beats <= 0.5 else 0.6  # curtas = palm mute
    return distorted_tone(freqs, dur, gain=style["gain"], tau=tau)


def build_chart_song(chart, style_name):
    """Transforma o chart (JSON) numa música completa em int16 (mono)."""
    style = STYLES[style_name]
    beat = 60 / chart["bpm"]
    offset = chart["offset"]
    notes = chart["notes"]

    last_beat = max(b for b, _ in notes)
    bars = math.ceil(last_beat / 4) + 1  # 1 compasso extra para a música "fechar"
    total = int((offset + bars * 4 * beat) * SAMPLE_RATE) + SAMPLE_RATE  # + cauda de 1 s
    tracks = {name: np.zeros(total) for name in ("lead", "guitar", "bass", "drums")}

    def put(name, wave, beat_pos, volume=1.0):
        start = int((offset + beat_pos * beat) * SAMPLE_RATE)
        end = min(total, start + len(wave))
        if start < end:
            tracks[name][start:end] += wave[:end - start] * volume

    # acompanhamento, compasso a compasso
    for bar in range(bars):
        bar_beat = bar * 4
        root = note_to_freq(style["progression"][bar % len(style["progression"])])

        chord_base = root * 2 ** style["guitar_up"]
        chord = triad(chord_base) if style["chord"] == "triad" else power_chord(chord_base)
        for pos, dur_beats in style["guitar"]:
            put("guitar", _guitar_wave(style, chord, dur_beats * beat, dur_beats), bar_beat + pos)

        for pos, dur_beats, semitones in style["bass"]:
            put("bass", bass_tone(root * 2 ** (semitones / 12), dur_beats * beat), bar_beat + pos)

        for piece, positions in style["drums"].items():
            for pos in positions:
                put("drums", DRUM_SOUNDS[piece], bar_beat + pos, style["drum_vol"][piece])

    # melodia: cada nota do JSON vira uma nota da escala do estilo
    for i, (b, lane) in enumerate(notes):
        gap = notes[i + 1][0] - b if i + 1 < len(notes) else 1.0
        dur_beats = max(0.1, min(gap * 0.95, style["lead"]["max_beats"]))
        freq = note_to_freq(style["lanes"][int(lane)])
        put("lead", _lead_wave(style, freq, dur_beats * beat), b)

    mix = sum(tracks[name] * volume for name, volume in style["mix"].items())
    return _to_int16(mix)


def chart_audio(path, style=None):
    """Atalho: caminho do JSON -> áudio int16. O estilo vem do nome do arquivo."""
    return build_chart_song(load_chart(path), style or style_from_path(path))


# ---------- saída ----------

def save_song(filename, audio):
    write(filename, SAMPLE_RATE, audio)


def audio_to_sound(audio):
    """int16 mono -> pygame Sound (duplica os canais se o mixer for estéreo)."""
    import pygame

    channels = pygame.mixer.get_init()[2]
    if channels > 1:
        audio = np.column_stack([audio] * channels)
    return pygame.sndarray.make_sound(audio)


def play_audio(audio, music=None):
    """Toca e espera acabar, usando o mixer/canal da sua classe Music (sem modificá-la)."""
    import pygame
    from Music import Music

    music = music or Music()
    music.channel.play(audio_to_sound(audio))
    while music.channel.get_busy():
        pygame.time.wait(50)
    return music


if __name__ == "__main__":
    if len(sys.argv) == 1:
        song = build_song()
        save_song("rock_theme.wav", song)
        print(f"rock_theme.wav gerado ({len(song) / SAMPLE_RATE:.1f} s)")
        play_audio(song)
    else:
        music = None
        for path in sys.argv[1:]:
            style = style_from_path(path)
            song = chart_audio(path, style)
            out = f"{style}.wav"
            save_song(out, song)
            print(f"{out} gerado ({len(song) / SAMPLE_RATE:.1f} s)")
            music = play_audio(song, music)
