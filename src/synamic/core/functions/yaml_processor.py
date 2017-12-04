# from ruamel.yaml import YAML
from ruamel.yaml import load, BaseLoader

# __yaml = YAML(typ="unsafe")


def load_yaml(text):
    # return __yaml.load(text)
    return load(text, BaseLoader)

