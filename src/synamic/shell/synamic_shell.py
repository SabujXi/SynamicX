"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


from .base_shell import BaseShell
import os
from shutil import rmtree
from synamic.dev_server.server import serve


class CommandProcessor(BaseShell):
    intro_text = 'Welcome to the Synamic shell.   Type help or ? to list commands.\n'
    prompt_text = '(synamic): '

    def __init__(self, synamic_class, start_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__global_for_py = {}
        self.__synamic_object = None
        self.__synamic_class = synamic_class
        self.__site_root = start_dir

    def get_or_create_synamic(self):
        if self.__synamic_object is None:
            self.__synamic_object = self.__synamic_class(self.__site_root)
        return self.__synamic_object

    def get_loaded_or_load_synamic(self):
        s = self.get_or_create_synamic()
        if not s.is_loaded:
            s.load()
        return s

    def on_cwd(self):
        self.pprint("Site Root: %s" % self.__site_root)

    def on_urls(self):
        s = self.get_loaded_or_load_synamic()
        self.pprint(s.urls)

    def on_settings(self, arg):
        if not arg:
            self.pprint(self.__synamic_object.site_settings.values())
        else:
            val = self.__synamic_object.site_settings.get(arg, 'null')
            self.print(val)

    def on_init(self, arg):
        'Initialize a synamic project'
        # print("init: ", arg)
        self.get_or_create_synamic().initialize_site()

    def on_reinit(self, arg):
        self.__synamic_object = self.__synamic_class(self.__site_root)
        self.__synamic_object.initialize_site()

    def on_load(self, arg):
        'Reload the current synamic project'
        s = self.get_or_create_synamic()
        s.load()

    def on_reload(self, arg):
        'Reload the current synamic project'
        self.__synamic_object = self.__synamic_class(self.__site_root)
        self.__synamic_object.load()

    def on_build(self, arg):
        'Build Synamic project that will result in static site'
        o = self.get_or_create_synamic()
        o.load()
        o.build()

    def on_rebuild(self):
        self.__synamic_object = o = self.__synamic_class(self.__site_root)
        o.load()
        o.build()

    def on_serve(self, arg):
        'Serve the current synamic project in localhost'
        serve(self.get_loaded_or_load_synamic(), 8000)

    def on_filter(self, arg):
        'Work with filter for pagination'
        s = self.get_or_create_synamic()
        if not s.is_loaded:
            s.load()
        self.pprint(s.filter_content(arg))


    def on_clean(self, arg):
        'Clean the build folder'
        o_dir = self.get_or_create_synamic().site_settings.output_dir
        o_dir_full = os.path.join(self.__site_root, o_dir)
        if os.path.exists(o_dir_full):
            print("Cleaning output dir: `%s`" % o_dir_full)
            top_paths = [os.path.join(o_dir_full, x) for x in os.listdir(o_dir_full)]
            for top_path in top_paths:
                if os.path.isfile(top_path):
                    os.remove(top_path)
                else:
                    rmtree(top_path)
        else:
            print("Output directory `%s` does not exist" % o_dir)

    def on_deploy(self, arg):
        'Deploy the build'
        print("deploy: ", arg)

    def on_shellx_s(self, *shellargs):
        self.print("on_s(): %s" % str(shellargs))


def start_shell(synamic_class, start_dir):
    CommandProcessor(synamic_class, start_dir).loop()
