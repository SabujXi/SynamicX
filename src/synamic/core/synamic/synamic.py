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
import jinja2
from synamic.core.contracts import SynamicContract
from synamic.core.synamic.sites.sites import Sites
from synamic.core.synamic.router import RouterService
from synamic.core.default_data import DefaultDataManager
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.object_manager import ObjectManager
from synamic.core.services.filesystem.path_tree import PathTree
from synamic.exceptions import get_source_snippet_from_text, SynamicTemplateError
from synamic.core.upload_manager.upload_manager import UploadManager


class Synamic(SynamicContract):
    def __init__(self, root_site_root):
        assert os.path.exists(root_site_root)
        assert os.path.isdir(root_site_root)
        self.__root_site_root = root_site_root

        # Default Config Manager
        self.__default_data = DefaultDataManager()

        # Object Manager
        self.__object_manager = ObjectManager(self)

        self.__path_tree = PathTree(self)

        self.__sites = Sites(self, self.__root_site_root)
        self.__router = RouterService(self)

        self.__upload_manager = UploadManager(self)

        # env
        self.__env = {
            'backend': 'file'
        }

        # dev server param
        self.__dev_params = {}

        self.__is_loaded = False

    @property
    def env(self):
        return self.__env

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        self.__sites.load()  # TODO: sites should be loaded individually.
        self.__upload_manager.load()
        self.__is_loaded = True

    @property
    def default_data(self):
        return self.__default_data

    @property
    def object_manager(self):
        return self.__object_manager

    @property
    def system_settings(self):
        return self.__default_data.get_system_settings()

    @property
    # @loaded
    def sites(self):
        return self.__sites

    @property
    def abs_root_path(self) -> str:
        return self.__root_site_root

    @property
    def path_tree(self):
        return self.__path_tree

    # @loaded
    @property
    def router(self):
        return self.__router

    @property
    def event_system(self):
        raise NotImplemented

    @property
    def upload_manager(self):
        return self.__upload_manager

    def set_dev_params(self, **paras):
        self.__dev_params.update(paras)

    @property
    def dev_params(self):
        return self.__dev_params.copy()

    def render_string_template(self, text, context=None, **ctx):
        return render_string_template(text, context=context, **ctx)


def render_string_template(text, context=None, **ctx):
    template = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(text)
    if context is None:
        context = {}
    context.update(ctx)
    try:
        rendered_text = template.render(context)
    except jinja2.TemplateError as e:
        # TODO: error reporting with source - it is not a file, it is a string.
        raise SynamicTemplateError(e)
    else:
        return rendered_text
