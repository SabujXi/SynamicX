from synamic.core.functions.normalizers import normalize_key, normalize_keys
from synamic.core.new_parsers.document_parser import FieldParser


class SiteSettings:
    def __init__(self, config):
        self.__config = config

        fn = config.settings_file_name
        full_fn = config.path_tree.get_full_path(fn)
        with open(full_fn, encoding='utf-8') as f:
            text = f.read()
        self.__root_field = FieldParser(text).parse()

    def __getitem__(self, item):
        return self.__root_field[item].to_dict()

    def __contains__(self, item):
        return item in self.__root_field.children_map

    def get(self, key, default):
        return self.__root_field.children_map.get(key, default)

    def keys(self):
        return tuple(self.__root_field.to_dict().keys())

    def values(self):
        return tuple(self.__root_field.to_dict().values())

    def items(self):
        return tuple(self.__root_field.to_dict().items())

    def __str__(self):
        return str(self.__root_field.to_dict())

    def __repr__(self):
        return repr(self.__str__())
