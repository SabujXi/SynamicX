"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

from synamic.core.services.filesystem.content_path import ContentPath2
from synamic.core.parsing_systems.document_parser import FieldParser, Field
from synamic.core.standalones.functions.decorators import not_loaded
from synamic.core.services.category.functions.construct_category_id import construct_category_id
from synamic.core.services.category.functions.construct_category_url import construct_category_url
from synamic.core.services.category.functions.normalize_category_title import normalize_category_title


class Category:
    def __init__(self, synamic, children=None, title=None, id=None, description=None, other_fields=None):
        assert title is not None
        self.__title = normalize_category_title(title)
        self.__title_lower = self.__title.lower()
        self.__id = construct_category_id(id, self.__title_lower)
        self.__description = description if description is not None else ''
        self.__children = () if children is None else children
        self.__other_fields = {} if other_fields is None else other_fields
        self.__url_object = construct_category_url(synamic, self)

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

    @property
    def url_object(self):
        return self.__url_object

    def __getitem__(self, item):
        return self.__other_fields.get(item, None)

    def __str__(self):
        return self.title + " : " + str(self.children)

    def __repr__(self):
        return repr(str(self))

    def __iter__(self):
        return iter(self.__children)


class CategoryService:
    def __init__(self, synamic):
        self.__synamic = synamic
        # self.__type_system = synamic_config.type_system
        self.__root_categories = []
        self.__category_map_by_id = {}
        self.__category_map_by_title_lower = {}
        self.__is_loaded = False

        self.__service_home_path = None
        self.__synamic.register_path(self.service_home_path)

    @property
    def service_home_path(self) -> ContentPath2:
        if self.__service_home_path is None:
            self.__service_home_path = self.__synamic.path_tree.create_path(('meta', 'taxonomies', 'categories'))
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
                    del dict_flat['id']
                description = dict_flat.get('description', None)
                if description is not None:
                    del dict_flat['description']

                res_list.append(self.__add_category(
                    title, id=id, description=description, others=dict_flat, children=category_field
                ))
        return tuple(res_list)

    def __add_category(self, title, id=None, description=None, others=None, children=None):
        cat = Category(
            self.__synamic,
            title=title,
            id=id,
            description=description,
            children=None if children is None else self._parse_category(children),
            other_fields=others
        )

        assert cat.id not in self.__category_map_by_id, "Duplicate category id: %s" % id
        self.__category_map_by_id[cat.id] = cat
        self.__category_map_by_title_lower[cat.title.lower()] = cat
        return cat

    def add_category(self, title, id=None, description=None, others=None, children=None):
        c = self.get_category_by_title(title)
        if c:
            return c
        return self.__add_category(title, id=id, description=description, others=others, children=None)

    def get_category_by_title(self, title):
        title = normalize_category_title(title).lower()
        c = self.__category_map_by_title_lower.get(title, None)
        return c

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

    def __iter__(self):
        return iter(self.get_sorted_categories())

    def get_sorted_categories(self, reverse=False):
        # sorts alphabetically
        categories = self.all
        sorted_categories = sorted(categories, key=lambda category: category.title, reverse=reverse)
        return sorted_categories
