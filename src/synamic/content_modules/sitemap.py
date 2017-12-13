import io
from synamic.core.functions.normalizers import normalize_key
from synamic.content_modules.text import TextContent, TextModule


class SitemapContent(TextContent):

    def get_stream(self):
        template_module, template_name = self.template_module_object, self.template_name
        contents = [c.get_content_wrapper() for c in self.config.filter_content("(text)")]
        res = template_module.render(template_name, contents=contents)
        f = io.BytesIO(res.encode('utf-8'))
        return f

    def trigger_pagination(self):
        print("No pagination for sitemap\n\n")


class SitemapModule(TextModule):

    @property
    def name(self):
        return normalize_key('sitemap')

    @property
    def content_class(self):
        return SitemapContent

    @property
    def dependencies(self):
        return {"synamic-template", "text", 'static'}

    @property
    def extensions(self):
        return {'md', 'markdown'}

    @property
    def root_url_path(self):
        return ""
