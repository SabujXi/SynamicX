from synamic.core.functions.yaml_processor import load_yaml
from synamic.core.synamic_config import SynamicConfig


def get_site_root_settings(config: SynamicConfig):
    fn = config.root_config_file_name
    full_fn = config.path_tree.get_full_path(fn)
    with open(full_fn, encoding='utf-8') as f:
        text = f.read()
    obj = load_yaml(text)
    # print(obj)
    # print(type(obj))

    return obj



