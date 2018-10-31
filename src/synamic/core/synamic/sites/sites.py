"""
Site objects should be the public interface to access Synamic. Synamic objects should not be included as the 
public interfaces.
"""
import os
import re
from synamic.core.synamic.sites._site import _Site
from synamic.core.configs._manager import DefaultConfigManager
from synamic.core.standalones.functions.decorators import loaded, not_loaded
_site_id_pattern = re.compile(r'^[a-z0-9_-]+$', re.I)


class Sites:
    def __init__(self, synamic, root_site_path):
        """
        :param root_site_path: Absolute path to the root site.
        """
        self.__synamic = synamic
        self.__root_site_path = root_site_path
        self.__default_configs = None
        self.__root_site = _Site(self.__synamic, tuple(), parent_site=None, root_site=None)
        self.__sites = [self.__root_site, ]
        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        assert os.path.exists(self.__root_site_path)
        # default configs
        self.__default_configs = DefaultConfigManager()

        # list all the site id components paths
        children_site_comps_ids = []
        _subsites_dirname = self.__default_configs.get('configs')['subsites_dir']
        self.__list_site_paths(children_site_comps_ids, tuple(), '')
        __sites_id_comps = tuple(children_site_comps_ids)
        # print(self.__sites_id_comps)
        for site_id_comps in __sites_id_comps:
            parent_site = self.get_by_comps(tuple(site_id_comps[:-1]))
            root_site = self.__root_site
            site = _Site(self.__synamic, site_id_comps, parent_site, root_site)
            self.__sites.append(site)

        # load all the sites.
        for site in self.__sites:
            print(site)
            site.load()
        self.__is_loaded = True
        return self

    @property
    def root_site(self):
        return self.__root_site

    @property
    def root_site_path(self):
        return self.__root_site_path

    def get_by_id(self, site_id: str):
        for site in self.__sites:
            if site.id == site_id:
                return site
        raise KeyError('Site with id %s not found' % site_id)

    def get_by_comps(self, id_comps: tuple):
        for site in self.__sites:
            if site.virtual_id_comps == id_comps:
                return site
        raise KeyError('Site with id comps %s not found' % str(id_comps))

    def comps2id(self, virtual_comps: tuple) -> str:
        assert type(virtual_comps) in (tuple, list)
        return '/'.join(virtual_comps)

    def id2comps(self, site_id):
        assert not site_id.startswith(('/', '\\'))
        assert not site_id.endswith(('/', '\\'))
        id_comps = site_id.split('/')
        for subsite_id in id_comps:
            if not _site_id_pattern.match(subsite_id):
                raise Exception('Site id %s is an invalid site id.' % site_id)
        return id_comps

    def virtual2real_comps(self, site_comps: tuple):
        return self.__get_real_site_path_comps(site_comps)

    def __get_real_site_path_comps(self, site_virtual_comps: tuple):
        """Adds `sites` in between"""
        assert not isinstance(site_virtual_comps, str)
        subsites_dirname = self.__default_configs.get('configs')['subsites_dir']
        real_comps = []
        for i in range(len(site_virtual_comps)):
            assert site_virtual_comps[i] != ''
            real_comps.append(subsites_dirname)
            real_comps.append(site_virtual_comps[i])
        # print('Real calc: of (%s)' % str(site_virtual_comps), real_comps)
        return tuple(real_comps)

    def __list_site_paths(self, result: list, v_path_comps_2_parent: tuple, start_with=''):
        virtual_site_comps = [*v_path_comps_2_parent]
        virtual_site_comps.append(start_with) if start_with != '' else None
        real_site_comps = self.__get_real_site_path_comps(tuple(virtual_site_comps))
        real_site_comps += (self.__default_configs.get('configs')['subsites_dir'], )
        subsites_dir_abs = os.path.join(self.__root_site_path, *real_site_comps)
        print('subsites_dir_abs : ', subsites_dir_abs)
        if os.path.exists(subsites_dir_abs):
            subsite_ids = []
            for site_id in os.listdir(subsites_dir_abs):
                if os.path.isdir(os.path.join(subsites_dir_abs, site_id)):
                    if _site_id_pattern.match(site_id):
                        subsite_ids.append(site_id)
                    else:
                        raise Exception('Invalid site id/dir name: %s' % site_id)
            if subsite_ids:
                for subsite_id in subsite_ids:
                    site_id_comps = [*v_path_comps_2_parent]
                    if start_with != '':
                        site_id_comps.append(start_with)
                    site_id_comps = tuple(site_id_comps)
                    next_site_id_comps = (*site_id_comps, subsite_id)
                    result.append(next_site_id_comps)
                    self.__list_site_paths(
                        result,
                        site_id_comps,
                        subsite_id
                    )
