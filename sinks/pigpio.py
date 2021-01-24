import pigpio
from core.sinks import Sink


class PiSink(Sink):
    def __init__(self, pins=(23, 24, 25), remote=''):
        self.pi = pigpio.pi(remote)
        self.pins = pins

    async def sink(self, x):
        for i in range(3):
            self.pi.set_PWM_dutycycle(self.pins[i], x[i])
