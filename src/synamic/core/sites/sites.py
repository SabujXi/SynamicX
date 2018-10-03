"""
Site objects should be the public interface to access Synamic. Synamic objects should not be included as the 
public interfaces.
"""
import os
import re
from synamic.core.configs._manager import DefaultConfigManager
_site_id_pattern = re.compile(r'^[a-z0-9_-]+$', re.I)


class _Site:
    def __init__(self, site_synamic, path_comps, parent_site, root_site):
        self.__path_comps = path_comps
        self.__synamic = site_synamic
        self.__parent_site = parent_site
        self.__root_site = root_site
        assert type(parent_site) in (self.__class__, None)
        assert type(root_site) in (self.__class__, None)

    def site_id(self):
        return '/'.join(self.__path_comps)

    def path_comps(self):
        return self.__path_comps

    def load(self):
        pass

    @property
    def synamic(self):
        return self.__synamic

    @property
    def parent_site(self):
        return self.__parent_site

    @property
    def root_site(self):
        return self.__root_site


class Sites:
    def __init__(self, root_site_path):
        """
        :param root_site_path: Absolute path to the root site.
        """
        self.__root_site_path = root_site_path
        self.__default_configs = None
        self.__root_site = None
        self.__sites_id_comps = ()
        self.__is_loaded = False

    def load(self):
        assert os.path.exists(self.__root_site_path)
        # default configs
        self.__default_configs = DefaultConfigManager()

        # list all the site id components paths
        children_site_comps_ids = []
        self.__list_site_paths(children_site_comps_ids, (), '')
        self.__sites_id_comps = tuple(children_site_comps_ids)
        print(self.__sites_id_comps)
        #


        # load all the sites.
        self.__is_loaded = True
        return self

    @property
    def root_site(self):
        return self.__root_site

    def get_site(self, site_id):
        pass







    def __get_real_subsite_path_comps(self, subsite_comps: tuple):
        """Adds sites in between"""
        real_comps = []
        subsites_dirname = self.__default_configs.get('configs')['subsites_dir']
        for i in range(len(subsite_comps)):
            if subsite_comps[i] == '':
                continue
            real_comps.append(subsite_comps[i])
            # if i%2 != 0:
            real_comps.append(subsites_dirname)
        return tuple(real_comps)

    def __list_site_paths(self, res_sites_id_comps: list, path_2_parent: tuple, start_with=''):
        subsites_dirname = self.__default_configs.get('configs')['subsites_dir']

        # for start_with_this in start_with:
        # real_subsite_path = []
        subsite_comps = [*path_2_parent]
        subsite_comps.append(start_with) if start_with != '' else None
        real_subsite_comps = self.__get_real_subsite_path_comps(tuple(subsite_comps))
        subsites_dir_abs = os.path.join(self.__root_site_path, subsites_dirname, *real_subsite_comps)
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
                    site_id_comps = [*path_2_parent]
                    if start_with != '':
                        site_id_comps.append(start_with)
                    site_id_comps = tuple(site_id_comps)
                    next_site_id_comps = (*site_id_comps, subsite_id)
                    res_sites_id_comps.append(next_site_id_comps)
                    self.__list_site_paths(
                        res_sites_id_comps,
                        site_id_comps,
                        subsite_id
                    )


