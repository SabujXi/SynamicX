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
from synamic.core.contracts.content import CDocType
from synamic.core.services.content.generated_content import GeneratedContent


class SCSS_CSSContent(GeneratedContent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.source_cpath is not None
        self.__css_str = None

    def get_stream(self):
        assert self.source_cpath is not None
        if self.__css_str is None:
            scss_fn = self.source_cpath.abs_path
            css_str = sass.compile(filename=scss_fn)
            self.__css_str = css_str
        else:
            css_str = self.__css_str
        css_io = io.BytesIO(css_str.encode('utf-8'))
        return css_io

    def __getitem__(self, item):
        return self.cfields[item]

    def __getattr__(self, item):
        return getattr(self.cfields, item)

    def __str__(self):
        return 'SCSS CSS Generated content for %s' % self.source_cpath.abs_path

    def __repr__(self):
        return repr(self.__str__())
