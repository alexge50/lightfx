from core.effects import Effect
from collections import namedtuple

import pyaudio

import numpy as np
import scipy.fftpack as fftpack
import scipy.signal
import colorsys

audio = pyaudio.PyAudio()

CHUNK = 2048
SAMPLE_RATE = 44100
TIME_STEP = 1. / SAMPLE_RATE
START_FREQUENCY = 20
END_FREQUENCY = 8280
BUFFER_SIZE = 8280 * 2


class MusicSync(Effect):
    OPTIONS_TYPE = None
    DEFAULT_OPTIONS = None

    def __init__(self):
        self.stream = audio.open(
            format=pyaudio.paFloat32,
            channels=2,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        self.buffer = np.array([0.] * BUFFER_SIZE)
        self.energy_blocks = np.array([0.] * (SAMPLE_RATE // CHUNK))
        self.past_intensity = np.array([0.] * (SAMPLE_RATE // CHUNK))
        self.past_saturation = np.array([0.] * SAMPLE_RATE)
        self.past_hues = np.array([0.] * 10)
        self.filtered_buffer = np.array([0.] * SAMPLE_RATE)
        self.current_color = np.array([0., 0., 0.])

    def run(self, delta_time, options):
        data = self.stream.read(CHUNK)
        data = np.frombuffer(data, dtype=np.float32)
        data = np.reshape(data, (-1, 2))
        self.buffer = np.append(self.buffer[CHUNK:], np.mean(data, axis=1))

        self.energy_blocks = np.append(self.energy_blocks[1:], np.sum((data[:, 0] ** 2 + data[:, 1] ** 2) / 2))

        self.past_intensity = np.clip((self.energy_blocks / CHUNK * 5) ** 2, 0, 0.2) * 5

        chunk = [np.max(self.filter((data[:, 0] + data[:, 1]) / 2, 200, SAMPLE_RATE, 6))] * CHUNK
        self.filtered_buffer = np.append(self.filtered_buffer[CHUNK:], chunk)

        self.past_saturation = np.append(self.past_saturation[CHUNK:], 1 - np.abs(data[:, 0] - data[:, 1]))

        data = self.buffer / np.max(np.abs(self.buffer))
        buffer_fft = fftpack.fft(data)
        power = np.abs(buffer_fft)
        power = 5 - 20 * np.log10(power / SAMPLE_RATE)
        power = power[:BUFFER_SIZE // 2]
        power = power / max(power)

        buckets = np.split(power, 360)
        buckets = np.array([np.max(x) for x in buckets])

        hue = np.argmax(buckets)

        self.past_hues = np.append(self.past_hues[1:], hue)
        self.past_hues[-1] = np.mean(self.past_hues)
        hue = self.past_hues[-1]

        if 0 <= self.filtered_buffer[-1] <= 0.7:
            bass_coeff = self.filtered_buffer[-1] / 0.7 * 0.1
        else:
            bass_coeff = 0.1 + (self.filtered_buffer[-1] - 0.7) / 0.3 * 0.9

        intensity = np.clip(self.past_intensity[-1] * (1. - bass_coeff), 0., 1.)

        self.current_color = (self.current_color * 0.5 + np.array([hue / 360, self.past_saturation[-1], intensity]) * 0.5)

        color = colorsys.hsv_to_rgb(h=self.current_color[0], s=self.current_color[1], v=self.current_color[2])

        return int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)

    @staticmethod
    def butter_lowpass(cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    @staticmethod
    def filter(data, cutoff, fs, order=5):
        b, a = MusicSync.butter_lowpass(cutoff, fs, order=order)
        y = scipy.signal.lfilter(b, a, data)
        return y
