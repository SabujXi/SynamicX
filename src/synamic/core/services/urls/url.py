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

from synamic.core.services.filesystem.content_path import _CPath


class _ContentUrl:
    @classmethod
    def __to_components(cls, url_comps_or_path: Union[str, list, tuple, _CPath], append_slash=False) -> tuple:
        # print("URl comps or path: %s" % url_comps_or_path)
        res_url_comps = []
        if type(url_comps_or_path) is str:
            if not re.match(r'[\\/]+$', url_comps_or_path):
                if append_slash:
                    url_comps_or_path += '/'
            for url_comp in re.split(r'[\\/]+', url_comps_or_path):
                res_url_comps.append(url_comp)

        elif type(url_comps_or_path) in (list, tuple):
            # print("URL AS LIST PATH: `%s`" % str(url_comps_or_path))
            assert not append_slash, "Cannot do append slashing for list/tuple comps - list or tuple comps are considered files -- ;) always files first"
            # assert type(url_comps_or_path) in {list, tuple}, "Url components can either be str, list or tuple"
            # validation for double space

            # removing empty str from middle - they will be intact at both ends
            # idx = 0
            # last_idx = len(url_comps_or_path) - 1
            # last_comp_was_empty = False  # last_comp_was_empty == ''
            for url_comp in url_comps_or_path:
                # assert not re.match(r'^\s+$', url_comp), "A component of an url cannot be one or all whitespaces"
                # if url_comp == '':
                #     if last_comp_was_empty:
                #         last_comp_was_empty = True
                #         continue
                #     last_comp_was_empty = True
                # else:
                #     last_comp_was_empty = False

                # if url_comp == '' and idx != 0 and idx != last_idx:
                #     idx += 1
                #     continue
                res_url_comps.append(url_comp)

            # if res_url_comps[-1] != '' and res_url_comps[-1] != 'index.html':
            #     # index.html (lower) is special
            #     res_url_comps.append('')

        elif type(url_comps_or_path) is _CPath:
            assert not append_slash, "Cannot do append slashing for static content (I hope you did not pass path of a dynamic content)"
            # for static file only - though no such checking is done
            # no append_slash things will happen here as it is for static content,
            # do not use this for dynamic content path

            assert url_comps_or_path.is_file, "Cannot create content url of a directory"
            res_url_comps = list(url_comps_or_path.path_comps)
        else:
            raise Exception('Invalid argument for url component: %s' % str(url_comps_or_path))
        if len(res_url_comps) == 0:
            res_url_comps.append('')

        if res_url_comps[-1] == 'index.html':
            res_url_comps[-1] = ''

        final_res_comps = []
        # print("Res url comps: %s" % str(res_url_comps))
        # removing duplicate components
        idx = 0
        last_idx = len(res_url_comps) - 1
        # last_comp_was_empty = False  # last_comp_was_empty == ''

        for url_comp in res_url_comps:
            assert not re.match(r'^\s+$', url_comp), "A component of an url cannot be one or all whitespaces"
            if not (idx == 0 or idx == last_idx):  # sparing the first and last empty string only
                if url_comp == '':
                    idx += 1
                    continue
            final_res_comps.append(url_comp)
            idx += 1

        if len(final_res_comps) == 2:  # eg ['', ''] == '/'.split('/')
            if final_res_comps[0] == '' and final_res_comps[1] == '':
                final_res_comps = ['']
        # print("Final Res url comps: %s" % str(final_res_comps))
        return tuple(final_res_comps)

    @classmethod
    def __to_content_components(cls, _url_comps):
        """
        __to_components() can be used for anything (e.g. in join() to join another string and construct url)
         and thus it does not prepend and empty string at the start. So, here this one comes handy.
         """
        if _url_comps[0] != '':
            _url_comps = ('', *_url_comps)
        return _url_comps

    def __init__(self, site, url_comps, append_slash=False):
        """
        append_slash is only for dynamic contents and only when the url_comps is being passed as sting (not: list, tuple, content path) 
        So, we are not persisting that data
        
        'index.html' in lower case is special throughout the url system - see the codes for extracting more info.
        
        if we indicate ...
        """
        self.__url_comps = self.__to_content_components(
                self.__to_components(url_comps, append_slash)
            )

        self.__site = site
        self.__of_static_file = type(url_comps) is _CPath
        self.__url_str = None

        self.__append_slash = append_slash

    def join(self, url_comps: Union[str, list, tuple], append_slash=False):
        assert type(url_comps) is not _CPath, "Static files components are all in one to construct an url, no need to include that here"
        this_comps = self.__url_comps
        other_comps = self.__to_components(url_comps, append_slash=append_slash)
        this_end = this_comps[-1]
        # print("Other url comps str: `%s`" % url_comps)
        # print("Other url comps Tuple: `%s`" % str(other_comps))
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
        # comps = this_comps + other_comps
        return self.__class__(self.__site, comps)  #, append_slash=append_slash)

    @property
    def of_static_file(self):
        return self.__of_static_file

    @property
    def is_dir(self):
        return True if self.__url_comps[-1] == '' else False

    @property
    def is_file(self):
        return not self.is_dir

    @property
    def file_name(self):
        fn = self.__url_comps[-1]
        if fn == '':
            fn = 'index.html'
        return fn

    @property
    def path_components(self):
        return self.__url_comps

    @property
    def path(self):
        if self.__url_str is None:
            comps = self.__url_comps
            if len(comps) == 1 and comps[0] == '':
                _url_str = self.__site.prefix_dir + '/'
            else:
                _url_str = self.__site.prefix_dir + "/".join(self.__url_comps)
            if not _url_str.startswith('/'):
                _url_str = '/' + _url_str
            self.__url_str = _url_str
        return self.__url_str

    @property
    def url_encoded_path(self):
        return urllib.parse.quote_plus(self.path, safe='/', encoding='utf-8')

    @property
    def absolute_url(self):
        raise NotImplemented

    @property
    def url(self):
        return self.url_encoded_path

    @property
    def real_path(self):
        p = self.path
        if p.endswith('/'):
            p += 'index.html'
        return p

    @property
    def dir_components(self):
        res = []
        if self.is_file:
            assert self.__url_comps[-1] != '', 'Logical error, ask Sabuj to fix | path: `%s`' % self.path
            dirs = self.__url_comps[:-1]
        else:
            dirs = self.__url_comps

        for d in dirs:
            if d == '':
                continue
            res.append(d)
        return tuple(res)

    @property
    def path_components(self):
        res = []
        if self.is_file:
            _paths = self.__url_comps
        else:
            _paths = list(self.__url_comps)
            _paths.append('index.html')

        for d in _paths:
            if d == '':
                continue
            res.append(d)
        return tuple(res)

    @property
    def to_content_path(self):
        return self.__site.path_tree.create_cpath(
            (self.__site.site_settings.output_dir, *self.path_components),
            is_file=self.is_file
        )

    @property
    def append_slash(self):
        return self.__append_slash

    def __str__(self):
        return self.path

    def __repr__(self):
        return repr(self.__str__())

    def __eq__(self, other):
        if self.path_components == other.path_comps:
            return True
        return False

    def __hash__(self):
        return hash(self.__url_comps)
