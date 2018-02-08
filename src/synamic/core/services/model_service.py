from synamic.core.new_parsers.document_parser import FieldParser, Field
from synamic.core.functions.decorators import loaded, not_loaded
from collections import OrderedDict


class ModelService:
    def __init__(self, synamic_config):
        self.__config = synamic_config
        self.__type_system = synamic_config.type_system
        self.__model_map = {}
        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        file_paths = self.__config.path_tree.list_file_paths('models')
        model_file_paths_map = self.__model_map
        for file_path in file_paths:
            if file_path.basename.endswith('.model.txt') and len(file_path.basename) > len('.model.txt'):
                model_name = file_path.basename[:len('.model.txt')-1]
                with file_path.relative_path.open('r', encoding='utf-8') as f:
                    model_txt = f.read()
                    model_file_paths_map[model_name] = {
                        'file_path': file_path,
                        'root_field': FieldParser(model_txt).parse()
                    }
        self.__is_loaded = True

    @loaded
    def get_converted(self, model_name, content_root_field: Field, content_txt):
        if model_name not in self.__model_map:
            raise Exception("Model `%s` not found" % model_name)
        model_root_field = self.__model_map[model_name]
        res_map = OrderedDict()

        def visitor(a_field, field_path, res_map: OrderedDict):
            """
            :param a_field: 
            :param field_path: is a tuple of nested field names 
            """
            dotted_field = ".".join([field.name for field in field_path])
            model_field = model_root_field.get(dotted_field, None)
            assert model_field is not None, "field is not defined in the model"

            typ_name = model_field.children_map.get('type', None)
            # default_str = model_field.children_map.get('default', None)
            assert typ_name is not None, "Type must be defined"
            converter = self.__config.type_system.get_converter(typ_name)
            converted_value = converter(a_field.value, self.__config)
            res_map[dotted_field] = converted_value
            return res_map

        content_root_field.visit(visitor, res_map)

        model_field = model_root_field.get('__body__', None)
        assert model_field is not None, "field is not defined in the model"
        typ_name = model_field.children_map.get('type', None)
        assert typ_name is not None, "Type must be defined"
        converter = self.__config.type_system.get_converter(typ_name)
        converted_value = converter(content_txt, self.__config)
        res_map['__dotted__'] = converted_value
