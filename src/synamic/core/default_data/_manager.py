import os
from synamic.core.parsing_systems.curlybrace_parser import SydParser
from synamic.core.parsing_systems.model_parser import ModelParser
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_file_contents(fn, default=None):
    full_fn = os.path.join(_BASE_DIR, fn)
    if not os.path.exists(full_fn):
        return default
    with open(full_fn, encoding='utf-8') as f:
        text = f.read()
    return text


class DefaultDataManager:
    def __init__(self):
        self.__loaded_syds = {}
        self.__loaded_models = {}

    def get_syd(self, name, default=None):
        if name in self.__loaded_syds:
            sydC = self.__loaded_syds[name]
        else:
            text = get_file_contents(name + '.syd', None)
            if text is None:
                return default
            sydC = SydParser(text).parse()
            self.__loaded_syds[name] = sydC
        return sydC

    def get_model(self, name, default=None):
        if name in self.__loaded_models:
            model = self.__loaded_models[name]
        else:
            text = get_file_contents(name + '.model', None)
            if text is None:
                return default
            model = ModelParser.parse(name, text)
            self.__loaded_models[name] = model
        return model
