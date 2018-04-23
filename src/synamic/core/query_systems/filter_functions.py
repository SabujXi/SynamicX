"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import re
from collections import namedtuple
import pprint
from synamic.core.exceptions.synamic_exceptions import *

valid_logical_operator_fun_names = {
    'AND',
    'OR'
}

valid_operators_fun_names = {
    'in',
    '!in',
    'contains',
    '!contains',
    'contains_ic',
    '!contains_ic',
    'startswith',
    '!startswith',
    'startswith_ic',
    '!startswith_ic',
    'endswith',
    '!endswith',
    'endswith_ic',
    '!endswith_ic',
    '==',
    '!=',
    '>',
    '<',
    '>=',
    '<='
}

valid_limiter_fun_names = {
    'limit',
    'offset',
    'from',
    'first',
    'last',
    'sort_by'
}

valid_producer_fun_names = {
    'one',
}


class _Patterns:
    module_name_pat = re.compile(r"^\s*(?P<module_name>[a-zA-Z0-9_-]+)", re.IGNORECASE)
    pipe_pat = re.compile(r"^\s*\|\s*")
    # pipe_or_end_pat = re.compile(r"^\s*\|")
    limiter_name_pat = re.compile(r"^\s*:(?P<limiter_name>[a-zA-Z0-9_]+)")
    limiter_operands_str_pat = re.compile(r"^[^|]+")
    producer_name_pat = re.compile(r"^\s*@(?P<producer_name>[a-zA-Z0-9_]+)")
    operator_pat = re.compile(r"^\s*(?P<operator>[a-zA-Z0-9=><!_@]+)\s+")
    logical_operator_pat = re.compile(r"^\s*(?P<logical_operator>AND|OR|&|\^)\s+")
    identifier_operand_pat = re.compile(r'^\s*(?P<dotted_operand>[a-zA-Z][a-zA-Z0-9_]*([.][a-zA-Z][a-zA-Z0-9_]*)*)')
    right_operand_pat = re.compile(
          r'^\s*(?P<integer_operand>[0-9]+)'  # integer value operand
          + r'|' +
          r'^\s*(?P<float_operand>[0-9]+\.[0-9]+)'  # float value operand
          + r'|' +
          r'^\s*(?P<dotted_operand>[a-zA-Z0-9_]+([.][a-zA-Z0-9_]+)*)'  # identifier_operand_pat.pattern
          + r'|' +
          '^\\s*(?P<string_operand>(\'|")[^\'"]*?\\6)'  # string value operand
          + r'|' +
          '^\\s*(?P<string_iterator_operand>\\[\\s*(\'|")[^\'"]*\\8\\s*(\\s*,\\s*(\'|")[^\'"]*\\10\\s*)*\\])'  # string iterator operand
    )


_FilterFuns = namedtuple('FilterFun', ['logical_operators', 'operators', 'limiters', 'producers'])
_filter_funs = _FilterFuns(logical_operators={}, operators={}, limiters={}, producers={})


# decorators
def operator_decorator(operator_name):
    def inner_wrapper(operator_fun):
        assert operator_name in valid_operators_fun_names, "Invalid operator name: %s" % operator_name
        assert operator_name not in _filter_funs.operators, "Duplicate operator fun"
        _filter_funs.operators[operator_name] = operator_fun
        return operator_fun
    return inner_wrapper


def logical_operator_decorator(operator_name):
    def inner_wrapper(logical_operator_fun):
        assert operator_name in valid_logical_operator_fun_names, "Invalid logical operator name"
        assert operator_name not in _filter_funs.logical_operators, "Duplicate logical operator fun"
        _filter_funs.logical_operators[operator_name] = logical_operator_fun
        return logical_operator_fun
    return inner_wrapper


def limiter_decorator(limiter_name):
    def inner_wrapper(limiter_fun):
        assert limiter_name in valid_limiter_fun_names, "Invalid limiter name"
        assert limiter_name not in _filter_funs.limiters, "Duplicate limiter"
        _filter_funs.limiters[limiter_name] = limiter_fun
        return limiter_fun
    return inner_wrapper


def producer_decorator(producer_name):
    def inner_wrapper(producer_fun):
        assert producer_name in valid_producer_fun_names, "Invalid producer name"
        assert producer_name not in _filter_funs.producers, "Duplicate producers"
        _filter_funs.producers[producer_name] = producer_fun
        return producer_fun
    return inner_wrapper


