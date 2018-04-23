"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


# from ruamel.yaml import YAML
from ruamel.yaml import load, BaseLoader

# __yaml = YAML(typ="unsafe")


def load_yaml(text):
    # return __yaml.load(text)
    return load(text, BaseLoader)

