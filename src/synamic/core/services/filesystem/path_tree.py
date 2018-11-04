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
from collections.__init__ import deque
regex_type = type(re.compile(""))
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
    def __str_path_to_comps(cls, path_str):
        # converting sting paths like ('x', 'a/b\\path_comp_str') to ('x', 'a', 'b', 'path_comp_str')
        # assert path_str.strip() != ''  # by empty path we mean site root
        str_comps = []
        for path_comp_str in _Patterns.path_sep.split(path_str):
            path_comp_str = path_comp_str.strip()
            str_comps.append(path_comp_str)
        return str_comps

    @classmethod
    def __sequence_path_to_comps(cls, path_sequence):
        str_comps = []
        for path_comp in path_sequence:
            if isinstance(path_comp, str):
                str_comps.extend(cls.__str_path_to_comps(path_comp))
            elif isinstance(path_comp, (list, tuple)):
                str_comps.extend(cls.__sequence_path_to_comps(path_comp))
            else:
                raise Exception('Invalid component type for path: %s' % str(type(path_comp)))
        return str_comps

    @classmethod
    def to_comps(cls, *path_comps):
        comps = []
        for path_comp in path_comps:
            if isinstance(path_comp, str):
                comps.extend(cls.__str_path_to_comps(path_comp))
            elif isinstance(path_comp, (tuple, list)):
                comps.extend(cls.__sequence_path_to_comps(path_comp))
            elif type(path_comp) is cls.__CPath:
                # TODO: should check that called and caller are in the same site. This method is clcass method
                # and i cannot check the validity now.
                comps.extend(path_comp.path_comps)
            else:
                raise Exception("Path comps must be list, tuple, string or __CPath object when it is not string: %s" % type(path_comp))

        # remove empty '' part except for the first and last one
        _ = []
        for idx, comp in enumerate(comps):
            if idx in {0, len(comps) - 1}:
                # keep empty string for first and last part
                _.append(comp)
            else:
                # ignore the empty string.
                if comp != '':
                    _.append(comp)
        comps = _

        # Relative URL processing.
        _ = []
        for idx, comp in enumerate(comps):
            if comp == '..':
                if idx > 0:
                    del _[-1]
            elif comp == '.':
                # skip
                continue
            else:
                _.append(comp)
        else:
            if _ == []:
                _ = ['']
            if _[0] != '':
                _.insert(0, '')
        comps = _

        return tuple(comps)

    def create_cpath(self, *path_comps, is_file=False):
        """
        Create a Content Path object.
        """
        comps = self.to_comps(*path_comps)
        if not is_file:
            if comps[-1] != '':
                comps += ('', )
        else:
            assert comps[-1] != ''
        path_obj = self.__CPath(self, self.__site, comps, is_file=is_file)
        return path_obj

    def create_file_cpath(self, *path_comps):
        return self.create_cpath(*path_comps, is_file=True)

    def create_dir_cpath(self, *path_comps):
        return self.create_cpath(*path_comps, is_file=False)

    def exists(self, *path) -> bool:
        comps = self.to_comps(*path)
        """Checks existence relative to the root"""
        return True if os.path.exists(self.__full_path(comps)) else False

    def is_file(self, *path) -> bool:
        comps = self.to_comps(*path)
        fn = self.__full_path(comps)
        return True if os.path.isfile(fn) else False

    def is_dir(self, *path) -> bool:
        comps = self.to_comps(*path)
        fn = self.__full_path(comps)
        return True if os.path.isdir(fn) else False

    def join(self, *content_paths):
        comps = self.to_comps(*content_paths)
        return self.create_cpath(comps)

    def open(self, file_path, *args, **kwargs):
        comps = self.to_comps(file_path)
        fn = self.__full_path(comps)
        return open(fn, *args, **kwargs)

    def makedirs(self, *dir_path):
        comps = self.to_comps(*dir_path)
        full_p = self.__full_path(comps)
        os.makedirs(full_p)

    @staticmethod
    def join_comps(*comps):
        """Comps must be strings
        Replacement for os path join as that discards empty string instead of putting a forward slash there"""
        _ = []
        for idx, comp in enumerate(comps):
            assert type(comp) is str
            while comp.endswith(('/', '\\')):
                comp = comp[:-1]
            if idx > 0:
                while comp.startswith(('/', '\\')):
                    comp = comp[1:]

            if idx not in (0, len(comps) - 1):
                if comp == '':
                    # ignore empty string to avoid double slash in path
                    continue
            _.append(comp)
        return '/'.join(_)

    def get_full_path(self, *comps) -> str:
        comps = self.to_comps(*comps)
        return self.join_comps(self.__site.abs_site_path, *comps)

    def __full_path(self, comps):
        # for internal use only where there is no normalization needed with self.to_comps
        """Comma separated arguments of path components or os.sep separated paths"""
        return self.join_comps(self.__site.abs_site_path, *comps)

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
                # path_obj = self.__CPath(self, self.__site, path_comps, is_file=True)
                path_obj = self.create_cpath(path_comps, is_file=True)
                if checker is not None and not checker(path_obj):
                    move_in = False
                elif path_base.startswith(self.__ignore_files_sw):
                    move_in = False

                if move_in:
                    files.append(path_obj)

            elif os.path.isdir(path_abs) and (directories_only is True or directories_only is None):
                # path_obj = self.__CPath(self, self.__site, path_comps, is_file=False)
                path_obj = self.create_cpath(path_comps, is_file=False)
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
        if type(initial_path_comps) is self.__CPath:
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

    def is_type_cpath(self, other):
        return type(other) is self.__CPath

    class __CPath:
        """
        CPath => Content Path
        Convention:
        1. Content Path will be indicated as cpath
        2. String Path will be indicated as path
        """
        def __init__(self, path_tree, site, cpath_comps, is_file=True):
            self.__path_tree = path_tree
            self.__cpath_comps = cpath_comps
            self.__site = site
            self.__is_file = is_file
            if is_file:
                assert cpath_comps[-1] != ''
            else:
                assert cpath_comps[-1] == ''

        @property
        def site(self):
            return self.__site

        @property
        def parent_cpath(self):
            path_comps = self.path_comps
            if len(path_comps) <= 1:
                # contents/a-file
                # contents/dirA/b-file
                # * contents cannot have parent (==None) (Content Path is not for the site root or above dirs! SO -_-)
                return None
            new_comps = path_comps[:-1]
            pp = self.__path_tree.create_cpath(new_comps, is_file=False)
            assert pp.is_dir, "Logical error, inform the developer (Sabuj)"  # Just to be safe from future bug.
            return pp

        @property
        def parent_cpaths(self) -> tuple:
            parent_paths = deque()
            pp = self.parent_cpath
            while pp is not None:
                parent_paths.appendleft(pp)
                pp = pp.parent_cpath

            return tuple(parent_paths)

        @property
        def relative_path(self):
            """
            Relative paths are relative from site root.
            """
            return self.__path_tree.join_comps(*self.__cpath_comps).replace('\\', '/')

        @property
        def path_comps(self):
            comps = self.__cpath_comps
            # remove empty string from both ends
            if len(comps) > 1 and comps[-1] == '':
                comps = comps[:-1]
            if len(comps) > 1 and comps[0] == '':
                comps = comps[1:]
            return tuple(comps)

        @property
        def abs_path(self):
            return self.__path_tree.get_full_path(self.__cpath_comps)

        @property
        def is_file(self):
            return self.__is_file

        @property
        def is_dir(self):
            return not self.__is_file

        @property
        def basename(self):
            """
            Relative base name
            """
            return self.__cpath_comps[-1]

        @property
        def dirname_comps(self):
            """
            Relative dirname
            """
            return self.__cpath_comps[:-1]

        @property
        def extension(self, dot_count=1):
            if self.is_file:
                dotted_parts = self.basename.rsplit(".", maxsplit=dot_count)
                if not len(dotted_parts) < dot_count + 1:
                    return ".".join(dotted_parts[-dot_count:])
            return ''

        def list_paths(self, initial_comps=(), depth=None):
            comps = self.__path_tree.to_comps(initial_comps)
            comps = (*self.__cpath_comps, *comps)
            return self.__path_tree.list_cpaths(
                initial_path_comps=comps,
                depth=depth
            )

        def list_files(self, initial_comps=(), depth=None):
            comps = self.__path_tree.to_comps(initial_comps)
            comps = (*self.__cpath_comps, *comps)
            return self.__path_tree.list_file_cpaths(
                initial_path_comps=comps,
                depth=depth
            )

        def list_dirs(self, initial_comps=(), depth=None):
            comps = self.__path_tree.to_comps(initial_comps)
            comps = (*self.__cpath_comps, *comps)
            return self.__path_tree.list_dir_cpaths(
                initial_path_comps=comps,
                depth=depth
            )

        def exists(self):
            """Real time checking"""
            return self.__path_tree.exists(self.__cpath_comps)

        def open(self, mode, *args, **kwargs):
            assert self.is_file, 'Cannot call open() on a directory: %s' % self.relative_path
            return self.__path_tree.open(self.__cpath_comps, mode, *args, **kwargs)

        def join(self, *path_str_or_cmps, is_file=True):
            """Creates a new path joining to this one"""
            comps = self.__path_tree.to_comps(*path_str_or_cmps) # [p for p in re.split(r'[\\/]+', path_str) if p != '']
            if self.is_dir:
                new_path_comps = (*self.path_comps, *comps)
            else:
                new_path_comps = (*self.path_comps[:-1], self.path_comps[-1] + comps[0], *comps[1:])
            return self.__path_tree.create_cpath(new_path_comps, is_file=is_file)

        @staticmethod
        def __process_regex(regex, ignorecase=True):
            """Matches against relative path"""
            if isinstance(regex, str):
                if ignorecase:
                    regex = re.compile(regex, re.IGNORECASE)
                else:
                    regex = re.compile(regex, re.IGNORECASE)
            else:
                assert type(regex) is regex_type, "regex argument must provide compiled regular expression or string"
            return regex

        def match(self, regex, ignorecase=True):
            """Matches against relative path"""
            regex = self.__process_regex(regex, ignorecase)
            return regex.match(self.relative_path)

        def match_basename(self, regex, ignorecase=True):
            """"""
            regex = self.__process_regex(regex, ignorecase)
            return regex.match(self.basename)

        def match_extension(self, regex, ignorecase=True):
            """"""
            regex = self.__process_regex(regex, ignorecase)
            return regex.match(self.extension)

        def startswith(self, *comps):
            ccomps = self.__path_tree.to_comps(comps)
            if not (len(self.path_comps) < len(ccomps)):
                if self.path_comps[:len(ccomps)] == ccomps:
                    return True
            return False

        def endswith(self, *comps):
            ccomps = self.__path_tree.to_comps(comps)
            if not (len(self.path_comps) < len(ccomps)):
                if self.path_comps[-len(ccomps):] == ccomps:
                    return True
            return False

        def getmtime(self):
            return os.path.getmtime(self.abs_path)

        @property
        def id(self):
            return '/'.join(self.path_comps)

        def __eq__(self, other):
            if self.path_comps == other.path_comps:
                return True
            return False

        def __hash__(self):
            return hash(self.path_comps)

        def __str__(self):
            return "__CPath: %s" % self.relative_path

        def __repr__(self):
            return repr(str(self))