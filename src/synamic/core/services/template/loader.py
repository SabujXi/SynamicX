from jinja2 import BaseLoader, TemplateNotFound


class SynamicJinjaFileSystemLoader(BaseLoader):
    def __init__(self):
        pass

    def get_source(self, environment, template):
        pass
