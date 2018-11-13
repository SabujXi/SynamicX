import io
from synamic.core.contracts import ContentContract, CDocType
from synamic.core.services.content.toc import Toc


class MarkedContent(ContentContract):
    def __init__(self, site, body_text, cfields):
        self.__site = site
        self.__body_text = body_text
        self.__cfields = cfields
        self.__cmodel = cfields.cmodel

        # validation
        assert CDocType.is_text(self.__cfields.cdoctype)

        self.__toc = None
        self.__body = None

    @property
    def site(self):
        return self.__site

    def get_stream(self):
        template_name = self.__cfields.get('template', 'default.html')
        templates = self.__site.get_service('templates')
        res = templates.render(template_name, context={
            'site': self.__site,
            'content': self
        })
        f = io.BytesIO(res.encode('utf-8'))
        return f

    def __render_body(self):
        body = self.__body
        if body is None:
            toc = Toc()
            # try with model converter
            body_field_key = self.__cmodel.body_field
            if body_field_key is None:
                body_field_key = '__body__'

            model_field = self.__cmodel.get(body_field_key)
            if model_field is not None:
                body = model_field.converter(self.__body_text, value_pack={
                    'toc': toc,
                    'from_cpath': self.cpath
                })

            # try with markdown renderer
            else:
                markdown_renderer = self.__site.get_service('types').get_converter('markdown')

                body = markdown_renderer(self.__body_text, value_pack={
                    'toc': toc,
                    'from_cpath': self.cpath
                })
            self.__toc = toc
            self.__body = body

    @property
    def body(self):
        self.__render_body()
        return self.__body

    @property
    def body_as_string(self):
        return self.body

    @property
    def body_as_bytes(self):
        return self.body.encode('utf-8')

    @property
    def cfields(self):
        return self.__cfields

    @property
    def toc(self):
        self.__render_body()
        return self.__toc

    def __getitem__(self, key):
        return self.__cfields[key]

    def __getattr__(self, key):
        return getattr(self.__cfields, key)

    def __str__(self):
        return "<%s>\n%s\n" % (self.cfields.cpath.relative_path, self['title'])

    def __repr__(self):
        return str(self)