class CodeGenerator:
    newline_pat = re.compile(r'^(\r\n|\n|\r)')

    def __init__(self, indent=0, space_count=4):
        self.__indentation_level = indent
        self.__space_count = space_count
        self.__code_lines = []
        self.add_code_line("def filter_fun(query_object):")
        self.indent()
        self.add_code_line("Q = query_object")

    def indent(self):
        self.__indentation_level += 1

    def dedent(self):
        self.__indentation_level -= 1

    def add_code_line(self, line):
        lines = self.newline_pat.split(line)
        line = ("\n " * self.__space_count * self.__indentation_level).join(lines)
        self.__code_lines.append(
            " " * self.__space_count * self.__indentation_level + line
        )

    def compile_and_get(self, query_id="query_src__:null"):
        src = self.to_str().strip()
        cod = compile(src, "query_id__:" + str(query_id), 'exec')
        namespace = {}
        exec(cod, globals(), namespace)
        filter_fun = namespace['filter_fun']
        return filter_fun, src

    def to_str(self):
        s = "\n".join(self.__code_lines)
        return s.rstrip().rstrip('\\')


class _QueryProxy:
    """
    Serial liner anding and oring
    """
    def __init__(self, query_obj, query_values):
        self.__origin_query_obj = query_obj
        self.__query_values = query_values

        self.__query_fun_name = None
        self.__opnds = []
        self.__chained_query_proxies = []

    @property
    def values(self):
        return self.__query_values

    def __getattr__(self, key):
        if self.__query_fun_name is None:
            self.__query_fun_name = key
            return self
        else:
            raise LogicalError("Beyond first level function is not allowed")

    def __call__(self, *args):
        assert self.__query_fun_name is not None, "Cannot call an attr before accessing it"
        self.__opnds = args
        return self

    @property
    def fun_name(self):
        assert self.__query_fun_name is not None, "No attr accessed"
        return self.__query_fun_name

    @property
    def operands(self):
        return tuple(self.__opnds)

    @property
    def chained_proxies(self):
        return tuple(self.__chained_query_proxies)

    def __and__(self, other):
        assert bool(self.__opnds), "Operands must not be empty by this time"
        assert type(other) is type(self), "Type mismatch"
        self.__chained_query_proxies.append(
            {
                'type': 'AND',
                'query': other
            }
        )
        return self

    def __or__(self, other):
        assert bool(self.__opnds), "Operands must not be empty by this time"
        assert type(other) is type(self), "Type mismatch"
        self.__chained_query_proxies.append(
            {
                'type': 'OR',
                'query': other
            }
        )
        return self

    def __xor__(self, other):
        return self.__or__(other)


class _Field:
    def __init__(self):
        self.__fields = []

    def __getattr__(self, key):
        self.__fields.append(key)
        return self

    @property
    def fields(self):
        assert bool(self.__fields), "No field was added to field"
        return tuple(self.__fields)

_function_cache_by_filter_str = {}
_function_cache_by_filter_id = {}


