import os
import re

regex_type = type(re.compile(""))


class Path:
    def __init__(self, relative_path, absolute_path, is_file=True):
        self.__relative_path = relative_path
        self.__absolute_path = absolute_path
        self.__is_file = is_file

        self.__ext = None

    @property
    def relative_path(self):
        return self.__relative_path

    @property
    def absolute_path(self):
        return self.__absolute_path

    @property
    def is_file(self):
        return self.__is_file

    @property
    def is_dir(self):
        return not self.__is_file

    @property
    def basename(self):
        return os.path.basename(self.relative_path)

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
        return os.path.exists(self.__absolute_path)

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

    def __list_paths_recursive(self, path_container: set, next_relative_root="", prefix_relative_root=""):
        """A function to get all paths recursively starting from abs_root but returns a list of paths relative to the 
        .root"""

        """
        prefix_relative_root is fixed on every recursion
        BUT next_relative_root isn't
        """

        absolute_root = self.get_full_path(prefix_relative_root, next_relative_root)
        print("Absolute root: ", absolute_root)
        assert os.path.exists(absolute_root), "Absolute root must exist"

        for path in os.listdir(absolute_root):
            path_rel = os.path.join(next_relative_root, path)
            path_abs = self.get_full_path(prefix_relative_root, path_rel)

            if os.path.isfile(path_abs):
                path_obj = Path(path_rel, path_abs, True)
            elif os.path.isdir(path_abs):
                path_obj = Path(path_rel, path_abs, False)
                # Recurse
                self.__list_paths_recursive(path_container, next_relative_root=path_rel, prefix_relative_root=prefix_relative_root)
            else:
                raise Exception("Path is neither dir, nor file")
            path_container.add(path_obj)

    def __list_paths(self, relative_root="", prefix_relative_root=""):
        path_container = set()
        self.__list_paths_recursive(path_container, relative_root, prefix_relative_root=prefix_relative_root)
        return path_container

    def __list_files(self, relative_root="", prefix_relative_root=""):
        paths = self.__list_paths(relative_root=relative_root, prefix_relative_root=prefix_relative_root)
        file_paths = set()
        for path in paths:
            if path.is_file:
                file_paths.add(path)
        return file_paths

    def __list_dirs(self, relative_root="", prefix_relative_root=""):
        paths = self.__list_paths(relative_root=relative_root, prefix_relative_root=prefix_relative_root)
        dir_paths = set()
        for path in paths:
            if path.is_dir:
                dir_paths.add(path)
        return dir_paths

    def get_full_path(self, *_path):
        """Comma separated arguments of path components or os.sep separated paths"""
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
            file_paths = self.__list_files(relative_root=mod.directory_name, prefix_relative_root=self.__config.get_module_root_dir(mod))

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
