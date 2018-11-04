from collections import defaultdict, OrderedDict, namedtuple
from synamic.core.contracts import DocumentType
from synamic.core.services.content.functions.content_splitter import content_splitter
from synamic.core.parsing_systems.model_parser import ModelParser
from synamic.core.parsing_systems.curlybrace_parser import SydParser
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.contracts import ContentContract, DocumentType


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

    def __cache_marked_content_fields(self, site):
        if site.synamic.env['backend'] == 'file':  # TODO: fix it.
            content_service = site.get_service('contents')
            path_tree = self.get_path_tree(site)
            content_dir = site.synamic.default_configs.get('dirs')['contents.contents']

            # for content
            file_paths = path_tree.list_file_cpaths(content_dir)
            for file_path in file_paths:
                if file_path.extension.lower() in {'md', 'markdown'}:
                    text = self.get_raw_data(site, file_path)
                    front_matter, body = content_splitter(file_path, text)
                    del body
                    fields_syd = self.make_syd(front_matter)
                    content_fields = content_service.build_content_fields(fields_syd, file_path)
                    # TODO: now content id is considered url - what to do with content id?
                    content_id = content_service.make_content_id(file_path)
                    url_object = self.content_fields_to_url(site, content_fields)
                    self.__cache.add_marked_content_fields(site, content_fields, url_object)
                    # self.__marked_content_fields_cachemap[site.id][content_id] = content_fields
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

    def content_fields_to_url(self, site, fields):
        assert site.get_service('contents').is_type_content_fields(fields)
        content_fields = fields
        # TODO: convert permalink to path and slug along with dir based url
        path = content_fields.get('path', None)
        slug = content_fields.get('slug', None)
        permalink = content_fields.get('permalink', None)  # Temporarily keeping it for backward compatibility.
        # TODO: remove it and keep path only
        if permalink is not None:
            path = permalink

        if path is not None:
            #  discard everything and keep it. No processing needed.
            pass
        elif slug is not None:
            # calculate through file system.
            cpath = content_fields.get_content_path()
            cpath_comps = cpath.path_comps
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
            cpath = content_fields.get_content_path()
            cpath_comps = cpath.path_comps
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
            for_document_type=content_fields.get_document_type()
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
            content_id = content_service.make_content_id(path)
            return self.__cache.get_marked_content_fields_by_cpath(site, path, default=default)
            # return self.__marked_content_fields_cachemap[site.id][content_id]

    #  @loaded
    def get_marked_content(self, site, path):
        # create content, meta, set meta with converters. Setting it from here will help caching.
        # TODO: other type of contents besides md contents.
        content_service = site.get_service('contents')
        path_tree = self.get_path_tree(site)
        contents_dir = site.default_configs.get('dirs')['contents.contents']
        if isinstance(path, str):
            file_cpath = path_tree.create_file_cpath(contents_dir + '/' + path)
        else:
            file_cpath = path
        if not file_cpath.exists():
            return None
        md_content = content_service.build_md_content(file_cpath)
        return md_content

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
        statics_dir = site.default_configs.get('dirs')['contents.statics']
        contents_dir = site.default_configs.get('dirs')['contents.contents']
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
        model_dir = site.synamic.default_configs.get('dirs')['metas.models']
        path_tree = site.get_service('path_tree')
        path = path_tree.create_file_cpath(model_dir, model_name + '.model')
        model_text = self.get_raw_data(site, path)
        return ModelParser.parse(model_name, model_text)

    def get_content_parts(self, site, content_path):
        text = self.get_raw_data(site, content_path)
        front_matter, body = content_splitter(content_path, text)
        front_matter_syd = self.make_syd(front_matter)  # Or take it from cache.
        return front_matter_syd, body

    def get_path_tree(self, site):
        path_tree = site.get_service('path_tree')
        return path_tree

    def geturl(self, site, url_str):
        _url_str_bk = url_str
        url_str = url_str.strip()
        low_url = url_str.lower()
        if low_url.startswith('http://') or low_url.startswith('https://') or low_url.startswith('ftp://'):
            return url_str

        if low_url.startswith('geturl://'):
            get_url_content = url_str[len('geturl://'):]
        else:
            get_url_content = url_str

        result_url = None
        url_for, for_value = get_url_content.split(':')
        assert url_for in ('file', 'sass')
        if url_for == 'file':
            file_cpath = site.get_service('path_tree').create_file_cpath(for_value)
            content_id = site.get_service('contents').make_content_id(file_cpath)
            marked_content_fields = self.__cache.get_marked_content_fields_by_cpath(site, file_cpath, None)
            if marked_content_fields is not None:
                result_url = self.content_fields_to_url(site, marked_content_fields)
            else:
                # try STATIC
                result_url = self.static_content_cpath_to_url(site, file_cpath, DocumentType.BINARY_DOCUMENT)
        elif url_for == 'sass':
            # pre-processor stuff. Must be in pre processed content.
            scss_cpath = site.get_service('pre_processor').get_processor('sass').make_cpath(for_value)
            scss_content = self.__cache.get_pre_processed_content_by_cpath(site, scss_cpath, None)
            if scss_content is not None:
                result_url = scss_content.url_object
        else:  # content
            raise NotImplemented

        if result_url is None:
            raise Exception('URL not found for geturl(): %s' % _url_str_bk)
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

        def content_fields_to_url(self, fields):
            return self.__object_manager.content_fields_to_url(self.site, fields)

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

        def add_marked_content_fields(self, site, content_fields, url_object):
            value = content_fields
            self.__add_content(site, value, url_object, content_fields.get_content_path(), self.TYPE_CONTENT_FIELDS)
            self.__cpath_to_content_fields[site.id][content_fields.get_content_path()] = content_fields

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
                return cfs.get_content_path()

        def get_all_marked_content_fields(self, site):
            all_fields = []
            for value_tuple in self.__contents_cachemap[site.id]:
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

        def clear_content_cache(self, site):
            self.__contents_cachemap[site.id].clear()
            self.__cpath_to_content_fields[site.id].clear()
            self.__cpath_to_pre_processed_contents[site.id].clear()

        def clear_marker_cache(self, site):
            self.__marker_by_id_cachemap[site.id].clear()

        def clear_syd_cache(self, site):
            self.__cpath_to_syd_cachemap[site.id].clear()

        def clear_cache(self, site):
            """Clear all"""
            self.clear_content_cache(site)
            self.clear_marker_cache(site)
            self.clear_syd_cache(site)
