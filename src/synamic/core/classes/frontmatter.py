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
Frontmatter must be normalized, and yes, the normalize_string() will be used. This normalizer will always normalize to
lowercase.
"""
from synamic.core.functions.normalizers import normalize_keys, normalize_key
from synamic.core.functions.date_time import parse_datetime
from collections import namedtuple

TemplateNameModuleNamePair = namedtuple('TemplateNameModuleNamePair', ['template_name', 'module_name'])

forntmatter_default_values = {
    normalize_key('title'): "",
    normalize_key('summary'): ""
}


class Frontmatter:
    def __init__(self, config, obj):
        if obj is None or obj == "":
            obj = {}
        assert isinstance(obj, dict), "The obj must either be None, empty string or an instance of dict"
        self.__map = obj
        self.__terms = None  # {}
        self.__values = None

        normalize_keys(self.__map)

        __other_values = {}

        for key, value in self.__map.copy().items():
            fun = config.get_frontmatter_value_parser(key)
            if fun is not None:
                self.__map[key] = fun(value)
            else:
                del self.__map[key]
                __other_values[key] = value

        self.__terms, self.__values = config.taxonomy.get_terms_from_frontmatter(__other_values)

    @property
    def terms(self):
        return self.__terms

    @property
    def values(self):
        return self.__values

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
        if key not in self:
            return forntmatter_default_values.get(key, default)
        return self.__map.get(key, default)

    def keys(self):
        return self.__map.keys()

    def items(self):
        return self.items()


class DefaultFrontmatterValueParsers:
    @staticmethod
    def _return_stripped_or_none_parser(txt):
        txt = txt.strip()
        return None if txt == '' else txt

    @staticmethod
    def _template_name_module_name_parser(txt):
        txt = txt.strip()
        if txt:
            if ':' in txt and txt[0] != ':' and txt[-1] != 0:
                template_name, module_name = txt.split(':')
            else:
                if txt[-1] == ':':
                    raise Exception('Invalid template name format: %s' % txt)
                template_name = txt
                module_name = 'synamic-template'
            return TemplateNameModuleNamePair(template_name=template_name, module_name=module_name)
        else:
            raise Exception('No template name provided')

    @staticmethod
    def _permalink_parser(txt):
        txt = txt.strip()
        if txt == 'index.html' or txt.endswith('/index.html'):
            if txt == 'index.html':
                txt = '/'
            else:
                txt = txt[:-len('index.html')]
        return txt

    @staticmethod
    def _author_parser(auth):
        auth = auth.strip()
        return auth

    @classmethod
    def default_value_parsers_map(cls):
        return {
            'permalink': cls._permalink_parser,
            'id': cls._return_stripped_or_none_parser,
            'name': cls._return_stripped_or_none_parser,
            'author': cls._author_parser,
            'template': cls._template_name_module_name_parser,
            'title': cls._return_stripped_or_none_parser,
            'summary': cls._return_stripped_or_none_parser,
            'created-on': parse_datetime,
            'updated-on': parse_datetime,
            'pagination-filter': cls._return_stripped_or_none_parser,
            'pagination-content-per-page': cls._return_stripped_or_none_parser,   # TODO: this should be convtd to nos
            'language': lambda s: normalize_key(s),
        }

    @classmethod
    def register_default_value_parsers(cls, config):
        """
         This method will register available parsers the parses value of frontmatter to callables.
        """
        for key, _callable in cls.default_value_parsers_map().items():
            config.register_frontmatter_value_parser(key, _callable)
