"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
from synamic.core.standalones.functions.decorators import not_loaded, loaded
from synamic.core.contracts import CDocType
from synamic.core.synamic.router import RouterService


class SitemapService:
    def __init__(self, site):
        self.__site = site
        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        self.__is_loaded = True

    @loaded
    def make_sitemap(self, all_cfields, url_str='sitemap.xml', mimetype='text/xml', cdoctype=CDocType.GENERATED_TEXT_DOCUMENT):
        content_service = self.__site.get_service('contents')
        url_texts = []
        for cfields in all_cfields:
            url_texts.append(self.__url_template(cfields))
        doc_text = self.__doc_template('\n'.join(url_texts))

        curl = RouterService.make_url(self.__site, url_str, for_cdoctype=cdoctype)
        synthetic_cfields = content_service.make_synthetic_cfields(curl, cdoctype, mimetype)
        gen_content = content_service.build_generated_content(synthetic_cfields, doc_text)
        return gen_content

    def __doc_template(self, urls_text):
        return \
f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_text}
</urlset>  
"""

    def __url_template(self, cfields):
        return \
f"""
    <url>
        <loc>{ cfields.curl.url }</loc>
        <lastmod>{ cfields.updated_on.strftime('%Y-%m-%d') }</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
    
"""
