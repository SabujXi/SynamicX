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
    def __init__(self, site):
        self.__is_loaded = False
        self.__site = site
        self.__template_env = None

    @not_loaded
    def load(self):
        assert not self.__is_loaded, "Module cannot be loaded twice"
        path_tree = self.__site.get_service('path_tree')
        templates_dir = self.__site.default_configs.get('dirs')['templates.templates']
        templates_dir_path = path_tree.create_dir_cpath(templates_dir)
        self.__template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                templates_dir_path.abs_path,
                encoding='utf-8', followlinks=False),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            extensions=[GetUrlExtension, ResizeImageExtension]
        )
        # setting config object to global of environment
        self.__template_env.site_config = self.__site
        self.__template_env.globals['site'] = self.__site

        self.__is_loaded = True

    @property
    def is_loaded(self):
        return self.__is_loaded

    def exists(self, template_name):
        return True if os.path.exists(os.path.join(self.__site.template_dir, template_name)) else False

    @loaded
    def render(self, template_name, context=None, **kwargs):
        assert self.__is_loaded, "Render cannot work until the template module_object is loaded"
        context = {} if context is None else context
        context.update(kwargs)

        is_from_parent, template_name = parent_config_str_splitter(template_name)

        if is_from_parent:
            result = self.__site.template_service.render(template_name, context=context)
        else:
            _template = self.__template_env.get_template(template_name)
            result = _template.render(context)
        return result
