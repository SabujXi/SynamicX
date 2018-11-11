from synamic.core.contracts import HostContract
from jinja2 import BaseLoader, TemplateNotFound


class SynamicJinjaFileSystemLoader(BaseLoader):
    def __init__(self, synamic, host: HostContract):
        self.__synamic = synamic
        self.__host = host

    def get_source(self, environment, template):
        pass
