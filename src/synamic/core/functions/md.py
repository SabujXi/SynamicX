import mistune


class SynamicRenderer(mistune.Renderer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.__config = config

    def image(self, src, title, alt_text):
        lsrc = src.lower()
        if lsrc.startswith('geturl:'):
            url = self.__config.get_url(src)
        else:
            url = src
        return "<img src='%s' title='%s' alt='%s'>" % (url, title, alt_text)

    def link(self, link, title, content):
        ll = link.lower()
        if ll.startswith('geturl://'):
            url = ll[len('geturl://'):]
            url = self.__config.get_url(url)
        else:
            url = link
        return "<a href='%s' title='%s'>%s</a>" % (url, title, content)


def render_markdown(config, text):
    renderer = SynamicRenderer(config)
    md = mistune.Markdown(renderer=renderer)
    return md.render(text)

