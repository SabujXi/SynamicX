"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


class SynamicException(Exception):
    def __init__(self, message, file_name=None, line_no=None):
        self.message = message
        self.file_name = file_name
        self.line_no = line_no

    def produce_message(self):
        return self.message

    def __str__(self):
        return self.produce_message()

    def __repr__(self):
        return repr(self.__str__())


class LogicalError(SynamicException):
    pass

class InvalidQueryString(SynamicException):
    pass

class GetUrlFailed(SynamicException):
    pass

class ParsingError(SynamicException):
    pass

class InvalidFrontMatter(SynamicException):
    pass


class InvalidFileNameFormat(SynamicException):
    pass


class DuplicateContentId(SynamicException):
    pass


class InvalidModuleType(SynamicException):
    pass


class DuplicateModule(SynamicException):
    pass


class CircularDependency(SynamicException):
    pass
