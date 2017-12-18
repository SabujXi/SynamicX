from .reference_implementations import MarkedContentImplementation, MarkedContentModuleImplementation


class TextContent(MarkedContentImplementation):
    @property
    def in_series(self):
        if not self.content_id:
            return None
        else:
            return self.config.series.get_all_series_by_mod_name_n_cid(self.module_object.name, self.content_id)


class TextModule(MarkedContentModuleImplementation):

    @property
    def name(self):
        return 'text'

    @property
    def content_class(self):
        return TextContent

    @property
    def dependencies(self):
        return {"synamic-template"}

