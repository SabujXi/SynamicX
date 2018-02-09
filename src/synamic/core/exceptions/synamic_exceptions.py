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
    def __init__(self, message, file_name=None):
        self.message = message
        self.file_name = file_name


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
