import io
import mimetypes

from synamic.core.contracts.document import MarkedDocumentContract
from synamic.core.filesystem.content_path.content_path2 import ContentPath2
from synamic.core.services.content.toc import Toc
from synamic.core.standalones.functions.md import render_markdown


class MarkedContentImplementation(MarkedDocumentContract):

    def __init__(self, synamic, path_object, url_object, body, fields, field_converters=None, content_type=None):
        self.__synamic = synamic
        self.__path = path_object
        self.__url_object = url_object
        self.__body = body
        self.__fields = fields
        self.__field_converters = field_converters
        self.__content_type = content_type
        self.__pagination = None
        self.__toc = Toc()

        render_markdown(synamic, self.__body.as_str, value_pack={
            'toc': self.__toc
        })

    @property
    def synamic(self):
        return self.__synamic

    @property
    def path_object(self) -> ContentPath2:
        return self.__path

    @property
    def url_object(self):
        return self.__url_object

    @property
    def id(self):
        return self.fields.get('id', None)

    @property
    def url_path(self):
        return self.url_object.path

    def get_stream(self):
        template_name = self.fields.get('template', 'default.html')
        res = self.__synamic.templates.render(template_name, content=self)
        f = io.BytesIO(res.encode('utf-8'))
        return f

    @property
    def content_type(self):
        return self.__content_type

    @property
    def mime_type(self):
        mime_type = 'octet/stream'
        path = self.url_object.real_path
        type, enc = mimetypes.guess_type(path)
        if type:
            mime_type = type
        return mime_type

    @property
    def body(self):
        return self.__body

    @property
    def fields(self):
        return self.__fields

    @property
    def field_converters(self):
        return self.__field_converters

    @property
    def pagination(self):
        return self.__pagination

    @property
    def toc(self):
        assert self.__toc is not None
        return self.__toc

    def _set_pagination(self, pg):
        if self.__pagination is None:
            self.__pagination = pg
        else:
            raise Exception("Cannot set pagination once it is set")

    def __get(self, key):
        value = self.__fields.get(key, None)
        return value

    def __getitem__(self, key):
        return self.__get(key)

    def __getattr__(self, key):
        return self.__get(key)

    def __str__(self):
        return self.path_object.relative_path

    def __repr__(self):
        return str(self)