def _produce_python_function_source(filter_src, filter_id=None):
    """
    :param filter_text: raw filter text
    :param values: are iterators
    :param local_namespace: namespace passed, for example, this. 
    :return: a tuple - not list or set or anything like that - the infamous immutable tuple
    """
    __filter_funs = _filter_funs

    if filter_id is not None:
        cached_function_src = _function_cache_by_filter_id.get(filter_id, None)
    else:
        cached_function_src = _function_cache_by_filter_str.get(filter_src, None)
    if cached_function_src is not None:
        function = cached_function_src['function']
        src = cached_function_src['src']
        return function, src

    filter_code = CodeGenerator()
    filter_code.add_code_line("Q\\")

    while len(filter_src) > 0:
        producer_name_match = _Patterns.producer_name_pat.match(filter_src)
        limiter_name_match = _Patterns.limiter_name_pat.match(filter_src)
        if producer_name_match:  # call producer
            # query_str
            producer_name = producer_name_match.group('producer_name')
            filter_code.add_code_line(
                ".%s" % (__filter_funs.producers[producer_name].__name__ + "()    \\")
            )
            filter_src = filter_src[producer_name_match.end():]
            break

        elif limiter_name_match:
            # call limiter
            limiter_name = limiter_name_match.group('limiter_name')
            filter_src = filter_src[limiter_name_match.end():]
            limiter_operands_str_match = _Patterns.limiter_operands_str_pat.match(filter_src)
            if not limiter_operands_str_match:
                raise InvalidQueryString("Expected limiter operand(s)")

            limiter_operands_str = limiter_operands_str_match.group()

            filter_src = filter_src[limiter_operands_str_match.end():]

            _limiter_operands = [x for x in limiter_operands_str.strip().split(' ') if len(x) != 0]
            limiter_operands = []
            for opnd in _limiter_operands:
                if _Patterns.identifier_operand_pat.match(opnd):
                    opnd = "Q.F." + opnd
                limiter_operands.append(opnd)

            filter_code.add_code_line(
                "." + __filter_funs.limiters[limiter_name].__name__ + "(%s)    \\" % ", ".join(limiter_operands)
            )
        else:  # operator
            logical_join_list = []
            while True:
                idnt_opnd_match = _Patterns.identifier_operand_pat.match(filter_src)
                if not idnt_opnd_match:
                    raise InvalidQueryString("Expected an identity operand")
                left_opnd = "Q.F." + idnt_opnd_match.group('dotted_operand')
                filter_src = filter_src[idnt_opnd_match.end():]
                operator_match = _Patterns.operator_pat.match(filter_src)
                if not operator_match:
                    raise InvalidQueryString("Expected an operator")
                operator = operator_match.group('operator')
                filter_src = filter_src[operator_match.end():]

                right_opnd_match = _Patterns.right_operand_pat.match(filter_src)
                is_identifier_operand = False

                if right_opnd_match:
                    value_dotted = right_opnd_match.group('dotted_operand')
                    value_integer = right_opnd_match.group('integer_operand')
                    value_float = right_opnd_match.group('float_operand')
                    value_string = right_opnd_match.group('string_operand')
                    value_string_iterator = right_opnd_match.group('string_iterator_operand')
                    if value_dotted:
                        right_opnd = 'Q.F.' + value_dotted
                        is_identifier_operand = True
                    elif value_integer:
                        right_opnd = value_integer
                    elif value_float:
                        right_opnd = value_float
                    elif value_string:
                        right_opnd = value_string
                    elif value_string_iterator:
                        right_opnd = value_string_iterator
                    else:
                        raise LogicalError("Something went wrong during right operand match")
                    filter_src = filter_src[right_opnd_match.end():]
                else:
                    raise InvalidQueryString("Expected right operand")

                logical_operator_match = _Patterns.logical_operator_pat.match(filter_src)

                if logical_operator_match:
                    filter_src = filter_src[logical_operator_match.end():]
                    logical_join_list.append(
                        (left_opnd, operator, right_opnd, logical_operator_match.group("logical_operator"))
                    )
                    continue
                else:
                    logical_join_list.append(
                        (left_opnd, operator, right_opnd, None)
                    )
                    break

            if len(logical_join_list) == 1:
                # no logical and or or whatever
                logic_opn = logical_join_list[0]
                left_opnd = logic_opn[0]
                operator = logic_opn[1]
                right_opnd = logic_opn[2]

                filter_code.add_code_line(
                    (".exp(%s)" % ("Q.P." + __filter_funs.operators[operator].__name__ + "(%s)" % ", ".join(
                        [left_opnd, right_opnd]))) + "\\"
                )
            else:
                arg_join_str_list = []

                for logic_opn in logical_join_list:
                    left_opnd = logic_opn[0]
                    operator = logic_opn[1]
                    right_opnd = logic_opn[2]
                    logic_operator = logic_opn[3]

                    if logic_operator is None:
                        arg_join_str_list.append(
                            ("Q.P." + __filter_funs.operators[operator].__name__ + "(%s)" % ", ".join(
                                [left_opnd, right_opnd]))
                        )
                    else:
                        if logic_operator == '&' or logic_operator == 'AND':
                            _logic_operator = '&'
                        elif logic_operator == '^' or logic_operator == '|' or logic_operator == 'AND':
                            _logic_operator = '^'
                        else:
                            raise InvalidQueryString("Did not expect so!!!")

                        arg_join_str_list.append(
                            "Q.P." + __filter_funs.operators[operator].__name__ + "(%s)" % (
                            ", ".join([left_opnd, right_opnd])) + " " + _logic_operator + " "
                        )

                filter_code.add_code_line(
                    (".exp(%s)" % " ".join(arg_join_str_list)) + "\\"
                )

        # matching a pipe if this is not the end of the string
        filter_src = filter_src.strip()
        if filter_src != '':
            pipe_match = _Patterns.pipe_pat.match(filter_src)
            if not pipe_match:
                raise InvalidQueryString("Expected a pipe for further query")
            filter_src = filter_src[pipe_match.end():]

    if len(_function_cache_by_filter_id):
        filter_id = max(_function_cache_by_filter_id.keys()) + 1
    else:
        filter_id = 1

    function, src = filter_code.compile_and_get(filter_id)
    _function_cache_by_filter_id[filter_id] = {'function': function, 'src': src}
    _function_cache_by_filter_str[filter_src] = {'function': function, 'src': src}
    return function, src, filter_id


