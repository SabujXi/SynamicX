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
from synamic.core.services.template.template_tags import GetCExtension, ResizeImageExtension
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.standalones.functions.parent_config_splitter import parent_config_str_splitter
from .loaders import SynamicJinjaFileSystemLoader
from synamic.exceptions import SynamicTemplateError


class SynamicTemplateService:
    def __init__(self, site):
        self.__is_loaded = False
        self.__site = site
        self.__template_env = None

    @not_loaded
    def load(self):
        self.__template_env = jinja2.Environment(
            loader=SynamicJinjaFileSystemLoader(self.__site),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            extensions=[GetCExtension, ResizeImageExtension]
        )
        # setting config object to global of environment
        self.__template_env.site_object = self.__site
        # self.__template_env.globals['site'] = self.__site

        self.__is_loaded = True

    @property
    def is_loaded(self):
        return self.__is_loaded

    def exists(self, template_name):
        return True if os.path.exists(os.path.join(self.__site.template_dir, template_name)) else False

    @loaded
    def render(self, template_name, context=None, **kwargs):
        context = {} if context is None else context
        context.update(kwargs)

        # is_from_parent, template_name = parent_config_str_splitter(template_name)

        try:
            template = self.__template_env.get_template(template_name)
            result = template.render(context)
        except jinja2.exceptions.TemplateError as e:
            raise SynamicTemplateError(e)

        return result
