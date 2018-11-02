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
import urllib.parse
from typing import Union
from synamic.core.contracts import DocumentType


class ContentUrl:
    @classmethod
    def path_to_components(cls, *url_path_comps: Union[str, list, tuple]) -> tuple:
        res_url_path_comps = []
        for _comps in url_path_comps:
            if isinstance(_comps, str):
                for url_comp in re.split(r'[\\/]+', _comps):
                    res_url_path_comps.append(url_comp)

            elif isinstance(_comps, (list, tuple)):
                for url_comp in _comps:
                    assert isinstance(url_comp, str)
                    res_url_path_comps.extend(
                        cls.path_to_components(url_comp)
                    )
            else:
                raise Exception('Invalid argument for url component: %s' % str(url_path_comps))

        # ../../../ recalculation and empty string removing from middle
        _ = []
        for idx, comp in enumerate(res_url_path_comps):
            if comp == '.':
                # just ignore it
                continue
            elif comp == '..' and idx != 0:
                #  delete the last comp and add current one (replace the last one)
                _[-1] = comp
            elif not (idx == 0 or idx == len(res_url_path_comps) - 1):  # sparing the first and last empty string only
                if comp == '':
                    pass  # ignore
            else:
                _.append(comp)
        res_url_path_comps = _

        # re-adding empty string for zero length comps
        if len(res_url_path_comps) == 0:
            res_url_path_comps.append('')

        # validating
        for idx, url_comp in enumerate(res_url_path_comps):
            assert not re.match(r'^\s+$', url_comp), "A component of an url cannot be one or all whitespaces"

        # ['', ''] issue
        if list(res_url_path_comps) == ['', '']:  # eg ['', ''] == '/'.split('/')
            res_url_path_comps = ['']
        # comps should begin with empty string ... we can only handle site root absolute url as there is no context for
        # relative url in this function.
        if res_url_path_comps[0] != '':
            res_url_path_comps.insert(0, '')
        return tuple(res_url_path_comps)

    def __init__(self, site, url_path_comps, for_document_type=None):
        """
        append_slash is only for dynamic contents and only when the url_path_comps is being passed as sting (not: list, tuple, content path)
        So, we are not persisting that data
        
        'index.html' in lower case is special throughout the url system - see the codes for extracting more info.
        
        if we indicate ...
        """
        self.__url_path_comps = self.path_to_components(
            url_path_comps
        )

        self.__site = site
        self.__for_document_type = for_document_type
        # TODO: fix this
        # assert type(self.__for_document_type) is DocumentType
        # assert DocumentType.is_text(self.__for_document_type) or DocumentType.is_binary(self.__for_document_type) or\
        #     self.__for_document_type == DocumentType.DIRECTORY
        self.__path_str = None
        self.__path_components_w_site = None
        self.__url_str = None

    @property
    def for_site(self):
        return self.__site

    @property
    def for_document_type(self):
        return self.__for_document_type

    def join(self, url_comps: Union[str, list, tuple], for_document_type=None):
        this_comps = self.__url_path_comps
        other_comps = self.path_to_components(url_comps)

        this_end = this_comps[-1]
        other_start = other_comps[0]

        if this_end != '' and other_start != '':
            comps = this_comps[:-1] + (this_end + other_start,) + other_comps[1:]
        elif this_end == '' or other_start == '':
            if this_end == '' and other_start == '':
                res_comp = ''
            elif this_end == '':
                res_comp = other_start
            else:
                assert other_start == ''
                res_comp = this_end
            comps = this_comps[:-1] + (res_comp,) + other_comps[1:]
        else:
            comps = this_comps + other_comps
        if for_document_type is None:
            for_document_type = self.__for_document_type
        return self.__class__(self.__site, comps, for_document_type)

    @property
    def path_components(self):
        return self.__url_path_comps

    @property
    def path_components_w_site(self):
        if self.__path_components_w_site is None:
            host_base_path = self.__site.object_manager.get_site_settings()['host_base_path']
            self.__path_components_w_site = self.path_to_components(
                host_base_path, self.__site.id.components, self.__url_path_comps
            )
        return self.__path_components_w_site

    @property
    def path_as_str(self):
        if self.__path_str is None:
            comps = self.path_components_w_site
            if comps == ('', ):
                path_str = '/'
            else:
                path_str = '/'.join(comps)
            self.__path_str = path_str
        return self.__path_str

    @property
    def path_as_str_encoded(self):
        return urllib.parse.quote_plus(self.path_as_str, safe='/', encoding='utf-8')

    @property
    def url(self):
        """URL with host name, port, path"""
        if self.__url_str is None:
            ss = self.__site.object_manager.get_site_settings()
            host_scheme = ss['host_scheme']
            hostname = ss['hostname']
            port = ss['port']
            if port:
                port_part = ':' + port
            else:
                port_part = ''
            _ = host_scheme + '://' + hostname + port_part + self.path_as_str
            self.__url_str = _
        return self.__url_str

    @property
    def url_encoded(self):
        return urllib.parse.quote_plus(self.url, safe='/', encoding='utf-8')

    @property
    def to_file_system_path(self):
        p = self.path_as_str
        if DocumentType.is_html(self.__for_document_type):
            index_file_name = self.__site.object_manager.get_site_settings()['index_file_name']
            if p.endswith('/'):
                p += index_file_name
            else:
                p += '/' + index_file_name
        else:
            # validation
            assert not p.endswith('/')
        return p

    @property
    def is_file(self):
        return DocumentType.is_file(self.__for_document_type)

    @property
    def to_cpath(self):
        return self.__site.path_tree.create_cpath(
            self.to_file_system_path,
            is_file=self.is_file
        )

    def __str__(self):
        return self.path_as_str

    def __repr__(self):
        return repr(self.__str__())

    def __eq__(self, other):
        return self.path_components_w_site == other.path_components_w_site

    def __hash__(self):
        return hash(self.path_components_w_site)

    @classmethod
    def parse_requested_url(cls, synamic, url_str):
        parsed_url = urllib.parse.urlparse(url_str)
        url_path = parsed_url.path
        # Unused for now: url_query = parsed_url.query
        # Unused for now: url_fragment = parsed_url.fragment
        path_segments = list(cls.path_to_components(url_path))
        assert path_segments[0] == ''
        del path_segments[0]

        # partition at special url comp
        site_ids_comps = [site_id.components for site_id in synamic.sites.ids]
        url_partition_comp = synamic.default_configs.get('settings')['url_partition_comp']

        site_id_components, path_components, special_components = [], [], []

        #  extract out site id.
        for site_id_comps in site_ids_comps:
            if len(path_segments) < len(site_id_comps):
                continue
            if path_segments[:len(site_id_comps)] == site_ids_comps:
                site_id_components = path_segments[:len(site_id_comps)]
                path_segments = path_segments[len(site_id_comps):]
                break

        # extract out paginated part
        assert '/' not in url_partition_comp
        assert ' ' not in url_partition_comp
        for idx, segment in enumerate(path_segments):
            if segment == url_partition_comp:
                special_components.extend(
                    path_segments[idx+1:]
                )
                break
            else:
                path_components.append(segment)

        site_id = synamic.sites.make_id('/'.join(site_id_components))

        return site_id, path_components, special_components
