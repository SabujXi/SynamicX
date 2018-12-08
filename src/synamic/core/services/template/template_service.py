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
from synamic.core.services.template.template_tags import GetCExtension, ResizeImageExtension
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from .loaders import SynamicJinjaFileSystemLoader
from synamic.exceptions import SynamicTemplateError


class SynamicTemplateService:
    def __init__(self, site):
        self.__is_loaded = False
        self.__site = site
        self.__template_env = None
        self.__themes = []

    @property
    def themes(self):
        return tuple(self.__themes)

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

        # themes
        system_settings = self.__site.synamic.system_settings
        template_cdir = self.__site.path_tree.create_dir_cpath(system_settings['dirs.templates.templates'])
        if template_cdir.exists():
            t_cdirs = template_cdir.list_dirs(depth=1)  # 1 or 0?
            for theme_cdir in t_cdirs:
                theme_syd_cfile = theme_cdir.join_as_cfile(system_settings['theme_info_file'])
                if theme_syd_cfile.exists():
                    syd = self.__site.object_manager.get_syd(theme_syd_cfile)
                    theme = Theme(self.__site, theme_cdir.basename, theme_cdir, syd)
                    self.__themes.append(theme)  # TODO: not being managed by ObjectManager -> should it be?
        self.__is_loaded = True

    @property
    def is_loaded(self):
        return self.__is_loaded

    # def exists(self, template_name):
    #     return True if os.path.exists(os.path.join(self.__site.template_dir, template_name)) else False

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


class Theme:
    def __init__(self, site, theme_id, theme_cdir, theme_info_syd):
        self.__site = site
        self.__theme_id = theme_id
        self.__cdir = theme_cdir
        self.__info = theme_info_syd

        # validation
        _tid = theme_info_syd.get('id', None)
        if _tid is not None:
            assert self.__theme_id == _tid  # TODO: Raise Synamic error here

    @property
    def id(self):
        return self.__theme_id

    @property
    def cdir(self):
        return self.__cdir

    @property
    def assets_cdir(self):
        assets_dir = self.__info.get('assets_dir', 'assets')
        return self.__cdir.join_as_cdir(assets_dir)

    @property
    def sass_cdir(self):
        return self.assets_cdir.join_as_cdir(
            self.__site.synamic.system_settings['theme_sass_dir']
        )

    @property
    def info(self):
        return self.__info
