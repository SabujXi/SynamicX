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
from synamic.core.services.content.marked_content import MarkedContent
from synamic.core.services.content.paginated_content import PaginationPage
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
        return type(other) is _ContentFields

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

        # TODO: can the following be more systematic and agile.
        # create markers that exists in fields/contents but not in the system
        for marker_id in ('tags', 'categories'):
            if marker_id in fields_syd:
                marker = self.__site.object_manager.get_marker(marker_id)
                marks = self.__site.get_service('types').get_converter('marker#' + marker_id)(fields_syd[marker_id])
                for mark in marks:
                    if marker.get_mark_by_id(mark.id, None) is None:
                        marker.add_mark(mark)

        return content_fields

    def build_md_content(self, file_path, cached_content_fields):
        mime_type = 'text/html'
        document_type = DocumentType.HTML_DOCUMENT

        _, body_text = self.__site.object_manager.get_content_parts(file_path)
        # mime type guess
        url_object = cached_content_fields.curl_object
        content = MarkedContent(self.__site,
                                file_path,
                                url_object,
                                body_text,
                                cached_content_fields,
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
        return _ContentFields(self.__site, content_file_path, url_object, model, document_type, raw_fileds, *a, **kwa)

    def build_chapters(self, chapters_fields):
        chapters = []
        for cfs in chapters_fields:
            chapters.append(Chapter(self.__site, cfs))
        return tuple(chapters)


class _ContentFields:
    def __init__(self, site, content_file_path, url_object, model, document_type, raw_fileds):
        self.__site = site
        self.__content_file_path = content_file_path
        self.__url_object = url_object
        self.__model = model
        self.__document_type = document_type
        self.__raw_fields = raw_fileds
        self.__converted_values = OrderedDict()

    def as_generated(self, url_object, document_type=DocumentType.GENERATED_HTML_DOCUMENT):
        """With fields will use .set() and thus it will only affect converted values."""
        return _GeneratedContentFields(self.__site, url_object, self.__model, document_type, self)

    def __convert_pagination(self, pagination_field):
        object_manager = self.__site.object_manager
        site_settings = object_manager.get_site_settings()
        per_page = site_settings['pagination_per_page']

        if isinstance(pagination_field, str):
            query_str = pagination_field
        else:
            query_str = pagination_field['query']
            per_page = pagination_field.get('per_page', None)
            if per_page is not None:
                assert isinstance(per_page, int)
                per_page = per_page
        fields = object_manager.query_fields(query_str)
        origin_content = object_manager.get_marked_content(self.cpath_object)
        assert self is origin_content.fields
        paginations, paginated_contents = PaginationPage.paginate_content_fields(
            self.__site,
            origin_content,
            fields,
            per_page
        )
        return paginations, paginated_contents

    def __convert_chapters(self, param):
        content_service = self.__site.get_service('contents')
        chapters = content_service.build_chapters(param)
        return chapters

    def get(self, key, default=None):
        raw_value = self.__raw_fields.get(key, None)
        if raw_value is None:
            return default

        value = self.__converted_values.get(key, None)
        if value is None:
            # special conversions
            if key in ('pagination', 'chapters'):
                if key == 'pagination':
                    pagination_field = raw_value
                    paginations, paginated_contents = self.__convert_pagination(pagination_field)
                    value = paginations[0]
                elif key == 'chapters':
                    content_service = self.__site.get_service('contents')
                    chapters = content_service.build_chapters(raw_value)
                    value = chapters
            # normal conversions through converter or else raw value
            else:
                model_field = self.__model.get(key, None)
                if model_field is not None:
                    value = model_field.converter(raw_value)
                else:
                    value = raw_value
            self.__converted_values[key] = value
        return value

    def set(self, key, value):
        """Converted fields will be affected only.
        Raw fields will stay intact."""
        self.__converted_values[key] = value

    @property
    def raw(self):
        return self.__raw_fields

    @property
    def keys(self):
        return tuple(set(self.__converted_values.keys()).union(set(self.__raw_fields.keys())))

    @property
    def document_type(self):
        return self.__document_type

    @property
    def model_object(self):
        return self.__model

    @property
    def curl_object(self):
        return self.__url_object

    @property
    def cpath_object(self):
        """Content file path"""
        return self.__content_file_path

    def __getitem__(self, key):
        return self.get(key, None)

    def __getattr__(self, key):
        return self.get(key, None)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__url_object == other.curl_object

    def __hash__(self):
        return hash(self.__url_object)


class _GeneratedContentFields:
    def __init__(self, site, url_object, model, document_type, origin_content_fields):
        self.__site = site
        self.__url_object = url_object
        self.__model = model
        self.__document_type = document_type
        self.__origin_content_fields = origin_content_fields

        self.__overridden_fields = {}

    def get(self, key, default=None):
        value = self.__overridden_fields.get(key, None)
        if value is None:
            value = self.__origin_content_fields.get(key, default)
        return value

    def set(self, key, value):
        """Converted fields will be affected only.
        Raw fields will stay intact."""
        self.__overridden_fields[key] = value

    @property
    def raw(self):
        return self.__origin_content_fields.raw

    @property
    def keys(self):
        return tuple(set(self.__origin_content_fields.keys()).union(set(self.__overridden_fields.keys())))

    @property
    def document_type(self):
        return self.__document_type

    @property
    def model_object(self):
        return self.__model

    @property
    def curl_object(self):
        return self.__url_object

    @property
    def cpath_object(self):
        raise NotImplemented

    def __getitem__(self, key):
        return self.get(key, None)

    def __getattr__(self, key):
        return self.get(key, None)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__url_object == other.curl_object

    def __hash__(self):
        return hash(self.__url_object)
