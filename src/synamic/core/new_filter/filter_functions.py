v = """
texts | title.length > 1 | title contains "yo yo" | tags contains ["done", "complete"] | title startswith "no no" | :limit 20 | :offset 2 | id > 6 | :from 2 5 | :first 5 | :last 1 | @list | @one
"""
import re
from pprint import pprint
from collections import namedtuple

module_name_pat = re.compile(r"^(?P<module_name>[a-zA-Z0-9_-]+)", re.IGNORECASE)
pipe_pat = re.compile(r"[\s]*\|[\s]*")

field_name_pat = re.compile(r"^(?P<field_name>[.a-zA-Z0-9_-]+)", re.IGNORECASE)
operator_pat = re.compile(r"^(?P<operator>[a-zA-Z0-9=><!_-]+)")

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
    'endswith',
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
    'last'
}

valid_producer_fun_names = {
    'one'
}


def parse(filter_text, values):
    filtered_vlaue_s = values.copy()
    filter_text = filter_text.strip()
    module_name = module_name_pat.match(filter_text).group("module_name")
    print(module_name)
    query_str = filter_text[len(module_name):]
    query_str = query_str.lstrip(" |\r\n\t")
    print(query_str)

    queries = pipe_pat.split(query_str)
    pprint(queries)

    for query in queries:
        query = query.strip()
        print(query)
        if query.startswith('@'):
            # call producer
            producer_name = query[1:]
            filtered_vlaue_s = __filter_funs.producers[producer_name](filtered_vlaue_s)
            break
        elif query.startswith(':'):
            # call limitter
            limiter_name = query[1:].split(' ')[0]
            limiter_operands = (eval(x) for x in query[1:].split(' ')[1:])
            filtered_vlaue_s = __filter_funs.limiters[limiter_name](filtered_vlaue_s, limiter_operands)
        else:  # operator
            field_name = field_name_pat.match(query).group('field_name')
            _query = query[len(field_name):].strip()
            operator = operator_pat.match(_query).group('operator')
            _query = _query[len(operator):].strip()
            operand = eval(_query)
            print("Field name: %s, operator: %s, operand: %s" % (field_name, operator, operand))
            filtered_vlaue_s = __filter_funs.operators[operator](filtered_vlaue_s, field_name, operand)
    return filtered_vlaue_s

parse(v, [])

_FilterFuns = namedtuple('FilterFun', ['operators', 'limiters', 'producers'])
__filter_funs = _FilterFuns(operators={}, limiters={}, producers={})


# decorators
def operator_decorator(operator_fun):
    def inner_wrapper(operator_name):
        assert operator_name not in valid_operators_fun_names, "Invalid operator name"
        assert operator_name not in __filter_funs.operators, "Duplicate operator fun"
        __filter_funs.operators[operator_name] = operator_fun
        return operator_fun
    return inner_wrapper


def limiter_decorator(limiter_fun):
    def inner_wrapper(limiter_name):
        assert limiter_name not in valid_limiter_fun_names, "Invalid limiter name"
        assert limiter_name not in __filter_funs.limiters, "Duplicate limiter"
        __filter_funs.limiters[limiter_name] = limiter_fun
        return limiter_fun
    return inner_wrapper


def producer_decorator(producer_fun):
    def inner_wrapper(producer_name):
        assert producer_name not in valid_producer_fun_names, "Invalid producer name"
        assert producer_name not in __filter_funs.producers, "Duplicate producers"
        __filter_funs.producers[producer_name] = producer_fun
        return producer_fun
    return inner_wrapper

# operators


@operator_decorator('==')
def operator_eq():
    pass


@operator_decorator('!=')
def operator_neq():
    pass


@operator_decorator('>')
def operator_gt():
    pass


@operator_decorator('<')
def operator_lt():
    pass


@operator_decorator('>=')
def operator_gteq():
    pass


@operator_decorator('<=')
def operator_lteq():
    pass


@operator_decorator('contains')
def operator_contains():
    pass


@operator_decorator('!contains')
def operator_not_contains():
    pass


@operator_decorator('contains_ic')
def operator_contains_ic():
    pass


@operator_decorator('!contains_ic')
def operator_not_contains_ic():
    pass


@operator_decorator('startswith')
def operator_startswith():
    pass


@operator_decorator('!startswith')
def operator_not_startswith():
    pass


@operator_decorator('startswith_ic')
def operator_startswith_ic():
    pass


@operator_decorator('!startswith_ic')
def operator_not_startswith_ic():
    pass


@operator_decorator('endswith')
def operator_endswith():
    pass


@operator_decorator('!endswith')
def operator_not_endswith():
    pass


@operator_decorator('endswith_ic')
def operator_endswith_ic():
    pass


@operator_decorator('!endswith_ic')
def operator_not_endswith_ic():
    pass


# limiter
@limiter_decorator('limit')
def limiter_limit():
    pass


@limiter_decorator('offset')
def limiter_offset():
    pass


@limiter_decorator('from')
def limiter_from():
    pass


@limiter_decorator('first')
def limiter_first():
    pass


@limiter_decorator('last')
def limiter_last():
    pass


# producer
# @producer_decorator('list')
# def producer_list():
#     pass


@producer_decorator('one')
def producer_one():
    pass
