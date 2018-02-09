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
import enum
import collections


@enum.unique
class FilterOperators(enum.Enum):
    MEMBERSHIP = '~'
    NOT_MEMBERSHIP = '!~'
    EQUAL = '=='
    GTE = '>='
    LTE = '<='
    GT = '>'
    LT = '<'
    NOT_EQUAL = '!='
    COMMA = ','


@enum.unique
class CombinatorOperators(enum.Enum):
    UNION = '&'
    INTERSECTION = '|'


@enum.unique
class SeparatorOperators(enum.Enum):
    MODULE_SEPARATOR = ':'
    SORT_SEPARATOR = ';'


@enum.unique
class LogicWords(enum.Enum):
    AND = 'and'
    OR = 'or'


logicwords_regex_or = "|".join([re.escape(o) for o in [o.value for o in list(LogicWords)]])
filter_operators_regex_or = "|".join([re.escape(o) for o in [o.value for o in list(FilterOperators)]])
combinator_operators_regex_or = "|".join([re.escape(o) for o in [o.value for o in list(CombinatorOperators)]])
separator_operators_regex_or = "|".join([re.escape(o) for o in [o.value for o in list(SeparatorOperators)]])


@enum.unique
class TokenTypes(enum.Enum):
    WHITESPACE = 'whitespace'
    BLOCK_START = 'block_start'
    BLOCK_END = 'block_end'
    DATA = 'data'
    LOGICAL_KEYWORD = 'logical_keyword'
    NAME = 'name'
    FILTER_OPERATOR = 'filter_operator'
    COMBINATOR_OPERATOR = 'combinator_operator'
    SEPARATOR_OPERATOR = 'separator_operator'


TokenContainer = collections.namedtuple('TokenContainer', ['type', 'value', 'start', 'end'])

# print(operators_regex_or,keywords_regex_or)

_name_pat = re.compile(r'[a-z][a-z0-9_-]*[a-z]', re.I)
_whitespace = re.compile(r'\s')
_quoted_str = re.compile(r'(\'|")(?P<data>.*?)\1')
_filter_operator_pat = re.compile(filter_operators_regex_or)  # ~, !~ for membership, union &, | intersection
_combinator_operator_pat = re.compile(combinator_operators_regex_or)  # ~, !~ for membership, union &, | intersection
_separator_operator_pat = re.compile(separator_operators_regex_or)  # ~, !~ for membership, union &, | intersection
_data_pat = re.compile(r'[^)]+')
_logical_keyword_pat = re.compile(logicwords_regex_or)
_sort_by_regex = re.compile(r'sort\s+by\s+(?P<filter_name>[a-z][a-z0-9_-]*[a-z])\s+in\s+(?P<order>asc|desc)', re.I)


class TravelString(str):
    # def __init__(self):
    #     super().__int__()
    def tokenize(self):
        tokens = []
        start = 0
        while start < len(self):
            #             print(s[start:])
            m = _whitespace.match(self, start)
            if m:
                tokens.append(TokenContainer(type=TokenTypes.WHITESPACE, value=m.group(), start=start, end=m.end()))
                start += m.end() - start
                continue
            if self[start] == '(':
                tokens.append(TokenContainer(type=TokenTypes.BLOCK_START, value='(', start=start, end=start + 1))
                start += 1
                continue

            if self[start] == ')':
                tokens.append(TokenContainer(type=TokenTypes.BLOCK_END, value=')', start=start, end=start + 1))
                start += 1
                continue

            m = _quoted_str.match(self, start)
            if m:
                tokens.append(TokenContainer(type=TokenTypes.DATA, value=m.group(2), start=start, end=m.end()))
                start += m.end() - start
                continue

            m = _logical_keyword_pat.match(self, start)
            if m:
                tokens.append(TokenContainer(type=TokenTypes.LOGICAL_KEYWORD, value=m.group(), start=start, end=m.end()))
                start += m.end() - start
                continue

            m = _name_pat.match(self, start)
            if m:
                tokens.append(TokenContainer(type=TokenTypes.NAME, value=m.group(), start=start, end=m.end()))
                start += m.end() - start
                continue

            m = _filter_operator_pat.match(self, start)
            if m:
                tokens.append(TokenContainer(type=TokenTypes.FILTER_OPERATOR, value=m.group(), start=start, end=m.end()))
                start += m.end() - start
                continue

            m = _combinator_operator_pat.match(self, start)
            if m:
                tokens.append(TokenContainer(type=TokenTypes.COMBINATOR_OPERATOR, value=m.group(), start=start, end=m.end()))
                start += m.end() - start
                continue

            m = _separator_operator_pat.match(self, start)
            if m:
                tokens.append(TokenContainer(type=TokenTypes.SEPARATOR_OPERATOR, value=m.group(), start=start, end=m.end()))
                start += m.end() - start
                if m.group() == SeparatorOperators.SORT_SEPARATOR.value:
                    tokens.append(TokenContainer(type=TokenTypes.DATA, value=self[start:].strip(), start=start, end=len(self)))
                    start = len(self)
                continue

            m = _data_pat.match(self, start)
            if m:
                tokens.append(TokenContainer(type=TokenTypes.DATA, value=m.group(), start=start, end=m.end()))
                start += m.end() - start
                continue

            tokens.append(TokenContainer(type=TokenTypes.DATA, value=self[start:], start=start, end=len(self)))
            start = len(self)
        return self.remove_whitespaces_commas(tokens)

    @staticmethod
    def remove_whitespaces_commas(tokens):
        """
        Remove white spaces from token for further processing.
        """
        _tokens = []
        for x in tokens:
            if x.type is TokenTypes.WHITESPACE or x.value == FilterOperators.COMMA.value:
                continue
            _tokens.append(x)
        return _tokens

    @staticmethod
    def display(tokens):
        for x in tokens:
            print("%s       : %s" % (x[3], x[2]))


