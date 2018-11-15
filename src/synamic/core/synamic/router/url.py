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
from synamic.core.contracts import CDocType
from synamic.core.standalones.functions.sequence_ops import Sequence
ext_pattern = re.compile(r'.+(\.[a-zA-Z0-9]{1,8})')
# used to check whether an url has an ext so that if it is html cdoctype /index.html is not used.


class ContentUrl:
    @classmethod
    def __str_path_to_comps(cls, path_str):
        comps = []
        for url_comp in re.split(r'[\\/]+', path_str):
            comps.append(url_comp)
        return comps

    @classmethod
    def __sequence_to_comps(cls, path_sequence):
        comps = []
        for url_comp in path_sequence:
            assert isinstance(url_comp, str)
            comps.extend(
                cls.__str_path_to_comps(url_comp)
            )
        return comps

    @classmethod
    def path_to_ccomponents(cls, *url_path_comps: Union[str, list, tuple]) -> tuple:
        res_url_path_comps = []
        for _comps in url_path_comps:
            if isinstance(_comps, str):
                res_url_path_comps.extend(cls.__str_path_to_comps(_comps))
            elif isinstance(_comps, (list, tuple)):
                res_url_path_comps.extend(cls.__sequence_to_comps(_comps))
            else:
                raise Exception('Invalid argument for url component: %s' % str(url_path_comps))

        # ignore empty ones
        _ = []
        for idx, comp in enumerate(res_url_path_comps):
            if idx == 0:  # sparing the first empty string only
                _.append(comp)
            else:
                if comp != '':
                    _.append(comp)
                # else ignore
        res_url_path_comps = _

        # ../../../ recalculation and empty string removing from middle
        _ = []
        for idx, comp in enumerate(res_url_path_comps):
            if comp == '.':
                # just ignore it
                continue
            elif comp == '..':
                #  delete the last comp and add current one (replace the last one)
                if idx == 0:
                    continue
                else:
                    if len(_) >= 1:
                        del _[-1]
            else:
                _.append(comp)
        res_url_path_comps = _

        # re-adding empty string for zero length comps
        if len(res_url_path_comps) == 0:
            res_url_path_comps.append('')

        # comps should begin with empty string ... we can only handle site root absolute url as there is no context for
        # relative url in this function.
        # TODO: DONE: unlike file system path, this last '' should be removed for len(comps) > 1
        # Done by ignoring all empty comps except for the first one -. see above
        # HTML (both gen & non-gen) cdoctype url that does not end with a file extension will have /index.html (take
        # from settings) as real file system url and for browser (client) representation it will end with /.
        # So, for html cdoctype'd urls that have a file extension (place checking so that it does not exceed
        # certain length + the last comp does not start with a dot '.' )
        #  will not end with / for client representation.

        # validating
        for idx, url_comp in enumerate(res_url_path_comps):
            assert not re.match(r'^\s+$', url_comp), "A component of an url cannot be one or all whitespaces"

        return tuple(res_url_path_comps)

    @classmethod
    def path_to_components(cls, *url_path_comps):
        path_comps = cls.path_to_ccomponents(*url_path_comps)
        return Sequence.strip(path_comps, ('',))

    def __init__(self, site, url_path_comps, for_cdoctype=CDocType.UNSPECIFIED):
        """
        append_slash is only for dynamic contents and only when the url_path_comps is being passed as sting (not: list, tuple, content path)
        So, we are not persisting that data
        
        'index.html' in lower case is special throughout the url system - see the codes for extracting more info.
        
        if we indicate ...
        """
        assert isinstance(for_cdoctype, CDocType), \
            f'cURL without a CDocType specified is not acceptable. When you are not going to use the url for final url '\
            f'generation (e.g. for query by url only) you should specify CDocType.UNSPECIFIED\n'\
            f'The type you provided was {type(for_cdoctype)} with the value {for_cdoctype}'
        assert CDocType.is_text(for_cdoctype) or CDocType.is_binary(for_cdoctype) or\
            for_cdoctype == CDocType.UNSPECIFIED

        self.__site = site
        self.__for_cdoctype = for_cdoctype
        # remove space from both end of url (it happens to be only on left.)
        self.__url_path_comps = self.path_to_ccomponents(url_path_comps)

        self.__path_str = None
        self.__path_components_w_site = None
        self.__url_str = None

    def clone(self, for_cdoctype=CDocType.UNSPECIFIED):
        """Besides copying, usable when trying different type of content in router. e.g. static content need path gen"""
        return self.__class__(self.__site, self.__url_path_comps, for_cdoctype=for_cdoctype)

    @property
    def for_site(self):
        return self.__site

    @property
    def for_cdoctype(self):
        return self.__for_cdoctype

    def __join_path_comps_for_url(self, comps):
        # comps must be a result of to_path_components/self.__url_path_comps
        if comps == ('',) or len(comps) == 0:
            path_str = '/'
        else:
            comps = list(comps)
            if CDocType.is_html(self.for_cdoctype):
                if comps[-1] != '':
                    comps.append('')
            else:
                if comps[-1] == '':
                    del comps[-1]
            path_str = '/'.join(comps)
        return path_str

    def join(self, url_comps: Union[str, list, tuple], for_cdoctype=CDocType.UNSPECIFIED):
        this_comps = self.__url_path_comps
        other_comps = self.path_to_ccomponents(url_comps)
        comps = []
        comps.extend(this_comps)
        comps.extend(other_comps)

        if for_cdoctype is None:
            for_cdoctype = self.__for_cdoctype
        return self.__class__(self.__site, comps, for_cdoctype=for_cdoctype)

    @property
    def path_components(self):
        return self.__url_path_comps

    @property
    def path_components_w_site(self):
        if self.__path_components_w_site is None:
            host_base_path = self.__site.settings['host_base_path']
            self.__path_components_w_site = self.path_to_ccomponents(
                host_base_path, self.__site.id.components, self.__url_path_comps
            )
        return self.__path_components_w_site

    @property
    def path_as_str(self):
        assert self.__for_cdoctype is not CDocType.UNSPECIFIED
        if self.__path_str is None:
            self.__path_str = self.__join_path_comps_for_url(self.path_components)
        return self.__path_str

    @property
    def path_as_str_w_site(self):
        assert self.__for_cdoctype is not CDocType.UNSPECIFIED
        if self.__path_str is None:
            self.__path_str = self.__join_path_comps_for_url(self.path_components_w_site)
        return self.__path_str

    @property
    def path_as_str_encoded(self):
        assert self.__for_cdoctype is not CDocType.UNSPECIFIED
        return urllib.parse.quote_plus(self.path_as_str, safe='/:#', encoding='utf-8')

    @property
    def path_as_str_w_site_encoded(self):
        assert self.__for_cdoctype is not CDocType.UNSPECIFIED
        return urllib.parse.quote_plus(self.path_as_str_w_site, safe='/:#', encoding='utf-8')

    @property
    def url(self):
        """URL with host name, port, path"""
        assert self.__for_cdoctype is not CDocType.UNSPECIFIED
        if self.__url_str is None:
            ss = self.__site.settings
            url_str = ss.site_address + self.path_as_str_w_site
            self.__url_str = url_str
        return self.__url_str

    @property
    def url_encoded(self):
        assert self.__for_cdoctype is not CDocType.UNSPECIFIED
        return urllib.parse.quote_plus(self.url, safe='/:#', encoding='utf-8')

    @property
    def to_file_system_path(self):
        # TODO: make it dirfn based
        p = self.path_as_str
        if CDocType.is_html(self.__for_cdoctype):
            index_file_name = self.__site.settings['index_file_name']
            if p.endswith('/'):
                p += index_file_name
            else:
                p += '/' + index_file_name
        else:
            # validation
            # assert not p.endswith('/')
            pass
        return p

    @property
    def to_cpath(self):
        # TODO: make it dirfn based
        return self.__site.path_tree.create_file_cpath(
            self.to_file_system_path
        )

    @property
    def to_cpath_w_site(self):
        # TODO: make it dirfn based
        return self.__site.synamic.path_tree.create_file_cpath(
            self.to_file_system_path
        )

    @property
    def to_dirfn_pair(self):
        path_comps = self.path_components
        if ext_pattern.match(path_comps[-1]):
            return path_comps[:-1], path_comps[-1]
        if CDocType.is_html(self.__for_cdoctype):
            index_file_name = self.__site.settings['index_file_name']
            return path_comps, index_file_name
        else:
            return path_comps[:-1], path_comps[-1]

    @property
    def to_dirfn_pair_w_site(self):
        path_comps = self.path_components_w_site
        if ext_pattern.match(path_comps[-1]):
            return path_comps[:-1], path_comps[-1]
        if CDocType.is_html(self.__for_cdoctype):
            index_file_name = self.__site.settings['index_file_name']
            return path_comps, index_file_name
        else:
            return path_comps[:-1], path_comps[-1]

    def __str__(self):
        # same as self.path_as_str_w_site, but cannot use that property due to CDocType check issue.
        # keep this method synced with self.path_as_str_w_site
        path_str = self.__join_path_comps_for_url(self.path_components_w_site)
        return f'CURL: {path_str}'

    def __repr__(self):
        return repr(self.__str__())

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.path_components_w_site == other.path_components_w_site

    def __hash__(self):
        return hash(self.path_components_w_site)

    @classmethod
    def parse_requested_url(cls, synamic, url_str):
        # python urlparse // bug workaround
        url_str = re.sub(r'(?<!:)/+', '/', url_str)

        parsed_url = urllib.parse.urlparse(url_str)
        url_path = parsed_url.path
        # Unused for now: url_query = parsed_url.query
        # Unused for now: url_fragment = parsed_url.fragment
        path_segments = list(cls.path_to_components(url_path))
        # partition at special url comp
        site_ids_comps = sorted([site_id.components for site_id in synamic.sites.ids], key=len, reverse=True)
        url_partition_comp = synamic.system_settings['url_partition_comp']

        site_id_components, path_components, special_components = [], [], []
        #  extract out site id.
        for site_id_comps in site_ids_comps:
            if Sequence.startswith(path_segments, site_id_comps):
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
