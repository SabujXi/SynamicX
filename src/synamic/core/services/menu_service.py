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
    __config = None

    @classmethod
    def set_config(cls, config):
        cls.__config = config

    def __init__(self, children=None, title=None, link=None):
        self.__title = title
        self.__link = link
        self.__children = children

    def __iter__(self):
        return iter(self.__children)

    @property
    def title(self):
        return self.__title

    @property
    def link(self):
        return self.__link

    @property
    def children(self):
        return self.__children

    @classmethod
    def _parse_menu(cls, starting_menu: Field) -> list:
        # res_list = res_list if res_list is not None else []
        res_list = []
        menus = starting_menu.get_multi('menu', None)
        if menus is not None:
            for menu in menus:
                title = menu.get('title', None)
                link = menu.get('title', None)

                if not (title is None or link is None):  # otherwise discard
                    # let's get the proper url
                    src = link.value
                    lsrc = link.value.lower()
                    if lsrc.startswith('geturl://'):
                        _url = link.value[len('geturl://'):]
                        url = cls.__config.get_url(_url)
                    else:
                        url = src
                    link = url

                    # title
                    # link

                    res_list.append(
                        Menu(
                            title=title,
                            link=link,
                            children=cls._parse_menu(menu.get_multi('menu', None))
                        )
                    )
        return res_list

    def _parse(self, root_field):
        if self.__children is None:
            self.__children = self._parse_menu(root_field)
        return self.__children


class MenuService:
    def __init__(self, synamic_config):
        self.__config = synamic_config
        self.__type_system = synamic_config.type_system
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

        file_paths = self.service_home_path.list_paths()

        Menu.set_config(self.__config)

        for file_path in file_paths:
            if file_path.basename.endswith('.menu.txt') and len(file_path.basename) > len('.menu.txt'):
                with file_path.open('r', encoding='utf-8') as f:
                    model_txt = f.read()
                    menu_id = file_path.basename[:-len('.menu.txt')]
                    root_menu = menu_map[menu_id] = Menu(
                        title='__root__',
                        link='__root_link__',
                    )
                    root_menu._parse(FieldParser(model_txt).parse())
        self.__is_loaded = True

    def __getattr__(self, key):
        return self.__menu_map.get(key)

    def __getitem__(self, key):
        return self.__menu_map.get(key)