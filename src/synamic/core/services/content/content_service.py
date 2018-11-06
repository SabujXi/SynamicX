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
from collections import OrderedDict
from synamic.core.contracts.content import DocumentType
from synamic.core.standalones.functions.decorators import not_loaded
from synamic.core.services.content.static_content import StaticContent
from synamic.core.services.content.generated_content import GeneratedContent
from synamic.core.services.content.toc import Toc
from synamic.core.services.content.marked_content import MarkedContentImplementation
from .chapters import Chapter


_invalid_url = re.compile(r'^[a-zA-Z0-9]://', re.IGNORECASE)


class ContentService:
    __slots__ = ('__site', '__is_loaded', '__contents_by_id', '__dynamic_contents', '__auxiliary_contents')

    def __init__(self, site):
        self.__site = site
        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        self.__is_loaded = True

    @classmethod
    def is_type_content_fields(cls, other):
        return type(other) is cls.__ContentFields

    def build_content_fields(self, fields_syd, file_cpath):
        # get dir meta syd
        # """It should not live here as it is compile time dependency"""
        # each field from meta syd will be converted with individual content model and site type system.
        dir_meta_file_name = self.__site.default_data.get_syd('configs')['dir_meta_file_name']
        _syd = self.__site.object_manager.empty_syd()
        parent_cpaths = file_cpath.parent_cpaths
        for dir_cpath in parent_cpaths:
            dir_meta_cfile = dir_cpath.join(dir_meta_file_name, is_file=True)
            if dir_meta_cfile.exists():
                dir_meta_syd = self.__site.object_manager.get_syd(dir_meta_cfile)
                _syd = _syd.new(dir_meta_syd)
        else:  # for else when loop ended normally without using break.
            fields_syd = _syd.new(fields_syd)

        # TODO: what is the document type???
        document_type = DocumentType.HTML_DOCUMENT
        model_name = 'content'  # model name for contents is 'content' - a builtin model exists with this name.
                                # User can only override no existing field creating another model with the same name
                                # under site's meta model directory.
        model = self.__site.object_manager.get_model(model_name)
        url_object = self.__site.object_manager.make_url_for_marked_content(
            file_cpath, path=fields_syd.get('path', None), slug=fields_syd.get('slug', None), for_document_type=document_type
        )

        content_fields = self.make_content_fields(file_cpath, url_object, model, document_type, fields_syd)
        return content_fields

    def build_md_content(self, file_path):
        markdown_renderer = self.__site.get_service('types').get_converter('markdown')
        document_type = DocumentType.HTML_DOCUMENT
        fields_syd, body_text = self.__site.object_manager.get_content_parts(file_path)
        content_fields = self.build_content_fields(fields_syd, file_path)
        toc = Toc()
        body = markdown_renderer(body_text, value_pack={
            'toc': toc
        }).rendered_markdown

        # mime type guess
        mime_type = 'text/html'
        url_object = content_fields.get_url_object()
        content = MarkedContentImplementation(self.__site,
                                              file_path,
                                              url_object,
                                              body,
                                              content_fields,
                                              toc,
                                              document_type,
                                              mime_type=mime_type)
        return content

    def build_paginated_md_content(self):
        # TODO: code it
        pass

    def build_static_content(self, path):
        path_tree = self.__site.get_service('path_tree')
        path_obj = path_tree.create_file_cpath(path)
        file_content = None
        mime_type = 'octet/stream'  # TODO: guess the content type here.
        document_type = DocumentType.BINARY_DOCUMENT

        url_object = self.__site.object_manager.static_content_cpath_to_url(path_obj, document_type)

        return StaticContent(
            self.__site,
            path_obj,
            url_object,
            file_content=file_content,
            document_type=document_type,
            mime_type=mime_type)

    def build_generated_content(
            self, url_object, file_content,
            document_type=DocumentType.GENERATED_TEXT_DOCUMENT, mime_type='octet/stream', source_cpath=None, **kwargs):
        return GeneratedContent(self.__site, url_object, file_content, document_type=document_type, mime_type=mime_type, source_cpath=source_cpath, **kwargs)

    def make_content_fields(self, content_file_path, url_object, model, document_type, raw_fileds, *a, **kwa):
        """Just makes an instance"""
        return self.__ContentFields(self.__site, content_file_path, url_object, model, document_type, raw_fileds, *a, **kwa)

    def build_chapters(self, chapters_fields):
        chapters = []
        for cfs in chapters_fields:
            chapters.append(Chapter(self.__site, cfs))
        return tuple(chapters)

    class __ContentFields:
        def __init__(self, site, content_file_path, url_object, model, document_type, raw_fileds, *a, **kwa):
            self.__site = site
            self.__content_file_path = content_file_path
            self.__url_object = url_object
            self.__model = model
            self.__document_type = document_type
            self.__raw_fields = raw_fileds
            self.__converted_values = OrderedDict()
            super().__init__(*a, *kwa)

        # def clone(self):
        #     return self.__class__(self.__site, self.__content_file_path)

        def get(self, key, default=None):
            raw_value = self.__raw_fields.get(key, None)
            if raw_value is None:
                return default

            value = self.__converted_values.get(key, None)
            if value is None:
                # convert with type system.
                if key in self.__model:
                    model_field = self.__model[key]
                    value = model_field.converter(raw_value)
                else:
                    value = raw_value
                self.__converted_values[key] = value
            return value

        def __getitem__(self, key):
            return self.get(key, None)

        def __getattr__(self, key):
            return self.get(key, None)

        def __eq__(self, other):
            if not isinstance(other, self.__class__):
                return False
            return self.__url_object == other.get_url_object()

        def __hash__(self):
            return hash(self.__url_object)

        @property
        def raw(self):
            return self.__raw_fields

        def get_keys(self):
            return self.__raw_fields.keys()

        def get_path_object(self):
            """Content file path"""
            return self.__content_file_path

        def get_model(self):
            return self.__model

        def get_document_type(self):
            return self.__document_type

        def get_url_object(self):
            return self.__url_object
