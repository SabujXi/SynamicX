from .reference_implementations import MarkedContentImplementation, MarkedContentModuleImplementation


class TextContent(MarkedContentImplementation):
    pass


class TextModule(MarkedContentModuleImplementation):

    @property
    def name(self):
        return 'text'

    @property
    def content_class(self):
        return TextContent

    @property
    def dependencies(self):
        return set()

