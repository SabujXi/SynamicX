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
We need a mini language for filtering content.
We specially need this for pagination.

Module filtering:
--------------------
module_name: <filtering_string>

filtering_string:
--------------------
Filtering string contains two parts 


tags 'net'  # serving as both `in` and `equal` operator
tags not 'net', 'fool' # serving as both `not in` and `not equal` operator
datetime > '';
price < '';

Example: (text: tags 'net', 'price'; sort by date in asc) && (categories new)

Queries can be done on and the rules are set for:
- content id
- content url name  #  ** planning to change url name to content_name **
- datetime (creation)
- tags
- categories


Parsing:
--------

allowed_filters = ['tags', 'categories', 'created_on' ...]

rules = txt.split("&&")

# rule validations
for rule in rules:
    assert rule.startswith("(") and rule.endswith(")"), "Invalid rules"
    
    mod_name = rule.split(":")[0]
    assert mod_name in mod_names
    
    filter = rule.split(":")[0].split(" ")[0]
    assert filter in allowed_filters
    
    comparison = ...
    comparables = ...
    sort_filter = ...
    sort_order = ...

rules_function_mapping = {
    '' : membership_fun,
    'not': not membership_fun,
    '>': gt fun,
    '<': lt_fun,
    '>=': ...
    '<=' ...
}

** value(s) of filter must always be single quoted **
"""

__all__ = [
    'parse_rules',
    'filter_dispatcher'
]

# Operator functions
def eq_operator(content_value, value):
    return content_value == value


def neq_operator(content_value, value):
    return not eq_operator(content_value, value)


def gt_operator(content_value, value):
    return content_value > value


def lt_operator(content_value, vlaue):
    return content_value < vlaue


def gte_operator(content_value, value):
    return gt_operator(content_value, value) or eq_operator(content_value, value)


def lte_operator(content_value, value):
    return lt_operator(content_value, value) or eq_operator(content_value, value)


def membership_operator(content_values, values):
    res = True
    for value in values:
        if value not in content_values:
            res = False
    return res


def negative_membership_operator(content_values, value):
    return not membership_operator(content_values, value)


operator_functions = {
    '==' : eq_operator,
    '!=' : neq_operator,
    '>' : gt_operator,
    '<' : lt_operator,
    '>=' : gte_operator,
    '<=' : lte_operator,
    'in' : membership_operator,
    'not in' : negative_membership_operator
}


# filter functions
allowed_filters = {
    'tags', 'categories', 'created-on', 'id', 'name'
}

allowed_sort_bys = {
    'created-on', 'id', 'name', 'title'
}


def filter_dispatcher(content, filter, operator, value_s):
    print("Filter: %s, Operators: %s, values: %s" % (filter, operator, value_s))
    if filter is None: # that means: and operator is None and value_s is None:
        assert operator is None and value_s is None
        return True

    if filter in content.frontmatter:
        if filter == 'tags' or filter == 'categories':
            content_value_s = getattr(content, filter)
        elif filter == 'created-on':
            content_value_s = getattr(content, 'created-on')
        else:
            content_value_s = content.frontmatter[filter]
        print("content_value_s: %s" % content_value_s)
        operator_fun = operator_functions[operator]
        print("Operator fun: %s" % operator_fun)
        return operator_fun(content_value_s, value_s)
    return False


combinators = {
    '&&',
    '//'
}


def parse_values(txt, filter, single=True):
    values = [x.strip().strip('\'') for x in txt.split(',')]
    parsed_values = []
    for val in values:
        if filter == 'created-on':
            from synamic.core.functions.date_time import parse_datetime
            val = parse_datetime(val)
        parsed_values.append(val)
    if single:
        return parsed_values[0]
    else:
        return parsed_values


def parse_rules(rules_txt, mod_names):
    import re, collections
    ParsedRule = collections.namedtuple('ParsedRule', ['module_name', 'filter', 'operator', 'value_s', 'combinator'])
    Sort = collections.namedtuple('Sort', ['by_filter', 'order'])
    """
    Sorting comes at the end of the all rules
    Example rule text:
        (text: tags in 'net', 'price') and (categories in 'new') | sort by <a filter name> in asc/desc
    """
    parsed_rules = []  # list of (mod_name, filter, operator, value_s)
    _rules_sort = rules_txt.rsplit("|", maxsplit=1)
    _rules, _sort = (_rules_sort[0], None) if len(_rules_sort) == 1 else _rules_sort  # assuming len of _rulses sort is 2 now
    rules = []
    Rule = collections.namedtuple("Rule", ['combinator', 'rule'])

    print("Rules: %s" % _rules)

    rules_combinators = [x.strip() for x in re.compile('(&&|//)').split(_rules)]
    print("RulesCombinators 0: %s" % rules_combinators)
    if len(rules_combinators) == 1:
        rules.append(Rule(combinator=None, rule=rules_combinators[0]))
    else:
        i = 0
        pair = []
        while i < len(rules_combinators):
            if i % 2 == 0:
                # adding rule
                pair.append(rules_combinators[i])
            else:
                pair.append(rules_combinators[i])
                rules.append(Rule(combinator=pair[1], rule=pair[0]))
                pair = []  # emptying for new pair
            i += 1
        if len(pair) == 1:
            rules.append(Rule(combinator=None, rule=pair[0]))
    print("RulesCombinators: %s" % rules_combinators)
    print("Rules array: %s" % rules)
    # rule validations
    for combinator, rule in rules:
        assert rule.startswith("(") and rule.endswith(")"), "Invalid rule: %s" % rule
        rule = rule.strip("()")

        # module name
        name_n_checks = rule.split("::")
        if len(name_n_checks) == 1:
            mod_name = name_n_checks[0]
            checks = ""
        else:
            mod_name, checks = name_n_checks
            assert len(name_n_checks) == 2
        checks = checks.strip()
        assert mod_name in mod_names, "Invalid module_object name: %s" % mod_name
        # filter
        filter = None
        if checks:
            for fl in allowed_filters:
                if checks.startswith(fl):
                    filter = fl
                    checks = checks[len(fl):]
            # assert filter, "No filter found" << no need of this as filter can be no existent

        operator = None
        if checks:
            checks = checks.strip()
            print("Checks: %s" % checks)
            _values = None
            for op in sorted(operator_functions.keys(), reverse=True):  # from bigger to smaller
                if checks.startswith(op):
                    operator = op
                    _values = checks[len(op):]

            assert operator, "A valid operator not found"

        value_s = None
        if operator:
            if operator == 'not in' or operator == 'in':  # multiple values
                value_s = parse_values(_values, filter, single=False)
            else:
                value_s = parse_values(_values, filter, single=True)

        parsed_rules.append(ParsedRule(mod_name, filter, operator, value_s, combinator))
    # Sort parsing
    sort = None
    if _sort:
        _sort = _sort.strip()
        sort_rule = re.compile(
            r"^sort\s+by\s+(?P<filter>%s)\s+in\s+(?P<order>asc|desc)" % "|".join(allowed_sort_bys), re.I)
        sort_match = sort_rule.match(_sort)
        if sort_match:
            sort = Sort(sort_match.group('filter'), sort_match.group('order'))
        else:
            raise Exception("Invalid sort: %s" % _sort)

    return parsed_rules, sort
