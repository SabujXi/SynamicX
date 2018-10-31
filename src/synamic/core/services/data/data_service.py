"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import configparser, json, toml
from synamic.core.standalones.functions.yaml_processor import load_yaml
from synamic.core.services.filesystem.content_path import _CPath
from synamic.core.parsing_systems.document_parser import FieldParser
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


class IniData(Data):
    def __init__(self, safeConfig: configparser.ConfigParser):
        self.__safe_config = safeConfig

    def get(self, item, default=None):
        try:
            section, option = item.split('.')
        except ValueError:
            # raise Exception('You are using a ini data and you must provide a section and a option')
            return default
        try:
            value = self.__safe_config.get(section, option)
        except configparser.NoSectionError:
            return default
        except configparser.NoOptionError:
            return default
        return value

    def ini_get(self, section, option, default):
        try:
            value = self.__safe_config.get(section, option)
        except configparser.NoSectionError:
            return default
        except configparser.NoOptionError:
            return default
        return value



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


class TomlData(Data):
    def __init__(self, dict_obj):
        self.__dict_obj = dict_obj

    def get(self, item, default=None):
        return get_from_dict(self.__dict_obj, item, default)

    def __str__(self):
        return str(self.__dict_obj)


class JsonData(Data):
    def __init__(self, objdict):
        assert type(objdict) is dict
        self.__obj_dict = objdict

    def get(self, item, default=None):
        return get_from_dict(self.__obj_dict, item, default)

    def __str__(self):
        return str(self.__obj_dict)


class YamlData(Data):
    def __init__(self, loaded_obj):
        self.__loaded_obj = loaded_obj

    def __str__(self):
        return str(self.__loaded_obj)

    def get(self, item, default=None):
        return self._get_from_obj(self.__loaded_obj, item, default)

    @staticmethod
    def _get_from_obj(map_obj, dotted_keys, default):
        keys = dotted_keys.split('.')
        if len(keys) == 1:
            return map_obj.get(keys[0], default)
        else:
            last_value = map_obj
            for key in keys:
                try:
                    last_value = last_value.get(key, default)
                except AttributeError:
                    last_value = default
                    break

            if last_value is map_obj or last_value is None:
                last_value = default
            return last_value


class DataService:
    """
    Currently supports: 
    - site field parser data (xxx.data.txt)
    - json (xxx.json)
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
    def service_home_path(self) -> ContentPath2:
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

            elif file_path.basename.endswith('.ini'):
                cp = configparser.ConfigParser()
                cp.read_string(self._get_file_content(file_path))
                data_obj = IniData(cp)
                data_name = file_path.basename[:-len('.ini')]

            elif file_path.basename.endswith('.toml'):
                data_obj = TomlData(toml.loads(self._get_file_content(file_path)))
                data_name = file_path.basename[:-len('.toml')]

            elif file_path.basename.endswith('.yaml') or file_path.basename.endswith('.yml'):
                ext = '.yaml' if file_path.basename.endswith('.yaml') else '.yml'
                data_obj = YamlData(load_yaml(self._get_file_content(file_path)))
                data_name = file_path.basename[:-len(ext)]
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
