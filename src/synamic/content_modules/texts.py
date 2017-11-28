import re
import io
import mimetypes

from synamic.core.contracts import ContentModuleContract, ContentContract
from synamic.core.classes.document import MarkedDocument
# from synamic.core.synamic_config import SynamicConfig
from synamic.core.functions.decorators import loaded, not_loaded
"""
Text files must start with a number. The initial zero of the number will be stripped off
A dot will follow the number, a space if optional.
- that is the id part - no two text file can have the same id -
the rest is the file name you want to give to it.
"""


class Text(ContentContract, MarkedDocument):
    def __init__(self, config, module, path, text_id, file_content: str):
        super().__init__(file_content, config, self)
        self.__text_id = text_id
        self.__config = config

        self.__module = module
        self.__path = path

    @property
    def module(self):
        return self.__module

    @property
    def path(self):
        return self.__path

    @property
    def content_id(self):
        return self.module.name + ":" + str(self.__text_id)

    def get_stream(self):
        template_module, template_name = self.template
        res = template_module.render(template_name, body=self.body)
        f = io.BytesIO(res.encode('utf-8'))
        return f

    @property
    def content_type(self):
        mime_type = 'octet/stream'
        path = self.url.real_path
        type, enc = mimetypes.guess_type(path)
        if type:
            mime_type = type
        return mime_type


class Texts(ContentModuleContract):

    _file_name_regex = re.compile("^(?P<id>[0-9]+)\. ?(.+)")

    def __init__(self, _cfg):
        self.__config = _cfg
        self.__text_map = {}

        self.__is_loaded = False

    @property
    def name(self):
        return "texts"

    @property
    def directory_name(self):
        return "texts"

    @property
    def parent_dir(self):
        return self.__config.content_dir

    @property
    def dotted_path(self):
        return "synamic.content_modules.texts.Texts"

    @property
    def dependencies(self):
        return {"synamic-template"}

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        paths = self.__config.path_tree.get_module_paths(self)
        text_ids = set()

        for file_path in paths:
            file_base_match = file_path.match_basename(self.__class__._file_name_regex)
            if not file_base_match:
                raise Exception("File name %s does not go with the file name format")

            text_id = file_base_match.group('id').lstrip('0')
            if text_id in text_ids:
                raise Exception("Two different texts files cannot have the same text id")

            with open(file_path.absolute_path, "r", encoding="utf-8") as f:
                text = f.read()
                text_obj = Text(self.__config,  self, file_path, text_id, text)
                if not text_obj.has_valid_frontmatter:
                    raise Exception("Front matter is corrupted or invalid")
                self.__text_map[text_id] = text_obj
                self.__config.add_url(text_obj.url)

        self.__is_loaded = True

    @property
    def extensions(self):
        return {'md', 'markdown'}

    @property
    def root_url_path(self):
        return ""