class QueryContainer:
    def __init__(self, queries, filter, order):
        self.__queries = queries
        self.__filter = filter
        self.__order = order

    @property
    def queries(self):
        return self.__queries

    @property
    def sort_filter_name(self):
        return self.__filter

    @property
    def sort_filter_order(self):
        return self.__order

    def __str__(self):
        return "%s\n\nsort filter name=%s\nsort order=%s\n" % (str(self.queries), self.sort_filter_name, self.sort_filter_order)


class Query:
    def __init__(self, mod_name):
        self.__module_name = mod_name
        self.__filters = []
        self.__combinator = None

    @property
    def module_name(self):
        return self.__module_name

    @property
    def has_filters(self):
        if len(self.__filters) > 0:
            return True
        return False

    @property
    def filters(self):
        return self.__filters

    def add_filter(self, f):
        assert type(f) is Filter
        self.__filters.append(f)

    @property
    def combinator(self):
        return self.__combinator

    @combinator.setter
    def combinator(self, com):
        self.__combinator = com

    def __str__(self):
        return "Query(module_name=%s, filters=\n%s  combinator=%s\n)" % (self.module_name, self.filters, self.combinator)

    def __repr__(self):
        return self.__str__()


class Filter:
    def __init__(self, filter_name):
        self.__filter_name = filter_name
        self.__operator = None
        self.__data_s = []
        self.__logical_operator = None

    @property
    def filter_name(self):
        return self.__filter_name

    @filter_name.setter
    def filter_name(self, name):
        self.__filter_name = name

    @property
    def operator(self):
        return self.__operator

    @operator.setter
    def operator(self, op):
        self.__operator = op

    @property
    def data_s(self):
        return self.__data_s

    @data_s.setter
    def data_s(self, d):
        self.__data_s.append(d)

    @property
    def has_logical_operator(self):
        return True if self.__logical_operator is not None else False

    @property
    def logical_operator(self):
        return self.__logical_operator

    @logical_operator.setter
    def logical_operator(self, op):
        self.__logical_operator = op

    def __str__(self):
        return "\n    Filter(filter_name=%s, operator=%s, data_s=%s)" % (self.filter_name, self.operator, self.data_s)

    def __repr__(self):
        return self.__str__()


