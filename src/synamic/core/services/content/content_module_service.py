"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import io
import re
import mimetypes
from synamic.core.contracts import BaseContentModuleContract, ContentContract
from synamic.core.contracts.document import MarkedDocumentContract
from synamic.core.functions.decorators import not_loaded, loaded
from synamic.core.classes.url import ContentUrl
from synamic.core.new_parsers.document_parser import DocumentParser
from collections import OrderedDict
from collections import deque
from synamic.core.classes.path_tree import ContentPath2
from synamic.core.event_system.event_types import EventTypes
from synamic.core.event_system.events import EventSystem, Handler
from synamic.core.services.content.pagination import Pagination
from synamic.core.new_filter.filter_functions import query_by_objects
from synamic.core.services.content.chapters import get_chapters


_invalid_url = re.compile(r'^[a-zA-Z0-9]://', re.IGNORECASE)


class MarkedContentImplementation(MarkedDocumentContract):

    def __init__(self, config, path_object, url_object, body, fields, field_converters=None, content_type=None):
        self.__config = config
        self.__path = path_object
        self.__url_object = url_object
        self.__body = body
        self.__fields = fields
        self.__field_converters = field_converters
        self.__content_type = content_type
        self.__pagination = None

    @property
    def config(self):
        return self.__config

    @property
    def path_object(self) -> ContentPath2:
        return self.__path

    @property
    def url_object(self):
        return self.__url_object

    @property
    def id(self):
        return self.fields.get('id', None)

    @property
    def url_path(self):
        return self.url_object.path

    def get_stream(self):
        template_name = self.fields.get('template', 'default.html')
        res = self.__config.templates.render(template_name, content=self)
        f = io.BytesIO(res.encode('utf-8'))
        return f

    @property
    def content_type(self):
        return self.__content_type

    @property
    def mime_type(self):
        mime_type = 'octet/stream'
        path = self.url_object.real_path
        type, enc = mimetypes.guess_type(path)
        if type:
            mime_type = type
        return mime_type

    @property
    def body(self):
        return self.__body

    @property
    def fields(self):
        return self.__fields

    @property
    def field_converters(self):
        return self.__field_converters

    @property
    def pagination(self):
        return self.__pagination

    def _set_pagination(self, pg):
        if self.__pagination is None:
            self.__pagination = pg
        else:
            raise Exception("Cannot set pagination once it is set")

    def __get(self, key):
        value = self.__fields.get(key, None)
        return value

    def __getitem__(self, key):
        return self.__get(key)

    def __getattr__(self, key):
        return self.__get(key)

    def __str__(self):
        return self.path_object.relative_path

    def __repr__(self):
        return str(self)


