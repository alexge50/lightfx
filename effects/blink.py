from core.effects import Effect
from collections import namedtuple

BlinkOptions = namedtuple('BlinkOptions', 'color time')


class Blink(Effect):
    OPTIONS_TYPE = BlinkOptions
    DEFAULT_OPTIONS = BlinkOptions((255, 0, 255), 0.5)

    def __init__(self):
        self.state = 1
        self.time = 0.

    def run(self, delta_time, options):
        self.time += delta_time / 1000

        color = ()

        if self.state == 1:
            color = options.color
        else:
            color = (0, 0, 0)

        if self.time > options.time:
            self.time = 0.
            self.state = 1 - self.state

        return color