class Parser:
    def __init__(self, toks):
        self.__toks = toks
        self.__cur_pos = -1
        self.__queries = []
        self.__filter = None
        self.__order = None
        # self.__cur_query = None

    def advance_pos(self, by):
        self.__cur_pos += by

    def find_next_token(self, advance_pos):
        assert advance_pos >= 0
        real_next_pos = self.__cur_pos + advance_pos
        if real_next_pos < len(self.__toks):
            return self.__toks[real_next_pos]
        return None

    def get_queries(self):
        self.advance_pos(1)
        self.do_block_start()
        # if not self.next__block_end(1):
        #     raise Exception("Did not end with a proper end block")
        return QueryContainer(self.__queries, self.__filter, self.__order)

    def do_block_start(self):
        cur_tok = self.__toks[self.__cur_pos]
        if cur_tok.type is not TokenTypes.BLOCK_START:
            raise Exception("Expected a start block here: %s" % cur_tok)
        else:
            # if not self.next__name(1):  #cur_tok.type is not TokenTypes.NAME:
            #     raise Exception("Invalid syntax, the next token should be of type name")
            # else:
            #     # self.next__operator(2)
            self.advance_pos(1)
            self.do_module_name()

    def do_module_name_separator(self):
        cur_tok = self.__toks[self.__cur_pos]
        if cur_tok.type is TokenTypes.BLOCK_END:
            return
        elif cur_tok.type is not TokenTypes.FILTER_OPERATOR:
            raise Exception("Expected an operator here")
        else:
            if cur_tok.value != FilterOperators.MODULE_SEPARATOR.value:
                raise Exception("Expected a module separator here")
            else:
                self.advance_pos(1)
                self.do_module_name()

    def do_module_name(self):
        cur_tok = self.__toks[self.__cur_pos]
        # print("In mod name: %s" % str(cur_tok))
        if cur_tok.type is not TokenTypes.NAME:
            raise Exception("Expected a module name here: %s" % str(cur_tok))
        else:
            self.__queries.append(Query(cur_tok.value))

            if self.next__block_end(1):
                self.advance_pos(1)
                self.do_block_end()
                return
            else:
                self.advance_pos(1)
                self.do_module_separator()

    def do_module_separator(self):
        cur_tok = self.__toks[self.__cur_pos]
        if cur_tok.type is not TokenTypes.SEPARATOR_OPERATOR:
            raise Exception("Expected module separator here: %s" % str(cur_tok))
        else:
            self.advance_pos(1)
            self.do_filter_name()
            # if self.next__block_end(1):
            #     return
            # else:
            #     if not self.next__operator(2):
            #         raise Exception("Must be an operator ther")
            #     else:
            #         if not self.next__operator(2).value == Operators.MODULE_SEPARATOR:
            #             raise Exception("Must be a module separator there")

    def do_filter_name(self):
        cur_tok = self.__toks[self.__cur_pos]
        if cur_tok.type is not TokenTypes.NAME:
            raise Exception("Must be a name here: %s" % str(cur_tok))
        else:
            # op = self.next__operator(1)
            # if not op:
            #     raise Exception("This should be an operator")
            self.__queries[-1].add_filter(Filter(cur_tok.value))
            self.advance_pos(1)
            self.do_filter_operator()

    def do_filter_operator(self):
        cur_tok = self.__toks[self.__cur_pos]
        if cur_tok.type is not TokenTypes.FILTER_OPERATOR:
            raise Exception("Expected a filter operator here")
        self.__queries[-1].filters[-1].operator = cur_tok.value
        self.advance_pos(1)
        self.do_data_s()

    def do_data_s(self):
        cur_tok = self.__toks[self.__cur_pos]
        if cur_tok.type is TokenTypes.DATA:
            self.__queries[-1].filters[-1].data_s = cur_tok.value
            if self.next__block_end(1):
                # if self.next__block_end(1).type is
                self.advance_pos(1)
                self.do_block_end()
                return
            else:
                next_tok = self.find_next_token(1)
                if next_tok:
                    if next_tok.type is TokenTypes.LOGICAL_KEYWORD:
                        self.advance_pos(1)
                        self.do_logical_operator()
                    else:
                        self.advance_pos(1)
                        self.do_data_s()
                else:
                    raise Exception("Cannot end such abruptly")

        else:
            # if len(self.__cur_query.filters[-1].data_s) > 0:
            raise Exception("Current token was expected to be data: %s" % str(cur_tok))

    def do_logical_operator(self):
        cur_tok = self.__toks[self.__cur_pos]
        print("LLLLLOOOOOGGGGIIIICAL: %s" % str(cur_tok))
        self.__queries[-1].filters[-1].logical_operator = cur_tok.value
        self.advance_pos(1)
        self.do_filter_name()

    def do_block_end(self):
        cur_tok = self.__toks[self.__cur_pos]
        if cur_tok.type is TokenTypes.BLOCK_END:
            if not self.find_next_token(1):
                return
            else:
                self.advance_pos(1)
                self.do_combinator()
        else:
            raise Exception("Expected block end here")

    def do_combinator(self):
        cur_tok = self.__toks[self.__cur_pos]
        if cur_tok.type is TokenTypes.COMBINATOR_OPERATOR:
            self.__queries[-1].combinator = cur_tok.value
            self.advance_pos(1)
            self.do_sort_separator()
        elif cur_tok.type is TokenTypes.SEPARATOR_OPERATOR:
            # self.advance_pos(1)
            self.do_sort_separator()
        else:
            raise Exception("Expected operator here: %s" % str(cur_tok))

    def do_sort_separator(self):
        cur_tok = self.__toks[self.__cur_pos]
        if cur_tok.type is TokenTypes.BLOCK_START:
            self.do_block_start()
        else:
            if cur_tok.value == SeparatorOperators.SORT_SEPARATOR.value:
                # self.__queries[-1].combinator = cur_tok.value
                self.advance_pos(1)
                self.do_sort()
            else:
                raise Exception("Expected sort separator here: %s" % str(cur_tok))

    def do_sort(self):
        cur_tok = self.__toks[self.__cur_pos]
        if cur_tok.type is not TokenTypes.DATA:
            raise Exception("Sort data was expected")
        else:
            data = cur_tok.value
            m = _sort_by_regex.match(data)
            if not m:
                raise Exception("Sort pattern did not match: %s where pattern was %s" % (data, _sort_by_regex.pattern))
            else:
                self.__filter = m.group('filter_name')
                self.__order = m.group('order')
                # print("Sort data: %s - %s" % (m.group('filter_name'), m.group('order')))

    def next__block_start(self, next_pos):
        tok = self.find_next_token(next_pos)
        if tok:
            if tok.type is TokenTypes.BLOCK_START:
                return tok
        return None

    def next__block_end(self, next_pos):
        tok = self.find_next_token(next_pos)
        if tok:
            if tok.type is TokenTypes.BLOCK_END:
                return tok
        return None

    def next__nothing(self, next_pos):
        tok = self.find_next_token(next_pos)
        if tok is None:
            return True
        return False


