import sly
from sly import Lexer, Parser
from collections import namedtuple

UrlStruct = namedtuple('UrlStruct', ('scheme', 'keys', 'path'))


def parse_getc(text) -> UrlStruct:
    """
    """
    text = text.strip()
    parser = GetCParser()
    lexer = GetCLexer()
    try:
        if text == '':
            res = None
        else:
            res = parser.parse(lexer.tokenize(text))
    except sly.lex.LexError as e:
        txt_rest = e.text
        err_before_txt = '_' * (len(text) - len(txt_rest))
        err_after_txt = '^' * len(txt_rest)
        err_txt = '\n' + text + '\n' + err_before_txt + err_after_txt

        raise GetCParsingError(
            ('Lexical error at index: %s' % e.error_index) +
            err_txt
        )
    else:
        return res

class GetCParsingError(Exception):
    pass


class GetCLexer(Lexer):
    tokens = {'SCHEME_NAME', 'SCHEME_SEP', 'KEY', 'KEY_SEP', 'PATH'}
    PATH = r'[^:]+$'
    SCHEME_NAME = r'[a-zA-Z]+(?=://)'
    SCHEME_SEP = r'://'
    KEY = r'[a-zA-Z_][a-zA-Z0-9_-]*'
    KEY_SEP = r':'


class GetCParser(Parser):
    # Get the token list from the lexer (required)
    tokens = GetCLexer.tokens

    # Grammar rules and actions
    @_('PATH',  # normal relative url
       'SCHEME_NAME SCHEME_SEP PATH',  # normal absolute url
       'SCHEME_NAME SCHEME_SEP keys PATH'  # geturl
       )
    def query(self, p):
        length = len(p)
        if length == 1:
            struct = UrlStruct(scheme='', keys=tuple(), path=p[0])
        elif length == 3:
            struct = UrlStruct(scheme=p[0], keys=tuple(), path=p[2])
        else:
            assert length == 4
            struct = UrlStruct(scheme=p[0], keys=p[2], path=p[3])
        return struct

    @_('KEY KEY_SEP',
       'KEY KEY_SEP keys')
    def keys(self, p):
        if len(p) == 2:
            return p[0],
        else:
            assert len(p) == 3
            return p[0], p[2][0]

    def error(self, token):
        if not token:
            err = GetCParsingError(
                "EOF before tokens could be parsed sensibly"
            )
        else:
            err = GetCParsingError(
                f"Parsing error at token: {token.type} -> {token.value}. Error at index {token.index}"
            )
        raise err


if __name__ == '__main__':
    while True:
        try:
            text = input('parse > ')
        except EOFError:
            raise
        if text:
            try:
                res = parse_getc(text)
            except GetCParsingError as e:
                print(e.args[0])
            else:
                print(res)
