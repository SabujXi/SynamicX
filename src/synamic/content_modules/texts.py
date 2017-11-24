import re
import os

from synamic.core.contracts import ContentModuleContract
from synamic.core.frontmatter import Document
from synamic.core.synamic_config import SynamicConfig

"""
Text files must start with a number. The initial zero of the number will be stripped off
A dot will follow the number, a space if optional.
- that is the id part - no two text file can have the same id -
the rest is the file name you want to give to it.
"""


class Texts(ContentModuleContract):

    _file_name_regex = re.compile("^(?P<id>[0-9]+)\. ?(.+)")

    def __init__(self, _cfg: SynamicConfig):
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
    def directory_path(self):
        return self.__config.path_tree.join(self.__config.content_dir, self.directory_name)

    @property
    def dotted_path(self):
        return "synamic.content_modules.texts.Texts"

    @property
    def dependencies(self):
        return {"synamic-template"}

    def is_loaded(self):
        return True if self.__is_loaded else False

    def load(self):
        assert not self.__is_loaded, "Cannot load twice"

        cfg = self.__config
        # rm = self.get_root_module()
        # dir = cfg.get_abs_path_for(rm.get_directory_name(), cfg.get_directory_name())
        paths = self.__config.path_tree.list_files(self.directory_path)

        text_ids = set()
        accepted_file_paths = set()

        for file_path in paths:
            print("File path in loop: %s" % file_path.absolute_path)
            print("Extension: %s" % file_path.extension)
            if file_path.extension.lower() not in self.extensions:
                continue
            file_base_match = file_path.match_basename(self.__class__._file_name_regex)

            if not file_base_match:
                raise Exception("File name %s does not go with the file name format")

            text_id = file_base_match.group('id').lstrip('0')

            if text_id in text_ids:
                raise Exception("Two different texts files cannot have the same text id")
            accepted_file_paths.add(file_path)

            with open(file_path.absolute_path, "r", encoding="utf-8") as f:
                text = f.read()
                document = Document(text)

                if not document.has_valid_front_matter:
                    raise Exception("Front matter is corrupted or invalid")
                else:
                    # yaml = YAML(typ="safe")
                    front_map = document.front_map

                    for field in front_map.keys():
                        # if field not in self.get_text_fileds():
                        #     raise Exception("Unknown field in text")
                        # else:
                        #     pass
                        pass
                self.__text_map[text_id] = document
            print("Text id loaded: %s" % text_id)

        self.__is_loaded = True

    def render(self):
        print("Entered render() of texts")
        assert self.is_loaded(), "Must be loaded before it can be rendered"
        print("Text map: %s" % self.__text_map)
        for id, document in self.__text_map.items():
            print("Document id: %s" % id)
            url = document.front_map['url']
            template_name = document.front_map['template']
            template_module = self.__config.get_module("synamic-template")
            url_parts = url.strip().split('/')
            url_dir_path = self.__config.path_tree.get_full_path(self.__config.output_dir, *url_parts)
            if not os.path.exists(url_dir_path):
                os.makedirs(url_dir_path)
            with open(os.path.join(url_dir_path, "index.html"), "w", encoding="utf-8") as f:
                content = template_module.render(template_name, body=document.body)
                print("Writing file: %s" % os.path.join(url_dir_path, "index.html"))
                f.write(content)
        print("Exited render() of texts")

    def register_url_prefix(self):
        pass

    @property
    def extensions(self):
        return {'md', 'markdown'}


class Text:
    def __init__(self, text_id, front_matter, body_text: str):
        self._text_id = text_id
        self._body = body_text
        self._front_mater = front_matter

    def get_body_text(self):
        return self._body

    def get_front_matter(self):
        return self._front_mater

    def get_id(self):
        return self._text_id


class TextUrl:

    def __init__(self, url="", name=""):
        self._url = url
        self._name = name

    def get_url(self):
        return self._url

    def get_url_name(self):
        return self._name


class TextFrontMatter:
    def __init__(self, front_map: dict):
        self._front_map = front_map

    def get_front_map(self):
        return self._front_map

    def get_title(self):
        return self._front_map.get("title", "")

    def get_url(self):
        """
        url can be of string or another map.
        eg:
            url: /my/path/to/file
        or:
            url:
                url: /my/path/to/file
                name: my_awesome_url_name
            
        - a '/' will be added at the end of the urls if it is not there.
        """
        m = self.get_front_map()
        _url = m["url"]
        url = None
        name = ""

        if type(url) is dict:
            url = _url['url']
            name = _url.get("name", "")
        elif type(url) is str:
            url = _url
        else:
            raise Exception("No-or-malformed url!")

        if not url.endswith("/"):
            url += "/"
        if not url.startswith("/"):
            url = "/" + url

        return TextUrl(url, name)

    def get_tags(self):
        pass

    def get_categories(self):
        pass

    def get_featured_image_url(self):
        pass

    def get_featured_thumb_url(self):
        pass

    def get_meta_tags(self):
        return self.get_front_map().get("meta_tags", "")

    def get_meta_description(self):
        return self.get_front_map().get("meta_description", "")

    def get_summary(self):
        pass

    def get_creation_datetime(self):
        """filed name is created_on"""
        pass

    def get_modification_datetime(self):
        """field name is modified_on"""
        pass


def parse_text():
    pass

# Base for series.py and text.py
import abc


class TextSeriesUrl(abc.ABC):

    @property
    @abc.abstractmethod
    def url(self):
        """
        url can be of string or another map.
        eg:
            url: /my/path/to/file
        or:
            url:
                url: /my/path/to/file
                name: my_awesome_url_name  # this name must conform to identifier as in variables

        - a '/' will be added at the end of the urls if it is not there.
        """
        pass

    @property
    @abc.abstractmethod
    def url_name(self):
        pass


class TextSeriesContract(abc.ABC):

    @abc.abstractmethod
    def __getitem__(self, item):
        """get item for front map"""
        pass

    @property
    @abc.abstractmethod
    def front_map(self):
        """A copy of front map - so that it will not be mutated"""
        pass

    @property
    @abc.abstractmethod
    def title(self):
        pass

    @property
    @abc.abstractmethod
    def url(self):
        pass

    @property
    @abc.abstractmethod
    def tags(self):
        pass

    @property
    @abc.abstractmethod
    def categories(self):
        pass

    @property
    @abc.abstractmethod
    def featured_image_url(self):
        pass

    @property
    @abc.abstractmethod
    def featured_thumb_url(self):
        pass

    @property
    @abc.abstractmethod
    def meta_tags(self):
        pass

    @property
    @abc.abstractmethod
    def meta_description(self):
        pass

    @property
    @abc.abstractmethod
    def summary(self):
        pass

    @property
    @abc.abstractmethod
    def creation_datetime(self):
        """filed name is created_on"""
        pass

    @property
    @abc.abstractmethod
    def modification_datetime(self):
        """field name is modified_on"""
        pass

