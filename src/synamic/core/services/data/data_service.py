"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import json
from synamic.core.standalones.functions.decorators import not_loaded


class Data:
    def get(self, item, default=None):
        raise NotImplemented

    def __getitem__(self, item):
        return self.get(item, None)

    def __repr__(self):
        return repr(self.__str__())


class FieldsData(Data):
    def __init__(self, ord_dict):
        self.__ord_dict = ord_dict

    def get(self, item, default=None):
        return self.__ord_dict.get(item, default)

    def __str__(self):
        return str(self.__ord_dict)


def get_from_dict(dict_map, dotted_keys, default):
    keys = dotted_keys.split('.')
    if len(keys) == 1:
        return dict_map.get(keys[0], default)
    else:
        last_value = dict_map
        for key in keys:
            if type(last_value) is dict:
                last_value = last_value.get(key)
            else:
                last_value = default
                break

        if last_value is dict_map or last_value is None:
            last_value = default
        return last_value


class JsonData(Data):
    def __init__(self, objdict):
        assert type(objdict) is dict
        self.__obj_dict = objdict

    def get(self, item, default=None):
        return get_from_dict(self.__obj_dict, item, default)

    def __str__(self):
        return str(self.__obj_dict)


class DataService:
    """
    Currently supports: 
    - syd (xxx.syd)
    - json (xxx.json)

    Supports have been removed for: (As I want to keep things clean and before syd like stuffs with lot of features including all those data type and conversions were not in synamic)
    - yaml (xxx.yaml, xxx.yml)
    - ini (xxx.ini)
    - toml (xxx.toml)
    """
    def __init__(self, site):
        self.__site = site
        self.__data_name_map = {}
        self.__is_loaded = False
        self.__service_home_path = None
        self.__site.register_path(self.service_home_path)

    @property
    def service_home_path(self):
        if self.__service_home_path is None:
            self.__service_home_path = self.__site.path_tree.create_cpath(('meta', 'data'))
        return self.__service_home_path

    @property
    def is_loaded(self):
        return self.__is_loaded

    def _get_file_content(self, fp):
        file_path = fp
        with file_path.open('r', encoding='utf-8') as f:
            model_txt = f.read()
        return model_txt

    @not_loaded
    def load(self):
        file_paths = self.service_home_path.list_files()

        for file_path in file_paths:
            if file_path.basename.endswith('.data.txt'):
                root_field = FieldParser(self._get_file_content(file_path)).parse()
                field_dict = root_field.to_dict_ordinary()
                data_obj = FieldsData(field_dict)
                data_name = file_path.basename[:-len('.data.txt')]

            elif file_path.basename.endswith('.json'):
                data_obj = JsonData(json.loads(self._get_file_content(file_path)))
                data_name = file_path.basename[:-len('.json')]
            else:
                # discard it
                continue

            self.__data_name_map[data_name] = data_obj

        self.__is_loaded = True

    def get(self, data_name):
        return self.__data_name_map.get(data_name, {})

    def __getitem__(self, item):
        return self.get(item)

    def __getattr__(self, item):
        return self.get(item)
