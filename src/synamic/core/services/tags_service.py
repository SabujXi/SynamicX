"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

from synamic.core.new_parsers.document_parser import FieldParser, Field
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.classes.path_tree import ContentPath2


class Tag:
    def __init__(self, title=None, id=None, description=None):
        self.__title = title
        self.__id = id
        self.__description = description

    @property
    def title(self):
        return self.__title

    @property
    def id(self):
        return self.__id

    @property
    def description(self):
        return self.__description


class TagsService:
    def __init__(self, synamic_config):
        self.__config = synamic_config
        self.__tags_by_id = {}
        self.__tags_by_title = {}
        self.__is_loaded = False

        self.__service_home_path = None
        self.__config.register_path(self.service_home_path)

    @property
    def service_home_path(self) -> ContentPath2:
        if self.__service_home_path is None:
            self.__service_home_path = self.__config.path_tree.create_path(('meta', 'tags'))
        return self.__service_home_path

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        file_paths = self.service_home_path.list_paths()

        for file_path in file_paths:
            if file_path.basename.endswith('.tags.txt') and len(file_path.basename) > len('.tags.txt'):
                with file_path.open('r', encoding='utf-8') as f:
                    model_txt = f.read()
                    root_tags = FieldParser(model_txt).parse()

                    for tag_field in root_tags.get_multi('tag'):
                        title = tag_field.get('title', '_untitled_')
                        id = tag_field.get('id', None)
                        description = tag_field.get('description', '')
                        assert id is not None and title is not None, "Tag id must exist"
                        tag = Tag(
                            title=title,
                            id=id,
                            description=description
                        )
                        self.__tags_by_id[tag.id] = tag
                        self.__tags_by_title[tag.title] = tag

        self.__is_loaded = True

    @property
    def tags(self):
        return tuple(self.__tags_by_title.values())

    def __getitem__(self, key):
        return self.__tags_by_id.get(key)