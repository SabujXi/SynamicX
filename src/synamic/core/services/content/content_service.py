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

from synamic.core.services.content.functions.construct_url_object import content_construct_url_object
from synamic.core.contracts.content import ContentContract
from synamic.core.contracts import BaseContentModuleContract
from synamic.core.standalones.functions.decorators import not_loaded
from synamic.core.services.content.static import StaticContent
from synamic.core.services.content.toc import Toc
from synamic.core.services.content.marked_content import MarkedContentImplementation


_invalid_url = re.compile(r'^[a-zA-Z0-9]://', re.IGNORECASE)


class _ContentFields(dict):
    def __init__(self, site, model, content_id, *a, **kwa):
        self.__site = site
        self.__model = model
        self.__content_id = content_id
        super().__init__(*a, *kwa)

    def clone(self):
        c = self.__class__(self.__site, self.__model)
        for key, value in self.items():
            c[key] = value
        return c

    def __getattr__(self, key):
        return self.get(key, None)

    def get_model(self):
        return self.__model

    def get_content_id(self):
        return self.__content_id


class ContentService(BaseContentModuleContract):
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

    def make_content_fields(self, fields_syd):
        types = self.__site.get_service('types')

        content_type = ContentContract.types.DYNAMIC

        model_name = fields_syd.get('model', 'content')  # TODO: default model is content not default
        model = self.__site.object_manager.get_model(model_name)
        content_fields = _ContentFields(self.__site, model)
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
        content_type = ContentContract.types.DYNAMIC
        fields_syd, body_text = self.__site.object_manager.get_content_parts(file_path)
        content_fields = self.make_content_fields(fields_syd)
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

        content = MarkedContentImplementation(self.__site, body, content_fields, toc,
                                              content_id=file_path.id(),
                                              content_type=content_type)
        return content

    def make_paginated_md_content(self):
        # TODO: code it
        pass

    def make_static_content(self, path):
        path_tree = self.__site.get_service('path_tree')
        path_obj = path_tree.create_file_cpath(path)
        return StaticContent(self.__site, path_obj)

    def all_static_paths(self):
        # TODO: move this method to object manager.
        paths = []
        path_tree = self.__site.get_service('path_tree')
        statics_dir = self.__site.default_configs.get('dirs')['statics.statics']
        contents_dir = self.__site.default_configs.get('dirs')['contents.contents']
        paths.extend(path_tree.list_file_cpaths(statics_dir))

        for path in path_tree.list_file_cpaths(contents_dir):
            if path.basename.lower().endswith(('.md', '.markdown')):
                paths.append(path)
        return paths
