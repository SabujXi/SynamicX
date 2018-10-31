import io
import mimetypes
from synamic.core.contracts.document import MarkedDocumentContract


class MarkedContentImplementation(MarkedDocumentContract):
    def __init__(self, site, body, content_fields, toc, content_id, content_type=None):
        self.__site = site
        self.__body = body
        self.__content_fields = content_fields
        self.__model = content_fields.get_model()
        self.__content_id = content_id
        self.__content_type = content_type
        self.__toc = toc

        # Objects like: Url, Pagination, etc.
        self.__objects = {}

    def get_stream(self):
        template_name = self.__content_fields.get('template', 'default.html')
        templates = self.__site.get_service('templates')
        res = templates.render(template_name, content=self)
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
        return self.__content_fields

    @property
    def pagination(self):
        return self.__pagination

    @property
    def toc(self):
        assert self.__toc is not None
        return self.__toc

    def __get(self, key):
        value = self.__objects.get(key, None)
        if value is None:
            value = self.__content_fields.get(key, None)
        return value

    def __getitem__(self, key):
        return self.__get(key)

    def __getattr__(self, key):
        return self.__get(key)

    def __str__(self):
        return self.path_object.relative_path

    def __repr__(self):
        return str(self)
