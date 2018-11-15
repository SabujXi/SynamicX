from synamic.core.object_manager.query import SimpleQueryParser
from synamic.core.standalones.functions.date_time import parse_datetime, parse_date, parse_time
from .types import Html, Markdown
import re
import datetime
from synamic.exceptions import SynamicMarkNotFound
from synamic.exceptions import SynamicInvalidNumberFormat


class _Pat:
    newline_pat = re.compile(r'\r\n|\n|\r', re.MULTILINE)
    number_pat = re.compile(r'''
                            ^(?P<number>
                                (?P<sign>[-+])?
                                (?P<int>[0-9]+)
                                (\.
                                    (?P<decimal>[0-9]+)
                                )?
                            )$''', re.VERBOSE)

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


_default_types = frozenset({
        'number',
        'string',
        'text',
        'date',
        'time',
        'datetime',
        'markdown',
        'html',

        'marker#type',
        'marker#tags',
        'marker#categories',
        'user',

        # TODO: add the following __document_types
        # template
        # image
        # attachment
        # etc

        'number[]',
        'string[]',
        'date[]',
        'time[]',
        'datetime[]',
})

_class_map = {}


def _add_converter_type(name):
    assert name in _default_types

    def class_or_fun_decorator(cls_or_fun):
        assert name not in _class_map
        _class_map[name] = cls_or_fun
        return cls_or_fun
    return class_or_fun_decorator


class ConverterCallable:
    def __init__(self, type_system, name, supported_compare_ops=frozenset()):
        self.__type_system = type_system
        self.__name = name
        self.__supported_compare_ops = frozenset(supported_compare_ops)
        # validation
        for op in self.__supported_compare_ops:
            assert op in SimpleQueryParser.COMPARE_OPERATORS_SET

    @property
    def type_system(self):
        return self.__type_system

    @property
    def name(self):
        return self.__name

    @property
    def supported_compare_ops(self):
        return self.__supported_compare_ops

    def supports_compare_op(self, op):
        return op in self.supported_compare_ops

    @classmethod
    def validate_op_value(cls, op, left_value, right_value):
        assert op in SimpleQueryParser.COMPARE_OPERATORS_SET
        if op in ('in', '!in'):
            assert isinstance(right_value, (list, tuple))
            assert not isinstance(left_value, (list, tuple))
        elif op in ('contains', '!contains'):
            assert isinstance(left_value, (list, tuple))
            assert not isinstance(right_value, (list, tuple))
        else:
            assert not isinstance(left_value, (list, tuple))
            assert not isinstance(right_value, (list, tuple))

    def compare(self, op, left_value, right_value):
        assert op in self.supported_compare_ops, f'op: {op}, supported ops: {self.supported_compare_ops}'
        self.validate_op_value(op, left_value, right_value)
        return SimpleQueryParser.COMPARE_OPERATOR_2_PY_OPERATOR_FUN[op](left_value, right_value)

    def __call__(self, value, *args, **kwargs):
        raise NotImplemented


class ConverterCallableListCompareMixin(ConverterCallable):
    def compare(self, op, left_value, right_value):
        assert op in self.supported_compare_ops
        if op in ('contains', '!contains'):
            right_value = right_value[0]
            self.validate_op_value(op, left_value, right_value)
            return SimpleQueryParser.COMPARE_OPERATOR_2_PY_OPERATOR_FUN[op](left_value, right_value)
        else:
            assert op in ('in', '!in')
            assert isinstance(left_value, (list, tuple)), '%s : %s' % (str(type(left_value)), str(left_value))
            assert isinstance(right_value, (list, tuple)), '%s : %s' % (str(type(right_value)), str(right_value))
            for single_value in left_value:
                if single_value not in right_value:
                    return False
            return True


@_add_converter_type('number')
class NumberConverter(ConverterCallable):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            '==',
            '!=',
            '>',
            '<',
            '>=',
            '<=',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        if isinstance(txt, (int, float)):
            return txt
        m_number = _Pat.number_pat.match(txt)
        if not m_number:
            raise SynamicInvalidNumberFormat(f"Invalid number format: {txt}")
        else:
            sign_str = m_number.group('sign')
            int_str = m_number.group('int')
            decimal_str = m_number.group('decimal')
            int_str = int_str.lstrip('0')
            if int_str == '':
                int_str = '0'
            num_str = sign_str + int_str + decimal_str

            if decimal_str:
                num = float(num_str)
            else:
                num = int(num_str)
            return num


@_add_converter_type('date')
class DateConverter(ConverterCallable):
    """May include locale in future"""
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            '==',
            '!=',
            '>',
            '<',
            '>=',
            '<=',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        if isinstance(txt, datetime.date):
            return txt
        return parse_date(txt)


@_add_converter_type('time')
class TimeConverter(ConverterCallable):
    """May include locale in future"""
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            '==',
            '!=',
            '>',
            '<',
            '>=',
            '<=',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        if isinstance(txt, datetime.time):
            return txt
        return parse_time(txt)


@_add_converter_type('datetime')
class DateTimeConverter(ConverterCallable):
    """May include locale in future"""
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            '==',
            '!=',
            '>',
            '<',
            '>=',
            '<=',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        if isinstance(txt, datetime.datetime):
            return txt
        return parse_datetime(txt)


