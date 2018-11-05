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
from synamic.core.services.content.static_content import StaticContent
from synamic.core.services.content.generated_content import GeneratedContent
from synamic.core.services.content.toc import Toc
from synamic.core.services.content.marked_content import MarkedContentImplementation


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

    @classmethod
    def is_type_content_id(cls, other):
        return type(other) is cls.__ContentID

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

        content_fields = self.make_content_fields(file_cpath, url_object, model, self.make_content_id(file_cpath), document_type, fields_syd)

        # convert with type system.
        for key in fields_syd.keys():
            if key in model:
                model_field = model[key]
                value = model_field.converter(fields_syd[key])
            else:
                value = fields_syd[key]
            content_fields[key] = value
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

        content_id = self.make_content_id(file_path.id)
        # mime type guess
        mime_type = 'text/html'
        url_object = content_fields.get_url_object()
        content = MarkedContentImplementation(self.__site,
                                              file_path,
                                              url_object,
                                              body,
                                              content_fields,
                                              toc,
                                              content_id,
                                              document_type,
                                              mime_type=mime_type)
        return content

    def build_paginated_md_content(self):
        # TODO: code it
        pass

    def build_static_content(self, path):
        path_tree = self.__site.get_service('path_tree')
        path_obj = path_tree.create_file_cpath(path)
        content_id = self.make_content_id(path_obj.id)
        file_content = None
        mime_type = 'octet/stream'  # TODO: guess the content type here.
        document_type = DocumentType.BINARY_DOCUMENT

        url_object = self.__site.object_manager.static_content_cpath_to_url(path_obj, document_type)

        return StaticContent(
            self.__site,
            path_obj,
            url_object,
            content_id,
            file_content=file_content,
            document_type=document_type,
            mime_type=mime_type)

    def build_generated_content(
            self, url_object, content_id, file_content,
            document_type=DocumentType.GENERATED_TEXT_DOCUMENT, mime_type='octet/stream', source_cpath=None, **kwargs):
        return GeneratedContent(self.__site, url_object, content_id, file_content, document_type=document_type, mime_type=mime_type, source_cpath=source_cpath, **kwargs)

    def make_content_fields(self, content_file_path, url_object, model, content_id, document_type, raw_fileds, *a, **kwa):
        """Just makes an instance"""
        return self.__ContentFields(self.__site, content_file_path, url_object, model, content_id, document_type, raw_fileds, *a, **kwa)

    def make_content_id(self, param):
        path_tree = self.__site.get_service('path_tree')
        if path_tree.is_type_cpath(param):
            str_id = param.id
        else:
            str_id = param
        return self.__ContentID(str_id)

    class __ContentFields(dict):
        def __init__(self, site, content_file_path, url_object, model, content_id, document_type, raw_fileds, *a, **kwa):
            assert ContentService.is_type_content_id(content_id)
            self.__site = site
            self.__content_file_path = content_file_path
            self.__url_object = url_object
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

        def __eq__(self, other):
            return self.__url_object == other.get_url_object()

        def __hash__(self):
            return hash(self.__url_object)

        def get_path_object(self):
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

        def get_url_object(self):
            return self.__url_object

    class __ContentID:
        def __init__(self, str_id):
            assert isinstance(str_id, str)
            self.__str_id = str_id

        @property
        def str_id(self):
            return self.__str_id

        def __eq__(self, other):
            return self.__str_id == other.str_id

        def __hash__(self):
            return hash(self.__str_id)

        def __str__(self):
            return "ContentID: %s" % self.str_id

        def __repr__(self):
            return repr(self.__str__())

