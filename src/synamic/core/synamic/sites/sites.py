"""
Site objects should be the public interface to access Synamic. Synamic objects should not be included as the 
public interfaces.
"""
import os
import sys
import re
import shutil
from collections import OrderedDict
from synamic.core.synamic.sites._site import _Site
from synamic.core.default_data._manager import DefaultDataManager
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.exceptions import SynamicError, SynamicErrors


class Sites:
    def __init__(self, synamic, root_site_path):
        """
        :param root_site_path: Absolute path to the root site.
        """
        self.__synamic = synamic
        self.__root_site_path = root_site_path
        self.__default_data = None
        self.__sites_map = OrderedDict({
            #  site_id: site
        })  # must be ordered dict to keep serial of adding intact.
        self.__root_site = None
        self.__is_loaded = False

        # adding the root site
        _root_site_id = self.make_id('')
        assert _root_site_id.components == tuple()
        _root_site = self.make_site(_root_site_id, self.__root_site_path, parent_site=None, root_site=None)
        self.__root_site = _root_site
        self.add_site(_root_site)

    @property
    def is_loaded(self):
        return self.__is_loaded

    @property
    def ids(self):
        return tuple(self.__sites_map.keys())

    def make_id(self, comps):
        return _SiteId(self.__synamic, comps)

    def get_id_sep(self):
        return self.__synamic.system_settings['site_id_sep']

    def make_site(self, site_id, site_root_path_abs, parent_site=None, root_site=None):
        """Only this method should know how to make a site - no direct _Site class instantiation"""
        site_id = self.make_id(site_id)
        return _Site(self.__synamic, site_id, site_root_path_abs, parent_site=parent_site, root_site=root_site)

    def add_site(self, site):
        assert isinstance(site, _Site)
        self.__sites_map[site.id] = site

    def get_abs_path_by_id(self, site_id):
        """A site might not be located under the 'sites' dir, instead it can be configured in configs.
        Setting such custom path is not implemented yet, but will be in future."""
        site_id = self.make_id(site_id)
        return self.get_by_id(site_id).abs_path

    @not_loaded
    def load(self):
        assert os.path.exists(self.__root_site_path)
        # default configs
        self.__default_data = DefaultDataManager()

        # list all the site id components paths
        # this implements the default sites dire mechanism - externally located site is not implemented yet.
        children_site_comps_ids = []
        _subsites_dirname = self.__synamic.system_settings['configs.subsites_dir']
        self.__list_site_paths(children_site_comps_ids, tuple(), '')
        __sites_id_comps = tuple(children_site_comps_ids)
        for site_id_comps in __sites_id_comps:
            site_id = self.make_id(site_id_comps)
            parent_site_id = site_id.parent_id
            assert parent_site_id is not None
            parent_site = self.get_by_id(parent_site_id)
            root_site = self.__root_site
            site_root_abs_path = os.path.join(self.__synamic.abs_root_path,
                                              *self.__get_real_site_path_comps(site_id.components))
            site = self.make_site(site_id, site_root_abs_path, parent_site=parent_site, root_site=root_site)
            self.add_site(site)
        # load all the sites.
        for site in self.__sites_map.values():
            site.load()
        self.__is_loaded = True
        return self

    @property
    def root_site(self):
        return self.__root_site

    @property
    def root_site_path(self):
        return self.__root_site_path

    def get_by_id(self, site_id):
        site_id = self.make_id(site_id)
        if site_id in self.__sites_map:
            return self.__sites_map[site_id]
        raise KeyError('Site with id %s not found' % site_id)

    def __get_real_site_path_comps(self, site_virtual_comps: tuple):
        """Adds `sites` in between"""
        assert not isinstance(site_virtual_comps, str)
        subsites_dirname = self.__synamic.system_settings['configs.subsites_dir']
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
        real_site_comps += (self.__synamic.system_settings['configs.subsites_dir'], )
        subsites_dir_abs = os.path.join(self.__root_site_path, *real_site_comps)
        if os.path.exists(subsites_dir_abs):
            subsite_ids = []
            for site_id in os.listdir(subsites_dir_abs):
                if os.path.isdir(os.path.join(subsites_dir_abs, site_id)):
                    subsite_ids.append(site_id)
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

    @loaded
    def build(self):
        try:
            # clean output directory

            output_dir = self.__synamic.system_settings['dirs.outputs.outputs']
            output_cdir = self.__synamic.path_tree.create_dir_cpath(output_dir)
            if not output_cdir.exists():
                output_cdir.makedirs()
            output_abs_path = output_cdir.abs_path
            except_root_paths = ('.git', '.gitignore', '.gitattributes')
            print(f'Removing paths from {output_abs_path} with some exceptions to {except_root_paths}')
            for o_basename in os.listdir(output_abs_path):
                full_path = os.path.join(output_abs_path, o_basename)
                if o_basename not in except_root_paths and not o_basename.startswith('.'):
                    print(f'Removing {full_path}')
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                    else:
                        shutil.rmtree(full_path)

            # build sites
            build_succeeded = True
            for site_id, site in self.__sites_map.items():
                print(f'>>> Building Site: {site_id}\n\n')
                build_succeeded = site.object_manager.build()
                if not build_succeeded:
                    build_succeeded = False
                    break
        except SynamicError as e:
            e = SynamicErrors(
                f'Error building sites:',
                e
            )
            print(e, file=sys.stderr)
            build_succeeded = False
        return build_succeeded

    @loaded
    def upload(self):
        return self.__synamic.upload_manager.get_uploader('firebase').upload()


