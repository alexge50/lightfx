class Sink:
    pass


def is_sink(x) -> bool:
    if not isinstance(x, type):
        return False

    return issubclass(x, Sink)
