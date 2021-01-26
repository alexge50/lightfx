import time


class Timer:
    def __init__(self, sleep=16):
        self.delta_time = 0
        self._previous_time = time.time_ns() / 1000000
        self._time = time.time_ns() / 1000000

    def frame(self):
        self._time = time.time_ns() / 1000000
        self.delta_time = self._time - self._previous_time
        self._previous_time = self._time