def getitem_getattr(o, key, default=None):
    value = default
    __getitem__ = getattr(o, '__getitem__', None)
    if __getitem__ is not None:
        try:
            value = __getitem__(key)
        except:
            pass
    else:
        value = getattr(o, key, default)
    return value


class Query:
    def __init__(self, filter_id, filter_str, values, field_converters = None):
        self.__values = values.copy() if getattr(values, 'copy', False) else tuple([x for x in values])
        self.__original_values = tuple(self.__values)
        # self.__filter_what = filter_what
        self.__filter_id = filter_id
        self.__filter_str = filter_str
        self.__field_converters = {} if field_converters is None else field_converters

    # @property
    # def filter_what(self):
    #     """
    #     Returns the module name (may also refer to other things in future) of the query.
    #     e.g.:
    #         query
    #     """
    #     assert self.__filter_what is not None, "Cannot access query_what property before it is set."
    #     return self.__filter_what

    @property
    def filter_str(self):
        """
        Returns the filter part (after query_what/module name) with whitespaces stripped from both sides. 
        """
        assert self.__filter_str is not None, "Cannot access filter_str property before it is set."
        return self.__filter_str

    @property
    def filter_id(self):
        """
        Returns the query id so that the bytecode can be accessed later without creating/compiling that again.
        """
        assert self.__filter_id is not None, "Cannot access query_id property before it is set."
        return self.__filter_id

    @property
    def P(self, values=None):
        if values is None:
            return _QueryProxy(self, self.__values)
        else:
            return _QueryProxy(self, values)

    @property
    def F(self):
        return _Field()

    @classmethod
    def F_TYPE(cls):
        return _Field

    def __set_values(self, new_values):
        if new_values is None:
            self.__values = None
        elif type(new_values) in {list, set, tuple, frozenset}:
            self.__values = tuple(new_values)
        else:
            self.__values = new_values

    def _get_lr_values(self, value, left_opnd: _Field, right_opnd):
        """get left and right values"""
        is_r_operand_field = False
        if type(right_opnd) is self.F_TYPE():
            is_r_operand_field = True
        # if type(right_opnd) is self.F_TYPE():
        #     is_r_operand_field = True

        ll = left_opnd.fields

        l_value = value
        for part1 in ll:
            # TODO: synamic uses dot joined field now and it that case it will not be a good solution, change accordingly
            l_value = getitem_getattr(l_value, part1)

        r_value = value
        if is_r_operand_field:
            rl = right_opnd.fields
            for part2 in rl:
                # TODO: synamic uses dot joined field now and it that case it will not be a good solution, change accordingly
                r_value = getitem_getattr(r_value, part2)
        else:
            l_dotted_field = ".".join(ll)
            # TODO: find a better way later as dotted joined field converter may not be ok as it is now
            # Though for field converters (!=values) this is perfectly ok. So, much focus must be given to value
            # extracting fields (two examples above)
            conv = self.__field_converters.get(l_dotted_field, None)
            if conv is not None:
                r_value = conv(right_opnd)  # synamic object field is unnecessary - at least we are not putting any markdown there that we need geturl of synamic dependent things
            else:
                r_value = right_opnd

        return l_value, r_value

    # def _get_lr_values_4_content_fields(self, value, left_opnd: _Field, right_opnd):
    #     """get left and right values"""
    #     is_r_operand_field = False
    #     if type(right_opnd) is self.F_TYPE():
    #         is_r_operand_field = True
    #
    #     ll = left_opnd.fields
    #     l_dotted_field = ".".join(ll)
    #
    #     l_value = value.fields.get(l_dotted_field)
    #
    #     if is_r_operand_field:
    #         rl = right_opnd.fields
    #         dotted_field = ".".join(rl)
    #         r_value = value.fields.get(dotted_field, None)
    #     else:
    #         conv = value.field_converters.get(l_dotted_field, None)
    #         if conv is not None:
    #             r_value = conv(right_opnd)
    #         else:
    #             r_value = right_opnd
    #
    #     return l_value, r_value

    def expr(self, query_proxy: _QueryProxy):
        values_set = set()
        ctx_values = tuple(query_proxy.values)

        one_fun_name = query_proxy.fun_name
        one_opnds = query_proxy.operands
        fun = getattr(self, one_fun_name)

        for value in ctx_values:
            # l_opnd, r_opnd = self._get_lr_values_4_content_fields(value, *one_opnds)
            l_opnd, r_opnd = self._get_lr_values(value, *one_opnds)
            if fun(l_opnd, r_opnd):
                values_set.add(value)

        for proxy_dict in query_proxy.chained_proxies:
            another_query_proxy = proxy_dict['query']
            chain_type = proxy_dict['type']

            fun_name = another_query_proxy.fun_name
            opnds = another_query_proxy.operands
            fun = getattr(self, fun_name)

            another_values_set = set()
            res = set()
            for value in ctx_values:
                # l_opnd, r_opnd = self._get_lr_values_4_content_fields(value, *opnds)
                l_opnd, r_opnd = self._get_lr_values(value, *opnds)
                if fun(l_opnd, r_opnd):
                    another_values_set.add(value)

            for value in ctx_values:
                if chain_type == 'AND':
                    if value in values_set and value in another_values_set:
                        res.add(value)
                else:
                    assert chain_type == 'OR'
                    if value in values_set or value in another_values_set:
                        res.add(value)
            values_set = res
            res = set()
        self.__set_values(values_set)
        return self

    exp = expr

    # operators
    @operator_decorator('==')
    def operator_eq(self, left_opnd, right_opnd):
        return left_opnd == right_opnd
    eq = operator_eq

    @operator_decorator('!=')
    def operator_neq(self, left_opnd, right_opnd):
        return left_opnd != right_opnd
    neq = operator_neq

    @operator_decorator('>')
    def operator_gt(self, left_opnd, right_opnd):
        return left_opnd > right_opnd
    gt = operator_gt

    @operator_decorator('<')
    def operator_lt(self, left_opnd, right_opnd):
        return left_opnd < right_opnd
    lt = operator_lt

    @operator_decorator('>=')
    def operator_gteq(self, left_opnd, right_opnd):
        return left_opnd >= right_opnd
    gteq = operator_gteq

    @operator_decorator('<=')
    def operator_lteq(self, left_opnd, right_opnd):
        return left_opnd <= right_opnd
    lteq = operator_lteq

    @operator_decorator('contains')
    def operator_contains(self, left_opnd, right_opnd):
        return left_opnd.__contains__(right_opnd)
    contains = operator_contains

    @operator_decorator('!contains')
    def operator_not_contains(self, left_opnd, right_opnd):
        return not left_opnd.__contains__(right_opnd)
    ncontains = operator_not_contains

    def _normalize_lr_values(self, l_value, r_value):
        """Normalize/lower left value and right value if appropriate"""
        if type(r_value) is list:
            r_value = []
            for x in r_value:
                if type(x) is int or type(x) is float:
                    pass
                else:
                    r_value.append(x.lower())
            r_value = tuple(r_value)
        elif type(r_value) is str:
            r_value = r_value.lower()

        if type(l_value) is list:
            l_value = []
            for x in l_value:
                if type(x) is int or type(x) is float:
                    pass
                else:
                    l_value.append(x.lower())
            l_value = tuple(l_value)
        elif type(l_value) is str:
            l_value = l_value.lower()
        return l_value, r_value

    @operator_decorator('contains_ic')
    def operator_contains_ic(self, left_opnd, right_opnd):
        l_value, r_value = self._normalize_lr_values(left_opnd, right_opnd)
        return l_value.__contains__(r_value)
    contains_ic = operator_contains_ic

    @operator_decorator('!contains_ic')
    def operator_not_contains_ic(self, left_opnd, right_opnd):
        l_value, r_value = self._normalize_lr_values(left_opnd, right_opnd)
        return not l_value.__contains__(r_value)
    ncontains_ic = operator_not_contains_ic

    @operator_decorator('startswith')
    def operator_startswith(self, left_opnd, right_opnd):
        return left_opnd.startswith(right_opnd)
    startswith = operator_startswith

    @operator_decorator('!startswith')
    def operator_not_startswith(self, left_opnd, right_opnd):
        return not left_opnd.startswith(right_opnd)
    nstartswith = operator_not_startswith

    @operator_decorator('startswith_ic')
    def operator_startswith_ic(self, left_opnd, right_opnd):
        l_value, r_value = self._normalize_lr_values(left_opnd, right_opnd)
        return l_value.startswith(r_value)
    startswith_ic = operator_startswith_ic

    @operator_decorator('!startswith_ic')
    def operator_not_startswith_ic(self, left_opnd, right_opnd):
        l_value, r_value = self._normalize_lr_values(left_opnd, right_opnd)
        return not l_value.startswith(r_value)
    nstartswith_ic = operator_not_startswith_ic

    @operator_decorator('endswith')
    def operator_endswith(self, left_opnd, right_opnd):
        return left_opnd.endswith(right_opnd)

    @operator_decorator('!endswith')
    def operator_not_endswith(self, left_opnd, right_opnd):
        return not left_opnd.endswith(right_opnd)

    @operator_decorator('endswith_ic')
    def operator_endswith_ic(self, left_opnd, right_opnd):
        l_value, r_value = self._normalize_lr_values(left_opnd, right_opnd)
        return l_value.endswith(r_value)

    @operator_decorator('!endswith_ic')
    def operator_not_endswith_ic(self, left_opnd, right_opnd):
        l_value, r_value = self._normalize_lr_values(left_opnd, right_opnd)
        return not l_value.endswith(r_value)

    # limiter
    @limiter_decorator('limit')
    def limiter_limit(self, count):

        if len(self.__values) > count:
            result = self.__values[:count]
        else:
            result = tuple(self.__values)

        self.__set_values(result)
        return self

    @limiter_decorator('offset')
    def limiter_offset(self, start):
        if len(self.__values) >= start:
            result = self.__values[start:]
        else:
            result = tuple(self.__values)
        self.__set_values(result)
        return self

    @limiter_decorator('from')
    def limiter_from(self, start, end):
        assert start <= end
        if len(self.__values) >= end:
            result = self.__values[start:end]
        else:
            result = tuple(self.__values)

        self.__set_values(result)
        return self

    @limiter_decorator('first')
    def limiter_first(self, count):
        return self.limiter_limit(count)

    @limiter_decorator('last')
    def limiter_last(self, count):
        if len(self.__values) >= count:
            result = self.__values[-count:]
        else:
            result = tuple(self.__values)

        self.__set_values(result)
        return self

    def _get_limiter_opnd_value_4_sort(self, value, opnd):
        val = value
        if type(opnd) is self.F_TYPE():
            # dotted_field = ".".join(opnd.fields)
            for field in opnd.fields:
                # val = value.fields[dotted_field]#(val, field)
                val = getattr(val, field, None)
        return val

    @limiter_decorator('sort_by')
    def limiter_sort_by(self, field, order):

        def sorter(val):
            val = self._get_limiter_opnd_value_4_sort(val, field)
            return val

        if order.lower() == 'asc':
            result = sorted(self.__values, key=sorter)
        else:
            result = sorted(self.__values, key=sorter, reverse=True)
        self.__set_values(result)
        return self

    @producer_decorator('one')
    def producer_one(self):
        if len(self.__values) == 0:
            result = None
            self.__set_values(None)
        else:
            result = self.__values[0]
            self.__set_values(self.__values[0])
        return result

    def result(self):
        return self.__values


