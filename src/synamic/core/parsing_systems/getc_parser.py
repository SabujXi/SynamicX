import sly
from sly import Lexer, Parser
from collections import namedtuple
from synamic.exceptions import SynamicGetCParsingError
from synamic.core.object_manager.query import generate_error_message

UrlStruct = namedtuple('UrlStruct', ('scheme', 'site_id', 'keys', 'path'))


def parse_getc(text) -> UrlStruct:
    """
    """
    text = text.strip()
    parser = GetCParser(text)
    lexer = GetCLexer()
    try:
        res = parser.parse(lexer.tokenize(text))
    except sly.lex.LexError as e:
        text_rest = e.text
        err_txt = generate_error_message(text, text_rest)

        raise SynamicGetCParsingError(
            f'Lexical error at index: {e.error_index}\nDetails: {err_txt}'
        )
    else:
        return res


class GetCLexer(Lexer):
    tokens = {'SCHEME_NAME', 'SCHEME_SEP', 'SITE_ID', 'KEY', 'KEY_SEP', 'PATH'}
    PATH = r'[^:]+$'
    SCHEME_NAME = r'[a-zA-Z]+(?=://)'
    SCHEME_SEP = r'://'
    SITE_ID = r'[^\s:/\\]+(~[^\s:/\\]+)+|~[^\s:/\\]+|~'
    # sync ~ this value with system system_settings['configs.site_id_sep']
    KEY = r'[a-zA-Z_][a-zA-Z0-9_-]*'
    KEY_SEP = r':'


class GetCParser(Parser):
    def __init__(self, text):
        self.__text = text

    # Get the token list from the lexer (required)
    tokens = GetCLexer.tokens

    # Grammar rules and actions
    @_('PATH',  # normal relative url
       'SCHEME_NAME SCHEME_SEP PATH',  # normal absolute url
       'SCHEME_NAME SCHEME_SEP keys PATH',  # geturl
       'SCHEME_NAME SCHEME_SEP SITE_ID KEY_SEP keys PATH'  # geturl
       )
    def query(self, p):
        length = len(p)
        if length == 1:
            struct = UrlStruct(scheme='', keys=tuple(), site_id=None, path=p[0])
        elif length == 3:
            struct = UrlStruct(scheme=p[0], keys=tuple(), site_id=None, path=p[2])
        elif length == 4:
            struct = UrlStruct(scheme=p[0], keys=p[2], site_id=None, path=p[3])
        else:
            assert length == 6
            struct = UrlStruct(scheme=p[0], keys=p[4], site_id=p[2], path=p[5])
        return struct

    @_('KEY KEY_SEP',
       'KEY KEY_SEP keys')
    def keys(self, p):
        if len(p) == 2:
            return p[0],
        else:
            assert len(p) == 3
            return p[0], p[2][0]

    def error(self, p):
        text = self.__text
        if not p:
            text_rest = ''
            err_txt = generate_error_message(text, text_rest)
            err = SynamicGetCParsingError(
                f"GetC End of param text before tokens could be parsed sensibly.\nDetails: {err_txt}"
            )
        else:
            text_rest = self.__text[p.index:]
            err_txt = generate_error_message(text, text_rest)
            err = SynamicGetCParsingError(
                f"GetC param Parsing error at token: {p.type} -> {p.value}."
                f" Error at index {p.index}.\nDetails:{err_txt}"
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
                for token in GetCLexer().tokenize(text):
                    print(token)
                res = parse_getc(text)
            except SynamicGetCParsingError as e:
                print(e.message)
            else:
                print(res)
