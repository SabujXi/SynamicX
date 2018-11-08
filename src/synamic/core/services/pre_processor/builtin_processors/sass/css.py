"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import sass
import io
from synamic.core.contracts.content import DocumentType
from synamic.core.services.content.generated_content import GeneratedContent


class SCSS_CSSContent(GeneratedContent):

    def __init__(self, site, curl, file_content,
                 document_type=DocumentType.GENERATED_TEXT_DOCUMENT, mime_type='text/css', source_cpath=None):
        super().__init__(site, curl, file_content, document_type=document_type, mime_type=mime_type, source_cpath=source_cpath)
        self.__scss_path = source_cpath

    def get_stream(self):
        scss_fn = self.__scss_path.abs_path
        css_str = sass.compile(filename=scss_fn)
        css_io = io.BytesIO(css_str.encode('utf-8'))
        del css_str
        return css_io

    def __str__(self):
        return 'Generated content for %s' % self.__scss_path.abs_path

    def __repr__(self):
        return repr(self.__str__())
