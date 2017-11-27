import os
import re

from synamic.core.contracts import ContentModuleContract
from synamic.core.exceptions import (
    InvalidFrontMatter,
    InvalidFileNameFormat,
    DuplicateContentId
)
from synamic.core.classes.document import MarkedDocument

"""
# Other frontmatter like texts

# Series Specific Frontmatter Example:

Chapters: # case insensitive
    - Chapter: # Starts with 'chapter', anything may follow it.
        title: # if the value is <get> then it is get from the text if the 'for' key refers to some text
        for: # may contain a numeric id, relative url, full (optionally external) url.
        
    -Section xyZ:
        title: what title
        
    -  Chapter 2: 
         title:
         for:

    -  Chapter XX: 
         title:
         for: 

    -  Chapter P1: 
         title:
         for: 
"""


class Chapter:
    def __init__(self, chapter_dict, synamic_cfg):
        self.__synamic_cfg = synamic_cfg
        self.__chapter_dict = {}
        for key, value in chapter_dict.keys():
            self.__chapter_dict[key.lower()] = value

    @property
    def title(self):
        return self.__chapter_dict.get("title", "")

    @property
    def for_url(self):
        """returns an url or UrlContract instance?"""
        # A lot of processing here
        return None


class Section:
    def __init__(self, section_dict):
        self.__section_dict = section_dict
        self.__chapter_list = []

    @property
    def title(self):
        return self.__section_dict.value() if self.__section_dict.value() else ""

    def add_chapter(self, chp):
        self.__chapter_list.append(chp)


class Chapters:

    def __init__(self, chapters_list, synamic_cfg):
        self.__chapters = []
        self.__sections = []
        self.__synamic_cfg = synamic_cfg

    def __process_chapters(self, chapters_list):

        _secs = []
        _last_sec = None

        for sec_or_chap in chapters_list:
            sec_or_chap = sec_or_chap.lower()
            if sec_or_chap.starts_with("section"):
                _last_sec = Section()
            else:
                pass




            # self.__chapters[key] = value




_file_name_regex = re.compile("^(?P<id>[0-9]+)\. ?(.+)")


class AllSeries(ContentModuleContract):
    def __init__(self, root_module, synamic_cfg_obj):
        self.__synamic_cfg_obj = synamic_cfg_obj
        self.__root_module_obj = root_module
        self.__document = None

        self._IS_LOADED = False

    def get_dependency_content_modules(self):
        return {self.__synamic_cfg_obj.get_series_content_module_name()}

    def get_config(self):
        return self.__synamic_cfg_obj

    def get_root_module(self):
        return self.__root_module_obj

    def is_loaded(self):
        return True if self._IS_LOADED else False

    def is_rendered(self):
        pass

    def _filter_text_files_callback(self, fn):
        if not os.path.isfile(fn):
            return False
        fnl = fn.lower()
        exts = self.get_extensions()
        matched = False
        for ext in exts:
            if fnl.endswith(ext):
                matched = True
        return True if matched else False

    def get_encoding(self):
        return "utf-8"

    def load(self):
        cfg = self.get_config()
        rm = self.get_root_module()
        dir = cfg.get_abs_path_for(rm.get_directory_name(), cfg.get_directory_name())
        file_names = cfg.get_paths(dir, comp_fun=self._filter_text_files_callback)
        file_ids = set()

        for fn in file_names:
            fn_match = _file_name_regex.match(fn)
            if not fn_match:
                raise InvalidFileNameFormat("File name %s does not go with the file name format")
            text_id = fn_match.group('id').lstrip('0')
            if text_id in file_ids:
                raise DuplicateContentId("Two different texts files cannot have the same series id")

        for fn in file_names:
            with open(fn, "r", encoding=self.get_encoding()) as f:
                _text = f.read()
                doc = MarkedDocument(_text)
                if not doc.has_valid_frontmatter:
                    raise InvalidFrontMatter("Front matter is corrupted or invalid")
                else:
                    front_map = doc.frontmatter

                    for field in front_map.keys():
                        if field not in self.get_text_fileds():
                            raise Exception("Unknown field in text")
                        else:
                            pass
        self._IS_LOADED = True

    def render(self):
        assert self.is_loaded(), "Must be loaded before it can be rendered"

    def register_url_prefix(self):
        pass

    def get_extensions(self):
        return ['md', 'markdown']

    def get_text_fileds(self):
        return {
            'title',
            'url',
        }

Module = AllSeries
