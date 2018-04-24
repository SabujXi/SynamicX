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
from typing import Union

from synamic.core.filesystem.content_path.content_path2 import ContentPath2


class PathTree(object):
    def __init__(self, _cfg):
        assert os.path.isdir(_cfg.site_root), "FileTree.__init__: _root must be a directory, `%s`" % _cfg.site_root
        self.__config = _cfg
        self.__paths_map = {}

    @classmethod
    def to_components(cls, path_comp):
        if type(path_comp) is str:
            path_str = path_comp
            assert path_str.strip() != ''
            comps = [x for x in re.split(r'[\\/]+', path_str) if x != '']
        else:
            assert type(path_comp) in {tuple, list}

            comps = path_comp
        return tuple(comps)

    @classmethod
    def vararg_to_components(cls, *vararg):
        comps = []
        for comp in vararg:
            for sub_comp in cls.to_components(comp):
                comps.append(sub_comp)
        return tuple(comps)

    def add_path(self, path: ContentPath2):
        assert type(path) is ContentPath2
        assert path.exists()
        p = self.__paths_map.get(path, None)
        if p is None:
            self.__paths_map[path.path_components] = path
        return p

    def get_path(self, comps) -> Union[ContentPath2, None]:
        assert type(comps) is tuple
        path = self.__paths_map.get(comps, None)
        if path is not None:
            return path
        else:
            # if self.exists(comps):
            #
            return None

    def create_path(self, path_comp, is_file=False, is_meta=False) -> ContentPath2:
        """
        Create a Content Path object.
        """
        comps = self.to_components(path_comp)
        cached_path = self.get_path(comps)
        if cached_path is not None:
            path_obj = cached_path
        else:
            path_obj = ContentPath2(self, self.__config.site_root, comps, is_file=is_file, is_meta=is_meta)
        return path_obj

    def exists(self, *path) -> bool:
        comps = self.vararg_to_components(*path)
        """Checks existence relative to the root"""
        return True if os.path.exists(self.__full_path(comps)) else False

    def is_file(self, *path) -> bool:
        comps = self.vararg_to_components(*path)
        fn = self.__full_path(comps)
        return True if os.path.isfile(fn) else False

    def is_dir(self, *path) -> bool:
        comps = self.vararg_to_components(*path)
        fn = self.__full_path(comps)
        return True if os.path.isdir(fn) else False

    def join(self, *content_paths) -> ContentPath2:
        comps = self.vararg_to_components(*content_paths)
        return self.create_path(comps)

    def open(self, file_path, *args, **kwargs):
        comps = self.to_components(file_path)
        fn = self.__full_path(comps)
        return open(fn, *args, **kwargs)

    def makedirs(self, *dir_path):
        comps = self.vararg_to_components(*dir_path)
        full_p = self.__full_path(comps)
        os.makedirs(full_p)

    def get_full_path(self, comps) -> str:
        comps = self.to_components(comps)
        return os.path.join(self.__config.site_root, *comps)

    def __full_path(self, comps):
        """Comma separated arguments of path components or os.sep separated paths"""
        return os.path.join(self.__config.site_root, *comps)

    def __contains__(self, comps):
        if type(comps) is tuple:
            return comps in self.__paths_map
        elif type(comps) is ContentPath2:
            return comps.path_components in self.__paths_map
        else:
            raise Exception("Invalid type provided")

    def __list_paths_loop2(self, starting_components=(), files_only=None, directories_only=None, depth=None):
        """
        A function to get all paths recursively starting from abs_root but returns a list of paths relative to the 
        .root
        prefix_relative_root is fixed on every recursion
        BUT next_relative_root isn't
        """
        for x in starting_components:
            assert '/' not in x and '\\' not in x

        # check that files only and directories only both are not set to the Truth value
        if files_only is True:
            assert directories_only is not True
        if directories_only is True:
            assert files_only is not True

        # depth
        assert depth is None or type(depth) is int
        if depth is None:
            depth = 2147483647

        absolute_root = self.__full_path(starting_components)
        absolute_site_root = self.__config.site_root
        assert os.path.exists(absolute_root), "Absolute root must exist: %s" % absolute_root

        # new
        to_travel = deque([((*starting_components, comp), 1) for comp in os.listdir(absolute_root)])
        # print("to travel:", to_travel)
        directories = []
        files = []

        while len(to_travel) != 0:
            path_comps_depth = to_travel.popleft()
            path_comps = path_comps_depth[0]
            path_depth = path_comps_depth[1]
            if path_depth > depth:
                break
            path = path_comps[-1]
            path_abs = self.__full_path(path_comps)
            if path.lower().endswith(ContentPath2.META_FILE_EXTENSION.lower()):
                # Skipping if meta file
                continue
            if path.startswith('.') or path.endswith(ContentPath2.META_FILE_EXTENSION):
                # "Files that start with dot (.) are special files and thus skipped. Later I may add special file " \
                # "features"
                continue

            cached_path = self.get_path(path_comps)
            if cached_path:
                if cached_path.is_dir:
                    directories.append(cached_path)
                else:
                    files.append(cached_path)
            else:
                if os.path.isfile(path_abs):
                    if files_only is True or files_only is None:
                        path_obj = ContentPath2(self, absolute_site_root, path_comps, is_file=True)
                        files.append(path_obj)
                        self.__paths_map[path_comps] = path_obj
                elif os.path.isdir(path_abs):
                    if directories_only is True or directories_only is None:
                        path_obj = ContentPath2(self, absolute_site_root, path_comps, is_file=False)
                        directories.append(path_obj)
                        self.__paths_map[path_comps] = path_obj
                        # Recurse
                    to_travel.extend(tuple([((*path_comps, comp), path_depth + 1) for comp in os.listdir(path_abs)]))
                else:
                    raise Exception("ContentPath is neither dir, nor file")
        return directories, files

    def list_paths(self, initial_path_comps=(), files_only=None, directories_only=None, depth=None):
        if type(initial_path_comps) is ContentPath2:
            starting_comps = initial_path_comps.path_components
        else:
            starting_comps = self.to_components(initial_path_comps)
        dirs, files = self.__list_paths_loop2(starting_comps, files_only=files_only, directories_only=directories_only, depth=depth)
        return dirs, files

    def list_file_paths(self, initial_path_comps=(), depth=None):
        _, files = self.list_paths(initial_path_comps, files_only=True, depth=depth)
        return files

    def list_dir_paths(self, initial_path_comps='', depth=None):
        dirs, _ = self.list_paths(initial_path_comps, directories_only=True, depth=depth)
        return dirs
