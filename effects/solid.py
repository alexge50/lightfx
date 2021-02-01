from core.effects import Effect
from collections import namedtuple

color = namedtuple('color', 'r g b')


class Solid(Effect):
    OPTIONS_TYPE = color
    DEFAULT_OPTIONS = color(255, 0, 255)

    def run(self, delta_time, options):
        return options[0], options[1], options[2]

