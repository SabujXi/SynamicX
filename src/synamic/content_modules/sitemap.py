import io
from synamic.content_modules.reference_implementations import MarkedContentModuleImplementation, MarkedContentImplementation


class SitemapContent(MarkedContentImplementation):
    def get_stream(self):
        template_module, template_name = self.template_module_object, self.template_name
        # TODO: later we will need other contents than text as filtered below
        contents = [c.get_content_wrapper() for c in self.config.filter_content("(text)")]
        res = template_module.render(template_name, contents=contents)
        f = io.BytesIO(res.encode('utf-8'))
        return f

    def trigger_pagination(self):
        print("No pagination for sitemap\n\n")
        return tuple()


class SitemapModule(MarkedContentModuleImplementation):
    @property
    def name(self):
        return 'sitemap'

    @property
    def content_class(self):
        return SitemapContent

    @property
    def dependencies(self):
        return {"synamic-template", "text", 'static'}

    @property
    def root_url_path(self):
        return ""
