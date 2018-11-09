"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
import io
from synamic.core.contracts.content import ContentContract, CDocType


class GeneratedContent(ContentContract):
    def __init__(self, site, synthetic_cfields, file_content, source_cpath=None, render_callable=None):

        self.__site = site
        self.__synthetic_cfields = synthetic_cfields
        self.__file_content = file_content
        self.__source_cpath = source_cpath
        self.__render_callable = render_callable  # render callable will accept 2 params: site, this content object

        # validation
        assert CDocType.is_generated(self.__synthetic_cfields.cdoctype)
        assert type(self.__file_content) in (type(None), bytes, bytearray, str)
        assert synthetic_cfields.cpath is None
        assert self.__file_content is not None or source_cpath is not None

    @property
    def site(self):
        return self.__site

    @property
    def cfields(self):
        return self.__synthetic_cfields

    @property
    def __get_content_as_str(self):
        if self.__file_content is not None:
            content = self.__file_content
            if isinstance(content, (bytearray, bytes)):
                content = content.decode('utf-8')
        else:
            with self.__source_cpath.open('r') as f:
                content = f.read()
        return content

    def get_stream(self):
        if callable(self.__render_callable):
            # so this content is renderable.
            text_content = self.__render_callable(self.__site, self)
            stream = io.BytesIO(text_content.encode('utf-8'))
        else:
            if self.__file_content is not None:
                if isinstance(self.__file_content, (bytes, bytearray)):
                    stream = io.BytesIO(self.__file_content)
                else:
                    stream = io.BytesIO(self.__file_content.encode('utf-8'))
            else:
                stream = self.__source_cpath.open('rb')
        return stream

    @property
    def body(self):
        if self.__file_content is not None:
            body = self.__file_content
        else:
            file_mode = 'r'
            if CDocType.is_binary(self.cfields.cdoctype):
                file_mode = 'rb'
            with self.__source_cpath.open(file_mode) as f:
                body = f.read()
        return body

    @property
    def body_as_bytes(self):
        body = self.body
        if not isinstance(body, (bytes, bytearray)):
            body = body.encode('utf-8')
        return body

    @property
    def body_as_string(self):
        body = self.body
        if not isinstance(body, str):
            body = body.decode('utf-8')
        return body

    def __getitem__(self, key):
        return self.__synthetic_cfields[key]

    def __getattr__(self, key):
        return getattr(self.__synthetic_cfields, key)

    def __str__(self):
        return "Generated content: <%s>\n" % str(self.cfields.curl) + '...'

    def __repr__(self):
        return str(self)

    @property
    def source_cpath(self):
        return self.__source_cpath

