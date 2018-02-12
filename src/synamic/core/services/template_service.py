"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import jinja2
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.classes.template_tags import GetUrlExtension


class SynamicTemplateService:
    def __init__(self, _cfg):
        self.__is_loaded = False
        self.__config = _cfg
        self.__template_env = None

        self.__service_home_path = None

        self.__config.register_path(self.service_home_path)

    @property
    def service_home_path(self):
        if self.__service_home_path is None:
            self.__service_home_path = self.__config.path_tree.create_path('templates')
        return self.__service_home_path

    @property
    def name(self):
        return "templates"

    @property
    def config(self):
        return self.__config

    @not_loaded
    def load(self):
        assert not self.__is_loaded, "Module cannot be loaded twice"
        self.__template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                self.__config.path_tree.get_full_path(self.__config.template_dir),
                encoding='utf-8', followlinks=False),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            extensions=[GetUrlExtension]
        )
        # setting config object to global of environment
        self.__template_env.synamic_config = self.__config
        self.__template_env.globals['synamic'] = self.__config

        self.__is_loaded = True

    @property
    def is_loaded(self):
        return self.__is_loaded

    @loaded
    def render(self, template_name, context=None, **kwargs):
        assert self.__is_loaded, "Render cannot work until the template module_object is loaded"
        context = {} if context is None else context
        context.update(kwargs)
        template = self.__template_env.get_template(template_name)
        return template.render(context)
