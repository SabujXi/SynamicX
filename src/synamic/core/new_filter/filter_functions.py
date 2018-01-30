v = """
texts | title.length > 1 | title contains "yo yo" | tags contains ["done", "complete"] | title startswith "no no" | :limit 20 | :offset 2 | id > 6 | :from 2 5 | :first 5 | :last 1 | @list | @one
"""
import re
from pprint import pprint

module_name_pat = re.compile(r"^(?P<module_name>[a-zA-Z0-9_-]+)", re.IGNORECASE)
pipe_pat = re.compile(r"[\s]*\|[\s]*")

field_name_pat = re.compile(r"^(?P<field_name>[.a-zA-Z0-9_-]+)", re.IGNORECASE)
operator_pat = re.compile(r"^(?P<operator>[a-zA-Z0-9=><!_-]+)")
operators_to_fun = {
    'contains': [1, None],
    '!contains': [1, None],
    'contains_ic': [1, None],
    '!contains_ic': [1, None],
    'startswith': [1, None],
    '!startswith': [1, None],
    'startswith_ic': [1, None],
    'endswith': [1, None],
    '!endswith_ic': [1, None],
    '=': [1, None],
    '!=': [1, None],
    '>': [1, None],
    '<': [1, None],
    '>=': [1, None],
    '<=': [1, None]
}

def parse(raw):
    raw = raw.strip()
    module_name = module_name_pat.match(raw).group("module_name")
    print(module_name)
    query_str = raw[len(module_name):]
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
        elif query.startswith(':'):
            # call limitter
            limiter_name = query[1:].split(' ')[0]
            limiter_operators = (eval(x) for x in query[1:].split(' ')[1:])
        else:  # operator
            field_name = field_name_pat.match(query).group('field_name')
            _query = query[len(field_name):].strip()
            operator = operator_pat.match(_query).group('operator')
            _query = _query[len(operator):].strip()
            operand = eval(_query)
            print("Field name: %s, operator: %s, operand: %s" % (field_name, operator, operand))

parse(v)

# operators
def operator_eq():
    pass

def operator_neq():
    pass

def operator_gt():
    pass

def operator_lt():
    pass

def operator_gteq():
    pass

def operator_lteq():
    pass

def operator_contains():
    pass

def operator_contains_ic():
    pass

def operator_startswith():
    pass

def operator_startswith_ic():
    pass

def operator_endswith():
    pass

def operator_endswith_ic():
    pass


# limiter

def limiter_limit():
    pass
def limiter_offset():
    pass
def limiter_from():
    pass
def limiter_first():
    pass
def limiter_last():
    pass

# producer

def producer_list():
    pass

def producer_one():
    pass
