import io
from synamic.core.contracts import ContentContract, DocumentType
from synamic.core.services.content.toc import Toc


class MarkedContent(ContentContract):
    def __init__(self, site, file_cpath, curl, body_text, content_fields, document_type, mime_type='text/plain'):
        self.__site = site
        self.__file_cpath = file_cpath
        self.__curl = curl
        self.__body_text = body_text
        self.__content_fields = content_fields
        self.__model = content_fields.cmodel
        self.__document_type = document_type
        self.__mime_type = mime_type

        # validation
        assert DocumentType.is_text(self.__document_type)

        self.__toc = None
        self.__body = None

    @property
    def site(self):
        return self.__site

    @property
    def document_type(self):
        return self.__document_type

    @property
    def cpath(self):
        return self.__file_cpath

    @property
    def curl(self):
        return self.__curl

    def get_stream(self):
        template_name = self.__content_fields.get('template', 'default.html')
        templates = self.__site.get_service('templates')
        res = templates.render(template_name, context={
            'site': self.__site,
            'content': self
        })
        f = io.BytesIO(res.encode('utf-8'))
        return f

    @property
    def mime_type(self):
        return self.__mime_type

    def __render_body(self):
        body = self.__body
        if body is None:
            markdown_renderer = self.__site.get_service('types').get_converter('markdown')
            toc = Toc()
            body = markdown_renderer(self.__body_text, value_pack={
                'toc': toc
            }).rendered_markdown
            self.__toc = toc
            self.__body = body

    @property
    def body(self):
        self.__render_body()
        return self.__body

    @property
    def fields(self):
        return self.__content_fields

    @property
    def toc(self):
        self.__render_body()
        return self.__toc

    def __get(self, key):
        return self.__content_fields.get(key, None)

    def __getitem__(self, key):
        return self.__get(key)

    def __getattr__(self, key):
        return self.__get(key)

    def __str__(self):
        return "<%s>\n%s\n\n%s" % (self.cpath.relative_path, self['title'], self.body[:100] + '...')

    def __repr__(self):
        return str(self)
