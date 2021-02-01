class LightFxException(Exception):
    pass


class InvalidOptions(LightFxException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class EffectNameNotFound(LightFxException):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'effect {self.name} not registered'


class IncorrectEffectType(LightFxException):
    def __init__(self, type_):
        self.type = type_

    def __str__(self):
        return f'effect type {self.type} is not valid'