import numpy as np
import pygame
from scipy.io.wavfile import write

NOTE_FREQUENCIES = {
    "C4": 261.63,
    "C#4": 277.18,
    "D4": 293.66,
    "D#4": 311.13,
    "E4": 329.63,
    "F4": 349.23,
    "F#4": 369.99,
    "G4": 392.00,
    "G#4": 415.30,
    "A4": 440.00,
    "A#4": 466.16,
    "B4": 493.88,
}


class Music:
    """Gera, toca e salva notas senoidais (mono, 16 bits).

    Relação básica: T = N / f
        T => duração do áudio (s)
        f => taxa de amostragem (Hz)
        N => número de amostras
    """

    SAMPLE_RATE = 44100
    MAX_AMPLITUDE = 32767  # maior valor de um inteiro de 16 bits com sinal
    BUFFER_SIZE = 2**9

    def __init__(self):
        # Se o mixer já foi iniciado (ex.: por pygame.init()), o init abaixo
        # seria ignorado e as configurações não valeriam. Reinicia antes.
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        pygame.mixer.init(
            frequency=self.SAMPLE_RATE,
            size=-16,  # inteiros de 16 bits com sinal
            channels=1,  # mono
            buffer=self.BUFFER_SIZE,
        )
        self.channel = pygame.mixer.Channel(0)

    # ---------- geração ----------

    def _generate_wave(self, note, duration):
        """Retorna a onda da nota como array numpy int16."""
        pure_note = note[:-1]
        octave = int(note[-1])
        factor = pure_note * 2 ** (octave - 4)
        freq = NOTE_FREQUENCIES[f'{pure_note}4'] * factor
        n_samples = int(duration * self.SAMPLE_RATE)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        wave = np.sin(2 * np.pi * freq * t)  # onda de -1 a 1
        return (wave * self.MAX_AMPLITUDE).astype(np.int16)

    def generate_note(self, note, duration):
        """Retorna a nota como pygame.mixer.Sound."""
        wave = self._generate_wave(note, duration)
        mixer_channels = pygame.mixer.get_init()[2]
        if mixer_channels > 1:
            # Mixer estéreo exige array 2D (amostras, canais)
            wave = np.column_stack([wave] * mixer_channels)
        return pygame.sndarray.make_sound(wave)

    # ---------- reprodução ----------

    def play_note(self, note, duration=0.25):
        if self.channel.get_busy():
            return
        self.channel.play(self.generate_note(note, duration))

    # ---------- gravação ----------

    def save_note(self, note, filename, duration=0.25):
        write(filename, self.SAMPLE_RATE, self._generate_wave(note, duration))

    def save_notes(self, filename, *notes, duration=0.25):
        waves = [self._generate_wave(note, duration) for note in notes]
        write(filename, self.SAMPLE_RATE, np.concatenate(waves))