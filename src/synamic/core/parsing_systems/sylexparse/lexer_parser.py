# TODO: this module is totally incomplete
import re
pattern_type = type(re.compile(''))


class _Patterns:
    name = re.compile(r'\w+')


def is_type_pattern(o):
    return type(o) == pattern_type


class SyLexer:
    PATTERN_TUPLES = ()

    def __init__(self):
        assert isinstance(self.PATTERN_TUPLES, (type(None), list, tuple))
        patterns = [] if not isinstance(self.PATTERN_TUPLES, (tuple, list)) else list(self.PATTERN_TUPLES)

        self._patterns = []
        self.__pattern_names = set()

        for pattern in patterns:
            assert isinstance(pattern, (list, tuple)) and len(pattern) == 2
            self.add_pattern(pattern[0], pattern[1])

    def add_pattern(self, token_name, pattern):
        assert token_name not in self.__pattern_names
        assert _Patterns.name.match(pattern[0])
        token_tuple = (token_name, pattern)
        self._patterns.append(token_tuple)
        self.__pattern_names.add(token_name)

    def lex(self, text):
        assert isinstance(text, str)
        if len(text) == 0:
            return ()
        pos = 0


class SyToken:
    def __init__(self, name, value, match, start, end):
        self.name = name
        self.value = value
        self.match = match
        self.start = start
        self.end = end


class SyRule:
    def __init__(self, name, patterns):
        assert isinstance(name, str)
        self._name = name
        self._patterns = []
        self.__pattern_names = set()
        if not isinstance(patterns, (list, tuple)):
            assert isinstance(patterns, (str, pattern_type))

    @property
    def name(self):
        return self._name

    def add_pattern(self, token_name, pattern):
        assert token_name not in self.__pattern_names
        assert _Patterns.name.match(pattern[0])
        token_tuple = (token_name, pattern)
        self._patterns.append(token_tuple)
        self.__pattern_names.add(token_name)
