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
from synamic.core.services.content.functions.create_marked_content import content_create_marked_content
from synamic.core.services.content.functions.paginate import content_paginate

from synamic.core.contracts import BaseContentModuleContract
from synamic.core.event_system.event_types import EventTypes
from synamic.core.event_system.events import Handler

from synamic.core.standalones.functions.decorators import not_loaded, loaded

_invalid_url = re.compile(r'^[a-zA-Z0-9]://', re.IGNORECASE)


class MarkedContentService(BaseContentModuleContract):
    __slots__ = ('__synamic', '__is_loaded', '__contents_by_id', '__dynamic_contents', '__auxiliary_contents')

    def __init__(self, synamic):
        self.__synamic = synamic
        self.__is_loaded = False
        self.__service_home_path = None
        self.__synamic.register_path(self.service_home_path)

        synamic.event_system.add_event_handler(
            EventTypes.CONTENT_POST_LOAD,
            Handler(self.__create_paginated_contents)
        )

        self.__default_field_values = {
            'language': 'en',
            'template': 'default.html'
        }

        self.__default_model_name = 'text'

        self.__pagination_complete = False

    @property
    def service_home_path(self):
        if self.__service_home_path is None:
            self.__service_home_path = self.__synamic.path_tree.create_path(('content',))
        return self.__service_home_path

    @property
    def name(self):
        return 'content'

    @property
    def config(self):
        return self.__synamic

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        paths = self.__synamic.path_tree.list_file_paths(*('content',))
        for file_path in paths:
            if file_path.extension.lower() in {'md', 'markdown'}:
                with file_path.open("r", encoding="utf-8") as f:
                    text = f.read()
                    content_obj = content_create_marked_content(self.__synamic, file_path, text)
                    self.__synamic.add_document(content_obj)
            else:
                self.__synamic.add_static_content(file_path)
        self.__is_loaded = True

    @loaded
    def __create_paginated_contents(self, event):
        assert self.__pagination_complete is False
        dynamic_contents = self.__synamic.dynamic_contents
        for cnt in dynamic_contents:
            query_str = cnt.fields.get('__pagination', None)
            if query_str is not None:
                aux_cnts = self.__paginate(dynamic_contents, cnt, query_str, contents_per_page=2)
                for aux_cnt in aux_cnts:
                    self.__synamic.add_auxiliary_content(aux_cnt)
        self.__pagination_complete = True

    @loaded
    def __paginate(self, contents, starting_content, filter_txt, contents_per_page=2):
        return content_paginate(self.__synamic, contents, starting_content, filter_txt, contents_per_page=contents_per_page)

    def __construct_url_object(self, path_object, slug_permalink_dict):
        return content_construct_url_object(self.__synamic, path_object, slug_permalink_dict)
