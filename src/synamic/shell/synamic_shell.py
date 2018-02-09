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


class CommandProcessor(BaseShell):
    intro_text = 'Welcome to the Synamic shell.   Type help or ? to list commands.\n'
    prompt_text = '(synamic): '

    def __init__(self, synamic_obj, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__global_for_py = {}
        self.__synamic_object = synamic_obj

    def on_settings(self, arg):
        if not arg:
            self.pprint(self.__synamic_object.site_settings.values())
        else:
            val = self.__synamic_object.site_settings.get(arg, 'null')
            self.print(val)

    def on_init(self, arg):
        'Initialize a synamic project'
        print("init: ", arg)

    def on_reload(self, arg):
        'Reload the current synamic project'
        print("reload: ", arg)

    def on_build(self, arg):
        'Build Synamic project that will result in static site'
        print("build: ", arg)

    def on_serve(self, arg):
        'Serve the current synamic project in localhost'
        print("serve: ", arg)

    def on_filter(self, arg):
        'Work with filter for pagination'
        print("filter: ", arg)

    def on_clean(self, arg):
        'Clean the build folder'
        print("clean: ", arg)

    def on_deploy(self, arg):
        'Deploy the build'
        print("deploy: ", arg)

    def on_shellx_s(self, *shellargs):
        self.print("on_s(): %s" % str(shellargs))


def start_shell(synamic_bject):
    CommandProcessor(synamic_bject).loop()
