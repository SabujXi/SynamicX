import types
from collections import defaultdict, OrderedDict
from synamic.core.services.content.content_splitter import content_splitter
from synamic.core.parsing_systems.model_parser import ModelParser
from synamic.core.parsing_systems.curlybrace_parser import SydParser
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.contracts import CDocType
from .query import QueryNode, SimpleQueryParser
from synamic.core.parsing_systems.getc_parser import parse_getc
from synamic.core.standalones.functions.sequence_ops import Sequence
from synamic.exceptions import (
    SynamicGetCParsingError,
    SynamicGetCError,
    SynamicMarkNotFound,
    SynamicMarkerNotFound,
    SynamicSydParseError,
    SynamicErrors,
    SynamicFSError,
    SynamicSiteNotFound,
    SynamicUserNotFound
)
from synamic import Nil


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

    def __reload_for__(self, site):
        self.__cache.clear_cache(site)
        self.__load_for__(site)

    def __load_for__(self, site):
        self.__cache_markers(site)
        self.__cache_users(site)
        self.__cache_marked_cfields(site)
        self.__cache_menus(site)
        self.__cache_data(site)
        self.__cache_pre_processed_contents(site)

    def __cache_marked_cfields(self, site):
        marked_extensions = site.system_settings['configs.marked_extensions']
        if site.synamic.env['backend'] == 'file':  # TODO: fix it.
            content_service = site.get_service('contents')
            path_tree = self.get_path_tree(site)
            content_dir = site.synamic.system_settings['dirs.contents.contents']
            content_cdir = path_tree.create_dir_cpath(content_dir)
            # for content
            if content_cdir.exists():  # check content dir existence before proceeding
                file_cpaths = content_cdir.list_files()
                for file_cpath in file_cpaths:
                    if file_cpath.extension.lower() in marked_extensions:
                        text = self.get_raw_text_data(site, file_cpath)
                        front_matter, body = content_splitter(file_cpath, text)
                        del body
                        try:
                            fields_syd = self.make_syd(front_matter)
                        except SynamicSydParseError as e:
                            raise SynamicErrors(
                                f'Synamic Syd parsing error during parsing front matter of file: '
                                f'{file_cpath.relative_path}\n'
                                f'<This error occurred during caching the cfileds of marked contents>',
                                e
                            )
                        cfields = content_service.build_cfields(fields_syd, file_cpath)
                        self.__cache.add_marked_cfields(site, cfields)
                    else:
                        # No need to cache anything about static file.
                        pass
        else:
            raise NotImplemented
            # database backend is not implemented yet. AND there is nothing to do here for db, skip it when implemented

    def __cache_users(self, site):
        user_service = site.get_service('users')
        user_ids = user_service.get_user_ids()
        for user_id in user_ids:
            user = user_service.make_user(user_id)
            self.__cache.add_user(site, user)

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

        # TODO: keep sitemap here forever? IT will not make the system happy... it should be created before byproduct
        # ...or even after.
        # TODO: also, provide some mechanism to add content to sitemap dynamically.
        # TODO: so this is not the place for sitemap.
        sitemap_service = site.get_service('sitemap')
        sitemap_content = sitemap_service.make_sitemap(self.query_cfields(site, ':sortby updated_on desc'))
        self.__cache.add_pre_processed_content(site, sitemap_content)

    def __cache_menus(self, site):
        menu_service = site.get_service('menus')
        menu_names = menu_service.get_menu_names()
        for menu_name in menu_names:
            menu = menu_service.make_menu(menu_name)
            self.__cache.add_menu(site, menu_name, menu)

    def __cache_data(self, site):
        data_service = site.get_service('data')
        data_names = data_service.get_data_names()
        for data_name in data_names:
            data_instance = data_service.make_data(data_name)
            self.__cache.add_data(site, data_instance)

    def make_url_for_marked_content(self, site, file_cpath, path=None, slug=None, for_cdoctype=CDocType.TEXT_DOCUMENT):
        nourl_content_dirs_sw = self.get_site_settings(site)['configs.nourl_content_dirs_sw']
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
                if not ccomp.startswith(nourl_content_dirs_sw):
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
                if not ccomp.startswith(nourl_content_dirs_sw):
                    _.append(ccomp)

            cpath_comps = _
            cpath_comps.append(basename)
            path = cpath_comps

        url_path_comps = path
        curl = self.__synamic.router.make_url(
            site,
            url_path_comps,
            for_cdoctype=for_cdoctype
        )
        return curl

    def static_content_cpath_to_url(self, site, cpath, for_cdoctype):
        assert CDocType.is_binary(for_cdoctype, not_generated=True)
        # For STATIC Files
        contents_dir = site.system_settings['dirs.contents.contents']
        contents_cdir = site.path_tree.create_dir_cpath(contents_dir)
        basename_contents = contents_cdir.basename
        url_comps = cpath.path_comps
        url_comps = Sequence.lstrip(url_comps, (basename_contents,))
        curl = self.__synamic.router.make_url(
            site,
            url_comps,
            for_cdoctype=for_cdoctype
        )
        return curl

    #  @loaded
    def get_cfields(self, site, path, default=None):
        path_tree = site.get_service('path_tree')
        path = path_tree.create_cpath(path)
        if site.synamic.env['backend'] == 'database':
            raise NotImplemented
        else:
            # file backend
            return self.__cache.get_marked_cfields_by_cpath(site, path, default=default)

    #  @loaded
    def get_marked_content(self, site, path):
        # create content, meta, set meta with converters. Setting it from here will help caching.
        # TODO: other type of contents besides md contents.
        content_service = site.get_service('contents')
        if isinstance(path, str):
            path_tree = self.get_path_tree(site)
            contents_cdir = path_tree.create_dir_cpath(site.system_settings['dirs.contents.contents'])
            file_cpath = contents_cdir.join(path, is_file=True)
        else:
            file_cpath = path

        # check cache
        marked_content = self.__cache.get_marked_content_by_cpath(site, file_cpath, None)
        if marked_content is not None:
            return marked_content

        if not file_cpath.exists():
            return None
        else:
            cached_cfields = self.__cache.get_marked_cfields_by_cpath(site, file_cpath)
            assert cached_cfields is not None
            marked_content = content_service.build_md_content(file_cpath, cached_cfields)
            # cache it.
            self.__cache.add_marked_content(site, marked_content)
            return marked_content

    def get_marked_content_by_curl(self, site, curl):
        cpath = self.__cache.get_marked_cpath_by_curl(site, curl)
        if cpath is None:
            return None
        return self.get_marked_content(site, cpath)

    def get_pre_processed_content_by_curl(self, site, curl):
        return self.__cache.get_pre_processed_content_by_curl(site, curl, None)

    def get_marked_contents_by_cpaths(self, site, cpaths):
        contents = []
        for cpath in cpaths:
            contents.append(self.get_marked_content(site, cpath))
        return contents

    def get_binary_content(self, site, path):
        path_tree = site.get_service('path_tree')
        if not path_tree.exists(path):
            return None
        else:
            content_service = site.get_service('contents')
            return content_service.build_static_content(path)

    def get_static_file_cpaths(self, site):
        marked_extensions = site.system_settings['configs.marked_extensions']
        paths = []
        path_tree = site.get_service('path_tree')
        contents_dir = site.system_settings['dirs.contents.contents']
        contents_cdir = path_tree.create_dir_cpath(contents_dir)

        if contents_cdir.exists():
            for path in contents_cdir.list_files(checker=lambda cp: cp.extension not in marked_extensions):
                paths.append(path)
        return paths

    @staticmethod
    def empty_syd():
        return SydParser('').parse()

    def get_raw_text_data(self, site, path, encoding='utf-8') -> str:
        path_tree = self.get_path_tree(site)
        if not path_tree.is_type_cpath(path):
            path = path_tree.create_file_cpath(path)
        with path.open('r', encoding=encoding) as f:
            text = f.read()
        return text

    def get_syd(self, site, path):
        path_tree = site.path_tree
        if not path_tree.is_type_cpath(path):
            cpath = path_tree.create_file_cpath(path)
        else:
            cpath = path
        syd = self.__cache.get_syd(site, cpath, default=None)
        if syd is None and cpath.exists():
            try:
                syd = SydParser(self.get_raw_text_data(site, cpath)).parse()
            except (SynamicSydParseError, SynamicFSError) as e:
                raise SynamicErrors(
                    f'Synamic error during parsing syd file: '
                    f'{cpath.relative_path}',
                    e
                )
            self.__cache.add_syd(site, cpath, syd)
        return syd

    @staticmethod
    def make_syd(raw_data):
        syd = SydParser(raw_data).parse()
        return syd

    def get_model(self, site, model_name):
        """Nothing from the system model be overridden - this is opposite of system syd to user settings."""
        processed_model = self.__cache.get_model(site, model_name, None)
        if processed_model is None:
            types = site.get_service('types')

            model_dir = site.synamic.system_settings['dirs.metas.models']
            path_tree = site.get_service('path_tree')
            user_model_cpath = path_tree.create_file_cpath(model_dir, model_name + '.model')

            if user_model_cpath.exists():
                user_model = ModelParser.parse(model_name, self.get_raw_text_data(site, user_model_cpath))
            else:
                user_model = None

            system_model = site.default_data.get_model(model_name, None)
            if system_model is None and processed_model is None:
                return None
            elif system_model is not None and user_model is not None:
                new_model = user_model.new(system_model)
            elif system_model is None:
                new_model = user_model
            else:
                new_model = system_model
            # put converters inside of the cfields
            for key, field in new_model.items():
                converter = types.get_converter(field.converter_name)
                field.set_converter(converter)
            self.__cache.add_model(site, new_model)
            return new_model
        else:
            return processed_model

    def get_content_parts(self, site, content_path):
        text = self.get_raw_text_data(site, content_path)
        front_matter, body = content_splitter(content_path, text)
        front_matter_syd = self.make_syd(front_matter)  # Or take it from cache.
        return front_matter_syd, body

    def get_path_tree(self, site):
        return site.get_service('path_tree')

    def get_curl_by_filename(self, site, filename, relative_cpath=None, default=None):
        if relative_cpath is None:
            cpath = site.path_tree.create_file_cpath(filename, forgiving=True)
        else:
            if filename.startswith(('/', '\\')):
                cpath = site.path_tree.create_file_cpath(filename, forgiving=True)
            else:
                cpath = relative_cpath.parent_cpath.join(filename, is_file=True, forgiving=True)
        if not cpath.exists():
            return default
        content = self.__cache.get_marked_content_by_cpath(site, cpath, default=None)
        if content is None:
            pre_content = self.__cache.get_pre_processed_content_by_cpath(site, cpath, default=None)
        else:
            return content.curl
        if pre_content is None:
            static_content = site.get_service('contents').build_static_content(cpath)
            return static_content.curl

    def getc(self, site, url_str, relative_cpath=None):
        """
        For: curl:// url:// cfields:// content:// etc.
        """
        url_struct = parse_getc(url_str)
        result = None
        if url_struct.scheme in ('cfields', 'curl', 'geturl', 'url', 'content', 'cpath'):
            if not url_struct.keys:
                raise SynamicGetCParsingError(f'Malformated getc param: {url_str}')
            key = url_struct.keys[0]  # TODO: add support for more chained keys later.
            path = url_struct.path
            assert key is not None and path is not None

            # find the proper site
            site_id_sep = self.__synamic.system_settings['configs.site_id_sep']
            site_id = url_struct.site_id

            if site_id == site_id_sep:
                site = site
                c_res = self.__getc(site, key, path, None)
            elif site_id is not None:
                site_id_obj = self.__synamic.sites.make_id(site_id)
                try:
                    site = self.__synamic.sites.get_by_id(site_id_obj)
                except KeyError:
                    raise SynamicSiteNotFound(
                        f'Site with id {site_id} was not found when looking for it in getc() for {url_str} and relative'
                        f' path {relative_cpath}'
                    )
                c_res = self.__getc(site, key, path, None)
            else:
                c_res = None
                sites_up = self.sites_up(site, url_struct.site_id)[0]
                for specific_site in sites_up:
                    c_res = self.__getc(specific_site, key, path, None)
                    if c_res is not None:
                        site = specific_site
                        break

            if c_res is not None:
                if url_struct.scheme == 'cfields':
                    result = c_res['cfields']
                elif url_struct.scheme == 'curl':
                    result = c_res['cfields'].curl
                elif url_struct.scheme in ('url', 'geturl'):
                    result = c_res['cfields'].curl.url
                elif url_struct.scheme == 'cpath':
                    result = c_res['cfields'].cpath
                elif url_struct.scheme == 'content':
                    static_content = c_res.get('static_content', None)
                    scss_content = c_res.get('scss_content', None)  # CAUTION: sCss vs sAss
                    if static_content is not None:
                        result = static_content
                    elif scss_content is not None:
                        result = static_content
                    else:
                        # marked cfields
                        marked_cfields = c_res.get('marked_cfields', None)
                        if marked_cfields is not None:
                            result = self.get_marked_content(site, marked_cfields.cpath)
        else:
            if not url_struct.scheme:
                curl = self.get_curl_by_filename(site, url_str, relative_cpath=relative_cpath)
                if curl:
                    url_str = curl.url
            return url_str
        if result is not None:
            return result
        else:
            raise SynamicGetCError(f"Not found for getc ->  {url_str}")

    def __getc(self, specific_site, key, path, default=None):
        content_service = specific_site.get_service('contents')
        getc_key, getc_path = key, path

        contents_cdir = specific_site.path_tree.create_dir_cpath(
            specific_site.system_settings['dirs.contents.contents']
        )

        result_cfields = default
        if getc_key not in ('file', 'sass', 'id'):
            raise SynamicGetCError(
                f'GetC key error. Currently only file, sass, id keys are allowed, but key {getc_key} was provided'
            )
        if getc_key == 'file':
            file_cpath = contents_cdir.join(getc_path, is_file=True)
            if file_cpath.exists():
                marked_cfields = self.__cache.get_marked_cfields_by_cpath(
                    specific_site, file_cpath, None
                )
                if marked_cfields is not None:
                    result_cfields = {
                        'cfields': marked_cfields,
                        'marked_cfields': marked_cfields
                    }
                else:
                    # try STATIC
                    static_content = content_service.build_static_content(file_cpath)
                    result_cfields = {
                        'cfields': static_content.cfields,
                        'static_content': static_content
                    }
        elif getc_key == 'sass':
            # pre-processor stuff. Must be in pre processed content.
            scss_cpath = specific_site.get_service('pre_processor').get_processor('sass').make_cpath(getc_path)
            scss_content = self.__cache.get_pre_processed_content_by_cpath(specific_site, scss_cpath, None)
            if scss_content is not None:
                result_cfields = {
                    'cfields': scss_content.cfields,
                    'scss_content': scss_content  # CAREFUL: sCss vs sAss
                }
        elif getc_key == 'id':
            for cfields in self.__cache.get_all_marked_cfields(specific_site):
                if cfields.id == getc_path:
                    result_cfields = {
                        'cfields': cfields,
                        'marked_cfields': cfields
                    }
                    break
        return result_cfields

    def get_site_settings(self, site):
        ss = self.__site_settings.get(site.id, None)
        if ss is None:
            ss = site.get_service('site_settings').make_site_settings()
            self.__site_settings[site.id] = ss
        return ss

    def get_content_by_segments(self, site, path_segments, pagination_segments):
        """Method primarily for router.get()"""
        pass

    def get_marker(self, site, marker_id, default=None, error_out=False):
        marker = self.__cache.get_marker(site, marker_id, default=None)
        if marker is None and error_out:
            raise SynamicMarkerNotFound(f'Marker does not exist: {marker_id}')
        else:
            if marker is None:
                return default
            else:
                return marker

    def get_marker_by_slug(self, site, slug, default=None):
        markers = self.get_markers(site)
        for marker in markers:
            if marker.get('slug', default=None) == slug:
                return marker
        return default

    def get_markers_by_type(self, site, marker_type):
        allowed_marker_types = {'single', 'multiple', 'hierarchical'}
        if marker_type not in allowed_marker_types:
            raise SynamicMarkerNotFound(
                f'Marker of type {marker_type} is not allowed. Only allowed markers are'
                f' {", ".join(allowed_marker_types)}'
            )
        _ = []
        for marker in self.__cache.get_markers(site):
            if marker.type == marker_type:
                _.append(marker)
        return _

    def get_markers(self, site):
        return self.__cache.get_markers(site)

    def get_all_cached_marked_cfields(self, site):
        # TODO: logic for cached content metas
        # - when to use it when not (when not cached)
        return self.__cache.get_all_marked_cfields(site)

    def get_all_pre_processed_contents(self, site):
        return self.__cache.get_all_pre_processed_content(site)

    def get_marked_cpath_by_curl(self, site, curl, default=None):
        return self.__cache.get_marked_cpath_by_curl(site, curl, default=default)

    def get_menu(self, site, menu_name, default=None):
        return self.__cache.get_menu(site, menu_name, default=default)

    def get_menus(self, site):
        return self.__cache.get_menus(site)

    def get_data(self, site, data_name, default=None):
        return self.__cache.get_data(site, data_name, default=default)

    @staticmethod
    def __convert_section_value(section, content_model):
        # TODO: for converter that returns single value implement mechanism that will help use in !in for them.
        converted_value = content_model[section.key].converter(section.value)
        return SimpleQueryParser.QuerySection(key=section.key, comp_op=section.comp_op, value=converted_value)

    def __query_cfields_left_right(self, section, result_set, content_model):
        matched_result = set()
        for cfields in result_set:
            field_value = cfields.get(section.key, None)
            converter = content_model[section.key].converter
            if field_value is not None:
                if converter.compare(section.comp_op, field_value, section.value):
                    matched_result.add(cfields)
            else:
                if section.comp_op in ('!=', '!in'):
                    matched_result.add(cfields)
        return matched_result

    def __query_cfields_by_node(self, node, result_set, content_model):
        if isinstance(node, SimpleQueryParser.QuerySection):
            # only one section here.
            left_section = node
            right_section = None
            logic_op = None
        else:
            assert isinstance(node, QueryNode)
            logic_op = node.logic_op
            if isinstance(node.left, QueryNode):
                return self.__query_cfields_by_node(node.left, result_set, content_model)
            else:
                left_section = node.left
                right_section = None

            if isinstance(node.right, QueryNode):
                return self.__query_cfields_by_node(node.left, result_set, content_model)
            else:
                right_section = node.right

        left_section = self.__convert_section_value(left_section, content_model)
        left_result = self.__query_cfields_left_right(left_section, result_set, content_model)
        if right_section is not None:
            right_section = self.__convert_section_value(right_section, content_model)
            right_result = self.__query_cfields_left_right(right_section, result_set, content_model)
        else:
            right_result = None

        if logic_op == '|':
            left_result.update(right_result)
        elif logic_op == '&':
            left_result.intersection_update(right_result)
        else:
            # keep as is
            pass
        result_set.clear()
        result_set.update(left_result)
        return result_set

    def query_cfields(self, site, query_str):
        content_model = site.object_manager.get_model('content')
        node, sort = SimpleQueryParser(query_str).parse()
        all_cfields_s = self.__cache.get_all_marked_cfields(site)
        result = set(all_cfields_s)
        if node is not None:
            self.__query_cfields_by_node(node, result, content_model)
        if sort is not None:
            def sorting_key_func(f):
                value = f[sort.by_key]
                if value is None:
                    value = Nil
                return value
            result = sorted(
                result,
                key=sorting_key_func,
                reverse=True if sort.order == 'desc' else False
            )

        return tuple(result)

    def query_contents(self, site, query_str):
        cfields_s = self.query_cfields(site, query_str)
        _ = []
        for cfields in cfields_s:
            _.append(
                self.get_marked_content(site, cfields.cpath)
            )
        return tuple(_)

    def get_user(self, starting_site, user_id):
        user = None
        sites_up, user_id = self.sites_up(starting_site, user_id)
        for site in sites_up:
            user = self.__cache.get_user(site, user_id, None)
            if user is not None:
                break
        if user is None:
            raise SynamicUserNotFound(
                f'User with user id {user_id} not found in the {starting_site} site, neither in the '
                f'upper hierarchy.'
            )
        return user

    def get_users(self, site):
        return self.__cache.get_users(site)

    def sites_up(self, starting_site, site_id):
        """All sites up to the root including the current one"""
        sites_up = []
        site = starting_site
        while True:
            sites_up.append(site)
            if site.has_parent:
                site = site.parent
            else:
                break
        return sites_up, site_id

    class __ObjectManagerForSite:
        def __init__(self, site, object_manager):
            self.__site = site
            self.__object_manager = object_manager
            self.__is_loaded = False

            # real object manager methods.
            self.__cached_om_methods = {}

        def __getattr__(self, key):
            res = self.__cached_om_methods.get(key, None)
            if res is None:
                attr = getattr(self.__object_manager, key)
                if not isinstance(attr, types.MethodType):  # or key.startswith('_')
                    res = attr
                else:
                    om_method = attr

                    def call_om_method(*args, **kwargs):
                        return om_method(self.__site, *args, **kwargs)
                    self.__cached_om_methods[key] = call_om_method
                    res = call_om_method
            return res

        @property
        def is_loaded(self):
            return self.__is_loaded

        @loaded
        def reload(self):
            self.__is_loaded = False
            self.__object_manager.__reload_for__(self.site)
            self.__is_loaded = True

        @not_loaded
        def load(self):
            self.__object_manager.__load_for__(self.site)
            self.__is_loaded = True

        @property
        def site(self):
            return self.__site

    class __Cache:
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

            # users
            self.__users_cachemap = defaultdict(dict)

            # data
            self.__data = defaultdict(dict)

            # >>>>>>>>
            # CONTENTS
            self.__pre_processed_cachemap = defaultdict(dict)  # curl to content
            self.__marked_contents_cachemap = defaultdict(dict)  # curl to content: default limit 100 per site. < limit not yet implemented
            self.__marked_cfields_cachemap = defaultdict(dict)  # curl to content

            self.__cpath_to_pre_processed_contents = defaultdict(dict)
            self.__cpath_to_marked_content = defaultdict(dict)
            self.__cpath_to_marked_cfields = defaultdict(dict)
            # <<<<<<<<

        def add_pre_processed_content(self, site, pre_processed_content, cpath=None):
            """Pre processed content is one kind of generated content, sor we cannot rely on source-cpath and thus cpath
            parameter is needed explicitly"""
            self.__pre_processed_cachemap[site.id][pre_processed_content.curl] = pre_processed_content
            if cpath is not None:
                self.__cpath_to_pre_processed_contents[site.id][cpath] = pre_processed_content

        def get_pre_processed_content_by_curl(self, site, curl, default=None):
            res = self.__pre_processed_cachemap[site.id].get(curl, default)
            return res

        def get_pre_processed_content_by_cpath(self, site, cpath, default=None):
            res = self.__cpath_to_pre_processed_contents[site.id].get(cpath, default)
            return res

        def get_all_pre_processed_content(self, site):
            return tuple(self.__pre_processed_cachemap[site.id].values())

        def add_marked_content(self, site, marked_content):
            # TODO: set limit to 100 or so
            self.__marked_contents_cachemap[site.id][marked_content.curl] = marked_content
            self.__cpath_to_marked_content[site.id][marked_content.cpath] = marked_content

        def get_marked_content_by_curl(self, site, curl, default=None):
            return self.__marked_contents_cachemap[site.id].get(curl, default)

        def get_marked_content_by_cpath(self, site, cpath, default=None):
            return self.__cpath_to_marked_content[site.id].get(cpath, default)

        def add_marked_cfields(self, site, cfields):
            self.__marked_cfields_cachemap[site.id][cfields.curl] = cfields
            self.__cpath_to_marked_cfields[site.id][cfields.cpath] = cfields

        def get_marked_cfields_by_curl(self, site, curl, default=None):
            return self.__marked_cfields_cachemap[site.id].get(curl, default)

        def get_marked_cfields_by_cpath(self, site, cpath, default=None):
            return self.__cpath_to_marked_cfields[site.id].get(cpath, default)

        def get_marked_cpath_by_curl(self, site, curl, default=None):
            cfs = self.get_marked_cfields_by_curl(site, curl, None)
            if cfs is None:
                return default
            else:
                return cfs.cpath

        def get_all_marked_cfields(self, site):
            return tuple(self.__marked_cfields_cachemap[site.id].values())

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

        def add_user(self, site, user):
            self.__users_cachemap[site.id][user.id] = user

        def get_user(self, site, user_id, default=None):
            return self.__users_cachemap[site.id].get(user_id, default)

        def get_users(self, site):
            return tuple(self.__users_cachemap[site.id].values())

        def add_data(self, site, data):
            self.__data[site.id][data.get_data_name()] = data

        def get_data(self, site, data_name, default=None):
            return self.__data[site.id].get(data_name, default=default)

        def clear_content_cache(self, site):
            self.__pre_processed_cachemap[site.id].clear()
            self.__marked_contents_cachemap[site.id].clear()
            self.__marked_cfields_cachemap[site.id].clear()
            self.__cpath_to_pre_processed_contents[site.id].clear()
            self.__cpath_to_marked_content[site.id].clear()
            self.__cpath_to_marked_cfields[site.id].clear()

        def clear_marker_cache(self, site):
            self.__marker_by_id_cachemap[site.id].clear()

        def clear_syd_cache(self, site):
            self.__cpath_to_syd_cachemap[site.id].clear()

        def clear_menus_cache(self, site):
            self.__menus_cachemap[site.id].clear()

        def clear_model(self, site):
            self.__models_cachemap[site.id].clear()

        def clear_users(self, site):
            self.__users_cachemap[site.id].clear()

        def clear_data(self, site):
            self.__data[site.id].clear()

        def clear_cache(self, site):
            """Clear all"""
            self.clear_content_cache(site)
            self.clear_marker_cache(site)
            self.clear_syd_cache(site)
            self.clear_menus_cache(site)
            self.clear_model(site)
            self.clear_users(site)
            self.clear_data(site)

    def build(self, site):
        output_dir = self.__synamic.system_settings['dirs.outputs.outputs']
        output_cdir = self.__synamic.path_tree.create_dir_cpath(output_dir)

        c_iter = CIter(site)
        for content in c_iter:
            curl = content.curl
            print(f'Writing {curl.url}')
            with content.get_stream() as fr:
                c_out_dir, fn = curl.to_dirfn_pair_w_site
                c_out_cdir = output_cdir.join(c_out_dir, is_file=False)
                if not c_out_cdir.exists():
                    c_out_cdir.makedirs()
                c_out_cfile = c_out_cdir.join(fn, is_file=True)
                with c_out_cfile.open('wb') as fw:
                    data = fr.read(1024)
                    while data:
                        fw.write(data)
                        data = fr.read(1024)
        return True


