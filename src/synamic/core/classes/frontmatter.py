"""
Frontmatter must be normalized, and yes, the normalize_string() will be used. This normalizer will always normalize to
lowercase.
"""
from synamic.core.functions.normalizers import normalize_keys, normalize_key


class Frontmatter:
    def __init__(self, obj):
        if obj is None or obj == "":
            obj = {}
        assert isinstance(obj, dict), "The obj must either be None, empty string or an instance of dict"
        self.__map = obj
        normalize_keys(self.__map)

    def __contains__(self, item):
        key = normalize_key(item)
        return key in self.__map

    def __getitem__(self, key):
        key = normalize_key(key)
        return self.__map[key]

    def __delitem__(self, key):
        key = normalize_key(key)
        return self.__map[key]

    def __setitem__(self, key, value):
        key = normalize_key(key)
        self.__map[key] = value

    def get(self, key, default=None):
        key = normalize_key(key)
        return self.__map.get(key, default)

    def keys(self):
        return self.__map.keys()

    def values(self):
        return self.values()

    def items(self):
        return self.items()
