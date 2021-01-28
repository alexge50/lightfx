import asyncio

from core.context import Context
import core.effects
from config import *


async def main_loop():
    context = Context(SINKS)

    for effect_file in EFFECTS:
        await context.add_effects(core.effects.load_effects(effect_file))

    await context.set_effect(DEFAULT_EFFECT)

    for controller in CONTROLLERS:
        await controller.start(context)

    while True:
        await context.frame()

        delta_time = await context.get_delta_time()
        effect_description = await context.get_effect_description()
        result = None

        if core.effects.is_effect_function(effect_description[0]):
            result = effect_description[0](delta_time, effect_description[1])
        elif effect_description[0] is not None:
            result = effect_description[0].run(delta_time, effect_description[1])

        for sink in context.sinks:
            await sink.sink(result)

        await asyncio.sleep(FRAME_TIME / 1000)


asyncio.run(main_loop())
