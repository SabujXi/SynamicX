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


class Category:
    __config = None

    @classmethod
    def set_config(cls, config):
        cls.__config = config

    def __init__(self, children=None, title=None, id=None, description=None):
        self.__title = title
        self.__id = id
        self.__description = description
        self.__children = children

    def __iter__(self):
        return iter(self.__children)

    @property
    def title(self):
        return self.__title

    @property
    def id(self):
        return self.__id

    @property
    def description(self):
        return self.__description

    @property
    def children(self):
        return self.__children

    @classmethod
    def _parse_category(cls, root_category_field: Field) -> list:
        res_list = []
        categories = root_category_field.get_multi('category', None)
        if categories is not None:
            for category in categories:
                title = category.get('title', '')
                id = category.get('id', None)
                description = category.get('description', '')

                res_list.append(
                    Category(
                        title=title,
                        id=id,
                        description=description,
                        children=cls._parse_category(category.get_multi('category', None))
                    )
                )
        return res_list

    def _parse(self, root_field):
        if self.__children is None:
            self.__children = self._parse_category(root_field)
        return self.__children


class CategoryService:
    def __init__(self, synamic_config):
        self.__config = synamic_config
        self.__type_system = synamic_config.type_system
        self.__category_map_by_id = {}
        self.__is_loaded = False

        self.__service_home_path = None
        self.__config.register_path(self.service_home_path)

    @property
    def service_home_path(self) -> ContentPath2:
        if self.__service_home_path is None:
            self.__service_home_path = self.__config.path_tree.create_path(('meta', 'categories'))
        return self.__service_home_path

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        category_map = self.__category_map_by_id

        file_paths = self.service_home_path.list_paths()

        Category.set_config(self.__config)

        for file_path in file_paths:
            if file_path.basename.endswith('.categories.txt') and len(file_path.basename) > len('.categories.txt'):
                with file_path.open('r', encoding='utf-8') as f:
                    model_txt = f.read()
                    root_category = Category(
                        title='__root__',
                        id=-100,
                        description=''
                    )
                    root_category._parse(FieldParser(model_txt).parse())

                    # TODO: set category by id. It's yet incomplete
        self.__is_loaded = True

    def __getattr__(self, key):
        return self.__menu_map.get(key)

    def __getitem__(self, key):
        return self.__menu_map.get(key)