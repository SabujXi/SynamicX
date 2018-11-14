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
schemed_url_pat = re.compile(r'^[a-zA-Z0-9_]+://')


class SynamicBaseRenderer(mistune.Renderer):
    def __init__(self, site, value_pack=None, **kwargs):
        super().__init__(**kwargs)
        self.__site__ = site
        self.__value_pack__ = value_pack if value_pack is not None else {}

    def image(self, src, title, alt_text):
        if not title:
            title = ''
        if not alt_text:
            alt_text = title
        url = self.__site__.object_manager.getc(src, relative_cpath=self.__value_pack__.get('from_cpath', None))
        return f"<img src='{url}' title='{title}' alt='{alt_text}' class='img-responsive center-block'>"

    def header(self, text, level, raw=None):
        html_id = self.__text_2_html5_id(text)
        toc = self.__value_pack__.get('toc', None)
        if toc is not None:
            toc.add(level, text, html_id)
        return f"<h{level} id='{html_id}'>{text}</h{level}>"

    def __text_2_html5_id(self, text):
        rpl_spc = re.sub(r'\s', '_', text)
        final = re.sub(r'["\']', '-', rpl_spc)
        return final


class SynamicContentRenderer(SynamicBaseRenderer):
    def link(self, link, title, content):
        url = self.__site__.object_manager.getc(link, relative_cpath=self.__value_pack__.get('from_cpath', None))
        # TODO: process link if a file is referenced directly.
        # TODO: Assert if it returns a str.
        return f"<a href='{url}' title='{title}'>{content}</a>"


class SynamicChaptersRenderer(SynamicContentRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def link(self, link, title, content):
        if schemed_url_pat.match(link):
            url_str = super().link(link, title, content)
        else:
            curl = self.__site__.object_manager.get_curl_by_filename(
                link,
                relative_cpath=self.__value_pack__.get('from_cpath', None)
            )
            url_str = curl.url
            # process the link
            curl_bucket = self.__value_pack__.get('curl_bucket', None)
            if curl_bucket is not None:
                curl_bucket.append(curl)
        return f"<a href='{url_str}' title='{title}'>{content}</a>"


def render_content_markdown(site, text, value_pack=None):
    renderer = SynamicContentRenderer(site, value_pack)
    md = mistune.Markdown(renderer=renderer)
    return md.render(text)


def render_chapters_markdown(site, text, value_pack=None):
    renderer = SynamicChaptersRenderer(site, value_pack)
    md = mistune.Markdown(renderer=renderer)
    return md.render(text)
