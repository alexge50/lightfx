from core.effects import Effect


class Solid(Effect):
    OPTIONS_TYPE = tuple
    DEFAULT_OPTIONS = (255, 0, 255)

    def run(self, delta_time, options):
        return options