class MarkedContentService(BaseContentModuleContract):
    __slots__ = ('__config', '__is_loaded', '__contents_by_id', '__dynamic_contents', '__auxiliary_contents')

    def __init__(self, _cfg):
        self.__config = _cfg
        self.__is_loaded = False
        self.__service_home_path = None
        self.__config.register_path(self.service_home_path)

        EventSystem.add_event_handler(
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
            self.__service_home_path = self.__config.path_tree.create_path(('content',))
        return self.__service_home_path

    @property
    def name(self):
        return 'content'

    @property
    def config(self):
        return self.__config

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        paths = self.__config.path_tree.list_file_paths(*('content',))
        for file_path in paths:
            if file_path.extension.lower() in {'md', 'markdown'}:
                with file_path.open("r", encoding="utf-8") as f:
                    text = f.read()
                    content_obj = self.__create_marked_content(file_path, text)
                    self.__config.add_document(content_obj)
            else:
                self.__config.add_static_content(file_path)
        self.__is_loaded = True

    def __create_marked_content(self, file_path, file_content):
        doc = DocumentParser(file_content).parse()
        model = self.__config.model_service.get_model(file_path.merged_meta_info.get('model', 'default'))

        ordinary_fields, field_converters = self.__convert_fields(model, doc)

        # convert field
        field_config_4_body = model.get('__body__', None)
        if field_config_4_body is not None:
            body_converter = field_config_4_body.converter
        else:
            body_converter = self.__config.type_system.get_converter('markdown')
        body = body_converter(doc.body, self.__config)
        #
        # TODO: later make them system field: slug -> _slug, permalink -> _permalink, pagination -> _pagination,
        # chapters -> _chapters; so that user can think that fields have direct one to one mapping with value
        slug_field = doc.root_field.get('slug', None)
        permalink_field = doc.root_field.get('permalink', None)
        pagination_field = doc.root_field.get('pagination', None)
        chapters_field = doc.root_field.get('chapters', None)

        ordinary_fields['__pagination'] = None if pagination_field is None else pagination_field.value
        # ordinary_fields['__chapters'] = None if chapters_field is None else chapters_field.value
        if chapters_field is not None:
            ordinary_fields['chapters'] = get_chapters(self.__config, chapters_field)
        else:
            ordinary_fields['chapters'] = None

        for key, value in file_path.merged_meta_info.items():
            if key not in {'slug', 'permalink', 'pagination', 'chapters', 'model'}:
                if key not in ordinary_fields:
                    ordinary_fields[key] = value
        #
        url_construction_dict = {
            'slug': None if slug_field is None else slug_field.value,
            'permalink': None if permalink_field is None else permalink_field.value
        }
        #
        url_object = self.__construct_url_object(file_path, url_construction_dict)

        content = MarkedContentImplementation(self.__config, file_path, url_object,
                                              body, ordinary_fields,
                                              field_converters=field_converters,
                                              content_type=ContentContract.types.DYNAMIC)
        return content

    @loaded
    def __create_auxiliary_marked_content(self, content, position):
        new_url = content.url_object.join("_/%s/" % position)
        # init_url = ContentUrl(self.__config, "_/%s/" % position)
        # new_url = init_url.join(content.url_object.path_components)
        return MarkedContentImplementation(self.__config,
                                           content.path_object,
                                           new_url,
                                           content.body,
                                           content.fields,
                                           content_type=ContentContract.types.AUXILIARY)

    @loaded
    def __create_paginated_contents(self, event):
        assert self.__pagination_complete is False
        dynamic_contents = self.__config.dynamic_contents
        for cnt in dynamic_contents:
            query_str = cnt.fields.get('__pagination', None)
            if query_str is not None:
                aux_cnts = self.__paginate(dynamic_contents, cnt, query_str, contents_per_page=2)
                for aux_cnt in aux_cnts:
                    self.__config.add_auxiliary_content(aux_cnt)
        self.__pagination_complete = True

    @loaded
    def __paginate(self, contents, starting_content, filter_txt, contents_per_page=2):
        rules_txt = filter_txt
        per_page = contents_per_page
        cnts = query_by_objects(contents, rules_txt)
        aux_contents = []

        paginations = []
        paginated_contents = []

        if cnts:
            q, r = divmod(len(cnts), per_page)
            divs = q
            if r > 0:
                divs += 1

            for i in range(divs):
                _cts = []
                for j in range(per_page):
                    idx = (i * per_page) + j  # (row * NUMCOLS) + column        #(i * divs) + j
                    if idx >= len(cnts):
                        break
                    _cts.append(cnts[idx])
                paginated_contents.append(tuple(_cts))

        if paginated_contents:
            i = 0
            prev_page = None
            for _page_contents in paginated_contents:

                pagination = Pagination(len(paginated_contents), _page_contents, i, per_page)
                paginations.append(pagination)

                if i == 0:
                    # setting pagination to the host content
                    starting_content._set_pagination(pagination)
                    pagination.host_page = starting_content
                    prev_page = starting_content

                else:
                    aux = self.__create_auxiliary_marked_content(
                        starting_content, pagination.position
                    )
                    # setting pagination to an aux content
                    aux._set_pagination(pagination)
                    pagination.host_page = aux

                    pagination.previous_page = prev_page
                    # TODO: content wrapper for prev/next page : done but it is still not in contract
                    prev_page.pagination.next_page = aux
                    prev_page = aux

                    aux_contents.append(aux)
                i += 1
        return tuple(aux_contents)

    def __convert_fields(self, model, doc):
        _fields = OrderedDict()
        _field_converters = OrderedDict()

        def content_fields_visitor(a_field, field_path, _res_map_: OrderedDict):
            """
            :param a_field:
            :param field_path: is a tuple of nested field names
            """
            dotted_field = ".".join([field for field in field_path])

            if dotted_field in {'pagination', 'slug', 'permalink', 'chapters'}:
                # skip them
                proceed = True
                return proceed

            field_config = model.get(dotted_field, None)

            if field_config is None:
                # deliver the raw sting to the field
                # assert model_field is not None, "field `%s` is not defined in the model" % dotted_field
                type_name = 'text'
                converter = self.__config.type_system.get_converter(type_name)
                converted_value = converter(a_field.value, self.__config)
            else:
                converter = field_config.converter
                converted_value = converter(a_field.value, self.__config)

            _res_map_[dotted_field] = converted_value
            _field_converters[dotted_field] = converter
            proceed = True
            return proceed

        doc.root_field.visit(content_fields_visitor, _fields)
        return _fields, _field_converters

    def __construct_url_object(self, path_object, slug_permalink_dict):
        # if self.__url is None:
        # so, /404.html should not be /404.html/(index.html) - see below.
        # Let's start from the root to make url.
        parent_paths = path_object.parent_paths
        url_comps = deque()

        if parent_paths:
            for path in parent_paths:
                meta_info = path.meta_info
                # permalink gets the first priority - whenever permalink is encountered, all previous calculation
                # is discarded
                pm = meta_info.get('permalink', None)
                sl = meta_info.get('slug', None)
                if pm is not None:
                    url_comps.clear()
                    url_comps.append(pm)
                elif sl is not None:
                        url_comps.append(sl)
                else:
                    # dir name will be used as slug when not not permalink, neither slug is defined
                    _slug = path.basename + '/'
                    url_comps.append(_slug)
                    # url_comps.append('')

        pm = slug_permalink_dict.get('permalink', None)
        sl = slug_permalink_dict.get('slug', None)
        by_base_name = False
        last_part = None
        if pm is not None:
            url_comps.clear()
            # url_comps.append(pm)
            last_part = pm
        elif sl is not None:
            # url_comps.append(sl)
            last_part = sl
        else:
            # dir name will be used as slug when not not permalink, neither slug is defined
            by_base_name = True
            last_part = path_object.basename
            # url_comps.append()

        _ext_match = re.match(r'(?P<file_name>.*)\.[a-z0-9]+$', last_part, re.I)
        if not _ext_match:
            if not last_part.endswith('/'):
                last_part += '/'
        else:
            if by_base_name:
                fn = _ext_match.group('file_name')
                if fn:
                    last_part = fn + '/'

        url_comps.append(last_part)
        cnt_url = ContentUrl(self.__config, '')

        for url_path_comp in url_comps:
            cnt_url = cnt_url.join(url_path_comp)  # append_slash=append_slash)
        # print("URL: `%s`" % cnt_url)
        return cnt_url


