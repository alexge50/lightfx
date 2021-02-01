from sinks.pigpio import PiSink
from controllers.shellsocket import ShellSocket


EFFECTS = [
]


SINKS = [
    PiSink((23, 24, 25))
]

CONTROLLERS = [
    ShellSocket()
]

DEFAULT_EFFECT = 'Solid'

FRAME_TIME = 16  # ms
