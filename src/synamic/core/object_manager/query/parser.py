import operator
from sly import Lexer, Parser
from synamic.core.parsing_systems.curlybrace_parser import SydParser  #covert_one_value
from collections import OrderedDict, namedtuple


class SimpleQueryParser:
    COMPARE_OPERATORS = tuple([
        'contains',
        '!contains',
        'in',
        '!in',
        '==',
        '!=',
        '>=',
        '<=',
        '>',
        '<',
    ])

    COMPARE_OPERATORS_SET = frozenset(COMPARE_OPERATORS)

    COMPARE_OPERATOR_2_PY_OPERATOR_FUN = {
        'contains': operator.contains,
        '!contains': lambda a, b: not operator.contains(a, b),
        'in': lambda a, b: operator.contains(b, a),
        '!in': lambda a, b: not operator.contains(b, a),
        '==': operator.eq,
        '!=': operator.ne,
        '>=': operator.ge,
        '<=': operator.le,
        '>': operator.gt,
        '<': operator.lt
    }

    QuerySection = namedtuple('QuerySection', ('key', 'comp_op', 'value'))

    def __init__(self, txt):
        self.__txt = txt

    def parse(self):
        """
        title == something | type in go, yes & age > 6
        """
        return parser.parse(lexer.tokenize(self.__txt))


class QueryNode:
    def __init__(self, logic_op, left, right):
        self.__logic_op = logic_op
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    @property
    def logic_op(self):
        return self.__logic_op

    def __str__(self):
        return """
        QueryNode( %s %s %s )
        """ % (str(self.left), str(self.logic_op), str(self.right))

    def __repr__(self):
        return repr(self.__str__())


def test(query):
    tokens = SimpleQueryParser(query).parse()
    for token in tokens:
        print(token)


if __name__ == 'l__main__':
    test('up sort asc | x == 1&time > 11:24 PM | date == 2013-2-1 | dt < 1023-12-12     11:33:43 am | a > b & c in d | d in ~hh        & m contains tag 1, tag 2 & n !in go sfsdfsdf')


class QueryValueLexer(Lexer):
    tokens = {'VALUE', }

    @_(r'[^&|]+')
    def VALUE(self, t):
        self.begin(QueryLexer)
        t.value = t.value.strip()
        return t


class QueryLexer(Lexer):
    tokens = {'KEY', 'COMP_OP', 'AND', 'OR'}
    ignore_ws = r'\s'

    @_(r'[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*')
    def KEY(self, t):
        return t

    @_(r'>|<|==|!=|>=|<=|\s*in|!in|\s*contains|!contains')
    def COMP_OP(self, t):
        self.begin(QueryValueLexer)
        t.value = t.value.strip()
        return t

    @_(r'&')
    def AND(self, t):
        return t

    @_(r'\|')
    def OR(self, t):
        return t

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1


class QueryParser(Parser):
    # Get the token list from the lexer (required)
    tokens = {*QueryLexer.tokens, *QueryValueLexer.tokens}
    precedence = [
        ('left', 'OR'),
        ('left', 'AND'),
    ]

    # Grammar rules and actions
    @_('KEY COMP_OP VALUE')
    def expr(self, p):
        converted_value = SydParser.covert_one_value(p[2])
        return SimpleQueryParser.QuerySection(key=p[0], comp_op=p[1], value=converted_value)

    @_('expr OR expr',
       'expr AND expr')
    def expr(self, p):
        left_section, right_section = p[0], p[2]
        return QueryNode(p[1], left_section, right_section)


parser = QueryParser()
lexer = QueryLexer()

if __name__ == '__main__':
    while True:
        try:
            text = input('parse > ')
        except EOFError:
            break
        if text:
            result = parser.parse(lexer.tokenize(text))
            print(result)
