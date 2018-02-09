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
import sys

import synamic.core.synamic_config
from synamic.core.synamic_config import SynamicConfig
from synamic.core.synamic import Synamic

"""
REMEMBER:
====deprecated===
- the content_modules that has no dependency must be loaded first.
-> meta contents: variables, tags, categories have no dependency
<-> templates has dependency on above
<- contents: texts, series, and-whatever-else-added later have dependency on meta contents || plain html has no dependency on others. But keep that loaded at this phase.
=================
A dependency resolver has been developed.

* Actually only contents is rendered. So, you /run/ content module_object - not others*
[
    
]
"""


def get_synamic(base_path):
    assert not (base_path != "" or base_path is not None), "Base path cannot be empty"
    assert os.path.exists(base_path), "Base path is non existent in the file system"
    return Synamic(SynamicConfig(base_path))


class SynamicInitProject:
    def __init__(self, synamic_obj):
        """        
        :param __site_root: 
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
        from synamic import test
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
            if path in synamic.core.synamic_config.ROOT_LEVEL_PATHS:
                if not do_force:
                    print("The directory contains projects paths/directories. Use -force or clean yourself to init."
                          " Forcing will not delete existing files/directories.", file=sys.stderr)
                    return

            else:
                for path2 in synamic.core.synamic_config.ROOT_LEVEL_DIRS:
                    if os.path.exists(os.path.join(self.SITE_BASE_PATH, path2)):
                        continue
                    else:
                        os.mkdir(os.path.join(self.SITE_BASE_PATH, path2))

        self._create_config_files()

    def _create_config_files(self):
        for path in synamic.core.synamic_config.ROOT_LEVEL_FILES:
            if not os.path.exists(os.path.join(self.SITE_BASE_PATH, path)):
                with open(os.path.join(self.SITE_BASE_PATH, path), "wb") as f:
                    pass


