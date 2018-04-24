import io
from synamic.core.contracts.content import ContentContract


class TemplateContent(ContentContract):
    def __init__(self, synamic, url_object, template_name, value_pack, mime_type="text/html"):
        self.__synamic = synamic
        self.__value_pack = value_pack
        self.__template_name = template_name
        self.__mime_type = mime_type
        self.__url_object = url_object

    @property
    def synamic(self):
        return self.__synamic

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
        res = self.__synamic.templates.render(self.__template_name, context=self.__value_pack)
        f = io.BytesIO(res.encode('utf-8'))
        return f

    @property
    def id(self):
        return None

    @property
    def content_type(self):
        return ContentContract.types.AUXILIARY
