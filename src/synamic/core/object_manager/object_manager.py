from collections import defaultdict, OrderedDict, namedtuple
from synamic.core.contracts import DocumentType
from synamic.core.services.content.functions.content_splitter import content_splitter
from synamic.core.parsing_systems.model_parser import ModelParser
from synamic.core.parsing_systems.curlybrace_parser import SydParser
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.contracts import ContentContract, DocumentType
from .query import SimpleQueryParser


class ObjectManager:
    def __init__(self, synamic):
        self.__synamic = synamic

        self.__site_object_managers = OrderedDict({})
        self.__site_settings = defaultdict(dict)

        self.__cache = self.__Cache(self.__synamic)

        self.__is_loaded = False

    def get_manager_for_site(self, site):
        if site.id not in self.__site_object_managers:
            om_4_site = self.__ObjectManagerForSite(site, self)
            self.__site_object_managers[site.id] = om_4_site
        else:
            om_4_site = self.__site_object_managers[site.id]
        return om_4_site

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        self.__is_loaded = True

    def _reload_for(self, site):
        self.__cache.clear_cache(site)
        self._load_for(site)

    def _load_for(self, site):
        self.__cache_markers(site)
        self.__cache_marked_content_fields(site)
        self.__cache_pre_processed_contents(site)
        self.__cache_menus(site)

    def __cache_marked_content_fields(self, site):
        if site.synamic.env['backend'] == 'file':  # TODO: fix it.
            content_service = site.get_service('contents')
            path_tree = self.get_path_tree(site)
            content_dir = site.synamic.default_data.get_syd('dirs')['contents.contents']

            # for content
            file_paths = path_tree.list_file_cpaths(content_dir)
            for file_path in file_paths:
                if file_path.extension.lower() in {'md', 'markdown'}:
                    text = self.get_raw_data(site, file_path)
                    front_matter, body = content_splitter(file_path, text)
                    del body
                    fields_syd = self.make_syd(front_matter)
                    content_fields = content_service.build_content_fields(fields_syd, file_path)
                    self.__cache.add_marked_content_fields(site, content_fields)
                else:
                    # No need to cache anything about static file.
                    pass
        else:
            raise NotImplemented
            # database backend is not implemented yet. AND there is nothing to do here for db, skip it when implemented

    def __cache_markers(self, site):
        marker_service = site.get_service('markers')
        marker_ids = marker_service.get_marker_ids()
        for marker_id in marker_ids:
            marker = marker_service.make_marker(marker_id)
            self.__cache.add_marker(site, marker_id, marker)
            # self.__marker_by_id_cachemap[site.id][marker_id] = marker

    def __cache_pre_processed_contents(self, site):
        pre_processor_service = site.get_service('pre_processor')
        pre_processors = pre_processor_service.pre_processors
        for pre_processor in pre_processors:
            generated_contents = pre_processor.get_generated_contents()
            for generated_content in generated_contents:
                self.__cache.add_pre_processed_content(site, generated_content, generated_content.source_cpath)
                # self.__pre_processed_content_cachemap[site.id][generated_content.id] = generated_content

    def __cache_menus(self, site):
        menu_service = site.get_service('menus')
        menu_names = menu_service.get_menu_names()
        for menu_name in menu_names:
            menu = menu_service.make_menu(menu_name)
            self.__cache.add_menu(site, menu_name, menu)

    def make_url_for_marked_content(self, site, file_cpath, path=None, slug=None, for_document_type=DocumentType.TEXT_DOCUMENT):
        if path is not None:
            #  discard everything and keep it. No processing needed.
            pass
        elif slug is not None:
            # calculate through file system.
            cpath_comps = file_cpath.path_comps
            basename = cpath_comps[-1]
            # TODO: what to do to basename? unused!
            cpath_comps = cpath_comps[1:-1]  # ignoring `contents` dir  TODO: make it more logical and dynamic
            # instead of hard coded.
            _ = []
            for ccomp in cpath_comps:
                if not ccomp.startswith('_'):
                    _.append(ccomp)

            cpath_comps = _
            cpath_comps.append(slug)
            path = cpath_comps
        else:
            # calculate through file system.
            cpath_comps = file_cpath.path_comps
            basename = cpath_comps[-1]
            cpath_comps = cpath_comps[1:-1]  # ignoring `contents` dir  TODO: make it more logical and dynamic
            # instead of hard coded.
            _ = []
            for ccomp in cpath_comps:
                if not ccomp.startswith('_'):
                    _.append(ccomp)

            cpath_comps = _
            cpath_comps.append(basename)
            path = cpath_comps

        url_path_comps = path
        url_object = self.__synamic.router.make_url(
            site,
            url_path_comps,
            for_document_type=for_document_type
        )
        return url_object

    def static_content_cpath_to_url(self, site, cpath, for_document_type):
        assert DocumentType.is_binary(for_document_type, not_generated=True)
        # For STATIC Files
        url_object = self.__synamic.router.make_url(
            site,
            cpath.path_comps,
            for_document_type=for_document_type
        )
        return url_object

    #  @loaded
    def get_content_fields(self, site, path, default=None):
        path_tree = site.get_service('path_tree')
        content_service = site.get_service('contents')
        path = path_tree.create_cpath(path)
        if site.synamic.env['backend'] == 'database':
            raise NotImplemented
        else:
            # file backend
            return self.__cache.get_marked_content_fields_by_cpath(site, path, default=default)

    #  @loaded
    def get_marked_content(self, site, path):
        # create content, meta, set meta with converters. Setting it from here will help caching.
        # TODO: other type of contents besides md contents.
        content_service = site.get_service('contents')
        path_tree = self.get_path_tree(site)
        contents_dir = site.default_data.get_syd('dirs')['contents.contents']
        if isinstance(path, str):
            file_cpath = path_tree.create_file_cpath(contents_dir + '/' + path)
        else:
            file_cpath = path
        if not file_cpath.exists():
            return None
        md_content = content_service.build_md_content(file_cpath)
        return md_content

    def get_marked_content_by_url(self, site, url_object):
        cpath = url_object.get_path_object()
        return self.get_marked_content(site, cpath)

    def get_binary_content(self, site, path):
        path_tree = site.get_service('path_tree')
        if not path_tree.exists(path):
            return None
        else:
            content_service = site.get_service('contents')
            return content_service.build_static_content(path)

    def get_static_file_paths(self, site):
        pass

    def all_static_paths(self, site):
        paths = []
        path_tree = site.get_service('path_tree')
        statics_dir = site.default_data.get_syd('dirs')['contents.statics']
        contents_dir = site.default_data.get_syd('dirs')['contents.contents']
        paths.extend(path_tree.list_file_cpaths(statics_dir))

        for path in path_tree.list_file_cpaths(contents_dir):
            if path.basename.lower().endswith(('.md', '.markdown')):
                paths.append(path)
        return paths

    @staticmethod
    def empty_syd():
        return SydParser('').parse()

    def get_raw_data(self, site, path) -> str:
        path_tree = self.get_path_tree(site)
        if not path_tree.is_type_cpath(path):
            path = path_tree.create_file_cpath(path)
        with path.open('r', encoding='utf-8') as f:
            text = f.read()
        return text

    def get_syd(self, site, path):
        path_tree = self.get_path_tree(site)
        if not path_tree.is_type_cpath(path):
            path = path_tree.create_file_cpath(path)

        syd = self.__cache.get_syd(site, path, default=None)
        if syd is None:
            syd = SydParser(self.get_raw_data(site, path)).parse()
            self.__cache.add_syd(site, path, syd)
        return syd

    def make_syd(self, raw_data):
        syd = SydParser(raw_data).parse()
        return syd

    def get_model(self, site, model_name):
        """Nothing from the system model be overridden - this is opposite of system syd to user settings."""
        types = site.get_service('types')

        model_dir = site.synamic.default_data.get_syd('dirs')['metas.models']
        path_tree = site.get_service('path_tree')
        user_model_cpath = path_tree.create_file_cpath(model_dir, model_name + '.model')

        processed_model = self.__cache.get_model(site, model_name, None)
        if processed_model is None:
            system_model = site.default_data.get_model(model_name, None)
            if system_model is None:
                user_model = ModelParser.parse(model_name, self.get_raw_data(site, user_model_cpath))
                new_model = user_model
            else:
                user_model = ModelParser.parse(model_name, self.get_raw_data(site, user_model_cpath))
                new_model = user_model.new(system_model)
            # put converters inside of the fields
            for key, field in new_model.items():
                converter = types.get_converter(field.converter_name)
                field.set_converter(converter)
            self.__cache.add_model(site, new_model)
            return new_model
        else:
            return processed_model

    def get_content_parts(self, site, content_path):
        text = self.get_raw_data(site, content_path)
        front_matter, body = content_splitter(content_path, text)
        front_matter_syd = self.make_syd(front_matter)  # Or take it from cache.
        return front_matter_syd, body

    def get_path_tree(self, site):
        return site.get_service('path_tree')

    @staticmethod
    def __get_with_x_scheme(url_str):
        url_str = url_str.strip()
        low_url = url_str.lower()
        if '://' in low_url:
            scheme, url_content = url_str.split('://', 1)
        else:
            scheme = None
            url_content = url_str

        if scheme is not None:
            if scheme.lower() not in ('geturl', 'getfields', 'getcontent'):
                ordinary_url = True
            else:
                scheme = scheme.lower()
                ordinary_url = False
        else:
            ordinary_url = True

        return ordinary_url, scheme, url_content

    def getfields(self, site, url_str):
        ordinary_url, scheme, url_content = self.__get_with_x_scheme(url_str)
        if ordinary_url:
            return url_str

        result_fields = None
        fields_for, for_value = url_content.split(':')
        assert fields_for in ('file', 'id')
        if fields_for == 'file':
            file_cpath = site.get_service('path_tree').create_file_cpath(for_value)
            marked_content_fields = self.__cache.get_marked_content_fields_by_cpath(site, file_cpath, None)
            if marked_content_fields is not None:
                result_fields = marked_content_fields

        elif fields_for == 'id':
            for marked_content_fields in self.__cache.get_all_marked_content_fields(site):
                if marked_content_fields.id == for_value:
                    result_fields = marked_content_fields
                    break
        else:  # content
            raise NotImplemented

        if result_fields is None:
            raise Exception('Fields not found for getfields(): %s' % url_str)
        else:
            return result_fields

    def getcontent(self, site, url_str):
        ordinary_url, scheme, url_content = self.__get_with_x_scheme(url_str)
        if ordinary_url:
            return url_str
        result_content = self.get_marked_content(site, self.getfields(site, url_str).get_path_object())
        return result_content

    def geturl(self, site, url_str):
        ordinary_url, scheme, url_content = self.__get_with_x_scheme(url_str)
        if ordinary_url:
            return url_str

        result_url = None
        url_for, for_value = url_content.split(':')
        assert url_for in ('file', 'sass', 'id')
        if url_for == 'file':
            file_cpath = site.get_service('path_tree').create_file_cpath(for_value)
            marked_content_fields = self.__cache.get_marked_content_fields_by_cpath(site, file_cpath, None)
            if marked_content_fields is not None:
                result_url = marked_content_fields.get_url_object()
            else:
                # try STATIC
                result_url = self.static_content_cpath_to_url(site, file_cpath, DocumentType.BINARY_DOCUMENT)
        elif url_for == 'sass':
            # pre-processor stuff. Must be in pre processed content.
            scss_cpath = site.get_service('pre_processor').get_processor('sass').make_cpath(for_value)
            scss_content = self.__cache.get_pre_processed_content_by_cpath(site, scss_cpath, None)
            if scss_content is not None:
                result_url = scss_content.url_object
        elif url_for == 'id':
            for content_fields in self.__cache.get_all_marked_content_fields(site):
                if content_fields.id == for_value:
                    result_url = content_fields.get_url_object()
                    break
        else:  # content
            raise NotImplemented

        if result_url is None:
            raise Exception('URL not found for geturl(): %s' % url_str)
        else:
            return result_url.url_encoded

    def get_site_settings(self, site):
        ss = self.__site_settings.get(site.id, None)
        if ss is None:
            ss = site.get_service('site_settings').make_site_settings()
            self.__site_settings[site.id] = ss
        return ss

    def get_content_by_segments(self, site, path_segments, pagination_segments):
        """Method primarily for router.get()"""
        pass

    def get_marker(self, site, marker_id):
        marker = self.__cache.get_marker(site, marker_id, default=None)
        if marker is None:
            raise Exception('Marker does not exist: %s' % marker_id)
        return marker

    def get_markers(self, site, marker_type):
        assert marker_type in {'single', 'multiple', 'hierarchical'}
        _ = []
        for marker in self.__cache.get_markers(site):
            if marker.type == marker_type:
                _.append(marker)
        return _

    def get_all_cached_marked_fields(self, site):
        # TODO: logic for cached content metas
        # - when to use it when not (when not cached)
        return self.__cache.get_all_marked_content_fields(site)

    def get_marked_cpath_by_curl(self, site, url_object, default=None):
        return self.__cache.get_marked_cpath_by_curl(site, url_object, default=default)

    def get_menu(self, site, menu_name, default=None):
        return self.__cache.get_menu(site, menu_name, default=default)

    @staticmethod
    def __convert_section_values(sections, content_model):
        _ = []
        for section in sections:
            converted_value = content_model[section.id].converter(section.value)
            _.append(
                SimpleQueryParser.Section(id=section.id, op=section.op, value=converted_value, logic=section.logic)
            )
        return _

    def query_fields(self, site, query_str):
        content_model = site.object_manager.get_model('content')
        converted_sections = self.__convert_section_values(SimpleQueryParser(query_str).parse(), content_model)

        all_contents_fields = self.__cache.get_all_marked_content_fields(site)
        result = set(all_contents_fields)

        while converted_sections:
            # &'s first
            and_idx = None
            for and_idx, section in enumerate(converted_sections):
                if section.logic == '&':
                    break
                else:
                    and_idx = None

            # for &
            if and_idx is not None:
                section_left = converted_sections.pop(and_idx)
                section_right = converted_sections.pop(and_idx)  # +1
            # for | or end of sections
            else:
                section_left = converted_sections.pop(0)
                if section_left.logic is not None:
                    section_right = converted_sections.pop(0)  # +1
                else:
                    assert len(converted_sections) == 0
                    section_right = None

            matched_result_left = set()
            matched_result_right = set()

            for matched_result, section, left in ([matched_result_left, section_left, True], [matched_result_right, section_right, False]):
                right = not left
                for content_fields in result:
                    if left or section is not None:
                        field_value = content_fields.get(section.id, None)
                        if field_value is not None:
                            converter = content_model[section.id].converter
                            if converter.compare(section.op, field_value, section.value):
                                matched_result.add(content_fields)
                        # else:
                        #     print(content_model)
                        #     raise Exception("Section field name %s does not exist on fields for: %s" % (section.id, str(content_fields.get_url_object())))
            matched_result = set()
            if section_right is not None:
                if section_left.logic == '|':
                    matched_result.update(matched_result_left)
                    matched_result.update(matched_result_right)
                else:
                    matched_result = matched_result_left.intersection(matched_result_right)
            else:
                matched_result = matched_result_left

            result = matched_result
        return result

    def query_contents(self, site, query_str):
        contents_fields = self.query_fields(site, query_str)
        _ = []
        for content_fields in contents_fields:
            _.append(
                self.get_marked_content(site, content_fields.get_path_object())
            )
        return tuple(_)

    def paginate_contents(self, site, query_str, per_page):
        contents = self.query_contents(site, query_str)
        ...
        ...
        ...

    class __ObjectManagerForSite:
        def __init__(self, site, object_manager):
            self.__site = site
            self.__object_manager = object_manager
            self.__is_loaded = False

        @property
        def is_loaded(self):
            return self.__is_loaded

        @loaded
        def reload(self):
            self.__is_loaded = False
            self.__object_manager._reload_for(self.site)
            self.__is_loaded = True

        @not_loaded
        def load(self):
            self.__object_manager._load_for(self.site)
            self.__is_loaded = True

        @property
        def site(self):
            return self.__site

        def get_content_fields(self, path):
            return self.__object_manager.get_content_fields(self.site, path)

        def get_marked_content(self, path):
            return self.__object_manager.get_marked_content(self.site, path)

        def get_binary_content(self, path):
            return self.__object_manager.get_binary_content(self.site, path)

        def get_static_file_paths(self):
            return self.__object_manager.get_static_file_paths(self.site)

        def all_static_paths(self):
            self.__object_manager.all_static_paths(self.site)

        def empty_syd(self):
            return self.__object_manager.empty_syd()

        def get_raw_data(self, path) -> str:
            return self.__object_manager.get_raw_data(self.site, path)

        def get_syd(self, path):
            return self.__object_manager.get_syd(self.site, path)

        def make_syd(self, raw_data):
            return self.__object_manager.make_syd(raw_data)

        def get_model(self, model_name):
            return self.__object_manager.get_model(self.site, model_name)

        def get_content_parts(self, content_path):
            return self.__object_manager.get_content_parts(self.site, content_path)

        def get_path_tree(self):
            return self.__object_manager.get_path_tree(self.site)

        def geturl(self, url_str):
            return self.__object_manager.geturl(self.site, url_str)

        def get_site_settings(self):
            return self.__object_manager.get_site_settings(self.site)

        def get_content_by_segments(self, path_segments, pagination_segments):
            return self.__object_manager.get_content_by_segments(self.site, path_segments, pagination_segments)

        def get_marker(self, marker_id):
            return self.__object_manager.get_marker(self.site, marker_id)

        def get_markers(self, marker_type):
            return self.__object_manager.get_markers(self.site, marker_type)

        @property
        def get_all_cached_marked_fields(self):
            return self.__object_manager.get_all_cached_marked_fields(self.site)

        def get_marked_cpath_by_curl(self, url_object, default=None):
            return self.__object_manager.get_marked_cpath_by_curl(self.site, url_object, default=None)

        def static_content_cpath_to_url(self, cpath, for_document_type):
            return self.__object_manager.static_content_cpath_to_url(self.site, cpath, for_document_type)

        def make_url_for_marked_content(self, file_cpath, path=None, slug=None, for_document_type=DocumentType.TEXT_DOCUMENT):
            return self.__object_manager.make_url_for_marked_content(self.site, file_cpath, path=path, slug=slug, for_document_type=for_document_type)

        def get_menu(self, menu_name, default=None):
            return self.__object_manager.get_menu(self.site, menu_name, default=default)

        def query_fields(self, query_str):
            return self.__object_manager.query_fields(self.site, query_str)

        def query_contents(self, query_str):
            return self.__object_manager.query_contents(self.site, query_str)

        def get_marked_content_by_url(self, url_object):
            return self.__object_manager.get_marked_content_by_url(self.site, url_object)

        def paginate_contents(self, query_str, per_page):
            return self.__object_manager.paginate_contents(self.site, query_str, per_page)

    class __Cache:
        ContentCacheTuple = namedtuple('ContentCacheTuple', ('type', 'value', 'cpath'))
        TYPE_CONTENT_FIELDS = 'f'
        TYPE_PRE_PROCESSED_CONTENT = 'p'

        def __init__(self, synamic):
            self.__synamic = synamic

            # marker
            self.__marker_by_id_cachemap = defaultdict(dict)
            # syd cachemap
            self.__cpath_to_syd_cachemap = defaultdict(dict)

            # menus
            self.__menus_cachemap = defaultdict(dict)

            # models
            self.__models_cachemap = defaultdict(dict)

            self.__contents_cachemap = defaultdict(dict)
            # key is url object value is a named tuple of
            # ContentCacheTuple

            self.__cpath_to_content_fields = defaultdict(dict)
            self.__cpath_to_pre_processed_contents = defaultdict(dict)

        def __add_content(self, site, value, url_object, path_object, value_type):
            assert url_object not in self.__contents_cachemap[site.id]
            content_cache_tuple = self.ContentCacheTuple(type=value_type, value=value, cpath=path_object)
            self.__contents_cachemap[site.id][url_object] = content_cache_tuple

        def add_pre_processed_content(self, site, pre_processed_content, path_object=None):
            value = pre_processed_content
            url_object = value.url_object
            self.__add_content(site, value, url_object, path_object, self.TYPE_PRE_PROCESSED_CONTENT)
            if path_object is not None:
                self.__cpath_to_pre_processed_contents[site.id][path_object] = pre_processed_content

        def add_marked_content_fields(self, site, content_fields):
            value = content_fields
            url_object = content_fields.get_url_object()
            self.__add_content(site, value, url_object, content_fields.get_path_object(), self.TYPE_CONTENT_FIELDS)
            self.__cpath_to_content_fields[site.id][content_fields.get_path_object()] = content_fields

        def get_marked_value_tuple_by_url(self, site, url_object, default=None):
            return self.__contents_cachemap[site.id].get(url_object, default)

        def get_marked_content_fields_by_url(self, site, url_object, default=None):
            value_tuple = self.get_marked_value_tuple_by_url(site, url_object, default=None)
            if value_tuple is not None:
                if value_tuple.type == self.TYPE_CONTENT_FIELDS:
                    return value_tuple.value
            return default

        def get_marked_cpath_by_curl(self, site, curl, default=None):
            cfs = self.get_marked_content_fields_by_url(site, curl, None)
            if cfs is None:
                return default
            else:
                return cfs.get_path_object()

        def get_all_marked_content_fields(self, site):
            all_fields = []
            for value_tuple in self.__contents_cachemap[site.id].values():
                if value_tuple.type == self.TYPE_CONTENT_FIELDS:
                    all_fields.append(value_tuple.value)
            return tuple(all_fields)

        def get_marked_content_fields_by_cpath(self, site, cpath, default=None):
            return self.__cpath_to_content_fields[site.id].get(cpath, default)

        def get_pre_processed_content_by_cpath(self, site, cpath, default=None):
            pc = self.__cpath_to_pre_processed_contents[site.id].get(cpath, None)
            if pc is None:
                return default
            return pc

        def add_marker(self, site, marker_id, marker):
            self.__marker_by_id_cachemap[site.id][marker_id] = marker

        def get_marker(self, site, marker_id, default=None):
            return self.__marker_by_id_cachemap[site.id].get(marker_id, default)

        def get_markers(self, site):
            return tuple(self.__marker_by_id_cachemap[site.id].values())

        def add_syd(self, site, cpath, syd):
            self.__cpath_to_syd_cachemap[site.id][cpath] = syd

        def get_syd(self, site, cpath, default=None):
            return self.__cpath_to_syd_cachemap[site.id].get(cpath, default)

        def add_menu(self, site, menu_name, menu):
            self.__menus_cachemap[site.id][menu_name] = menu

        def get_menu(self, site, menu_name, default=None):
            menu = self.__menus_cachemap[site.id].get(menu_name, None)
            if menu is None:
                return default
            return menu

        def get_menus(self, site):
            return tuple(self.__menus_cachemap[site.id].values())

        def add_model(self, site, model):
            self.__models_cachemap[site.id][model.model_name] = model
            return model

        def get_model(self, site, model_name, default=None):
            return self.__models_cachemap[site.id].get(model_name, default)

        def clear_content_cache(self, site):
            self.__contents_cachemap[site.id].clear()
            self.__cpath_to_content_fields[site.id].clear()
            self.__cpath_to_pre_processed_contents[site.id].clear()

        def clear_marker_cache(self, site):
            self.__marker_by_id_cachemap[site.id].clear()

        def clear_syd_cache(self, site):
            self.__cpath_to_syd_cachemap[site.id].clear()

        def clear_menus_cache(self, site):
            self.__menus_cachemap[site.id].clear()

        def clear_model(self, site):
            self.__models_cachemap[site.id].clear()

        def clear_cache(self, site):
            """Clear all"""
            self.clear_content_cache(site)
            self.clear_marker_cache(site)
            self.clear_syd_cache(site)
            self.clear_menus_cache(site)
            self.clear_model(site)
