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
from synamic.core.new_parsers.document_parser import FieldParser, Field
from collections import OrderedDict
from typing import Union

regex_type = type(re.compile(""))


class ContentPath2:
    META_FILE_EXTENSION = ".meta.txt"

    def __init__(self, path_tree, site_root, path_comps, is_file=True, is_meta=False):
        if not is_file:
            assert is_meta is False, "Directories cannot be meta"

        self.__path_tree = path_tree
        self.__path_comps = path_comps
        self.__site_root = site_root
        self.__is_file = is_file
        self.__is_meta = is_meta

        self.__meta_info = OrderedDict()
        self.__merged_meta_info = OrderedDict()
        self.__meta_path = None

    # def parent_dir_path(self):
    #     path_comps = self.path_components
    #     if len(path_comps) in (0, 1):
    #         raise Exception("Not allowed to query the paths parent of site root")
    #     # elif len(path_comps) == 1:
    #     #     return self.__path_tree.site_root_path
    #     else:
    #         return self.__path_tree.get_path(self.path_components[:-1])

    @property
    def parent_path(self):
        if len(self.__path_comps) <= 1:
            # contents/a-file
            # contents/dirA/b-file
            # * contents cannot have parent (==None) (Content Path is not for the site root or above dirs! SO -_-)
            return None
        pp = self.__path_tree.create_path(self.path_components[:-1])
        assert pp.is_dir, "Logical error, inform the developer (Sabuj)"  # Just to be safe from future bug.
        return pp

    @property
    def parent_paths(self) -> deque:
        parent_paths = deque()
        pp = self.parent_path
        while pp is not None:
            parent_paths.appendleft(pp)
            pp = pp.parent_path

        return parent_paths

    @property
    def site_root(self):
        return self.__site_root

    @property
    def relative_path(self):
        """
        Relative paths are relative from site root.
        """
        # print("*** rel path: %s" % str(self.relative_path_components))
        return os.path.join(*self.__path_comps)

    @property
    def norm_relative_path(self):
        """
        Relative normalized paths are relative to own module_object.
        """
        return os.path.join(*[p.lower() for p in self.__path_comps])

    @property
    def path_components(self):
        return self.__path_comps

    @property
    def norm_path_components(self):
        return tuple((p.lower() for p in self.__path_comps))

    @property
    def absolute_path(self):
        # print("ROOT ABSOLUTE PATH: %s" % self.root_absolute_path)
        # print("RELATIVE PATH COMPONENTS: %s" % str(self.__relative_path_comps))
        return os.path.join(self.site_root, *self.__path_comps)

    @property
    def is_file(self):
        return self.__is_file

    @property
    def is_meta(self):
        return self.__is_meta

    @property
    def is_dir(self):
        return not self.__is_file

    @property
    def basename(self):
        """
        Relative base name 
        """
        return self.__path_comps[-1]

    @property
    def dirname(self):
        """
        Relative dirname 
        """
        return self.__path_comps[:-1]

    @property
    def extension(self, dot_count=1):
        if self.is_file:
            dotted_parts = self.basename.rsplit(".", maxsplit=dot_count)
            if not len(dotted_parts) < dot_count + 1:
                return ".".join(dotted_parts[-dot_count:])
        return None

    def list_paths(self, initial_comps=(), depth=None):
        comps = self.__path_tree.to_components(initial_comps)
        comps = (*self.__path_comps, *comps)
        return self.__path_tree.list_paths(
            initial_path_comps=comps,
            depth=depth
        )

    def list_files(self, initial_comps=(), depth=None):
        comps = self.__path_tree.to_components(initial_comps)
        comps = (*self.__path_comps, *comps)
        return self.__path_tree.list_file_paths(
            initial_path_comps=comps,
            depth=depth
        )

    def list_dirs(self, initial_comps=(), depth=None):
        comps = self.__path_tree.to_components(initial_comps)
        comps = (*self.__path_comps, *comps)
        return self.__path_tree.list_dir_paths(
            initial_path_comps=comps,
            depth=depth
        )

    def exists(self):
        """Real time checking"""
        # print("__REL PATH: %s" % self.relative_path)
        return self.__path_tree.exists(self.path_components)

    def open(self, mode, *args, **kwargs):
        return self.__path_tree.open(self.path_components, mode, *args, **kwargs)

    def join(self, path_str_or_cmps, is_file=True, is_meta=False):
        """Creates a new path joining to this one"""
        comps = self.__path_tree.to_components(path_str_or_cmps)  # [p for p in re.split(r'[\\/]+', path_str) if p != '']
        if self.is_dir:
            new_path_comps = (*self.path_components, *comps)
        else:
            new_path_comps = (*self.path_components[:-1], self.path_components[-1] + comps[0], *comps[1:])
        return self.__path_tree.create_path(new_path_comps, is_file=is_file, is_meta=is_meta)

    @property
    def meta_path(self):
        """
        Returns a path object or None - not a string. Meta paths must return None for the same case.

        Meta files are the FILES that have `.meta.txt` extension at the end of them (case sensitive).
        Meta files can exist both for:
            - directory
            - files
        Every file does not need to have a meta file.
        The primary intention of providing meta file is providing custom url_object, id, name to the static files.
        So, it is redundant to add meta file for things like `.md` files. But, in future we can customize that behavior to add something extra.

        Meta files for directories:
            In future we can customize directory based behaviors with meta file for directories.
            Currently this feature will not be added.

        Possible future bug:
            `.meta.txt` being case sensitive, in users may provide extension in case insensitive ways and fail applications.
        """
        if self.__meta_path is None:
            if self.is_file:
                comps = "." + self.basename + self.META_FILE_EXTENSION #(*self.path_components[:-1], "." + self.basename + self.META_FILE_EXTENSION)
            else:
                assert self.is_dir, "Logical error"  # just for detecting future bug.
                comps = self.META_FILE_EXTENSION #(*self.path_components, self.META_FILE_EXTENSION)
            meta_path = self.join(comps, is_file=True, is_meta=True)
            # print("Meta Path `%s` Comps `%s` for `%s`" % (meta_path, comps, self.path_components))
            if meta_path.exists():
                """
                Files have meta path like: file_name.meta.txt
                Directories: dir_name/.meta.txt
                """
                self.__meta_path = meta_path
        return self.__meta_path

    @property
    def meta_info(self):
        """
         Meta fields are flat. That means they have depth of one.
         So, it is key->value pairs - no nested things.
        """
        if not self.__meta_info:
            if self.meta_path:
                with self.meta_path.open('r', encoding='utf-8') as f:
                    txt = f.read()
                    root_field = FieldParser(txt).parse()
                    self.__meta_info = root_field.to_dict_ordinary()
        return self.__meta_info

    @property
    def merged_meta_info(self):
        if not self.__merged_meta_info:
            merged_map = OrderedDict()
            for pp in self.parent_paths:
                p_meta_info = pp.meta_info
                if p_meta_info:
                    for key, value in p_meta_info.items():
                        merged_map[key] = value

            if self.meta_info:
                for key, value in self.meta_info:
                    merged_map[key] = value
            self.__merged_meta_info = merged_map
        return self.__merged_meta_info

    def __match_process_regex(self, regex, ignorecase=True):
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
        regex = self.__match_process_regex(regex, ignorecase)
        return regex.match(self.relative_path)

    def match_basename(self, regex, ignorecase=True):
        """"""
        regex = self.__match_process_regex(regex, ignorecase)
        return regex.match(self.basename)

    def match_extension(self, regex, ignorecase=True):
        """"""
        regex = self.__match_process_regex(regex, ignorecase)
        return regex.match(self.extension)

    def __eq__(self, other):
        if self.path_components == other.path_components:
            return True
        return False

    def __hash__(self):
        return hash(self.path_components)

    def __str__(self):
        return "ContentPath2: %s" % self.relative_path

    def __repr__(self):
        return repr(str(self))


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