def get_query_container(query_str):
    toks = TravelString(query_str).tokenize()
    queries = Parser(toks).get_queries()
    print(queries)
    return queries


# Operator functions
def eq_operator(content_value, value):
    print("%s ==? %s\n" % (content_value, value))
    return True if content_value == value else False


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
    '~' : membership_operator,
    '!~' : negative_membership_operator
}


# filter functions
allowed_filters = {
    'tags', 'categories', 'created-on', 'id', 'name', 'language'
}

allowed_sort_bys = {
    'created-on', 'id', 'name', 'title'
}


def filter_dispatcher(query: Query, content):
    if not query.has_filters:
        return True

    res = None

    for _filter in query.filters:
        # _filter = [0]
        filter = _filter.filter_name
        operator = _filter.operator
        value_s = _filter.data_s
        if filter in content.frontmatter:
            if filter == 'tags' or filter == 'categories':
                content_value_s = getattr(content, filter)
            elif filter == 'created-on':
                content_value_s = getattr(content, 'created_on')
                value_s = value_s[0]
            else:
                content_value_s = content.frontmatter[filter]
                value_s = value_s[0]
            # print("content_value_s: %s" % content_value_s)
            operator_fun = operator_functions[operator]
            # print("Operator fun: %s" % operator_fun)
            _res = operator_fun(content_value_s, value_s)
        else:
            _res = False
        if value_s == 'en':
            print("\nLLLLLLOOOOOOOOOPPPPPPPPP: %s=> %s : %s" % (filter, value_s, content_value_s))

        if value_s == 'bn':
            print("\nLLLLLLOOOOOOOOOPPPPPPPPP: %s=> %s : %s" % (filter, value_s, content_value_s))

        if res is None:
            res = _res
            print("\n\nLLLLLLOOOOOOOOOPPPPPPPPP: %s" % _filter.logical_operator)
        else:
            if filter.logical_operator == 'and':
                res = res and _res
            else:
                res = res or _res
    return res



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


# get_query_container("(text: tag == 'x' and id > '5') & (blog)")