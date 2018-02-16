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
import re
from synamic.core.functions.date_time import parse_datetime, parse_date, parse_time
from .types import Html, Markdown


class _Pat:
    newline_pat = re.compile(r'\r\n|\n|\r', re.MULTILINE)
    number_pat = re.compile(r'^(?P<number>[0-9]+(.[0-9]+)?)$')

    separator_comma_pat = re.compile(r',[^,]?')
    # separator_comma_pat = re.compile(r',[^,]*')
    multiple_commas_pat = re.compile(r'(?P<start>[^,]*)(?P<commas>,{2,})(?P<end>[^,]*)')
    # multiple_commas_pat = re.compile(r'(?P<start>[^,]*)(?P<commas>,{2})*(?P<end>[^,]*)')

    @staticmethod
    def multiple_commas_repl_fun(mobj):
        commas = mobj.group('commas')
        commas = commas[1:]
        start = mobj.group('start')
        end = mobj.group('end')
        if start is None:
            start = ''
        if end is None:
            end = ''
        return start + commas + end


class TypeSystem:
    __default_types = frozenset({
        'number',
        'string',
        'text',
        'date',
        'time',
        'datetime',
        'markdown',
        'html',

        'taxonomy.tags',

        # TODO:
        # template
        # image
        # attachment
        # etc

        'number[]',
        'string[]',
        'date[]',
        'time[]',
        'datetime[]'
    })

    __type_converters = {}

    def __init__(self, synamic_object):
        self.__synamic_object = synamic_object

    @classmethod
    def default_types(cls):
        return cls.__default_types

    @classmethod
    def registered_types(cls):
        return tuple(cls.__type_converters.keys())

    @classmethod
    def get_converter(cls, type_name):
        converter = cls.__type_converters.get(type_name, None)
        if converter is not None:
            return converter
        raise Exception("Converter with name `%s` not found" % type_name)

    @classmethod
    def add_converter(cls, type_name, converter_fun):
        converter = cls.__type_converters.get(type_name, None)
        if converter is not None:
            raise Exception("A converter with the type name already exists: `%s`" % type_name)
        assert callable(converter_fun), "Type converter is not callable: `%s`" % str(converter_fun)
        cls.__type_converters[type_name] = converter_fun
        return converter_fun

    @classmethod
    def decorator_converter(cls, type_name):
        def decorator_converter_wrapper(fn):
            cls.add_converter(type_name, fn)
            return fn
        return decorator_converter_wrapper


def _decorator_default_converter(type_name):
    if type_name not in TypeSystem.default_types():
        raise Exception("Invalid default type name: `%s`" % type_name)

    def decorator_default_converter_wrapper(fn):
        TypeSystem.add_converter(type_name, fn)
        return fn
    return decorator_default_converter_wrapper


@_decorator_default_converter('datetime')
def _datetime_converter(txt, synamic_config_obj=None, *args, **kwargs):
    return parse_datetime(txt)


@_decorator_default_converter('date')
def _date_converter(txt, synamic_config_obj=None, *args, **kwargs):
    return parse_date(txt)


@_decorator_default_converter('time')
def _time_converter(txt, synamic_config_obj=None, *args, **kwargs):
    return parse_time(txt)


@_decorator_default_converter('string')
def _string_converter(txt, synamic_config_obj=None, *args, **kwargs):
    """Strings are single line things, so, any multi-line will be skipped and the first line will be taken"""
    txts = _Pat.newline_pat.split(txt)
    return txts[0]


@_decorator_default_converter('text')
def _text_converter(txt, synamic_config_obj=None, *args, **kwargs):
    """return as is"""
    return txt


@_decorator_default_converter('markdown')
def _markdown_converter(txt, synamic_config_obj=None, *args, **kwargs):
    """
    Return a markdown instance.
    """
    assert synamic_config_obj is not None
    return Markdown(txt, synamic_config_obj)


@_decorator_default_converter('html')
def _html_converter(txt, synamic_config_obj=None, *args, **kwargs):
    """
    Probably should return a Html instance. 
    """
    return Html(txt)


@_decorator_default_converter('number[]')
def _number_list_converter(txt, synamic_config_obj=None, *args, **kwargs):
    txts = txt.split(',')
    num_strs = [x.strip() for x in txts]
    numbers = []
    for num_str in num_strs:
        m_number = _Pat.number_pat.match(num_str)
        if not m_number:
            raise Exception("Invalid number format: `%s`" % num_str)
        else:
            num_str = m_number.group('number')
            num_str = num_str.lstrip('0')
            if num_str == '':
                num_str = '0'
            if '.' in num_str:
                num = float(num_str)
            else:
                num = int(num_str)
            numbers.append(num)
    return tuple(numbers)


@_decorator_default_converter('string[]')
def _string_list_converter(txt, synamic_config_obj=None, *args, **kwargs):
    """
    Separator for string is comma (,) - so what if someone want to put a comma inside their string?
     Ans: precede that with another comma.
    So, when more than consecutive comma is found the first one is skipped and the later ones are considered as literal commas
    """
    res = []
    strings = _Pat.separator_comma_pat.split(txt)
    for string in strings:
        string = string.strip()
        string = _Pat.multiple_commas_pat.sub(_Pat.multiple_commas_repl_fun, string)
        res.append(string)
    return tuple(strings)


@_decorator_default_converter('taxonomy.tags')
def _tags_converter(txt, synamic_config_obj=None, *args, **kwargs):
    """Strings are single line things, so, any multi-line will be skipped and the first line will be taken"""
    # print("TAGS txt: %s" %txt)
    sy_tags = synamic_config_obj.tags
    res = []
    strings = _Pat.separator_comma_pat.split(txt)
    for string in strings:
        string = string.strip()
        if string != '':
            string = _Pat.multiple_commas_pat.sub(_Pat.multiple_commas_repl_fun, string)
            res.append(
                sy_tags.add_tag(string)
            )
    # print("Tags: %s" % str(res))
    return tuple(res)


@_decorator_default_converter('date[]')
def _date_list_converter(txt, synamic_config_obj=None, *args, **kwargs):
    res = []
    txt = txt.strip()
    date_str_list = txt.split(',')
    for date_str in date_str_list:
        date_str = date_str.strip()
        res.append(
           parse_date(date_str)
        )
    return tuple(res)


@_decorator_default_converter('time[]')
def _time_list_converter(txt, synamic_config_obj=None, *args, **kwargs):
    res = []
    txt = txt.strip()
    time_str_list = txt.split(',')
    for time_str in time_str_list:
        time_str = time_str.strip()
        res.append(
            parse_time(time_str)
        )
    return tuple(res)


@_decorator_default_converter('datetime[]')
def _datetime_list_converter(txt, synamic_config_obj=None, *args, **kwargs):
    res = []
    txt = txt.strip()
    datetime_str_list = txt.split(',')
    for datetime_str in datetime_str_list:
        datetime_str = datetime_str.strip()
        res.append(
            parse_datetime(datetime_str)
        )
    return tuple(res)
