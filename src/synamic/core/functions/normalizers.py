"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import sys
import re
import os


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


_schemed_url = re.compile(r'^[a-z]+://', re.I)


def normalize_content_url_path(url_str):
    """
    Normalized content url_object path:
      1. Replace all '\' with '/'
      2. A preceding '/' will be added if not present (No relative path in this framework as we are not writing any raw html: md, template and raw html).
      3. TO-DO: Resolve ./, ../../../ and the like.
       
    0. Note:
        Url path must not be a complete - that is it must not start with any scheme.
    """
    # 0
    assert not _schemed_url.match(url_str), "Url path cannot start with a scheme"
    # 1
    url_str = url_str.replace('\\', '/')
    # 2
    if not url_str.startswith('/'):
        url_str = '/' + url_str
    # 3 TO-DO

    return url_str


def split_content_url_path_components(normalized_url):
    """As splitting depends on normalize_content_url_path() I must keep this function below that as done here"""
    url_str = normalized_url.lstrip('/')
    return url_str.split('/')


def generalize_content_url_path(url_str):
    """
    Convert to lower the result of normalize_content_url_path
    """
    n_url = normalize_content_url_path(url_str)
    return n_url.lower()


def newline_normalizer(text):
    raise NotImplemented


# def normalize_relative_file_path(path):
#     return os.path.normpath(path).lstrip(r'\/').replace('\\', '/')  # Url friendly
