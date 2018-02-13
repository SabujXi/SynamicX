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
    def __init__(self, children=None, title=None, id=None, description=None, other_fields=None):
        assert title is not None
        self.__title = title
        self.__id = id
        self.__description = description if description is not None else ''
        self.__children = children
        self.__other_fields = {} if other_fields is None else other_fields

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

    # def __getattr__(self, item):
    #     return self.__other_fields.get(item, None)

    def __getitem__(self, item):
        return self.__other_fields.get(item, None)

    def __str__(self):
        return self.title + " : " + str(self.children)

    def __repr__(self):
        return repr(str(self))


class CategoryService:
    def __init__(self, synamic_config):
        self.__config = synamic_config
        # self.__type_system = synamic_config.type_system
        self.__root_categories = []
        self.__category_map_by_id = {}
        self.__category_map_by_title_lower = {}
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
        file_paths = self.service_home_path.list_files()

        root_cat_cats2d = []
        for file_path in file_paths:
            if file_path.basename.endswith('.categories.txt') and len(file_path.basename) > len('.categories.txt'):
                with file_path.open('r', encoding='utf-8') as f:
                    model_txt = f.read()
                    root_categories1d = self._parse_category(FieldParser(model_txt).parse())
                    root_cat_cats2d.append(root_categories1d)
        for cat_arr1d in root_cat_cats2d:
            for cat in cat_arr1d:
                self.__root_categories.append(cat)
        self.__is_loaded = True

        # for rcat in self.all:
        #     print("Cat: %s" % rcat)
        #     print("Cat xt: %s" % rcat.ext)

    def _parse_category(self, root_category_field: Field) -> tuple:
        res_list = []
        category_fields = root_category_field.get_multi('category', None)
        if category_fields is not None:
            for category_field in category_fields:
                dict_flat = category_field.to_dict_flat()
                title = dict_flat.get('title', None)
                if title is None:
                    raise Exception("Title is a must")
                else:
                    # title = title.value
                    del dict_flat['title']
                id = dict_flat.get('id', None)
                if id is not None:
                    # id = id.value
                    del dict_flat['id']
                description = dict_flat.get('description', None)
                if description is not None:
                    # description = description.value
                    del dict_flat['description']

                cat = Category(
                    title=title,
                    id=id,
                    description=description,
                    children=self._parse_category(category_field),
                    other_fields=dict_flat
                )

                if id is not None:
                    if id in self.__category_map_by_id:
                        raise Exception("Duplicate category id: %s" % id)
                    else:
                        self.__category_map_by_id[id] = cat
                self.__category_map_by_title_lower[title.lower()] = cat

                res_list.append(cat)
        return tuple(res_list)

    # def _parse(self, root_field):
    #     if self.__children is None:
    #         self.__children = self._parse_category(root_field)
    #     return self.__children

    @property
    def all(self):
        return tuple(self.__category_map_by_title_lower.values())

    @property
    def all_root(self):
        return tuple(self.__root_categories)

    def __getattr__(self, key):
        return self.__category_map_by_id.get(key, None)

    def __getitem__(self, key):
        return self.__category_map_by_id.get(key, None)
