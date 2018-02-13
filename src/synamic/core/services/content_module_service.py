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
from collections import deque
from synamic.core.classes.path_tree import ContentPath2

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
        self.__field_converters = None

        self.__url = None
        self.__pagination = None
        # loading body and field
        doc = DocumentParser(self.__file_content).parse()
        model = self.__config.model_service.get_model(self.model_name)
        self.__convert_fields(model, doc)

    def __convert_fields(self, model, doc):
        self.__fields = OrderedDict()
        self.__field_converters = OrderedDict()

        def content_fields_visitor(a_field, field_path, _res_map_: OrderedDict):
            """
            :param a_field:
            :param field_path: is a tuple of nested field names
            """
            dotted_field = ".".join([field for field in field_path])
            field_config = model.get(dotted_field, None)

            if field_config is None:
                # deliver the raw sting to the field
                # assert model_field is not None, "field `%s` is not defined in the model" % dotted_field
                type_name = 'text'
                converter = self.__config.type_system.get_converter(type_name)
                converted_value = converter(a_field.value, self.__config)

            else:
                # print(field_config.type)
                # print("For Field: %s" % field_config.for_field)
                converter = field_config.converter
                # print("For Field Converter: %s" % field_config.converter)
                converted_value = converter(a_field.value, self.__config)

            _res_map_[dotted_field] = converted_value
            self.__field_converters[dotted_field] = converter
            proceed = True
            return proceed

        field_config_4_body = model.get('__body__', None)
        if field_config_4_body is not None:
            body_converter = field_config_4_body.converter
        else:
            body_converter = self.__config.type_system.get_converter('markdown')
        doc.root_field.visit(content_fields_visitor, self.__fields)
        self.__body = body_converter(doc.body, self.__config)

    @property
    def language(self):
        ln = self.__fields.get('language', None)
        if ln is not None:
            return ln

        ln = 'en'
        pp = self.path_object.parent_path
        while pp is not None:
            _ln = pp.meta_info.get('language', None)
            if _ln is None:
                break
            else:
                ln = _ln
            pp = pp.parent_path
        return ln

    @property
    def model_name(self):
        mn = 'text'
        pp = self.path_object.parent_path
        while pp is not None:
            _mn = pp.meta_info.get('model', None)
            if _mn is None:
                break
            else:
                mn = _mn
            pp = pp.parent_path
        return mn

    @property
    def config(self):
        return self.__config

    @property
    def path_object(self) -> ContentPath2:
        return self.__path

    @property
    def content_id(self):
        return self.fields.get('id', None)

    @property
    def id(self):
        return self.content_id

    @property
    def url_path(self):
        return self.url_object.path

    def get_stream(self):
        template_name = 'default.html'
        pp = self.path_object.parent_path

        while pp is not None:
            meta_template_name = pp.meta_info.get('template', None)
            # print(pp.meta_info)
            if meta_template_name is not None:
                template_name = meta_template_name
                break
            pp = pp.parent_path

        cont_template_name = self.fields.get('template', None)
        if cont_template_name is not None:
            template_name = cont_template_name
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
            # so, /404.html should not be /404.html/(index.html) - see below.
            # Let's start from the root to make url.
            parent_paths = self.path_object.parent_paths
            url_comps = deque()

            if parent_paths:
                for path in parent_paths:
                    meta_info = path.meta_info
                    # permalink gets the first priority - whenever permalink is encountered, all previous calculation
                    # is discarded
                    # print("Meta Inf: `%s`" % str(meta_info))
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

            pm = self.fields.get('permalink', None)
            sl = self.fields.get('slug', None)
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
                last_part = self.path_object.basename
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
                cnt_url = cnt_url.join(url_path_comp)#, append_slash=append_slash)
            # print("URL: `%s`" % cnt_url)
            self.__url = cnt_url
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
        return self.__getattr__(key)

    def __getattr__(self, key):
        res = getattr(self.__content, key, None)
        if res is None:
            res = self.__content.fields.get(key, None)
        return res


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