def extract_what_and_query(full_query):
    full_query = full_query.strip()
    filter_what = None
    filter_text = None

    m_filter_what = _Patterns.module_name_pat.match(full_query)
    if m_filter_what is not None:
        filter_what = bk_filter_what = m_filter_what.group("module_name")
        filter_what = filter_what.strip()
        # skip pipe
        filter_text_with_pipe = full_query[len(bk_filter_what):].strip()
        m_pipe = _Patterns.pipe_pat.match(filter_text_with_pipe)
        if m_pipe is not None:
            pipe_str = m_pipe.group()
            # populate filter text
            filter_text = filter_text_with_pipe[len(pipe_str):].strip()

    return filter_what, filter_text


def filter_objects(objects, filter_text, filter_id=None):
    if filter_text.strip() == '' or filter_text is None:
        return tuple(objects)

    filter_str = filter_text.strip()
    if filter_str.strip() == '' or filter_str is None:
        return tuple(objects)

    function_src = _produce_python_function_source(filter_str, filter_id)
    function, src, filter_id = function_src

    #
    q = Query(filter_id, filter_str, objects)

    # print(src)
    try:
        function(q)
    except:
        raise
    result = q.result()
    return result


def query_by_synamic_4_dynamic_contents(synamic_obj, query_text, filter_id=None):
    # get values from synamic object
    values = synamic_obj.dynamic_contents

    filter_what, filter_text = extract_what_and_query(query_text)
    return filter_objects(values, filter_text, filter_id=filter_id)


