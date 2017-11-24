from synamic.core.contracts.modules.base_template_contract import TemplateModuleContract
from synamic.core.synamic_config import SynamicConfig


class SynamicTemplate(TemplateModuleContract):
    def __init__(self, _cfg: SynamicConfig):
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

        import jinja2
        self.__template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                self.__config.path_tree.get_full_path(self.__config.template_dir, self.directory_name),
                encoding='utf-8', followlinks=False),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        self.__is_loaded = True

    @property
    def is_loaded(self):
        return self.__is_loaded

    def render(self, template_name, context=None, **kwargs):
        assert self.__is_loaded, "Render cannot work until the template module is loaded"
        context = {} if context is None else context
        context.update(kwargs)
        template = self.__template_env.get_template(template_name)
        return template.render(context)