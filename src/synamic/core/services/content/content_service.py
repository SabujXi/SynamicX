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
import mimetypes
from synamic.core.services.content.functions.construct_url_object import content_construct_url_object
from synamic.core.contracts.content import ContentContract, DocumentType
from synamic.core.standalones.functions.decorators import not_loaded
from synamic.core.services.content.static import StaticContent
from synamic.core.services.content.toc import Toc
from synamic.core.services.content.marked_content import MarkedContentImplementation


_invalid_url = re.compile(r'^[a-zA-Z0-9]://', re.IGNORECASE)


class _ContentFields(dict):
    def __init__(self, site, content_file_path, model, content_id, document_type, raw_fileds, *a, **kwa):
        self.__site = site
        self.__content_file_path = content_file_path
        self.__model = model
        self.__content_id = content_id
        self.__document_type = document_type
        self.__raw_fields = raw_fileds
        super().__init__(*a, *kwa)

    def clone(self):
        c = self.__class__(self.__site, self.__model)
        for key, value in self.items():
            c[key] = value
        return c

    def __getattr__(self, key):
        return self.get(key, None)

    def get_content_path(self):
        """Content file path"""
        return self.__content_file_path

    def get_model(self):
        return self.__model

    def get_content_id(self):
        return self.__content_id

    def get_document_type(self):
        return self.__document_type

    def get_raw_fields(self):
        return self.__raw_fields


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

    def make_content_fields(self, fields_syd, file_cpath):
        # get dir meta syd
        # """It should not live here as it is compile time dependency"""
        # each field from meta syd will be converted with individual content model and site type system.
        dir_meta_file_name = self.__site.default_configs.get('configs')['dir_meta_file_name']
        _syd = self.__site.object_manager.empty_syd()
        parent_cpaths = file_cpath.parent_cpaths
        for dir_cpath in parent_cpaths:
            dir_meta_cfile = dir_cpath.join(dir_meta_file_name, is_file=True)
            if dir_meta_cfile.exists():
                dir_meta_syd = self.__site.object_manager.get_syd(dir_meta_cfile)
                _syd = _syd.new(dir_meta_syd)
        else:  # for else when loop ended normally without using break.
            fields_syd = _syd.new(fields_syd)

        types = self.__site.get_service('types')
        # TODO: what is the document type???
        document_type = DocumentType.HTML_DOCUMENT
        model_name = fields_syd.get('model', 'content')  # TODO: default model is 'content' not 'default'
        model = self.__site.object_manager.get_model(model_name)
        content_fields = _ContentFields(self.__site, file_cpath, model, file_cpath.id, document_type, fields_syd)

        # convert with type system.
        for key in fields_syd.keys():
            if key in model:
                model_field = model[key]
                converter_name = model_field.converter
                converter = types.get_converter(converter_name)
                value = converter(fields_syd[key])
            else:
                value = fields_syd[key]
            content_fields[key] = value
        return content_fields

    def make_md_content(self, file_path):
        markdown_renderer = self.__site.get_service('types').get_converter('markdown')
        document_type = DocumentType.HTML_DOCUMENT
        fields_syd, body_text = self.__site.object_manager.get_content_parts(file_path)
        content_fields = self.make_content_fields(fields_syd, file_path)
        toc = Toc()
        body = markdown_renderer(body_text, value_pack={
            'toc': toc
        }).rendered_markdown

        # pagination & chapters will be evaluated later - Lazy Evaluation.
        # chapters -> _chapters; so that user can think that fields have direct one to one mapping with value
        # slug_field = content_fields.get('slug', None)  # final segment of url path
        # path_field = content_fields.get('path', None)  # url path
        #
        # if slug_field is None and path_field is None:
        #     slug_field = file_path.basename

        # pagination & chapters will be evaluated later - Lazy Evaluation.
        # TODO: pagination_field = content_fields.get('pagination', None)
        # TODO: chapters_field = content_fields.get('chapters', None)

        # ordinary_fields['__pagination'] = None if pagination_field is None else pagination_field.value
        # # ordinary_fields['__chapters'] = None if chapters_field is None else chapters_field.value
        # if chapters_field is not None:
        #     ordinary_fields['chapters'] = get_chapters(site, chapters_field)
        # else:
        #     ordinary_fields['chapters'] = None
        #
        # for key, value in file_path.merged_meta_info.items():
        #     if key not in {'slug', 'permalink', 'pagination', 'chapters', 'model'}:
        #         if key not in ordinary_fields:
        #             ordinary_fields[key] = value
        # #
        # url_construction_dict = {
        #     'slug': None if slug_field is None else slug_field.value,
        #     'permalink': None if permalink_field is None else permalink_field.value
        # }
        # #
        # url_object = content_construct_url_object(site, file_path, url_construction_dict)

        content_id =file_path.id
        # mime type guess
        mime_type = 'text/html'
        content = MarkedContentImplementation(self.__site,
                                              file_path,
                                              body,
                                              content_fields,
                                              toc,
                                              content_id,
                                              document_type,
                                              mime_type=mime_type)
        return content

    def make_paginated_md_content(self):
        # TODO: code it
        pass

    def make_static_content(self, path):
        path_tree = self.__site.get_service('path_tree')
        path_obj = path_tree.create_file_cpath(path)
        content_id = path_obj.id
        file_content = None
        mime_type = 'octet/stream'  # TODO: guess the content type here.
        return StaticContent(
            self.__site,
            path_obj,
            content_id,
            file_content=file_content,
            document_type=DocumentType.BINARY_DOCUMENT,
            mime_type=mime_type)

