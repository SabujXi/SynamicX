import os
import re
from collections import deque
regex_type = type(re.compile(""))


class _CPath:
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

    @property
    def parent_cpath(self):
        if len(self.__cpath_comps) <= 1:
            # contents/a-file
            # contents/dirA/b-file
            # * contents cannot have parent (==None) (Content Path is not for the site root or above dirs! SO -_-)
            return None
        pp = self.__path_tree.create_cpath(self.path_comps[:-1])
        assert pp.is_dir, "Logical error, inform the developer (Sabuj)"  # Just to be safe from future bug.
        return pp

    @property
    def parent_cpaths(self) -> deque:
        parent_paths = deque()
        pp = self.parent_cpath
        while pp is not None:
            parent_paths.appendleft(pp)
            pp = pp.parent_path

        return parent_paths

    @property
    def relative_path(self):
        """
        Relative paths are relative from site root.
        """
        # print("*** rel path: %s" % str(self.relative_path_components))
        # return os.path.join(*self.__cpath_comps)
        return os.path.join(*self.__cpath_comps).replace('\\', '/')

    @property
    def path_comps(self):
        return tuple(self.__cpath_comps)

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

    def join(self, path_str_or_cmps, is_file=True):
        """Creates a new path joining to this one"""
        comps = self.__path_tree.to_comps(path_str_or_cmps)  # [p for p in re.split(r'[\\/]+', path_str) if p != '']
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
        return "_CPath: %s" % self.relative_path

    def __repr__(self):
        return repr(str(self))
