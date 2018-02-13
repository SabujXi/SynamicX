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


class Menu:
    def __init__(self, config, title=None, link=None, id=None, children=None, other_fields=None):
        assert title is not None
        self.__config = config
        self.__title = title
        self.__link = link
        self.__id = id
        self.__children = children if children is not None else ()
        self.__other_fields = {} if other_fields is None else other_fields

    def __iter__(self):
        return iter(self.__children)

    @property
    def title(self):
        return self.__title

    @property
    def link(self):
        # if self.__link is None:
        lsrc = self.__link.lower()
        if lsrc.startswith('geturl://'):
            _url = self.__link[len('geturl://'):]
            url = self.__config.get_url(_url)
        else:
            url = self.__link
        # self.__link = url

        # print("link : %s" % url)
        # return self.__link
        return url


    @property
    def children(self):
        return self.__children

    def __getattr__(self, item):
        return self.__other_fields.get(item, None)

    def __getitem__(self, item):
        return self.__other_fields.get(item, None)

    def __str__(self):
        return self.title + " (%s) : " % self.link + str(self.children)

    def __repr__(self):
        return repr(str(self))


class MenuService:
    def __init__(self, synamic_config):
        self.__config = synamic_config
        self.__menu_map = {}
        self.__is_loaded = False

        self.__service_home_path = None
        self.__config.register_path(self.service_home_path)

    @property
    def service_home_path(self) -> ContentPath2:
        if self.__service_home_path is None:
            self.__service_home_path = self.__config.path_tree.create_path(('meta', 'menus'))
        return self.__service_home_path

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        menu_map = self.__menu_map
        file_paths = self.service_home_path.list_files()

        for file_path in file_paths:
            if file_path.basename.endswith('.menu.txt') and len(file_path.basename) > len('.menu.txt'):
                with file_path.open('r', encoding='utf-8') as f:
                    model_txt = f.read()
                    menu_id = file_path.basename[:-len('.menu.txt')]
                    menu_map[menu_id] = Menu(
                        config=self.__config,
                        title='__root__',
                        link='__root_link__',
                        children=self._parse_menu(FieldParser(model_txt).parse())
                    )

        self.__is_loaded = True

    def _parse_menu(self, starting_menu: Field) -> tuple:
        # print(starting_menu)
        # res_list = res_list if res_list is not None else []
        res_list = []
        menus = starting_menu.get_multi('menu', None)
        if menus is not None:
            for menu in menus:
                dict_flat = menu.to_dict_flat()
                title = dict_flat.get('title', None)
                assert title is not None
                del dict_flat['title']
                link = dict_flat.get('link', None)
                if link is not None:
                    del dict_flat['link']
                res_list.append(
                    Menu(
                        config=self.__config,
                        title=title,
                        link=link,
                        children=self._parse_menu(menu),
                        other_fields=dict_flat
                    )
                )
        return tuple(res_list)

    @property
    def all_root(self):
        return tuple(self.__root_menus)
    #
    # def __getattr__(self, key):
    #     return self.__menu_map.get(key, None)

    def __getitem__(self, key):
        return self.__menu_map.get(key, None)
