from core.effects import Effect
from collections import namedtuple
import random

BlinkRandomOptions = namedtuple('BlinkRandomOptions', 'color_palette time')


class BlinkRandom(Effect):
    OPTIONS_TYPE = BlinkRandomOptions
    DEFAULT_OPTIONS = BlinkRandomOptions([], 0.5)

    def __init__(self):
        self.state = 0
        self.time = 0.
        self.color = (0, 0, 0)

    def run(self, delta_time, options):
        self.time += delta_time / 1000

        color = (0, 0, 0)

        if self.state == 1:
            color = self.color
        else:
            color = (0, 0, 0)
            if len(options.color_palette) == 0:
                self.color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
            else:
                self.color = options.color_palette[random.randint(0, len(options.color_palette) - 1)]

        if self.time > options.time:
            self.time = 0.
            self.state = 1 - self.state

        return tuple(color)