@_add_converter_type('string')
class StringConverter(ConverterCallable):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            '==',
            '!=',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        """Strings are single line things, so, any multi-line will be skipped and the first line will be taken"""
        if isinstance(txt, (int, float)):
            txt = str(txt)
        assert isinstance(txt, str)
        txts = _Pat.newline_pat.split(txt)
        return txts[0]


@_add_converter_type('text')
class TextConverter(ConverterCallable):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            '==',
            '!=',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        """return as is"""
        assert isinstance(txt, str)
        return txt


@_add_converter_type('markdown')
class MarkdownConverter(ConverterCallable):
    def __call__(self, txt, value_pack=None, *args, **kwargs):
        """
        Return a markdown instance.
        """
        return Markdown(self.type_system.site, txt, value_pack=value_pack)


@_add_converter_type('html')
class HtmlConverter(ConverterCallable):
    def __call__(self, txt, *args, **kwargs):
        """
        Probably should return a Html instance.
        """
        return Html(txt)


@_add_converter_type('number[]')
class NumberListConverter(ConverterCallableListCompareMixin):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            'contains',
            '!contains',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        number_converter = self.type_system.get_converter('number')
        txts = txt.split(',')
        num_strs = [x.strip() for x in txts]
        numbers = []
        for num_str in num_strs:
            number = number_converter(num_str)
            numbers.append(number)
        return tuple(numbers)


@_add_converter_type('string[]')
class StringListConverter(ConverterCallableListCompareMixin):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            'contains',
            '!contains',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
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


@_add_converter_type('date[]')
class DateListConverter(ConverterCallableListCompareMixin):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            'contains',
            '!contains',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        date_converter = self.type_system.get_converter('date')
        res = []
        txt = txt.strip()
        date_str_list = txt.split(',')
        for date_str in date_str_list:
            date_str = date_str.strip()
            res.append(
                date_converter(date_str)
            )
        return tuple(res)


@_add_converter_type('time[]')
class TimeListConverter(ConverterCallableListCompareMixin):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            'contains',
            '!contains',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        time_converter = self.type_system.get_converter('time')
        res = []
        txt = txt.strip()
        time_str_list = txt.split(',')
        for time_str in time_str_list:
            time_str = time_str.strip()
            res.append(
                time_converter(time_str)
            )
        return tuple(res)


@_add_converter_type('datetime[]')
class DateTimeListConverter(ConverterCallableListCompareMixin):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            'contains',
            '!contains',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        datetime_converter = self.type_system.get_converter('datetime')
        res = []
        txt = txt.strip()
        datetime_str_list = txt.split(',')
        for datetime_str in datetime_str_list:
            datetime_str = datetime_str.strip()
            res.append(
                datetime_converter(datetime_str)
            )
        return tuple(res)


@_add_converter_type('marker#type')
class MarkTypeConverter(ConverterCallable):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            '==',
            '!=',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        object_manager = self.type_system.site.object_manager
        type_marker = object_manager.get_marker('type')
        title = txt.strip()
        mark = type_marker.get_mark_by_title(title, None)
        if mark is None:
            raise SynamicMarkNotFound(f'Mark with title {title} does not exist')
        return mark


@_add_converter_type('marker#tags')
class MarkTagsConverter(ConverterCallableListCompareMixin):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            'contains',
            '!contains',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        """Strings are single line things, so, any multi-line will be skipped and the first line will be taken"""
        object_manager = self.type_system.site.object_manager
        tag_marker = object_manager.get_marker('tags')
        res = []
        tag_titles = _Pat.separator_comma_pat.split(txt)
        for title in tag_titles:
            title = title.strip()
            if title != '':
                title = _Pat.multiple_commas_pat.sub(_Pat.multiple_commas_repl_fun, title)
                mark = tag_marker.get_mark_by_title(title, None)
                if mark is None:
                    mark = tag_marker.make_mark_by_title(title)
                res.append(
                    mark
                )
        return tuple(res)


@_add_converter_type('marker#categories')
class MarkCategoriesConverter(ConverterCallableListCompareMixin):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            'contains',
            '!contains',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, txt, *args, **kwargs):
        object_manager = self.type_system.site.object_manager
        categories_marker = object_manager.get_marker('categories')
        res = []
        categories_titles = _Pat.separator_comma_pat.split(txt)
        for title in categories_titles:
            title = title.strip()
            if title != '':
                title = _Pat.multiple_commas_pat.sub(_Pat.multiple_commas_repl_fun, title)
                mark = categories_marker.get_mark_by_title(title, None)
                if mark is None:
                    mark = categories_marker.make_mark_by_title(title)
                res.append(
                    mark
                )
        return tuple(res)


# TODO: implement in !in for all the converter that returns single value - currently it does not work.
@_add_converter_type('user')
class UserConverter(ConverterCallable):
    def __init__(self, type_system, name):
        supported_ops = frozenset([
            '==',
            '!=',
            'in',
            '!in'
        ])
        super().__init__(type_system, name, supported_ops)

    def __call__(self, user_id, *args, **kwargs):
        object_manager = self.type_system.site.object_manager
        user = object_manager.get_user(user_id)
        return user
