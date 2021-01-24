from contextlib import contextmanager
from collections import namedtuple
from asyncio import Lock

import core.timer
import core.effects
import core.sinks

State = namedtuple("State", "options current_effect delta_time")


class Context:
    def __init__(self, sinks):
        self._effects = {}
        self._options = None
        self._current_effect = None
        self._lock = Lock()
        self._timer = core.timer.Timer()

        self.sinks = [x for x in sinks if core.sinks.is_sink(type(x))]

    @contextmanager
    async def state(self):
        try:
            async with self._lock:
                state = State(
                    options=self._options,
                    current_effect=self._current_effect,
                    delta_time=self._timer.delta_time
                )
                yield state
        finally:
            await self.set_effect(state.current_effect)
            await self.set_options(state.options)

    async def read_only_state(self):
        async with self._lock:
            return State(
                options=self._options,
                current_effect=self._current_effect,
                delta_time=self._timer.delta_time
            )

    async def add_effects(self, effects: dict):
        async with self._lock:
            self._effects.update(effects)

    async def set_effect(self, effect):
        async with self._lock:
            if isinstance(effect, str) and effect in self._effects:
                self._current_effect = self._effects[effect]()
                self._options = type(self._current_effect).default_options()
            elif core.effects.is_effect_function(effect):
                self._current_effect = effect
                self._options = None

    async def set_options(self, options):
        async with self._lock:
            if self._current_effect is str:
                if isinstance(options, type(self._current_effect).options_type()) or \
                        type(self._current_effect).options_type() is None:
                    self._options = options
            elif core.effects.is_effect_function(self._current_effect):
                self._options = options

    async def get_effect_description(self) -> ():
        async with self._lock:
            return self._current_effect, self._options

    async def frame(self):
        async with self._lock:
            self._timer.frame()

    async def get_delta_time(self):
        async with self._lock:
            return self._timer.delta_time
