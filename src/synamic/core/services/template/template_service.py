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
from synamic.core.services.template.template_tags import GetUrlExtension, ResizeImageExtension
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.standalones.functions.parent_config_splitter import parent_config_str_splitter


class SynamicTemplateService:
    def __init__(self, synamic):
        self.__is_loaded = False
        self.__synamic = synamic
        self.__template_env = None

        self.__service_home_path = None

        self.__synamic.register_path(self.service_home_path)

    @property
    def service_home_path(self):
        if self.__service_home_path is None:
            self.__service_home_path = self.__synamic.path_tree.create_path('templates')
        return self.__service_home_path

    @property
    def name(self):
        return "templates"

    @property
    def config(self):
        return self.__synamic

    @not_loaded
    def load(self):
        assert not self.__is_loaded, "Module cannot be loaded twice"
        self.__template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                self.__synamic.path_tree.get_full_path(self.__synamic.template_dir),
                encoding='utf-8', followlinks=False),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            extensions=[GetUrlExtension, ResizeImageExtension]
        )
        # setting config object to global of environment
        self.__template_env.synamic_config = self.__synamic
        self.__template_env.globals['synamic'] = self.__synamic

        self.__is_loaded = True

    @property
    def is_loaded(self):
        return self.__is_loaded

    def exists(self, template_name):
        return True if os.path.exists(os.path.join(self.__synamic.template_dir, template_name)) else False

    @loaded
    def render(self, template_name, context=None, **kwargs):
        assert self.__is_loaded, "Render cannot work until the template module_object is loaded"
        context = {} if context is None else context
        context.update(kwargs)

        is_from_parent, template_name = parent_config_str_splitter(template_name)

        if is_from_parent:
            result = self.__synamic.template_service.render(template_name, context=context)
        else:
            _template = self.__template_env.get_template(template_name)
            result = _template.render(context)
        return result
