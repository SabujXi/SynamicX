"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import os
import re
from collections import deque
from synamic.core.services.filesystem.content_path import _CPath
from synamic.core.standalones.functions.decorators import loaded, not_loaded


class _Patterns:
    path_sep = re.compile(r'[\\/]+')


class PathTree(object):
    def __init__(self, site):
        self.__site = site
        # TODO: assert os.path.isdir(site.site_root), "FileTree.__init__: _root must be a directory, `%s`"
        #  % site.site_root

        # default configs
        _dc = site.default_configs.get('configs')
        self.__ignore_dirs_sw = _dc.get('ignore_dirs_sw', None)
        self.__ignore_files_sw = _dc.get('ignore_files_sw', None)
        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        self.__is_loaded = True

    @classmethod
    def to_comps(cls, path_comp):
        comps = []
        if type(path_comp) is str:
            path_str = path_comp
            # assert path_str.strip() != ''  # by empty path we mean site root
            path_str = os.path.normpath(path_str)
            path_comp_str_s = []
            for path_comp_str in _Patterns.path_sep.split(path_str):
                path_comp_str = path_comp_str.strip()
                if path_comp_str != '':
                    path_comp_str_s.append(path_comp_str)
            comps.extend(path_comp_str_s)
        elif type(path_comp) in {tuple, list}:
            # converting sting paths like ('x', 'a/b\\path_comp_str') to ('x', 'a', 'b', 'path_comp_str')
            _i = 0
            while _i < len(path_comp):
                comp_ = path_comp[_i]
                # comp_str = os.path.normpath(comp_str)
                path_comp_s = cls.to_comps(comp_)
                comps.extend(path_comp_s)
                _i += 1
        elif type(path_comp) is _CPath:
            comps = path_comp.path_comps
        else:
            raise Exception("Path comps must be list, tuple, string or _CPath object when it is not string: %s" % type(path_comp))

        # Relative URL processing.
        new_comps = []
        for comp in comps:
            if comp == '..':
                if len(new_comps) > 0:
                    del new_comps[-1]
            elif comp == '.':
                # skip
                continue
            else:
                new_comps.append(comp)

        return tuple(new_comps)

    @classmethod
    def varargs_to_comps(cls, *vararg):
        comps = []
        for comp in vararg:
            sub_comps = cls.to_comps(comp)
            comps.extend(sub_comps)
        return tuple(comps)

    def create_cpath(self, *path_comps, is_file=False) -> _CPath:
        """
        Create a Content Path object.
        """
        _ = []
        _.extend(path_comps)
        comps = self.to_comps(_)
        path_obj = _CPath(self, self.__site, comps, is_file=is_file)
        return path_obj

    def create_file_cpath(self, *path_comps):
        return self.create_cpath(*path_comps, is_file=True)

    def create_dir_cpath(self, *path_comps):
        return self.create_cpath(*path_comps, is_file=False)

    def exists(self, *path) -> bool:
        comps = self.varargs_to_comps(*path)
        """Checks existence relative to the root"""
        return True if os.path.exists(self.__full_path(comps)) else False

    def is_file(self, *path) -> bool:
        comps = self.varargs_to_comps(*path)
        fn = self.__full_path(comps)
        return True if os.path.isfile(fn) else False

    def is_dir(self, *path) -> bool:
        comps = self.varargs_to_comps(*path)
        fn = self.__full_path(comps)
        return True if os.path.isdir(fn) else False

    def join(self, *content_paths) -> _CPath:
        comps = self.varargs_to_comps(*content_paths)
        return self.create_cpath(comps)

    def open(self, file_path, *args, **kwargs):
        comps = self.to_comps(file_path)
        fn = self.__full_path(comps)
        return open(fn, *args, **kwargs)

    def makedirs(self, *dir_path):
        comps = self.varargs_to_comps(*dir_path)
        full_p = self.__full_path(comps)
        os.makedirs(full_p)

    def get_full_path(self, comps) -> str:
        comps = self.to_comps(comps)
        return os.path.join(self.__site.abs_site_path, *comps)

    def __full_path(self, comps):
        # for internal use only where there is no normalization needed with self.to_comps
        """Comma separated arguments of path components or os.sep separated paths"""
        return os.path.join(self.__site.abs_site_path, *comps)

    def __list_cpaths_loop2(self, starting_comps=(), files_only=None, directories_only=None, depth=None, exclude_comps_tuples=(), checker=None):
        """
        A function to get all paths recursively starting from abs_root but returns a list of paths relative to the 
        .root
        prefix_relative_root is fixed on every recursion
        BUT next_relative_root isn't
        
        exclude_comps_tuples: *components* list that are excluded from listing
        checker: callables that accepts parameters: __ContentPath2 instance.
        """
        for comp in starting_comps:
            assert type(comp) is str, "Components must be of type string. %s found" % str(type(comp))

        for comps in exclude_comps_tuples:
            assert type(comps) is tuple, "exclude_comps_tuples must contain tuple of strings as path. %s found" % str(type(comps))

        # check that files only and directories only both are not set to the Truth value
        if files_only is True:
            assert directories_only is not True
        if directories_only is True:
            assert files_only is not True

        # depth
        assert depth is None or type(depth) is int, "Type of depth must be None or int, %s found with value %s" %(str(type(depth)), str(depth))
        if depth is None:
            depth = 2147483647

        # old code p1
        # for x in starting_comps:
        #     assert '/' not in x and '\\' not in x

        # new code p1: converting sting paths like ('x', 'a/b\\c') to ('x', 'a', 'b', 'c')

        absolute_root = self.__full_path(starting_comps)
        absolute_site_root = self.__site.abs_site_path
        assert os.path.exists(absolute_root), "Absolute root must exist: %s" % absolute_root

        # new
        to_travel = deque([((*starting_comps, comp), 1) for comp in os.listdir(absolute_root)])
        directories = []
        files = []

        while len(to_travel) != 0:
            path_comps_n_depth = to_travel.popleft()
            path_comps = path_comps_n_depth[0]
            path_depth = path_comps_n_depth[1]
            if path_depth > depth:
                break
            path_base = path_comps[-1]
            path_abs = self.__full_path(path_comps)

            # skip paths of exclude dirs
            do_continue = False
            for exclude_comps in exclude_comps_tuples:
                if path_depth == len(exclude_comps):
                    # if self.norm_components(path_comps) == self.norm_components(exclude_comps):
                    if path_comps == exclude_comps:
                        do_continue = True
                        break
            if do_continue:
                continue

            if os.path.isfile(path_abs) and (files_only is True or files_only is None):
                move_in = True
                path_obj = _CPath(self, self.__site, path_comps, is_file=True)
                if checker is not None and not checker(path_obj):
                    move_in = False
                elif path_base.startswith(self.__ignore_files_sw):
                    move_in = False

                if move_in:
                    files.append(path_obj)

            elif os.path.isdir(path_abs) and (directories_only is True or directories_only is None):
                path_obj = _CPath(self, self.__site, path_comps, is_file=False)
                move_in = True
                if checker is not None and not checker(path_obj):
                    move_in = False
                if path_base.startswith(self.__ignore_dirs_sw):
                    move_in = False
                if move_in:
                    directories.append(path_obj)
                    # Recurse
                    to_travel.extend(tuple([((*path_comps, comp), path_depth + 1) for comp in os.listdir(path_abs)]))
            else:
                raise Exception("ContentPath is neither dir, nor file")
        return directories, files

    def list_cpaths(self, initial_path_comps=(), files_only=None, directories_only=None, depth=None, exclude_compss=(), checker=None):
        if type(initial_path_comps) is _CPath:
            starting_comps = initial_path_comps.path_components
        else:
            starting_comps = self.to_comps(initial_path_comps)
        _exclude_compss = []
        for pc in exclude_compss:
            _exclude_compss.append(self.to_comps(pc))
        exclude_compss = tuple(_exclude_compss)

        dirs, files = self.__list_cpaths_loop2(starting_comps, files_only=files_only, directories_only=directories_only, depth=depth, exclude_comps_tuples=exclude_compss, checker=checker)
        return dirs, files

    def list_file_cpaths(self, initial_path_comps=(), depth=None, exclude_compss=(), checker=None):
        _, files = self.list_cpaths(initial_path_comps, files_only=True, depth=depth, exclude_compss=exclude_compss, checker=checker)
        return files

    def list_dir_cpaths(self, initial_path_comps='', depth=None, exclude_compss=(), checker=None):
        dirs, _ = self.list_cpaths(initial_path_comps, directories_only=True, depth=depth, exclude_compss=exclude_compss, checker=checker)
        return dirs
