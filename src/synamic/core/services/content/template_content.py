import io
from synamic.core.contracts.content import ContentContract


class TemplateContent(ContentContract):
    def __init__(self, site, url_object, template_name, value_pack, mime_type="text/html"):
        self.__site = site
        self.__value_pack = value_pack
        self.__template_name = template_name
        self.__mime_type = mime_type
        self.__url_object = url_object

    @property
    def site(self):
        return self.__site

    @property
    def path_object(self):
        return None

    @property
    def url_object(self):
        return self.__url_object

    @property
    def mime_type(self):
        return self.__mime_type

    def get_stream(self):
        res = self.__site.templates.render(self.__template_name, context=self.__value_pack)
        f = io.BytesIO(res.encode('utf-8'))
        return f

    @property
    def id(self):
        return None

    @property
    def document_type(self):
        return ContentContract.__document_types.AUXILIARY
