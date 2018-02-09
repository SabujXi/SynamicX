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
from synamic.core.functions.normalizers import normalize_relative_file_path
from synamic.core.functions.yaml_processor import load_yaml
from synamic.core.functions.normalizers import normalize_keys
from collections import deque
from synamic.core.new_parsers.document_parser import FieldParser, Field
from collections import OrderedDict

regex_type = type(re.compile(""))


class ContentPath2:
    META_FILE_EXTENSION = ".meta.txt"

    def __init__(self, path_tree, root_absolute_path, relative_path_comps, comp_relative_starting_idx=0, is_file=True, is_meta=False):
        self.__path_tree = path_tree
        self.__relative_path_comps = relative_path_comps
        self.__root_absolute_path = root_absolute_path
        self.__relative_start_idx = comp_relative_starting_idx
        self.__is_file = is_file
        self.__is_meta = is_meta

        self.__meta_info = OrderedDict()
        self.__meta_path = None

    @property
    def root_absolute_path(self):
        return self.__root_absolute_path

    @property
    def relative_path(self):
        """
        Relative paths are relative from site root.
        """
        print("*** rel path: %s" % str(self.relative_path_components))
        return os.path.join(*self.__relative_path_comps)

    @property
    def relative_path_components(self):
        return self.__relative_path_comps

    @property
    def normalized_relative_path(self):
        """
        Relative normalized paths are relative to own module_object.
        """
        p = normalize_relative_file_path(self.relative_path)
        return p

    @property
    def listing_relative_path(self):
        """
        Relative to where they were started listing 
        """
        return os.path.join(*self.__relative_path_comps[self.__relative_start_idx:])

    @property
    def normalized_listing_relative_path(self):
        """
        Relative to where they were started listing 
        """
        return normalize_relative_file_path(self.listing_relative_path)

    @property
    def absolute_path(self):
        print("ROOT ABSOLUTE PATH: %s" % self.root_absolute_path)
        print("RELATIVE PATH COMPONENTS: %s" % str(self.__relative_path_comps))
        return os.path.join(self.root_absolute_path, *self.__relative_path_comps)

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
        return self.__relative_path_comps[-1]

    @property
    def dirname(self):
        """
        Relative dirname 
        """
        return os.path.dirname(self.__relative_path_comps[-1])

    @property
    def extension(self, dot_count=1):
        if self.is_file:
            dotted_parts = self.basename.rsplit(".", maxsplit=dot_count)
            if not len(dotted_parts) < dot_count + 1:
                return ".".join(dotted_parts[-dot_count:])
        return None

    def list_paths(self, initial_path='', files_only=None, directories_only=None, depth=None):
        return self.__path_tree.list_paths(
            initial_path=initial_path,
            files_only=files_only,
            directories_only=directories_only,
            depth=depth
        )

    def list_files(self):
        pass

    def list_dirs(self):
        pass

    def exists(self):
        """Real time checking"""
        print("__REL PATH: %s" % self.relative_path)
        return self.__path_tree.exists(self.relative_path)

    def parent_dir_path(self):
        path_comps = self.relative_path_components
        if len(path_comps) == 0:
            raise Exception("Not allowed to query the paths parent of site root")
        elif len(path_comps) == 1:
            return self.__path_tree.site_root_path
        else:
            return self.__path_tree.get(self.relative_path_components[:-1])

    def open(self, mode, *args, **kwargs):
        return self.__path_tree.open_file(self.relative_path, mode, *args, **kwargs)

    def join(self, path_str, is_file=True, is_meta=False):
        """Creates a new path joining to this one"""
        comps = [p for p in re.split(r'[\\/]+', path_str) if p != '']
        if self.is_dir:
            new_path_comps = (*self.relative_path_components, *comps)
        else:
            new_path_comps = (*self.relative_path_components[:-1], self.relative_path_components[-1] + comps[0], *comps[1:])
        return ContentPath2(self.__path_tree, self.root_absolute_path, new_path_comps, comp_relative_starting_idx=self.__relative_start_idx, is_file=is_file, is_meta=is_meta)

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
            meta_path = self.join(self.META_FILE_EXTENSION, is_file=True, is_meta=True)
            if meta_path.exists():
                """
                Files have meta path like: file_name.meta.txt
                Directories: dir_name/.meta.txt
                """
                self.__meta_path = meta_path
        return self.__meta_path

    @property
    def meta_info(self):
        if not self.__meta_info:
            if self.meta_path:
                with self.meta_path.open('r', encoding='utf-8') as f:
                    txt = f.read()
                    root_field = FieldParser(txt).parse()
                    self.__meta_info = root_field.to_dict_ordinary()
        return self.__meta_info

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
        if self.relative_path_components == other.relative_path_components:
            return True
        return False

    def __hash__(self):
        return hash(self.relative_path_components)

    def __str__(self):
        return "ContentPath2: %s" % self.relative_path

    def __repr__(self):
        return repr(str(self))


