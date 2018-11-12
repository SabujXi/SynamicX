import re
from synamic.exceptions import SynamicModelParsingError, get_source_snippet_from_text
_key_pattern = re.compile(r'^[a-z0-9_]+(\.[a-z0-9_]+)*$', re.I)


class ModelField:
    def __init__(self, key, converter_name, required, unique):
        self.__key = key
        self.__converter_name = converter_name
        self.__required = required
        self.__unique = unique
        self.__converter = None

    def clone(self):
        return self.__class__(self.__key, self.__converter_name, self.__required, self.__unique)

    def set_converter(self, converter):
        # TODO: Importing ConverterCallable is impossible as this module is imported from type system.
        # Fix it or leave it.
        # assert isinstance(converter, ConverterCallable)
        assert self.__converter is None
        self.__converter = converter

    @property
    def key(self):
        return self.__key

    @property
    def converter_name(self):
        return self.__converter_name

    @property
    def converter(self):
        return self.__converter

    @property
    def required(self):
        return self.__required

    @property
    def unique(self):
        return self.__unique


class Model(dict):
    def __init__(self, model_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__model_name = model_name
        self.__args = tuple(args)
        self.__kwargs = kwargs.copy()

    def clone(self):
        another = self.__class__(self.__model_name, *self.__args, **self.__kwargs)
        for key, value in self.items():
            another[key] = value.clone()
        return another

    @property
    def model_name(self):
        return self.__model_name

    @property
    def body_field(self):
        return self.get('__body__', None)

    def new(self, *others):
        another = self.clone()
        for other in others:
            assert type(other) is self.__class__
            another.update(other.clone())
        return another


class ModelParser:
    @classmethod
    def empty_model(cls, model_name):
        return cls.parse(model_name, '')

    @staticmethod
    def parse(model_name, model_text):
        model = Model(model_name)
        lines = model_text.splitlines()
        line_no = 0
        for line in lines:
            line_no += 1
            line = line.strip()
            if line == '':
                # skip empty lines
                continue
            if line.startswith(('//', '#')):
                # skip comments
                continue
            else:
                # process
                key_value = line.split(':', 1)
                if len(key_value) == 1:
                    source_snippet = get_source_snippet_from_text(model_text, line_no, limit=10)
                    raise SynamicModelParsingError(f'Parsing error of model {model_name} at line {line_no}\n'
                                                   f'Details:\n{source_snippet}')
                else:
                    key, value = key_value
                    key = key.strip()
                    value = value.strip()

                    if not _key_pattern.match(key):
                        source_snippet = get_source_snippet_from_text(model_text, line_no, limit=10)
                        raise SynamicModelParsingError(f'Key {key} in model {model_name} did not match with key '
                                                       f'pattern at line no {line_no}\n'
                                                       f'Details:\n{source_snippet}')

                    parts = value.split('|')
                    parts = [part.strip() for part in parts]

                    converter = parts[0]
                    required = False
                    unique = False
                    parts_rest = parts[1:]
                    for part in parts_rest:
                        part = part.lower()
                        if part == 'required':
                            required = True
                        if part == 'unique':
                            unique = True
                    model_field = ModelField(key, converter, required, unique)
                    model[key] = model_field

        return model

