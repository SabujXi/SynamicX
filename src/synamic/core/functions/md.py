"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import mistune


class SynamicRenderer(mistune.Renderer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.__config = config

    def image(self, src, title, alt_text):
        lsrc = src.lower()
        if lsrc.startswith('geturl://'):
            _url = src[len('geturl://'):]
            url = self.__config.get_url(_url)
        else:
            url = src
        return "<img src='%s' title='%s' alt='%s' class='img-responsive center-block'>" % (url, title, alt_text)

    def link(self, link, title, content):
        ll = link.lower()
        if ll.startswith('geturl://'):
            _url = link[len('geturl://'):]
            url = self.__config.get_url(_url)
        else:
            url = link
        return "<a href='%s' title='%s'>%s</a>" % (url, title, content)


def render_markdown(config, text):
    renderer = SynamicRenderer(config)
    md = mistune.Markdown(renderer=renderer)
    return md.render(text)

