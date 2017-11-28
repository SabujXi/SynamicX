import jinja2
from synamic.core.contracts.modules.base_template_contract import TemplateModuleContract
from synamic.core.functions.decorators import loaded
from synamic.core.classes.template_tags import GetUrlExtension


class SynamicTemplate(TemplateModuleContract):
    def __init__(self, _cfg):
        self.__is_loaded = False
        self.__config = _cfg
        self.__template_env = None

    @property
    def name(self):
        return "synamic-template"

    @property
    def directory_name(self):
        return "synamic-templates"

    @property
    def directory_path(self):
        return self.__config.path_tree.join(self.__config.template_dir, self.directory_name)

    @property
    def dotted_path(self):
        return "synamic.template_modules.synamic_template.SynamicTemplate"

    @property
    def dependencies(self):
        return set()

    def load(self):
        assert not self.__is_loaded, "Module cannot be loaded twice"
        self.__template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                self.__config.path_tree.get_full_path(self.__config.template_dir, self.directory_name),
                encoding='utf-8', followlinks=False),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            extensions=[GetUrlExtension]
        )
        # setting config object to global of environment
        self.__template_env.synamic_config = self.__config

        self.__is_loaded = True

    @property
    def is_loaded(self):
        return self.__is_loaded

    @loaded
    def render(self, template_name, context=None, **kwargs):
        assert self.__is_loaded, "Render cannot work until the template module is loaded"
        context = {} if context is None else context
        context.update(kwargs)
        # test
        # context['config2'] =
        # test 2
        template = self.__template_env.get_template(template_name)
        return template.render(context)
