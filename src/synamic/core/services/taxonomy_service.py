"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


from synamic.core.new_parsers.document_parser import FieldParser, Field
from synamic.core.functions.decorators import loaded, not_loaded
from collections import OrderedDict


class TaxonomyService:
    def __init__(self, synamic_config):
        self.__config = synamic_config
        self.__type_system = synamic_config.type_system
        self.__model_map = {}
        self.__is_loaded = False

        self.__service_home_path = None
        self.__config.register_path(self.service_home_path)

    @property
    def service_home_path(self):
        if self.__service_home_path is None:
            self.__service_home_path = self.__config.path_tree.create_path(('models',))
        return self.__service_home_path

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        file_paths = self.__config.path_tree.list_file_paths('models')
        model_file_paths_map = self.__model_map
        for file_path in file_paths:
            if file_path.basename.endswith('.model.txt') and len(file_path.basename) > len('.model.txt'):
                model_name = file_path.basename[:-(len('.model.txt'))]
                # print(":::::::::::::::::::::: Model name `%s`" % model_name)
                with file_path.open('r', encoding='utf-8') as f:
                    model_txt = f.read()
                    model_file_paths_map[model_name] = {
                        'file_path': file_path,
                        'root_field': FieldParser(model_txt).parse()
                    }
                    # print("\n\n\n\nModel parsing: %s" % file_path.absolute_path)
        self.__is_loaded = True

    @loaded
    def get_converted(self, model_name, content_root_field: Field, content_txt):
        if model_name not in self.__model_map:
            raise Exception("Model `%s` not found" % model_name)
        model_root_field = self.__model_map[model_name]['root_field']
        res_map = OrderedDict()

        def visitor(a_field, field_path, _res_map_: OrderedDict):
            """
            :param a_field: 
            :param field_path: is a tuple of nested field names 
            """
            # print("Processing field: %s" % a_field.name)
            dotted_field = ".".join([field for field in field_path])
            model_field = model_root_field.get(dotted_field, None)
            if model_field is None:
                # deliver the raw sting to the field
                # assert model_field is not None, "field `%s` is not defined in the model" % dotted_field
                type_name = 'text'
            else:
                type_field = model_field.children_map.get('type', None)
                assert type_field is not None, "Type must be defined"
                # default_value_str = model_field.children_map.get('default', None)
                type_name = type_field.value
                # default_str = model_field.children_map.get('default', None)
            converter = self.__config.type_system.get_converter(type_name)
            converted_value = converter(a_field.value, self.__config)
            _res_map_[dotted_field] = {'value': converted_value, 'converter': converter}
            return _res_map_

        # print('model map %s' % self.__model_map)

        content_root_field.visit(visitor, res_map)

        model_field = model_root_field.get('__body__', None)
        if model_field is not None:
            typ_name = model_field.children_map.get('type', None)
            assert typ_name is not None, "Type must be defined"
        else:
            typ_name = 'markdown'
        converter = self.__config.type_system.get_converter(typ_name)
        converted_value = converter(content_txt, self.__config)
        res_map['__body__'] = converted_value

        return res_map
