import os
import re
from synamic.core.functions.normalizers import normalize_relative_file_path
from synamic.core.functions.yaml_processor import load_yaml
from synamic.core.functions.normalizers import normalize_keys
from collections import deque


regex_type = type(re.compile(""))


class ContentPath2:
    META_FILE_EXTENSION = ".meta.yaml"

    def __init__(self, root_absolute_path, relative_path_comps, comp_relative_starting_idx=0, is_file=True, is_meta=False):

        self.__relative_path_comps = relative_path_comps
        self.__root_absolute_path = root_absolute_path
        self.__relative_start_idx = comp_relative_starting_idx
        self.__is_file = is_file
        self.__is_meta = is_meta

        self.__meta_info = dict()
        self.__meta_path = None

    @property
    def root_absolute_path(self):
        return self.__root_absolute_path

    @property
    def relative_path(self):
        """
        Relative paths are relative from site root.
        """
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
        return os.path.dirname(self.__relative_path_comps[:-1])

    @property
    def extension(self, dot_count=1):
        if self.is_file:
            dotted_parts = self.basename.rsplit(".", maxsplit=dot_count)
            if not len(dotted_parts) < dot_count + 1:
                return ".".join(dotted_parts[-dot_count:])
        return None

    @property
    def exists(self):
        """Real time checking"""
        return os.path.exists(self.__root_absolute_path)

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
            mpf = self.basename + self.META_FILE_EXTENSION
            abs_mp = os.path.join(os.path.dirname(self.absolute_path), mpf)
            if os.path.exists(abs_mp) and os.path.isfile(abs_mp):
                self.__meta_path = self.__class__(self.root_absolute_path, os.path.join(self.dirname, mpf), is_file=True, is_meta=True)
        return self.__meta_path

    @property
    def meta_info(self):
        if not self.__meta_info:
            if self.meta_path:
                with open(self.meta_path.absolute_path, 'r', encoding='utf-8') as f:
                    txt = f.read()
                    loaded = load_yaml(txt)
                    if type(loaded) is dict:
                        self.__meta_info = loaded
                    elif type(loaded) is not dict:
                        self.__meta_info = {'__error_info_': "Meta file content could not be loaded as dict"}
                normalize_keys(self.__meta_info)
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


class PathTree(object):
    def __init__(self, _cfg):
        assert os.path.isdir(_cfg.site_root), "FileTree.__init__: _root must be a directory, `%s`" % _cfg.site_root
        self.__config = _cfg

        # Paths are reserved by modules.
        # Once a module reserves a path other modules cannot use that.
        self.__paths_by_content_modules = {}
        self.__other_paths = set()

    def __list_paths_loop2(self, starting_components=()):
        """
        A function to get all paths recursively starting from abs_root but returns a list of paths relative to the 
        .root
        prefix_relative_root is fixed on every recursion
        BUT next_relative_root isn't
        """
        for x in starting_components:
            assert '/' not in x and '\\' not in x

        absolute_root = self.get_full_path(*starting_components)
        assert os.path.exists(absolute_root), "Absolute root must exist: %s" % absolute_root

        # new
        to_travel = deque([(*starting_components, comp) for comp in os.listdir(absolute_root)])
        # print("to travel:", to_travel)
        directories = []
        files = []

        # pos = 0
        while len(to_travel) != 0:
            path_comps = to_travel.popleft()
            path = path_comps[-1]
            path_abs = self.get_full_path(*path_comps)
            if path.lower().endswith(ContentPath2.META_FILE_EXTENSION.lower()):
                # Skipping if meta file
                continue
            if os.path.isfile(path_abs):
                path_obj = ContentPath2(absolute_root, path_comps, comp_relative_starting_idx=len(starting_components), is_file=True)
                files.append(path_obj)
            elif os.path.isdir(path_abs):
                path_obj = ContentPath2(absolute_root, path_comps, comp_relative_starting_idx=len(starting_components), is_file=False)
                directories.append(path_obj)
                # Recurse
                to_travel.extend(tuple([(*path_comps, comp) for comp in os.listdir(path_abs)]))
            else:
                raise Exception("ContentPath is neither dir, nor file")
        return directories, files

    def __list_mod_paths(self, mod):
        starting_comps = (self.__config.get_module_root_dir(mod), mod.name)
        return self.__list_paths_loop2(starting_comps)

    def __list_mod_files(self, mod):
        dirs, files = self.__list_mod_paths(mod)
        return files

    def __list_mod_dirs(self, mod):
        ds, fs = self.__list_mod_paths(mod)
        return ds

    def get_full_path(self, *_path):
        """Comma separated arguments of path components or os.sep separated paths"""
        # print(repr(_path))
        return os.path.join(self.__config.site_root, *_path)

    def get_full_path_by_module(self, mod, *_path):
        return os.path.join(self.__config.site_root, mod.name, *_path)

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

    def get_module_paths(self, mod_obj):
        paths = self.__list_mod_files(mod_obj)
        assert paths is not None, "Module name must exist"
        return paths

    def load(self):
        """Nothing to do! This should just stay idle and return"""

    def open_file(self, file_name, *args, **kwargs):
        fn = self.get_full_path(file_name)
        return open(fn, *args, **kwargs)
