from synamic.core.functions.yaml_processor import load_yaml
from synamic.core.functions.normalizers import normalize_key, normalize_keys


class SiteSettings:
    def __init__(self, config):
        self.__config = config

        fn = config.settings_file_name
        full_fn = config.path_tree.get_full_path(fn)
        with open(full_fn, encoding='utf-8') as f:
            text = f.read()
        obj = load_yaml(text)

        if not obj:
            obj = {}

        self.__settings_obj = obj
        normalize_keys(self.__settings_obj)

    def __getitem__(self, item):
        item = normalize_key(item)
        return self.__settings_obj[item]

    def __setitem__(self, key, value):
        key = normalize_key(key)
        self.__settings_obj[key] = value

    def __delitem__(self, key):
        key = normalize_key(key)
        del self.__settings_obj[key]

    def __contains__(self, item):
        item = normalize_key(item)
        return item in self.__settings_obj

    def keys(self):
        return self.__settings_obj.keys()

    def values(self):
        return self.__settings_obj.values()

    def items(self):
        return self.__settings_obj.items()
