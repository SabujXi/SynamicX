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
from synamic.core.classes.pagination import PaginationStream
from synamic.core.contracts import BaseContentModuleContract, ContentContract
from synamic.core.contracts.document import MarkedDocumentContract
from synamic.core.functions.decorators import not_loaded, loaded
from synamic.core.classes.url import ContentUrl
from synamic.core.new_parsers.document_parser import DocumentParser
from collections import OrderedDict


_invalid_url = re.compile(r'^[a-zA-Z0-9]://', re.IGNORECASE)


class AuxMarkedContentImplementation(MarkedDocumentContract):
    def __init__(self, marked_content, page_no):
        self.__marked_content = marked_content
        self.__page_no = page_no
        self.__url = None

        self.__pagination = None

    @property
    def pagination(self):
        return self.__pagination

    @pagination.setter
    def pagination(self, pgn):
        self.__pagination = pgn

    @property
    def config(self):
        return self.__marked_content.config

    @property
    def path_object(self):
        return None

    @property
    def content_id(self):
        return None

    def get_stream(self):
        template_name = self.fields.get('template', None)
        res = self.config.templates.render(template_name, content=self.get_content_wrapper())
        f = io.BytesIO(res.encode('utf-8'))
        return f

    @property
    def content_type(self):
        return self.types.AUXILIARY

    @property
    def mime_type(self):
        return self.__marked_content.mime_type

    @property
    def body(self):
        return self.__marked_content.body

    @property
    def fields(self):
        return self.__marked_content.fields

    @property
    def field_converters(self):
        return self.__marked_content.field_converters

    @property
    def url_object(self):
        if self.__url is None:
            # print("Fields: %s" % self.fields)
            self.__url = ContentUrl(self.config, '_/' + self.fields['permalink'] + '/' + str(self.__page_no), append_slash=True)
        return self.__url

    @property
    def absolute_url(self):
        return self.url_object.full_url

    def get_content_wrapper(self):
        # TODO: should place in contract!
        # So, with cotract it can be used in paginator too
        return ContentWrapper(self)


class MarkedContentImplementation(MarkedDocumentContract):
    def __init__(self, config, path_object, file_content: str):
        self.__config = config
        self.__path = path_object
        self.__content_type = ContentContract.types.DYNAMIC
        self.__file_content = file_content

        self.__body = None
        self.__fields = None

        self.__url = None

        # loading body and field
        doc = DocumentParser(self.__file_content).parse()

        res_map = self.__config.model_service.get_converted('text', doc.root_field, doc.body)
        # print("Resp Map : %s" % res_map)
        self.__body = res_map['__body__']
        del res_map['__body__']
        self.__fields = OrderedDict()
        self.__field_converters = OrderedDict()
        for k, v in res_map.items():
            self.__fields[k] = v['value']
            self.field_converters[k] = v['converter']
        # print("Resp Map2: %s" % res_map)

        self.__pagination = None

    # temporary for fixing sitemap
    @property
    def config(self):
        return self.__config

    @property
    def path_object(self):
        return self.__path

    @property
    def content_id(self):
        return self.fields.get('id', None)

    def get_stream(self):
        template_name = self.fields.get('template', None)
        res = self.__config.templates.render(template_name, content=self.get_content_wrapper())
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
    def url_object(self):
        if self.__url is None:
            # print("Fields: %s" % self.fields)

            # so, /404.html should not be /404.html/(index.html) - see below.
            slug = self.fields['permalink']
            if not re.match(r'.*\.[a-z0-9]+$', slug, re.I):
                if not slug.endswith('/'):
                    slug += '/'
            self.__url = ContentUrl(self.__config, slug)
        return self.__url

    @property
    def absolute_url(self):
        return self.url_object.full_url

    def get_content_wrapper(self):
        # TODO: should place in contract!
        # So, with cotract it can be used in paginator too
        return ContentWrapper(self)

    @property
    def pagination(self):
        return self.__pagination

    @pagination.setter
    def pagination(self, pgn):
        self.__pagination = pgn

    def trigger_post_processing(self):
        """For example: pagination"""
        query_str = self.fields.get('pagination', None)
        if query_str is not None:
            page_stream = PaginationStream(self.__config, self, query_str)

            for aux_cnt in page_stream.auxiliary_contents:
                self.__config.add_document(aux_cnt)

    def create_auxiliary(self, page_no):
        return AuxMarkedContentImplementation(self, page_no)

    def __str__(self):
        return self.path_object.relative_path

    def __repr__(self):
        return str(self)


class ContentWrapper:
    __slots__ = ('__content',)

    def __init__(self, content):
        self.__content = content

    def __getitem__(self, key):
        res = getattr(self.__content, key, None)
        if res is None:
            res = self.__content.fields.get(key, None)
        return res

    def __getattr__(self, key):
        return self.__getitem__(key)

    @property
    def id(self):
        return self.__content.content_id

    @property
    def url_path(self):
        return self.__content.url_object.path


class MarkedContentService(BaseContentModuleContract):
    __slots__ = ('__config', '__is_loaded', '__contents_by_id', '__dynamic_contents', '__auxiliary_contents')

    def __init__(self, _cfg):
        self.__config = _cfg
        self.__is_loaded = False
        self.__service_home_path = None

        self.__config.register_path(self.service_home_path)

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
        # print(paths)

        for file_path in paths:
            if file_path.extension.lower() in {'md', 'markdown'}:
                with file_path.open("r", encoding="utf-8") as f:
                    text = f.read()
                    content_obj = MarkedContentImplementation(self.__config, file_path, text)

                    content_id = content_obj.fields.get('id', None)
                    # if content_id in self.__dynamic_contents:
                    #     if content_obj.content_id is not None:
                    #         raise Exception("Duplicate `{module_name}` content id. It is `{content_id}`".format(module_name=self.name, content_id=content_obj.id))
                    self.__config.add_document(content_obj)
            else:
                self.__config.add_static_content(file_path)
        self.__is_loaded = True
