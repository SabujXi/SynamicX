"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
import os
import collections
import jinja2.exceptions

__all__ = ['SynamicError', 'SynamicTemplateError', 'SynamicQueryParsingError', 'SynamicGetCParsingError']


def format_msg_map(msg_map):
    lines = []
    for key, value in msg_map.items():
        if isinstance(value, str) and '\n' in value:
            value = '\n' + value
        lines.append(
            f'{key}: {value}'
        )
    if lines:
        lines.append('\n')
    return '\n'.join(lines)


def get_source_snippet(fn, line_no, limit=10):
    if os.path.exists(fn):
        with open(fn, encoding='utf-8') as f:
            source = f.read()
    else:
        source = ''
    lines = source.splitlines()

    half_limit = limit//2
    half_limit_l = half_limit
    if line_no >= half_limit:
        half_limit_l = line_no - half_limit
    else:
        half_limit_l = 1
    res = []
    res.extend(
        ['....' + line for line in lines[half_limit_l - 1:line_no - 1]]
    )

    error_line = lines[line_no - 1]
    res.append('->..' + error_line)

    res.extend(
        ['....' + line for line in lines[line_no:line_no + half_limit]]
    )
    return '\n'.join(res)


class SynamicError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return repr(self.__str__())


class SynamicTemplateError(SynamicError):
    def __init__(self, jinja_ex):
        assert isinstance(jinja_ex, jinja2.exceptions.TemplateError),\
            f'Exception instance passed to {self.__class__} must be of jinja2.TemplateError'
        self.error_map = error_map = collections.OrderedDict()
        self.error_type = None
        self.message = None

        if isinstance(jinja_ex, jinja2.exceptions.TemplateSyntaxError):
            self.error_type = 'Template Syntax Error'
            self.message = self.message
            error_map['Error Message'] = jinja_ex.message
            error_map['Line No'] = jinja_ex.lineno
            error_map['Template Name'] = jinja_ex.name
            error_map['File Name'] = jinja_ex.filename
            error_map['Source'] = get_source_snippet(jinja_ex.filename, jinja_ex.lineno, limit=10)
        elif isinstance(jinja_ex, jinja2.exceptions.TemplateRuntimeError):
            self.error_type = 'Template Runtime Error'
            self.message = self.message
        elif isinstance(jinja_ex, jinja2.exceptions.TemplatesNotFound):
            self.error_type = 'Templates not Found'
            self.message = self.message
            error_map['Template Names'] = jinja_ex.names
        elif isinstance(jinja_ex, jinja2.exceptions.TemplateNotFound):
            self.error_type = 'A Template not Found'
            self.message = self.message
            error_map['Template Name'] = jinja_ex.name
        elif isinstance(jinja_ex, jinja2.exceptions.UndefinedError):
            self.error_type = 'Template Undefined Variable'
            self.message = self.message
        else:
            raise Exception('What have i missed!?')

        self.message = \
\
f"""
Error Type: {self.error_type}
{format_msg_map(self.error_map)}
Details:
{str(jinja_ex)}
"""


class SynamicQueryParsingError(SynamicError):
    """Raised when there is an error in lexing or parsing query string."""


class SynamicGetCParsingError(SynamicError):
    """Raised when there is an error in lexing or parsing param string of getc()"""


class LogicalError(SynamicError):
    pass


class InvalidQueryString(SynamicError):
    pass


class GetUrlFailed(SynamicError):
    pass


class GetContentFailed(SynamicError):
    pass


class ParsingError(SynamicError):
    pass


class InvalidFrontMatter(SynamicError):
    pass


class InvalidFileNameFormat(SynamicError):
    pass


class DuplicateContentId(SynamicError):
    pass