class _SiteId:
    __path_pat_split_by = re.compile(r'[\\/]')
    __ws_pat = re.compile(r'\s', re.MULTILINE)

    def __init__(self, synamic, comps):
        self.__synamic = synamic
        site_id_sep = self.__synamic.system_settings['configs.site_id_sep']
        _bk_comps = comps
        # start processing
        if isinstance(comps, self.__class__):
            self.__id_components = comps.components
        else:
            # normalizing to a list for easy iteration
            if isinstance(comps, (tuple, list)):
                _ = []
                for c in comps:
                    assert isinstance(c, str)
                    _.extend(c.split(site_id_sep))
                id_components = _
            else:
                assert isinstance(comps, str)
                id_components = comps.split(site_id_sep)

            # hunting down anything with / or \ and split at that position
            _ = []
            for c in id_components:
                _.extend(self.__path_pat_split_by.split(c))
            id_components = _

            # filter out any empty string
            _ = []
            for c in id_components:
                if c.strip() == '':
                    continue
                _.append(c)
            id_components = _

            # validating for invalid character
            for c in id_components:
                if self.__ws_pat.search(c):
                    raise Exception('Site id cannot contain white space characters: %s' % _bk_comps)

            # instance variable initialization
            self.__id_components = tuple(id_components)

    @property
    def components(self) -> tuple:
        return self.__id_components

    @property
    def path_as_ids(self):
        ids = []
        for c in self.components:
            ids.append(self.__class__(self.__synamic, c))
        return tuple(ids)

    @property
    def parent_components(self):
        if len(self.components) == 0:
            return None
        return self.components[:-1]

    @property
    def parent_id(self):
        parent_comps = self.parent_components
        if parent_comps is None:
            return None
        return self.__class__(self.__synamic, parent_comps)

    @property
    def as_string(self):
        site_id_sep = self.__synamic.system_settings['configs.site_id_sep']
        return site_id_sep.join(self.components)

    @property
    def is_root(self):
        return len(self.components) == 0

    def __len__(self):
        return len(self.components)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.components == other.components

    def __hash__(self):
        return hash(self.components)

    def __str__(self):
        return self.as_string

    def __repr__(self):
        return repr(self.__str__())
