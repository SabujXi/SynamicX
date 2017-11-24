from ruamel.yaml import YAML
from synamic.core.synamic_config import SynamicConfig


def get_site_root_settings(config: SynamicConfig):
    yaml = YAML(typ="safe")
    fn = config.root_config_file_name
    full_fn = config.path_tree.get_full_path(fn)
    with open(full_fn, encoding='utf-8') as f:
        text = f.read()
    obj = yaml.load(text)
    # print(obj)
    # print(type(obj))

    return obj



