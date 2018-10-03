import re
_key_pattern = re.compile(r'^[a-z0-9_]+(\.[a-z0-9_]+)*$', re.I)


class ModelField:
    def __init__(self, key, converter, required, unique):
        self.__key = key
        self.__converter = converter
        self.__required = required
        self.__unique = unique

    @property
    def key(self):
        return self.__key

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

    @property
    def _model_name(self):
        return self.__model_name

    @property
    def _body_field(self):
        return self.get('__body__', None)


class ModelParser:
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
                    raise Exception('Parsing error of model %s at line %d' % (model_name, line_no))
                else:
                    key, value = key_value
                    key = key.strip()
                    value = value.strip()
                    assert _key_pattern.match(key), 'Key %s in model %s did not match with key pattern' % (key, model_name)

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