class PathTree(object):
    def __init__(self, _cfg):
        assert os.path.isdir(_cfg.site_root), "FileTree.__init__: _root must be a directory, `%s`" % _cfg.site_root
        self.__config = _cfg

        self.__site_root_path = ContentPath2(self, self.__config.site_root, (), is_file=False)
        self.__paths_map = {}

    @property
    def site_root_path(self):
        return self.__site_root_path

    def add_path(self, path: ContentPath2):
        assert type(path) is ContentPath2
        assert path.exists()
        p = self.__paths_map.get(path, None)
        if p is None:
            self.__paths_map[path.relative_path_components] = path
        return p

    def get_path(self, comps):
        assert type(comps) is tuple
        path = self.__paths_map.get(comps, None)
        if path is not None:
            return path
        else:
            # if self.exists(comps):
            #
            return None

    def __contains__(self, comps):
        if type(comps) is tuple:
            return comps in self.__paths_map
        elif type(comps) is ContentPath2:
            return comps.relative_path_components in self.__paths_map
        else:
            raise Exception("Invalid type provided")

    def __list_paths_loop2(self, starting_components=(), files_only=None, directories_only=None, depth=None):
        """
        A function to get all paths recursively starting from abs_root but returns a list of paths relative to the 
        .root
        prefix_relative_root is fixed on every recursion
        BUT next_relative_root isn't
        """
        print("Starting Components in list path loop: %s" % str(starting_components))
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

        absolute_root = self.get_full_path(*starting_components)
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
            path_abs = self.get_full_path(*path_comps)
            if path.lower().endswith(ContentPath2.META_FILE_EXTENSION.lower()):
                # Skipping if meta file
                continue
            if path.startswith('.'):
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
                        path_obj = ContentPath2(self, absolute_site_root, path_comps, comp_relative_starting_idx=len(starting_components), is_file=True)
                        files.append(path_obj)
                        self.__paths_map[path_comps] = path_obj
                elif os.path.isdir(path_abs):
                    if directories_only is True or directories_only is None:
                        path_obj = ContentPath2(self, absolute_site_root, path_comps, comp_relative_starting_idx=len(starting_components), is_file=False)
                        directories.append(path_obj)
                        self.__paths_map[path_comps] = path_obj
                        # Recurse
                    to_travel.extend(tuple([((*path_comps, comp), path_depth + 1) for comp in os.listdir(path_abs)]))
                else:
                    raise Exception("ContentPath is neither dir, nor file")
        return directories, files

    def get_full_path(self, *_path):
        """Comma separated arguments of path components or os.sep separated paths"""
        print(repr((self.__config.site_root, *_path)))
        return os.path.join(self.__config.site_root, *_path)

    def exists(self, *_path):
        """Checks existence relative to the root"""
        return True if os.path.exists(self.get_full_path(*_path)) else False

    def join(self, *_paths):
        return os.path.join(*_paths)

    def exists_file(self, *_path):
        full_path = self.get_full_path(*_path)
        return True if os.path.exists(full_path) and os.path.isfile(full_path) else False

    def exists_dir(self, _path):
        full_path = self.get_full_path(*_path)
        return True if os.path.exists(full_path) and os.path.isdir(full_path) else False

    def list_paths(self, initial_path='', files_only=None, directories_only=None, depth=None):
        if initial_path == '':
            starting_comps = ()
        else:
            starting_comps = tuple(re.split(r'\\|/', initial_path))
        dirs, files = self.__list_paths_loop2(starting_comps, files_only=files_only, directories_only=directories_only,
                                              depth=depth)
        return dirs, files

    def list_file_paths(self, initial_path='', files_only=None, directories_only=None, depth=None):
        if initial_path == '':
            starting_comps = ()
        else:
            starting_comps = tuple(re.split(r'\\|/', initial_path))
        dirs, files = self.__list_paths_loop2(starting_comps, files_only=files_only, directories_only=directories_only,
                                       depth=depth)
        return files

    def list_dir_paths(self, initial_path='', files_only=None, directories_only=None, depth=None):
        if initial_path == '':
            starting_comps = ()
        else:
            starting_comps = tuple(re.split(r'\\|/', initial_path))
        dirs, files = self.__list_paths_loop2(starting_comps, files_only=files_only, directories_only=directories_only,
                                       depth=depth)
        return dirs

    def open_file(self, file_name, mode, *args, **kwargs):
        fn = self.get_full_path(file_name)
        return open(fn, mode, *args, **kwargs)

    def makedirs(self, dir_path):
        full_p = self.get_full_path(dir_path)
        os.makedirs(full_p)

    def create_path(self, path_comp, is_file=False):
        """
        Create a Content Path object.
        """
        if type(path_comp) is str:
            path_str = path_comp
            assert path_str.strip() != ''
            comps = [x for x in re.split(r'[\\/]+', path_str) if x != '']
        else:
            assert type(path_comp) in {tuple, set, frozenset, list}
            comps = path_comp
        path_obj = ContentPath2(self, self.__config.site_root, comps, is_file=is_file)
        return path_obj
