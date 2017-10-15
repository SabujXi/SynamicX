import os
import sys
from . import default_site_config
from . import scan

class Synamic:
    instance = None
    def __init__(self, SITE_BASE_PATH=None):
        self.SITE_BASE_PATH = SITE_BASE_PATH

    def get_base_path(self):
        return self.SITE_BASE_PATH

    def scan(self):
        pass

    @classmethod
    def get_synamic_instance(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

class SynamicInitProject:
    def __init__(self, synamic_obj):
        """        
        :param SITE_BASE_PATH: 
        """
        SITE_BASE_PATH = synamic_obj.get_base_path()

        if not SITE_BASE_PATH:
            self.SITE_BASE_PATH = os.getcwd()
        else:
            self.SITE_BASE_PATH = SITE_BASE_PATH

        self.valid_args = set()
        self.valid_args_map = {}

        self._process_cmd_argv()

        if not SITE_BASE_PATH:
            if "base" in self.valid_args:
                self.SITE_BASE_PATH = os.path.join(self.SITE_BASE_PATH, self.valid_args_map["base"])

        # print(self.valid_args)
        # print(self.valid_args_map)

    def _process_cmd_argv(self):
        argv = sys.argv.copy()
        argc = len(sys.argv) - 1
        del argv[0]
        argv_last_idx = argc - 1
        # print(argv)


        i = 0
        while i < argc:
            key = argv[i]
            value = None
            if key.startswith("-"):
                key = key.lstrip("-")
                if i + 1 <= argv_last_idx:
                    next_argv = argv[i + 1]
                    if not next_argv.startswith("-"):
                        value = next_argv
                        i += 1
            self.valid_args.add(key.lower()) # Commands are case insensitive
            self.valid_args_map[key] = value
            i += 1
        self.dispatch_commands()

    def dispatch_commands(self):
        if "init" in self.valid_args:
            if "force" in self.valid_args:
                self.initialize_project(True)
            else:
                self.initialize_project(False)
            return
        if "unittest" in self.valid_args:
            self.start_unittest()

    def start_unittest(self):
        import unittest
        from . import test
        loader = unittest.TestLoader()
        suite = loader.discover(os.path.dirname(test.__file__), pattern="test_*.py")
        test_runner = unittest.runner.TextTestRunner()
        test_runner.run(suite)


    def initialize_project(self, do_force=False):
        """
        This method will help create the needed directories automatically.
        - If a root path from default_site_config exists it will not perform the operation.
        - If -force is used the above mentioned operation will be performed but the directories or paths that are 
          already there will stay as is.
        :param do_force: commands to create dirs forcefully when True 
        :return: None
        """
        root_level_paths = [x.lower() for x in os.listdir(self.SITE_BASE_PATH)]
        for path in root_level_paths:
            if path in default_site_config.ROOT_LEVEL_PATHS_LOWER:
                if not do_force:
                    print("The directory contains projects paths/directories. Use -force or clean yourself to init."
                          " Forcing will not delete existing files/directories.", file=sys.stderr)
                    return

            else:
                for path2 in default_site_config.ROOT_LEVEL_DIRS_LOWER:
                    if os.path.exists(os.path.join(self.SITE_BASE_PATH, path2)):
                        continue
                    else:
                        os.mkdir(os.path.join(self.SITE_BASE_PATH, path2))

        self._create_config_files()

    def _create_config_files(self):
        for path in default_site_config.ROOT_LEVEL_FILES_LOWER:
            if not os.path.exists(os.path.join(self.SITE_BASE_PATH, path)):
                with open(os.path.join(self.SITE_BASE_PATH, path), "wb") as f:
                    pass


