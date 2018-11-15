"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
import re
from collections import deque
from synamic.core.contracts import BaseFsBackendContract
from .backends import FileSystemBackend
from synamic.core.contracts import HostContract, SiteContract, SynamicContract
from synamic.exceptions import SynamicInvalidCPathComponentError
from synamic.core.standalones.functions.sequence_ops import Sequence


regex_type = type(re.compile(""))
from synamic.core.standalones.functions.decorators import loaded, not_loaded


class _Patterns:
    path_sep = re.compile(r'[\\/]+')


class PathTree(object):
    def __init__(self, host):
        assert isinstance(host, HostContract)
        self.__host = host
        # TODO: assert os.path.isdir(host.site_root), "FileTree.__init__: _root must be a directory, `%s`"
        #  % host.site_root

        # default backend system
        self.__fs = FileSystemBackend()
        self.__is_loaded = False

    @classmethod
    def for_site(cls, site):
        assert isinstance(site, SiteContract)
        return cls(site)

    @property
    def host(self):
        return self.__host

    @property
    def is_site_host(self):
        return isinstance(self.__host, SiteContract)

    @property
    def is_synamic_host(self):
        return isinstance(self.__host, SynamicContract)

    @property
    def fs(self):
        return self.__fs

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
                raise SynamicInvalidCPathComponentError(
                    f'Invalid component type for path: {type(path_comp)} whose value is {path_comp}'
                )

        return str_comps

    @classmethod
    def to_cpath_ccomps(cls, *path_comps):
        """Creates special cpath components that can have '' empty string on both ends
        To get components (without empty string on both ends) use path_comps property on cpath object"""
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
                raise SynamicInvalidCPathComponentError(
                    f"Path comps must be list, tuple, string or __CPath object when it is not string: {type(path_comp)}"
                    f" where value is {path_comp}"
                )

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

    @classmethod
    def to_path_comps(cls, *path_comps):
        """The one returned by CPath.path_comps"""
        ccomps = cls.to_cpath_ccomps(*path_comps)
        # remove empty string from both ends
        if len(ccomps) > 1 and ccomps[-1] == '':
            ccomps = ccomps[:-1]
        if len(ccomps) > 1 and ccomps[0] == '':
            ccomps = ccomps[1:]

        comps = ccomps
        return comps

    def create_cpath(self, *path_comps, is_file=False, forgiving=False):
        """
        Create a Content Path object.
        :forgiving: if forgiving is True then it will not consider a result of path component ending in '' to be error.
            This method is only for end user who do not know deep details or for from template or when you want a relaxed
            way of doing things * Must not use in synamic core development.*
        """
        ccomps = self.to_cpath_ccomps(*path_comps)
        if not is_file:  # directory
            if ccomps[-1] != '':
                ccomps += ('', )
        else:  # file
            if not forgiving:  # is file & not forgiving
                assert ccomps[-1] != ''
            else:  # is file & forgiving.
                if len(ccomps) > 1 and ccomps[-1] == '':
                    ccomps = ccomps[:-1]

        path_obj = self.__CPath(self, self.__host, ccomps, is_file=is_file)
        return path_obj

    def create_file_cpath(self, *path_comps, forgiving=False):
        return self.create_cpath(*path_comps, is_file=True, forgiving=forgiving)

    def create_dir_cpath(self, *path_comps, forgiving=False):
        return self.create_cpath(*path_comps, is_file=False, forgiving=forgiving)

    def exists(self, *path) -> bool:
        comps = self.to_cpath_ccomps(*path)
        """Checks existence relative to the root"""
        return True if self.__fs.exists(self.__full_path__(comps)) else False

    def is_file(self, *path) -> bool:
        comps = self.to_cpath_ccomps(*path)
        fn = self.__full_path__(comps)
        return True if self.__fs.is_file(fn) else False

    def is_dir(self, *path) -> bool:
        comps = self.to_cpath_ccomps(*path)
        fn = self.__full_path__(comps)
        return True if self.__fs.is_dir(fn) else False

    def join(self, *content_paths):
        comps = self.to_cpath_ccomps(*content_paths)
        return self.create_cpath(comps)

    def open(self, file_path, *args, **kwargs):
        comps = self.to_cpath_ccomps(file_path)
        fn = self.__full_path__(comps)
        return open(fn, *args, **kwargs)

    def makedirs(self, *dir_path):
        comps = self.to_cpath_ccomps(*dir_path)
        full_p = self.__full_path__(comps)
        self.__fs.makedirs(full_p)

    @staticmethod
    def join_comps(*comps):
        """Comps must be strings
        Replacement for os path join as that discards empty string instead of putting a forward slash there"""
        _ = []
        for idx, comp in enumerate(comps):
            assert isinstance(comp, str), f'Provided type {type(comp)}'
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
        comps = self.to_cpath_ccomps(*comps)
        return self.join_comps(self.__host.abs_root_path, *comps)

    def __full_path__(self, comps):
        # for internal use only where there is no normalization needed with self.to_cpath_comps
        """Comma separated arguments of path components or os.sep separated paths"""
        return self.join_comps(self.__host.abs_root_path, *comps)

    def __list_cpaths_loop2(self, starting_comps=(), files_only=None, directories_only=None, depth=None, exclude_cpaths=(), checker=None, respect_settings=True):
        return self.__ListCPathsLoop(
            self,
            starting_comps=starting_comps,
            files_only=files_only,
            directories_only=directories_only,
            depth=depth,
            exclude_cpaths=exclude_cpaths,
            checker=checker,
            respect_settings=respect_settings)()

    def list_cpaths(self, initial_path_comps=(), files_only=None, directories_only=None, depth=None, exclude_compss=(), checker=None):
        if type(initial_path_comps) is self.__CPath:
            assert initial_path_comps.is_dir
            starting_comps = initial_path_comps.path_comps
        else:
            starting_comps = self.to_cpath_ccomps(initial_path_comps)
        _exclude_compss = []
        for pc in exclude_compss:
            _exclude_compss.append(self.to_cpath_ccomps(pc))
        exclude_compss = tuple(_exclude_compss)

        dirs, files = self.__list_cpaths_loop2(starting_comps, files_only=files_only, directories_only=directories_only, depth=depth, exclude_cpaths=exclude_compss, checker=checker)
        return dirs, files

    def list_file_cpaths(self, initial_path_comps=(), depth=None, exclude_compss=(), checker=None):
        _, files = self.list_cpaths(initial_path_comps, files_only=True, depth=depth, exclude_compss=exclude_compss, checker=checker)
        return files

    def list_dir_cpaths(self, initial_path_comps='', depth=None, exclude_compss=(), checker=None):
        dirs, _ = self.list_cpaths(initial_path_comps, directories_only=True, depth=depth, exclude_compss=exclude_compss, checker=checker)
        return dirs

    def is_type_cpath(self, other):
        return type(other) is self.__CPath

    def __set_fs__(self, fs_instance):
        assert isinstance(fs_instance, BaseFsBackendContract)
        self.__fs = fs_instance

    class __ListCPathsLoop:
        def __init__(self, path_tree, starting_comps=(), files_only=None, directories_only=None, depth=None, exclude_cpaths=None, checker=None, respect_settings=True):
            self.path_tree = path_tree
            self.starting_comps = None
            self.files_only = files_only
            self.directories_only = directories_only
            self.depth = depth
            self.exclude_cpaths = None
            self.checker = checker
            self.respect_settings = respect_settings

            if starting_comps is None:
                self.starting_comps = ()
            else:
                self.starting_comps = self.path_tree.to_path_comps(starting_comps)

            for exclude_comps in exclude_cpaths:
                assert type(exclude_comps) is tuple, f"exclude_cpaths must contain tuple of strings as path." \
                                                     f" {exclude_comps} found"

            # check that files only and directories only both are not set to the Truth value
            if files_only is True:
                assert directories_only is not True
            if directories_only is True:
                assert files_only is not True

            # depth
            assert isinstance(depth, (type(None), int)), f"Type of depth must be None or int, {type(depth)}" \
                                                             f" found with value {depth}"
            if depth is None:
                self.depth = 2147483647

            # exclude cpaths validation
            _ = set()
            if exclude_cpaths is None:
                exclude_cpaths = set()
            for exclude_cpath in exclude_cpaths:
                assert self.path_tree.is_type_cpath(exclude_cpath)
                _.add(exclude_cpath)
            else:
                self.exclude_cpaths = _

            # default configs
            _dc = self.path_tree.host.system_settings['configs']
            self.__ignore_dirs_sw = _dc.get('ignore_dirs_sw', None)
            self.__ignore_files_sw = _dc.get('ignore_files_sw', None)

        def __call__(self, *args, **kwargs):
            """
                    A function to get all paths recursively starting from abs_root but returns a list of paths relative to the
                    .root
                    prefix_relative_root is fixed on every recursion
                    BUT next_relative_root isn't

                    exclude_comps_tuples: *components* list that are excluded from listing
                    checker: callables that accepts parameters: __ContentPath2 instance.
                    """
            absolute_root = self.path_tree.__full_path__(self.starting_comps)
            assert self.path_tree.fs.exists(absolute_root), f"Absolute root must exist: {absolute_root}"

            # new
            to_travel = deque([((*self.starting_comps, comp), 1) for comp in self.path_tree.fs.listdir(absolute_root)])
            directories = []
            files = []

            while len(to_travel) != 0:
                path_comps_n_depth = to_travel.popleft()
                path_comps = path_comps_n_depth[0]
                path_depth = path_comps_n_depth[1]
                if path_depth > self.depth:
                    break
                path_base = path_comps[-1]
                path_abs = self.path_tree.__full_path__(path_comps)

                if self.path_tree.fs.is_file(path_abs) and (self.files_only in (True, None)):
                    move_in = True
                    path_obj = self.path_tree.create_cpath(path_comps, is_file=True)
                    if self.checker is not None and not self.checker(path_obj):
                        move_in = False

                    elif self.respect_settings and path_base.startswith(self.__ignore_files_sw):
                        move_in = False

                    elif path_obj in self.exclude_cpaths:
                        move_in = False

                    if move_in:
                        files.append(path_obj)

                elif self.path_tree.fs.is_dir(path_abs) and (self.directories_only in (True, None)):
                    path_obj = self.path_tree.create_cpath(path_comps, is_file=False)
                    move_in = True
                    if self.checker is not None and not self.checker(path_obj):
                        move_in = False

                    elif self.respect_settings and path_base.startswith(self.__ignore_dirs_sw):
                        move_in = False

                    elif path_obj in self.exclude_cpaths:
                        move_in = False

                    if move_in:
                        directories.append(path_obj)
                        # Recurse
                        to_travel.extend(
                            tuple([((*path_comps, comp), path_depth + 1) for comp in self.path_tree.fs.listdir(path_abs)]))
                else:
                    raise Exception(f"ContentPath is neither dir, nor file: {path_abs}")
            return directories, files

    class __CPath:
        """
        CPath => Content Path
        Convention:
        1. Content Path will be indicated as cpath
        2. String Path will be indicated as path
        """
        def __init__(self, path_tree, site, cpath_special_comps, is_file=True):
            self.__path_tree = path_tree
            self.__cpath_special_comps = cpath_special_comps
            self.__site = site
            self.__is_file = is_file
            if is_file:
                assert cpath_special_comps[-1] != ''
            else:
                assert cpath_special_comps[-1] == ''

            # make path comps
            comps = self.__cpath_special_comps
            # remove empty string from both ends
            if len(comps) > 1 and comps[-1] == '':
                comps = comps[:-1]
            if len(comps) > 1 and comps[0] == '':
                comps = comps[1:]

            self.__path_comps = comps

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
                # TODO: content should have prent with empty comps ()? If I put < 1 then app will stuck in infinite loop
                # Fix it.
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
            return self.__path_tree.join_comps(*self.__cpath_special_comps).replace('\\', '/')

        @property
        def path_comps(self):
            return tuple(self.__path_comps)

        @property
        def path_comps_w_site(self):
            return (*self.__site.id.components, *self.__path_comps[1:])

        @property
        def cpath_comps(self):
            """Special cpath comps that can have '' empty string on both ends - path tree's to components make this
            special components"""
            return tuple(self.__cpath_special_comps)

        @property
        def abs_path(self):
            return self.__path_tree.get_full_path(self.__cpath_special_comps)

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
            return self.path_comps[-1]

        @property
        def basename_wo_ext(self):
            if self.is_file:
                base, dot, ext = self.basename.rpartition('.')
                if dot == '':
                    base = ext
                    ext = ''
            else:
                base = self.basename
            return base

        @property
        def dirname_comps(self):
            """
            Relative dirname
            """
            return self.__cpath_special_comps[:-1]

        @property
        def extension(self, dot_count=1):
            if self.is_file:
                dotted_parts = self.basename.rsplit(".", maxsplit=dot_count)
                if not len(dotted_parts) < dot_count + 1:
                    ext = ".".join(dotted_parts[-dot_count:])
                    return ext
            return ''

        def list_cpaths(self, files_only=None, depth=None, exclude_compss=(), checker=None):
            return self.__path_tree.list_cpaths(
                files_only=files_only,
                initial_path_comps=self,
                depth=depth,
                exclude_compss=exclude_compss,
                checker=checker
            )

        def list_files(self, depth=None, exclude_compss=(), checker=None):
            _, cfiles = self.list_cpaths(files_only=True, depth=depth, exclude_compss=exclude_compss, checker=checker)
            return cfiles

        def list_dirs(self, depth=None, exclude_compss=(), checker=None):
            dirs, _ = self.list_cpaths(files_only=False, depth=depth, exclude_compss=exclude_compss, checker=checker)
            return dirs

        def exists(self):
            """Real time checking"""
            return self.__path_tree.exists(self.__cpath_special_comps)

        def open(self, mode, *args, **kwargs):
            assert self.is_file, 'Cannot call open() on a directory: %s' % self.relative_path
            return self.__path_tree.open(self.__cpath_special_comps, mode, *args, **kwargs)

        def makedirs(self):
            assert self.is_dir
            return self.__path_tree.fs.makedirs(self.abs_path)

        def join(self, *path_str_or_cmps, is_file=True, forgiving=False):
            """Creates a new path joining to this one"""
            comps = self.__path_tree.to_cpath_ccomps(*path_str_or_cmps) # [p for p in re.split(r'[\\/]+', path_str) if p != '']
            if self.is_dir:
                new_path_comps = (*self.path_comps, *comps)
            else:
                new_path_comps = (*self.path_comps[:-1], self.path_comps[-1] + comps[0], *comps[1:])
            return self.__path_tree.create_cpath(new_path_comps, is_file=is_file, forgiving=forgiving)

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
            ccomps = self.__path_tree.to_cpath_ccomps(comps)
            if not (len(self.path_comps) < len(ccomps)):
                if self.path_comps[:len(ccomps)] == ccomps:
                    return True
            return False

        def endswith(self, *comps):
            ccomps = self.__path_tree.to_cpath_ccomps(comps)
            if not (len(self.path_comps) < len(ccomps)):
                if self.path_comps[-len(ccomps):] == ccomps:
                    return True
            return False

        def getmtime(self):
            return self.__path_tree.fs.getmtime(self.abs_path)

        def getctime(self):
            return self.__path_tree.fs.getctime(self.abs_path)

        @property
        def id(self):
            return '/'.join(self.path_comps)

        def __eq__(self, other):
            if not isinstance(other, self.__class__):
                return False
            return self.path_comps == other.path_comps and self.is_file == other.is_file

        def __hash__(self):
            return hash(self.path_comps)

        def __str__(self):
            return f"CPath: {self.relative_path}"

        def __repr__(self):
            return repr(str(self))
