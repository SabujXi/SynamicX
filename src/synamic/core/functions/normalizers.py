import sys


def normalize_string(string):
    return string.lower()


def normalize_key(key):
    return sys.intern(key.lower())


def normalize_keys(obj):
    """
    Normalize keys of a map/dictionary-like-object
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_key = normalize_key(key)
            del obj[key]
            obj[new_key] = value
            # Recurse
            normalize_keys(value)
    elif isinstance(obj, list) or \
            isinstance(obj, tuple) or \
            isinstance(obj, set):
        collection = obj
        for value in collection:
            normalize_keys(value)
    else:
        """Ignore it, it has: String, None, etc. that are not collections of other objects"""
    return obj


def normalize_content_url(url_str):
    pass


def newline_normalizer(text):
    raise NotImplemented


