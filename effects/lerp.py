from core.effects import Effect
from collections import namedtuple

LerpOptions = namedtuple('LerpOptions', 'color1 color2 completion_speed')


class Lerp(Effect):
    OPTIONS_TYPE = LerpOptions
    DEFAULT_OPTIONS = LerpOptions((255, 0, 255), (0, 0, 0), 0.1)

    def __init__(self):
        self.previous_color = (255, 0, 255)
        self.target_color = (0, 0, 0)
        self.completion = 0.
        self.which_next = 1

    def run(self, delta_time, options):
        self.completion = min(self.completion, 1.)
        color = (
            (self.target_color[0] - self.previous_color[0]) * self.completion + self.previous_color[0],
            (self.target_color[1] - self.previous_color[1]) * self.completion + self.previous_color[1],
            (self.target_color[2] - self.previous_color[2]) * self.completion + self.previous_color[2],
        )

        self.completion += options.completion_speed * (delta_time / 1000)

        if self.completion > 1:
            self.previous_color = self.target_color

            if self.which_next == 1:
                self.target_color = options.color1
                self.which_next = 2
            else:
                self.target_color = options.color2
                self.which_next = 1
            self.completion = 0.

        return tuple(int(min(x, 255)) for x in color)

