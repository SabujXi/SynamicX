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


class GetCExtension(Extension):
    tags = {'geturl', 'getc'}

    def __init__(self, environment):
        super().__init__(environment)
        environment.extend(
            site_object=None
        )

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        token = parser.stream.expect(lexer.TOKEN_STRING)
        url_name_or_id = nodes.Const(token.value)
        call = self.call_method('_get_url', [url_name_or_id], lineno=lineno)
        return nodes.Output([call], lineno=lineno)

    def _get_url(self, parameter):
        url = self.environment.site_object.object_manager.getc(parameter)
        return url


class ResizeImageExtension(Extension):
    tags = {'resize'}

    def __init__(self, environment):
        super().__init__(environment)
        environment.extend(
            site_object=None
        )

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        args = [parser.parse_expression()]
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        path, width, height = args
        call = self.call_method('_resize', [path, width, height], lineno=lineno)
        return nodes.Output([call], lineno=lineno)

    def _resize(self, path, width, height):
        cnt = self.environment.site_object.object_manager.resize_image(path, width, height)
        return cnt.curl.path_as_str
