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
import sys


class CommandProcessor(BaseShell):
    intro_text = 'Welcome to the Synamic shell.   Type help or ? to list commands.\n'
    prompt_text = '(synamic)$ '

    def __init__(self, synamic_class, start_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__global_for_py = {}
        self.__synamic_object = None
        self.__synamic_class = synamic_class
        self.__root_site_root = start_dir

    def get_or_create_synamic(self):
        if self.__synamic_object is None:
            self.__synamic_object = self.__synamic_class(self.__root_site_root)
        return self.__synamic_object

    def on_cwd(self):
        self.pprint("Site Root: %s" % self.__root_site_root)

    def on_urls(self):
        raise NotImplemented

    def on_settings(self, arg):
        if not arg:
            self.pprint(self.__synamic_object.settings.values())
        else:
            val = self.__synamic_object.settings.get(arg, 'null')
            self.print(val)

    def on_init(self, *args):
        'Initialize a synamic project'
        raise NotImplemented

    def on_load(self, *args):
        'Reload the current synamic project'
        s = self.get_or_create_synamic()
        if not s.is_loaded:
            s.load()

    def on_build(self, *args):
        'Build Synamic project that will result in static site'
        o = self.get_or_create_synamic()
        if not o.is_loaded:
            o.load()
        return o.sites.build()

    def on_reset(self):
        self.__synamic_object = None
        self.print(f'Synamic object set to none so that new instance start from the beginning')

    def on_serve(self, *args):
        '''Serve the current synamic project in localhost'''
        from synamic.entry_points.aio_server import aio_server

        SITE_ROOT = self.__root_site_root
        host = 'localhost'
        port = '8087'
        return aio_server.serve(SITE_ROOT, host, port)

    def on_upload(self, *args):
        'Deploy the build'
        if len(args) < 1:
            self.print_error(f'No upload parameter provided')
            exit(1)
        uploader_name = args[0].strip()
        synamic = self.get_or_create_synamic()
        if not synamic.is_loaded:
            synamic.load()
        uploader = synamic.upload_manager.get_uploader(uploader_name, None)
        if uploader is None:
            self.print_error(f'No uploader found with name {uploader_name}')
            exit(1)
        else:
            upload_res = uploader.upload()
            if upload_res:
                exit(0)
            else:
                exit(1)


def start_shell(synamic_class, start_dir):
    CommandProcessor(synamic_class, start_dir).run_command(sys.argv[1:])
