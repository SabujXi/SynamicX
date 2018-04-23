"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

from jinja2 import nodes, lexer
from jinja2.ext import Extension


class GetUrlExtension(Extension):
    tags = {'geturl'}

    def __init__(self, environment):
        super().__init__(environment)
        environment.extend(
            synamic_config=None
        )

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        token = parser.stream.expect(lexer.TOKEN_STRING)
        url_name_or_id = nodes.Const(token.value)
        call = self.call_method('_get_url', [url_name_or_id], lineno=lineno)
        return nodes.Output([call], lineno=lineno)

    def _get_url(self, parameter):
        url = self.environment.synamic_config.get_url(parameter)
        return url
