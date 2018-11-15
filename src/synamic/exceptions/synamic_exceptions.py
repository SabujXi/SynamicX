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

__all__ = [
    # functions
    'get_source_snippet_from_file', 'get_source_snippet_from_text',
    # exception classes
    'SynamicError', 'SynamicErrors', 'SynamicTemplateError', 'SynamicQueryParsingError', 'SynamicGetCParsingError',
    'SynamicGetCError', 'SynamicPreProcessorNotFound', 'SynamicMarkerNotFound', 'SynamicMarkNotFound',
    'SynamicInvalidNumberFormat', 'SynamicModelParsingError', 'SynamicInvalidDateTimeFormat',
    'SynamicSettingsError', 'SynamicInvalidCPathComponentError', 'SynamicPathDoesNotExistError',
    'SynamicSydParseError', 'SynamicFSError', 'SynamicDataError', 'SynamicMarkerIsNotPublic', 'SynamicSiteNotFound',
    'SynamicUserNotFound',
]


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


def get_source_snippet_from_file(fn, line_no, limit=10):
    if os.path.exists(fn):
        with open(fn, encoding='utf-8') as f:
            source = f.read()
    else:
        source = ''
    return get_source_snippet_from_text(source, line_no, limit=limit)


def get_source_snippet_from_text(text, line_no, limit=10):
    source = text
    lines = source.splitlines()

    half_limit = limit//2
    half_limit_l = half_limit
    if line_no > half_limit:
        half_limit_l = line_no - half_limit
    else:
        half_limit_l = 1
    res = []
    res.extend(
        ['.... ' + line for line in lines[half_limit_l - 1:line_no - 1]]
    )

    error_line = lines[line_no - 1]
    res.append('->.. ' + error_line)

    res.extend(
        ['.... ' + line for line in lines[line_no:line_no + half_limit]]
    )
    return '\n'.join(res)


class SynamicError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return repr(self.__str__())


class SynamicErrors(SynamicError):
    def __init__(self, message, *synamic_errors):
        messages_for_errors = ''
        for err in synamic_errors:
            assert isinstance(err, SynamicError)
            messages_for_errors += f'\n{err.__class__.__name__}:\n{"-" * len(err.__class__.__name__)}\n' + err.message

        self.message = message + '\n' + messages_for_errors
        self.errors = synamic_errors


class SynamicTemplateError(SynamicError):
    def __init__(self, jinja_ex):
        assert isinstance(jinja_ex, jinja2.exceptions.TemplateError),\
            f'Exception instance passed to {self.__class__.__name__} must be of jinja2.TemplateError'
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
            error_map['Source'] = get_source_snippet_from_file(jinja_ex.filename, jinja_ex.lineno, limit=10)
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


class SynamicGetCError(SynamicError):
    """Desired result was not found with SynamicGetCError"""


class SynamicPreProcessorNotFound(SynamicError):
    """Raised when pre processor not found"""


class SynamicMarkerNotFound(SynamicError):
    """Marker not found"""


class SynamicMarkNotFound(SynamicError):
    """Mark Not found"""


class SynamicMarkerIsNotPublic(SynamicError):
    """When marker is not public"""


class SynamicInvalidNumberFormat(SynamicError):
    """When number format is invalid"""


class SynamicInvalidDateTimeFormat(SynamicError):
    """When date, time or datetime is invalid"""


class SynamicModelParsingError(SynamicError):
    """When model cannot be parsed properly"""


class SynamicSettingsError(SynamicError):
    """Error related to settings and settings values"""


class SynamicInvalidCPathComponentError(SynamicError):
    """When a component passed to the cpath processing code is invalid."""


class SynamicPathDoesNotExistError(SynamicError):
    """When the path is non existent"""


class SynamicSydParseError(SynamicError):
    """Syd parse error in curlybrace parser."""


class SynamicFSError(SynamicError):
    """Synamic file system error"""


class SynamicDataError(SynamicError):
    """Exception for data in data service"""


class SynamicSiteNotFound(SynamicError):
    """Site not found"""


class SynamicUserNotFound(SynamicError):
    """User not found"""


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
