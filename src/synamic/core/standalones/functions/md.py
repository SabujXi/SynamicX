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


class _Patterns:
    schemed_url_pat = re.compile(r'^[a-zA-Z0-9_]+://')
    md_include = re.compile(
        r"!include\(\s*(?P<path>[^)]+)\s*\)"
    )
    md_include_template = re.compile(
        r"""(\s+|\A)!include_template\(\s*(?P<path>[^)]+)\s*\)"""
    )
    md_attr = re.compile(
        r"""(\s+|\A)!attr\(\s*(?P<dotted_path>[a-zA-Z_][a-zA-Z0-9_.]*)\s*\)"""
    )
    html_getc_url = re.compile(
        r"""
        (?P<link_attr>src|href)\s*=\s*(['"])(?P<getc_url>[^'"]+)\2
        """,
        re.X | re.I
    )


class SynamicInlineLexer(mistune.InlineLexer):
    def enable_include(self):
        self.rules.include = _Patterns.md_include
        # self.default_rules.append('include')
        self.default_rules.insert(0, 'include')

    def enable_include_template(self):
        self.rules.include_template = _Patterns.md_include_template
        self.default_rules.insert(1, 'include_template')

    def enable_attr(self):
        self.rules.attr = _Patterns.md_attr
        self.default_rules.insert(2, 'attr')

    def enable_all_inline(self):
        self.enable_include()
        self.enable_include_template()
        self.enable_attr()

    def output_include(self, m):
        path = m.group('path')
        return self.renderer.include(path.strip(), m.group())

    def output_include_template(self, m):
        path = m.group('path')
        return self.renderer.include_template(path.strip(), m.group())

    def output_attr(self, m):
        path = m.group('dotted_path')
        return self.renderer.attr(path.strip(), m.group())


class SynamicBaseRenderer(mistune.Renderer):
    def __init__(self, site, value_pack=None, md_cpath=None, cfields=None, **kwargs):
        super().__init__(**kwargs)
        self._site = site
        self._value_pack = value_pack if value_pack is not None else {}

        self._md_cpath = md_cpath
        self._cfields = cfields
        self._variables = {
            'site': self._site,
            'cfields': self._cfields
        }

    def image(self, src, title, alt_text):
        if not title:
            title = ''
        if not alt_text:
            alt_text = title
        url = self._site.object_manager.getc(src, relative_cpath=self._md_cpath)
        return f"<img src='{url}' title='{title}' alt='{alt_text}' class='img-responsive center-block'>"

    def header(self, text, level, raw=None):
        html_id = self.__text_2_html5_id(text)
        toc = self._value_pack.get('toc', None)
        if toc is not None:
            toc.add(level, text, html_id)
        return f"<h{level} id='{html_id}'>{text}</h{level}>"

    def __text_2_html5_id(self, text):
        rpl_spc = re.sub(r'\s', '_', text)
        final = re.sub(r'["\']', '-', rpl_spc)
        return final

    def include(self, path, original_text):
        # TODO: synamic exception throwing on failure with details.
        parent_cdir = self._md_cpath.parent_cpath
        include_cfile = parent_cdir.join_as_cfile(path)
        if not include_cfile.exists():
            include_cfile = self._site.cpaths.contents_cdir.join_as_cfile(path)
        if not include_cfile.exists():
            return original_text

        if include_cfile.extension.lower() in self._site.synamic.system_settings['configs.marked_extensions']:
            assert include_cfile.basename.startswith(
                self._site.synamic.system_settings['configs.ignore_files_sw'].as_tuple
            ), f"Cannot include marked file that is not ignored in usual content search. " \
               f"i.e. file name must start with any of " \
               f"{self._site.synamic.system_settings['configs.ignore_files_sw'].as_tuple}"
            with include_cfile.open('r', encoding='utf-8') as fr:
                md_text = fr.read()
            return render_content_markdown(self._site, md_text, value_pack=self._value_pack, md_cpath=include_cfile, cfields=self._cfields)
        elif include_cfile.extension.lower() in self._site.synamic.system_settings['configs.html_extensions']:
            with include_cfile.open('r', encoding='utf-8') as fr:
                html_text = fr.read()
            return self._html_getc_processor(html_text, self._site, include_cfile)
        else:
            return original_text

    @staticmethod
    def _html_getc_processor(html_text, site, html_cpath):
        # TODO: synamic exception throwing with details
        def _html_getc_replacer(m):
            link_attr = m.group('link_attr')
            getc_url = m.group('getc_url')
            url = site.object_manager.getc(getc_url, relative_cpath=html_cpath)
            return f'{link_attr}="{url}"'
        return _Patterns.html_getc_url.sub(_html_getc_replacer, html_text)

    def include_template(self, path, original_text):
        # TODO: synamic exception throwing with details
        template_name = path
        rendered_text = self._site.get_service('templates').render(template_name, context=self._variables)
        return rendered_text

    def attr(self, dotted_path, original_text):
        # TODO: synamic exception throwing with details
        keys = dotted_path.split('.')
        root_key = keys[0]
        child_keys = keys[1:]
        root_obj = self._variables.get(root_key, None)
        if root_obj is None:
            return original_text

        obj = root_obj
        for key in child_keys:
            obj = getattr(root_obj, key, None)
            if obj is None:
                return original_text
        return str(obj)


class SynamicContentRenderer(SynamicBaseRenderer):
    def link(self, link, title, content):
        url = self._site.object_manager.getc(link, relative_cpath=self._md_cpath)
        # TODO: process link if a file is referenced directly.
        # TODO: Assert if it returns a str.
        return f"<a href='{url}' title='{title}'>{content}</a>"


class SynamicChaptersRenderer(SynamicContentRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def link(self, link, title, content):
        if _Patterns.schemed_url_pat.match(link):
            url_str = super().link(link, title, content)
        else:
            curl = self._site.object_manager.get_curl_by_filename(
                link,
                relative_cpath=self._md_cpath
            )
            url_str = curl.url
            # process the link
            curl_bucket = self._value_pack.get('curl_bucket', None)
            if curl_bucket is not None:
                curl_bucket.append(curl)
        return f"<a href='{url_str}' title='{title}'>{content}</a>"


def render_content_markdown(site, text, value_pack=None, md_cpath=None, cfields=None):
    renderer = SynamicContentRenderer(site, value_pack=value_pack, md_cpath=md_cpath, cfields=cfields)

    synamic_inline = SynamicInlineLexer(renderer)
    synamic_inline.enable_all_inline()

    md = mistune.Markdown(renderer=renderer, inline=synamic_inline)
    return md.render(text)


def render_chapters_markdown(site, text, value_pack=None, md_cpath=None, cfields=None):
    renderer = SynamicChaptersRenderer(site, value_pack=value_pack, md_cpath=md_cpath, cfields=cfields)

    synamic_inline = SynamicInlineLexer(renderer)
    synamic_inline.enable_all_inline()

    md = mistune.Markdown(renderer=renderer, inline=synamic_inline)
    return md.render(text)
