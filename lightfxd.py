import asyncio
import importlib.util
from dataclasses import dataclass
import argparse
import glob

from core.context import Context
import core.effects


@dataclass
class Config:
    effects: list
    sinks: list
    controllers: list
    default_effect: object
    frame_time: int


def load_config(path):
    spec = importlib.util.spec_from_file_location('config', path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    return config


async def main_loop(config: Config):
    context = Context(config.sinks)

    for effect_file in config.effects:
        await context.add_effects(core.effects.load_effects(effect_file))

    if config.default_effect is not None:
        await context.set_effect(config.default_effect)

    for controller in config.controllers:
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

        await asyncio.sleep(config.frame_time / 1000)


config = Config([], [], [], None, 10)

config.effects = glob.glob('effects/*.py')

parser = argparse.ArgumentParser(description='lightfx daemon')
parser.add_argument('--config', nargs=1, default=None, help="config file path")

args = parser.parse_args()

if args.config is not None:
    config_script = load_config(args.config[0])

    if 'EFFECTS' in dir(config_script):
        config.effects.extend(config_script.EFFECTS)

    if 'SINKS' in dir(config_script):
        config.sinks.extend(config_script.SINKS)

    if 'CONTROLLERS' in dir(config_script):
        config.controllers.extend(config_script.CONTROLLERS)

    if 'DEFAULT_EFFECT' in dir(config_script):
        config.default_effect = config_script.DEFAULT_EFFECT

    if 'FRAME_TIME' in dir(config_script):
        config.frame_time = config_script.FRAME_TIME


asyncio.run(main_loop(config))
