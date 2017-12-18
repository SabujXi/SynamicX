from synamic.core.functions.normalizers import normalize_key
from synamic.content_modules.text import TextContent, TextModule


class HomeContent(TextContent):
    pass


class HomeModule(TextModule):

    @property
    def name(self):
        return 'home'

    @property
    def content_class(self):
        return HomeContent

    @property
    def dependencies(self):
        return {"synamic-template", "text"}

    @property
    def root_url_path(self):
        return ""