class CIter:
    def __init__(self, site):
        self.__site = site

    def __make_clist(self):
        content_service = self.__site.get_service('contents')
        # marked
        clist = []

        all_cfields = self.__site.object_manager.get_all_cached_marked_cfields()
        all_pre_content = self.__site.object_manager.get_all_pre_processed_contents()
        all_static_cpaths = self.__site.object_manager.get_static_file_cpaths()
        all_users = self.__site.object_manager.get_users()
        all_marks = []

        for marker in self.__site.object_manager.get_markers():
            if not marker.is_public:
                continue
            marks = marker.marks
            for mark in marks:
                all_marks.append(mark.content)

        clist.extend(all_cfields)
        clist.extend(all_pre_content)
        clist.extend(all_static_cpaths)
        clist.extend(all_users)
        clist.extend(all_marks)

        # pagination pages
        pagination_pages = []
        for cfields in all_cfields:
            root_pagination = cfields.pagination
            if content_service.is_type_pagination_page(root_pagination):
                for page_no in range(1, root_pagination.total_pagination):
                    sub_page = root_pagination.get_sub_page(page_no)
                    assert content_service.is_type_pagination_page(sub_page), f'Type: {type(sub_page)}'
                    pagination_pages.append(sub_page)
        clist.extend(pagination_pages)
        return clist

    def __iter__(self):
        return self.__CListIterator(self.__make_clist(), self.__site)

    class __CListIterator:
        def __init__(self, clist, site):
            self.__clist = clist
            self.__idx = 0
            self.__site = site

            self.__content_service = self.__site.get_service('contents')
            self.__markers_service = self.__site.get_service('markers')
            self.__users_service = self.__site.get_service('users')
            self.__path_tree = self.__site.path_tree

        def __next__(self):
            if self.__idx >= len(self.__clist):
                del self.__clist
                del self.__site
                del self.__content_service
                del self.__markers_service
                del self.__users_service
                del self.__path_tree
                raise StopIteration

            elem = self.__clist[self.__idx]
            self.__idx += 1

            # marked content
            if self.__content_service.is_type_cfields(elem):
                cfields = elem
                content = self.__site.object_manager.get_marked_content(cfields.cpath)

            elif self.__content_service.is_type_generated_content(elem):
                content = elem

            # static content
            elif self.__path_tree.is_type_cpath(elem):
                cpath = elem
                content = self.__content_service.build_static_content(cpath)

            # user
            elif self.__users_service.is_type_user(elem):
                user = elem
                content = user.content

            # mark
            elif self.__markers_service.is_type_mark(elem):
                mark = elem
                content = mark.content

            # pagination pages
            elif self.__content_service.is_type_pagination_page(elem):
                pagination_page = elem
                content = pagination_page.host_content

            else:
                raise Exception(f'Something impossible happened or you introduced a bug.')

            return content
