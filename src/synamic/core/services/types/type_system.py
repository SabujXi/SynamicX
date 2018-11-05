from .converters import _class_map, ConverterCallable, _default_types
"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


"""
1. Every module should have a .module.config.txt file at the root of it,
2. The module config file will have info about which data model it will follow.
3. Models will be stored inside 'models' of the site root folder.
4. Along with a default model per module's contents, a content file can specify a specific model with `_model` field.
"""


class TypeSystem:
    def __init__(self, site):
        self.__site = site
        self.__type_converters = {}
        self.__loaded = False

    @property
    def site(self):
        return self.__site

    def load(self):
        for name, converter_class in _class_map.items():
            self.add_converter(name, converter_class)
        self.__loaded = True

    def default_types(self):
        return _default_types

    def registered_types(self):
        return tuple(self.__type_converters.keys())

    def get_converter(self, type_name):
        converter = self.__type_converters.get(type_name, None)
        if converter is not None:
            return converter
        raise Exception("Converter with name `%s` not found" % type_name)

    def add_converter(self, type_name, converter):
        assert type_name not in self.__type_converters, "A converter with the type name already exists: `%s`" % type_name
        if issubclass(converter, ConverterCallable):
            _ = converter(self, type_name)
        else:
            _ = converter(self, type_name)  # they are the same for now as class must accept the type system
            #  and type name as the arguments
            assert callable(_), 'Provided class instance is not callable or __call__ is not defined on it: %s' % str(converter)
        converter = _
        self.__type_converters[type_name] = converter
        return converter
