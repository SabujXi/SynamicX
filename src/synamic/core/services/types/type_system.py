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

from synamic.core.standalones.functions.date_time import parse_datetime, parse_date, parse_time

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


_default_converters = {}


def _decorate_converter(type_name):
    def method_decorator(method):
        def method_executor(self, *me_args, **me_kwargs):
            return method(self, type_name, *me_args, **me_kwargs)
        _default_converters[type_name] = method_executor
        return method_executor
    return method_decorator


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
        'taxonomy.categories',
        'user',

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

    def __init__(self, synamic):
        self.__synamic = synamic
        self.__type_converters = {}

        for name, converter in _default_converters.items():
            self.add_converter(name, converter)

        # use for loop to add

    def load(self):
        self.__loaded = True

    def default_types(self):
        return self.__default_types

    def registered_types(self):
        return tuple(self.__type_converters.keys())

    def get_converter(self, type_name):
        converter = self.__type_converters.get(type_name, None)
        if converter is not None:
            return converter
        raise Exception("Converter with name `%s` not found" % type_name)

    def add_converter(self, type_name, converter_fun):
        converter = self.__type_converters.get(type_name, None)
        if converter is not None:
            raise Exception("A converter with the type name already exists: `%s`" % type_name)
        assert callable(converter_fun), "Type converter is not callable: `%s`" % str(converter_fun)
        self.__type_converters[type_name] = converter_fun
        return converter_fun

    @_decorate_converter('datetime')
    def _datetime_converter(self, txt, *args, **kwargs):
        return parse_datetime(txt)

    @_decorate_converter('date')
    def _date_converter(self, txt, *args, **kwargs):
        return parse_date(txt)

    @_decorate_converter('time')
    def _time_converter(self, txt, *args, **kwargs):
        return parse_time(txt)

    @_decorate_converter('string')
    def _string_converter(self, txt, *args, **kwargs):
        """Strings are single line things, so, any multi-line will be skipped and the first line will be taken"""
        txts = _Pat.newline_pat.split(txt)
        return txts[0]

    @_decorate_converter('text')
    def _text_converter(self, txt, *args, **kwargs):
        """return as is"""
        return txt

    @_decorate_converter('markdown')
    def _markdown_converter(self, txt, *args, **kwargs):
        """
        Return a markdown instance.
        """
        return Markdown(txt, self.__synamic)

    @_decorate_converter('html')
    def _html_converter(self, txt, *args, **kwargs):
        """
        Probably should return a Html instance.
        """
        return Html(txt)

    @_decorate_converter('number[]')
    def _number_list_converter(self, txt, *args, **kwargs):
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

    @_decorate_converter('string[]')
    def _string_list_converter(self, txt, *args, **kwargs):
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

    @_decorate_converter('taxonomy.tags')
    def _tags_converter(self, txt, *args, **kwargs):
        """Strings are single line things, so, any multi-line will be skipped and the first line will be taken"""
        # print("TAGS txt: %s" %txt)
        # TODO: how to get tags in the new system
        sy_tags = synamic_config_obj.tags
        res = []
        tag_titles = _Pat.separator_comma_pat.split(txt)
        for title in tag_titles:
            title = title.strip()
            if title != '':
                title = _Pat.multiple_commas_pat.sub(_Pat.multiple_commas_repl_fun, title)
                res.append(
                    sy_tags.add_tag(title)
                )
        return tuple(res)

    @_decorate_converter('user')
    def _user_converter(self, txt, *args, **kwargs):
        content_obj = None
        for cnt in synamic.content_service.users:
            print(txt)
            print(cnt.user_id)
            if txt == cnt.user_id:
                content_obj = cnt
                break
        return content_obj

    @_decorate_converter('taxonomy.categories')
    def _categories_converter(self, txt, *args, **kwargs):
        """Strings are single line things, so, any multi-line will be skipped and the first line will be taken"""
        sy_categories = synamic_config_obj.categories
        res = []
        category_titles = _Pat.separator_comma_pat.split(txt)
        for title in category_titles:
            title = title.strip()
            if title != '':
                title = _Pat.multiple_commas_pat.sub(_Pat.multiple_commas_repl_fun, title)
                res.append(
                    sy_categories.add_category(title)
                )
        return tuple(res)

    @_decorate_converter('date[]')
    def _date_list_converter(self, txt, *args, **kwargs):
        res = []
        txt = txt.strip()
        date_str_list = txt.split(',')
        for date_str in date_str_list:
            date_str = date_str.strip()
            res.append(
                parse_date(date_str)
            )
        return tuple(res)

    @_decorate_converter('time[]')
    def _time_list_converter(self, txt, *args, **kwargs):
        res = []
        txt = txt.strip()
        time_str_list = txt.split(',')
        for time_str in time_str_list:
            time_str = time_str.strip()
            res.append(
                parse_time(time_str)
            )
        return tuple(res)

    @_decorate_converter('datetime[]')
    def _datetime_list_converter(self, txt, *args, **kwargs):
        res = []
        txt = txt.strip()
        datetime_str_list = txt.split(',')
        for datetime_str in datetime_str_list:
            datetime_str = datetime_str.strip()
            res.append(
                parse_datetime(datetime_str)
            )
        return tuple(res)


class ConverterCallable:
    def __init__(self, synamic, converter_fun):
        self.__synamic = synamic
        self.__converter_fun = converter_fun

    def __call__(self, value, *args, **kwargs):
        return self.__converter_fun(value, self.__synamic, *args, **kwargs)
