"""
Frontmatter must be normalized, and yes, the normalize_string() will be used. This normalizer will always normalize to
lowercase.
"""


class Frontmatter:
    def __init__(self, obj):
        if obj is None or obj == "":
            obj = {}
        assert isinstance(obj, dict), "The obj must either be None, empty string or an instance of dict"
        self.__map = obj
        self.__normalize_keys(self.__map)

    @staticmethod
    def string_normalizer(string):
        return string.lower()

    def __normalize_keys(self, obj):
        if isinstance(obj, dict):
            _map = obj
            for key, value in _map.items():
                new_key = self.string_normalizer(key)
                del _map[key]
                _map[new_key] = value
                self.__normalize_keys(value)

        elif isinstance(obj, list) or\
                isinstance(obj, tuple) or\
                isinstance(obj, set):
            collection = obj
            for value in collection:
                self.__normalize_keys(value)
        else:
            """Ignore it, it has: String, None, etc. that are not collections of other objects"""
    def __getitem__(self, key):
        key = self.string_normalizer(key)
        return self.__map[key]

    def __delitem__(self, key):
        key = self.string_normalizer(key)
        return self.__map[key]

    def __setitem__(self, key, value):
        key = self.string_normalizer(key)
        self.__map[key] = value

    def get(self, key, default=None):
        key = self.string_normalizer(key)
        return self.__map.get(key, default)

    def keys(self):
        return self.__map.keys()

    def values(self):
        return self.values()

    def items(self):
        return self.items()
