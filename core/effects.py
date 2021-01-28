from inspect import signature, getmembers
import importlib.util
from pathlib import Path


class Effect:
    OPTIONS_TYPE = None
    DEFAULT_OPTIONS = None

    @classmethod
    def options_type(cls):
        return cls.OPTIONS_TYPE

    @classmethod
    def default_options(cls):
        return cls.DEFAULT_OPTIONS


def load_effects(file_path) -> {str: type}:
    module_name = Path(file_path).stem

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return dict(getmembers(module, is_effect_type))


def is_effect_type(x) -> bool:
    if not isinstance(x, type):
        return False

    return issubclass(x, Effect) and x is not Effect


def is_effect_function(x) -> bool:
    if callable(x):
        return len(signature(x).parameters) == 2