def query_by_objects(objects, query_text, filter_id=None):
    # get values from synamic object
    values = objects
    filter_what, filter_text = extract_what_and_query(query_text)
    return filter_objects(values, filter_text, filter_id=filter_id)


def query_in_template(query_text):
    # get synamic object from the context
    # for now I am mocking it
    synamic_object = MockSynamic(mock_values())
    # change it later for right implementation

    return query_by_synamic_4_dynamic_contents(synamic_object, query_text, None)


def mock_values():
    d = [
        {'name': "Sabuj", 'age': 28},
        {'name': "XSabuj", 'age': 20},
        {'name': "YSabuj", 'age': 10},
        {'name': "uabuj", 'age': 18},
        {'name': "pabuj", 'age': 2},
        {'name': "SSSSSabuj", 'age': 2},

    ]

    class O:
        def __init__(self, d):
            self.name = d['name']
            self.age = d['age']

        def __str__(self):
            return str({'name': self.name, 'age': self.age})

        def __repr__(self):
            return self.__str__()

    o = [O(x) for x in d]

    return o


class MockSynamic:
    def __init__(self, module_values):
        self.__values = module_values

    @property
    def dynamic_contents(self):
        return self.__values

    def get_contents_by_module_name(self, whatever):
        return self.__values


def test(q="xxx | name endswith_ic 'j' | age > 10 ^ name contains_ic 's' | :sort_by age 'des'| :first 1"):
    mock_synamic = MockSynamic(mock_values())
    result = query_by_synamic_4_dynamic_contents(mock_synamic, q)
    pprint.pprint(result)

