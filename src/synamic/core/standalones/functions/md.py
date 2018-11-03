"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import re
import mistune


class SynamicRenderer(mistune.Renderer):
    def __init__(self, site, value_pack=None, **kwargs):
        super().__init__(**kwargs)
        self.__site = site
        self.__value_pack = value_pack if value_pack is not None else {}

    def image(self, src, title, alt_text):
        lsrc = src.lower()
        if lsrc.startswith('geturl://'):
            _url = src[len('geturl://'):]
            url = self.__site.object_manager.get_url(_url)
        else:
            url = src
        return "<img src='%s' title='%s' alt='%s' class='img-responsive center-block'>" % (url, title, alt_text)

    def link(self, link, title, content):
        ll = link.lower()
        if ll.startswith('geturl://'):
            _url = link[len('geturl://'):]
            url = self.__site.object_manager.get_url(_url)
        else:
            url = link
        return "<a href='%s' title='%s'>%s</a>" % (url, title, content)

    def header(self, text, level, raw=None):
        html_id = self.__text_2_html5_id(text)
        toc = self.__value_pack.get('toc', None)
        if toc is not None:
            toc.add(level, text, html_id)
        # print(text)
        return "<h%s id='%s'>%s</h%s>" % (level, html_id, text, level)

    def __text_2_html5_id(self, text):
        rpl_spc = re.sub(r'\s', '_', text)
        final = re.sub(r'"|\'', '-', rpl_spc)
        return final


def render_markdown(site, text, value_pack=None):
    renderer = SynamicRenderer(site, value_pack)
    md = mistune.Markdown(renderer=renderer)
    return md.render(text)
