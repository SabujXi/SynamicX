import os
import re
from synamic.core.functions.decorators import loaded, not_loaded

regex_type = type(re.compile(""))


class ContentPath:
    META_FILE_EXTENSION = ".meta.yaml"

    def __init__(self, root_absolute_path, relative_path, module, is_file=True, is_meta=False):
        """
        Changelog:
            Intended: parameter list change from `relative_path, absolute_path` to `relative_path, root_absolute_path`
            :param module: 
        """
        self.__relative_path = relative_path
        self.__root_absolute_path = root_absolute_path
        self.__module = module
        self.__is_file = is_file
        self.__is_meta = is_meta

        self.__meta_path = None

        self.__ext = None

    @property
    def root_absolute_path(self):
        return self.__root_absolute_path

    @property
    def relative_path(self):
        """
        Relative paths are relative to own module.
        """
        return self.__relative_path

    @property
    def relative_path_from_root(self):
        return os.path.join(self.__module.config.get_module_root_dir(self.__module), self.__module.name, self.__relative_path)

    @property
    def relative_path_from_module_root(self):
        return os.path.join(self.__module.name, self.__relative_path)

    @property
    def absolute_path(self):
        return os.path.join(self.root_absolute_path, self.__module.config.get_module_root_dir(self.__module), self.__module.name, self.relative_path)

    @property
    def is_file(self, fresh_check=False):
        """
        
        :param fresh_check:
            Turning fresh check to True will check from the file system that the file is file. Same applies for is_dir
        """
        if fresh_check and self.__is_file:
            assert os.path.isfile(self.absolute_path)
        return self.__is_file

    @property
    def is_meta(self):
        return self.__is_meta

    @property
    def is_dir(self, fresh_check=False):
        if fresh_check and not self.__is_file:
            assert os.path.isdir(self.absolute_path)
        return not self.__is_file

    @property
    def basename(self):
        """
        Relative base name 
        """
        return os.path.basename(self.relative_path)

    @property
    def dirname(self):
        """
        Relative dirname 
        """
        return os.path.dirname(self.relative_path)

    @property
    def extension(self):
        if self.__ext is None:
            if self.is_file:
                basename = os.path.basename(self.relative_path)
                dotted_parts = basename.rsplit(".", maxsplit=1)
                if dotted_parts:
                    self.__ext = dotted_parts[-1]
                else:
                    self.__ext = ""
            else:
                self.__ext = ""
        return self.__ext

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
        The primary intention of providing meta file is providing custom url, id, name to the static files.
        So, it is redundant to add meta file for things like `.md` files. But, in future we can customize that behavior to add something extra.
        
        Meta files for directories:
            In future we can customize directory based behaviors with meta file for directories.
            Currently this feature will not be added.
            
        Possible future bug:
            `.meta.txt` being case sensitive, in users may provide extension in case insensitive ways and fail applications.
        """
        if self.__meta_path is None:
            mpf = os.path.join(self.basename, self.META_FILE_EXTENSION)
            abs_mp = os.path.join(self.root_absolute_path, self.dirname, mpf)
            if os.path.exists(abs_mp) and os.path.isfile(abs_mp):
                self.__meta_path = self.__class__(self.root_absolute_path, os.path.join(self.dirname, mpf), is_file=True, is_meta=True)
        return self.__meta_path

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

    def __list_paths_recursive(self, path_container: set, mod, next_relative_root=""):
        """
        A function to get all paths recursively starting from abs_root but returns a list of paths relative to the 
        .root
        :param mod: Module object"""

        """
        prefix_relative_root is fixed on every recursion
        BUT next_relative_root isn't
        """

        #  absolute_root = self.get_full_path(prefix_relative_root, next_relative_root)
        prefix_relative_root = os.path.join(mod.config.get_module_root_dir(mod), mod.name)
        absolute_root = self.get_full_path(prefix_relative_root, next_relative_root)
        # print("Absolute root: ", absolute_root)
        print(absolute_root)
        assert os.path.exists(absolute_root), "Absolute root must exist"

        for path in os.listdir(absolute_root):
            path_rel = os.path.join(next_relative_root, path)
            path_abs = self.get_full_path(prefix_relative_root, path_rel)
            if path_abs.endswith(ContentPath.META_FILE_EXTENSION):
                # Skipping if meta file
                continue
            if os.path.isfile(path_abs):
                path_obj = ContentPath(self.__config.site_root, path_rel, mod, is_file=True)
            elif os.path.isdir(path_abs):
                path_obj = ContentPath(self.__config.site_root, path_rel, mod, is_file=False)
                # Recurse
                self.__list_paths_recursive(path_container, mod, next_relative_root=path_rel)
            else:
                raise Exception("ContentPath is neither dir, nor file")
            path_container.add(path_obj)

    def __list_mod_paths(self, mod):
        path_container = set()
        self.__list_paths_recursive(path_container, mod)
        return path_container

    def __list_mod_files(self, mod):
        paths = self.__list_mod_paths(mod)
        file_paths = set()
        for path in paths:
            if path.is_file:
                file_paths.add(path)
        return file_paths

    def __list_mod_dirs(self, mod):
        paths = self.__list_mod_paths(mod)
        dir_paths = set()
        for path in paths:
            if path.is_dir:
                dir_paths.add(path)
        return dir_paths

    def get_full_path(self, *_path):
        """Comma separated arguments of path components or os.sep separated paths"""
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
        paths = self.__paths_by_content_modules.get(mod_obj.name)
        assert paths is not None, "Module name must exist"
        return paths

    def get_untracked_content_paths(self):
        return self.__other_paths

    def load(self):
        content_modules = self.__config.content_modules
        for mod in content_modules:
            self.__paths_by_content_modules[mod.name] = set()
            # dir = mod.directory_name
            file_paths = self.__list_mod_files(mod)

            if mod.extensions is None:
                # take all
                for x in file_paths:
                    self.__paths_by_content_modules[mod.name].add(x)
            else:
                for x in file_paths:
                    if x.extension.lower() in mod.extensions:
                        self.__paths_by_content_modules[mod.name].add(x)
                    else:
                        self.__other_paths.add(x)
