import os
from synamic.core.parsing_systems.curlybrace_parser import SydParser
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_file_contents(fn):
    full_fn = os.path.join(_BASE_DIR, fn)
    with open(full_fn, encoding='utf-8') as f:
        text = f.read()
    return text


class DefaultConfigManager:
    def __init__(self):
        self.__loaded = {}

    def get(self, name):
        if name in self.__loaded:
            sydC = self.__loaded[name]
        else:
            text = get_file_contents(name + '.syd')
            sydC = SydParser(text).parse()
            self.__loaded[name] = sydC
        return sydC