def test_will_fail_as_dicts_are_unhashable(q="xxx | name endswith_ic 'j' | age > 10 ^ name contains_ic 's' | :sort_by age 'des'| :first 1"):
    d = [
        {'name': "Sabuj", 'age': 28},
        {'name': "XSabuj", 'age': 20},
        {'name': "YSabuj", 'age': 10},
        {'name': "uabuj", 'age': 18},
        {'name': "pabuj", 'age': 2},
        {'name': "SSSSSabuj", 'age': 2},

    ]
    result = query_by_objects(d, q)
    pprint.pprint(result)

"""
# expression can be unary (without &, ^) or binary (with &, ^)
# operators are always binary

v0 =>
texts | title.length > 1 OR title.length < 100 | | title.length > 1 AND title.length < 100 | title contains "yo yo" | tags contains ["done", "complete"] | title startswith "no no" | :limit 20 | :offset 2 | id > 6 | :from 2 5 | :first 5 | :last 1 | @one


v => 
texts | title.length > 1 OR title.length < 100 | title.length > 1 AND title.length < 100 | title contains "yo yo" | tags contains ["done", "complete"] | title startswith "no no" | :limit 20 | :offset 2 | id > 6 | :from 2 5 | :first 5 | :last 1 | @one

"""

if __name__ == '__main__':
    test(q="xxx | age > 1 ^ name contains_ic 's' | :sort_by age 'des'| :first 100")

