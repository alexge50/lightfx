from core.effects import Effect
from collections import namedtuple

SolidOptions = namedtuple('SolidOptions', 'color')


class Solid(Effect):
    OPTIONS_TYPE = SolidOptions
    DEFAULT_OPTIONS = SolidOptions((255, 0, 255))

    def run(self, delta_time, options):
        return options.color

