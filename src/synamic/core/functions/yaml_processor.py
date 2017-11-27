from ruamel.yaml import YAML

__yaml = YAML(typ="safe")


def load_yaml(text):
    return __yaml.load(text)

