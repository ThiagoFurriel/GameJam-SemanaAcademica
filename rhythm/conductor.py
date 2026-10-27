import time
from pathlib import Path

import pygame

# get_pos() trepida alguns ms a cada leitura, então só vale comparar de vez em
# quando e só corrigir quando o desvio passa claramente do ruído.
DRIFT_CHECK_INTERVAL = 1.0
DRIFT_TOLERANCE = 0.030
# fração do desvio corrigida por checagem: corrigir aos poucos evita que as notas pulem.
DRIFT_CORRECTION = 0.25


def _mixer_position():
    position = pygame.mixer.music.get_pos()
    return None if position < 0 else position / 1000


class Conductor:
    """relógio da fase: diz em que ponto da música estamos, em segundos."""

    def __init__(self, offset=0.0, music=None, clock=time.perf_counter, audio_position=None):
        # offset = segundos entre o início do arquivo de áudio e o beat 0 do chart
        self.offset = offset
        self.music = music
        self._clock = clock
        self._audio_position = audio_position
        self._has_music = False
        self._start = 0.0
        self._last_check = 0.0

    def start(self):
        if self.music is not None and Path(self.music).exists() and pygame.mixer.get_init():
            pygame.mixer.music.load(str(self.music))
            pygame.mixer.music.play()
            self._has_music = True
            if self._audio_position is None:
                self._audio_position = _mixer_position

        self._start = self._clock()
        self._last_check = self._start

    @property
    def song_time(self):
        return self._clock() - self._start - self.offset

    @property
    def music_playing(self):
        return self._has_music and pygame.mixer.music.get_busy()

    def update(self):
        if self._audio_position is None:
            return
        now = self._clock()
        if now - self._last_check < DRIFT_CHECK_INTERVAL:
            return
        self._last_check = now
        audio = self._audio_position()
        if audio is None:
            return
        drift = (now - self._start) - audio
        if abs(drift) > DRIFT_TOLERANCE:
            self._start += drift * DRIFT_CORRECTION

    def stop(self):
        if self._has_music:
            pygame.mixer.music.stop()
