import io
from synamic.core.contracts import ContentContract, DocumentType


class MarkedContentImplementation(ContentContract):
    def __init__(self, site, file_cpath, url_object, body, content_fields, toc, content_id, document_type, mime_type='text/plain'):
        assert site.get_service('contents').is_type_content_id(content_id)
        self.__site = site
        self.__file_cpath = file_cpath
        self.__url_object = url_object
        self.__body = body
        self.__content_fields = content_fields
        self.__model = content_fields.get_model()
        self.__content_id = content_id
        self.__document_type = document_type
        self.__mime_type = mime_type
        self.__toc = toc

        # Objects like: Url, Pagination, etc.
        self.__objects = {}

        # validation
        assert self.__toc is not None
        assert DocumentType.is_text(self.__document_type)

    @property
    def id(self):
        return self.__content_id

    @property
    def document_type(self):
        return self.__document_type

    @property
    def path_object(self):
        return self.__file_cpath

    @property
    def url_object(self):
        return self.__url_object

    def get_stream(self):
        template_name = self.__content_fields.get('template', 'default.html')
        templates = self.__site.get_service('templates')
        res = templates.render(template_name, content=self)
        f = io.BytesIO(res.encode('utf-8'))
        return f

    @property
    def mime_type(self):
        return self.__mime_type

    @property
    def body(self):
        return self.__body

    @property
    def fields(self):
        return self.__content_fields

    @property
    def raw_fields(self):
        raise NotImplemented

    @property
    def toc(self):
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
        # return self.body  # TODO: fix this long repr... file path and summary?
        return "<%s>\n%s\n\n%s" % (self.path_object.relative_path, self['title'], self.body[:100] + '...')

    def __repr__(self):
        return str(self)
