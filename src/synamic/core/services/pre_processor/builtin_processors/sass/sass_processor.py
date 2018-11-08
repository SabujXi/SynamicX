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
from .css import SCSS_CSSContent
from synamic.core.contracts import DocumentType


class SASSProcessor:
    def __init__(self, site, processor_cpath):
        self.__site = site
        self.__processor_cpath = processor_cpath
        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        self.__is_loaded = True

    def get_generated_contents(self):
        content_objects = []
        content_service = self.__site.get_service('contents')
        sass_file_cpaths = self.__processor_cpath.list_files()
        for file_cpath in sass_file_cpaths:
            scss_basename = file_cpath.basename
            if file_cpath.extension.lower() in {'scss'}:
                if not scss_basename.lower().startswith('_'):
                    # partial file in not not condition, ignore it.
                    curl = self.get_css_curl(file_cpath)
                    synthetic_fields = content_service.make_synthetic_cfields(
                        curl,
                        document_type=DocumentType.GENERATED_BINARY_DOCUMENT,
                        fields_map=None)
                    file_content = None
                    document_type = DocumentType.GENERATED_TEXT_DOCUMENT
                    mime_type = 'text/css'

                    content_obj = SCSS_CSSContent(self.__site, synthetic_fields, curl, file_content,
                                                  document_type=document_type,
                                                  mime_type=mime_type,
                                                  source_cpath=file_cpath)
                    content_objects.append(content_obj)
            else:
                curl = self.get_static_file_curl(file_cpath)
                synthetic_fields = content_service.make_synthetic_cfields(self, curl, document_type=DocumentType.GENERATED_BINARY_DOCUMENT, fields_map=None)
                file_content = None
                content_obj = content_service.build_generated_content(
                    synthetic_fields,
                    curl, file_content,
                    document_type=DocumentType.GENERATED_TEXT_DOCUMENT, mime_type='octet/stream',
                    source_cpath=file_cpath
                )
                content_objects.append(content_obj)
        return content_objects

    def make_cpath(self, *path_comps, is_file=True):
        return self.__processor_cpath.join(*path_comps, is_file=is_file)

    def get_css_curl(self, scss_file_path):
        url_path_comps = self.__processor_cpath.parent_cpath.get_comps_after(scss_file_path)
        assert len(url_path_comps) > 0
        scss_basename = url_path_comps[-1]
        parent_comps = url_path_comps[1:]
        css_file_base_name = scss_basename[:len(scss_basename) - len('.scss')] + '.css'

        css_url_path_comps = (*parent_comps[1:], css_file_base_name)
        curl = self.__site.synamic.router.make_url(
            self.__site, css_url_path_comps, for_document_type=DocumentType.GENERATED_BINARY_DOCUMENT
        )
        return curl

    def get_static_file_curl(self, file_cpath):
        url_path_comps = self.__processor_cpath.parent_cpath.get_comps_after(file_cpath)
        assert len(url_path_comps) > 0
        curl = self.__site.synamic.router.make_url(
            self.__site, url_path_comps, for_document_type=DocumentType.GENERATED_BINARY_DOCUMENT
        )
        return curl
