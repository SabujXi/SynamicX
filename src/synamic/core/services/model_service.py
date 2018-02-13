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
from collections import deque


class FieldConfig:
    @staticmethod
    def __field_boolean_converter(none_or_txt):
        res = False
        if none_or_txt is not None:
            none_or_txt = none_or_txt.strip().lower()
            if none_or_txt in {'yes', 'true', 'y', 't', '0'}:
                res = True
        return res

    def __init__(self, synamic_config, for_field, _type, default=None, unique=None, content_specific=None, required=None, others=None):
        self.__synamic_config = synamic_config
        self.__for_field = for_field
        self.__type = _type
        self.__default = default
        self.__unique = self.__field_boolean_converter(unique)
        self.__content_specific = self.__field_boolean_converter(content_specific)
        self.__required = self.__field_boolean_converter(required)
        self.__others = {} if others is None else others

    @property
    def for_field(self):
        return self.__for_field

    @property
    def type(self):
        return self.__type

    @property
    def default(self):
        if self.__default is None:
            return None
        return self.converter(self.__default, self.__synamic_config)

    @property
    def unique(self):
        return self.__unique

    @property
    def content_specific(self):
        return self.__content_specific

    @property
    def required(self):
        return self.__required

    @property
    def converter(self):
        # print("Converter(): Type is: %s" % self.type)
        cnv = self.__synamic_config.type_system.get_converter(self.type)
        # print("Converter(): fun is %s" % str(cnv))
        return cnv

    def __getitem__(self, key):
        return self.__others.get(key)

    # def __getattr__(self, key):
    #     print("FieldConfig.__getattr__: key: %s" % str(key))
    #     return self.__others.get(key)


class Model:
    def __init__(self, model_name, model_path):
        self.__name = model_name
        self.__model_path = model_path
        self.__field_config_map = {}

    @property
    def path_object(self):
        return self.__model_path

    @property
    def name(self):
        return self.__name

    def add(self, dotted_field, field_config):
        self.__field_config_map[dotted_field] = field_config

    def get(self, dotted_field, default=None):
        res = self.__field_config_map.get(dotted_field, None)
        if res is None:
            return default
        else:
            return res

    def __contains__(self, item):
        return item in self.__field_config_map


class ModelService:
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
        for file_path in file_paths:
            if file_path.basename.endswith('.model.txt') and len(file_path.basename) > len('.model.txt'):
                model_name = file_path.basename[:-(len('.model.txt'))]
                with file_path.open('r', encoding='utf-8') as f:
                    model_txt = f.read()
                    model = self.__model_map[model_name] = Model(model_name, file_path)
                    self.__parse(FieldParser(model_txt).parse(), model)
        # print(self.__model_map)
        self.__is_loaded = True

    def __parse(self, model_root_filed: Field, model: Model):

        target_child_stack = deque()

        def process_typing_field_configs(processing_child):
            # target_child_stack.append(processing_child)
            if not processing_child.has_children:
                target_child_stack.pop()
                child_with_typing = target_child_stack[-1]
                # print(processing_child)
                # print(child_with_typing)
                _type = child_with_typing.get('_type', None)
                if _type is None:
                    raise Exception("Expected a _type field - the last target must have children and one children must"
                                    " be called as _type")
                for _n_child in child_with_typing.children_map.values():
                    assert not _n_child.has_children, "Type specification section's fields must not have any nested " \
                                                      "fields"
                ordi_dict = child_with_typing.to_dict_ordinary()
                type_name = _type.value
                del ordi_dict['_type']
                unique = ordi_dict.get('unique', None)
                if unique is not None:
                    del ordi_dict['unique']
                content_specific = ordi_dict.get('content_specific', None)
                if content_specific is not None:
                    del ordi_dict['content_specific']
                required = ordi_dict.get('required', None)
                if required is not None:
                    del ordi_dict['required']

                default = ordi_dict.get('default', None)
                if default is not None:
                    del ordi_dict['default']

                for_field = ".".join(x.name for x in target_child_stack)

                fc = FieldConfig(
                    self.__config,
                    for_field,
                    type_name,
                    default=default,
                    unique=unique,
                    content_specific=content_specific,
                    others=ordi_dict
                )
                model.add(for_field, fc)
                processed_typing = True
            else:
                if len(target_child_stack) == 0:
                    return True
                else:
                    for another_pchild in processing_child.children_map.values():
                        target_child_stack.append(another_pchild)
                        _processed_typing = process_typing_field_configs(another_pchild)
                        if _processed_typing:
                            break

                processed_typing = False

            return processed_typing

        for child in model_root_filed.children_map.values():
            target_child_stack.append(child)
            process_typing_field_configs(child)
            target_child_stack.clear()

    def get_model(self, model_name, default=None):
        return self.__model_map.get(model_name, default)
