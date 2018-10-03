"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
from synamic.core.standalones.functions.decorators import not_loaded


class _Menu:
    def __init__(self, synamic, title=None, link=None, id=None, children=None, other_fields=None):
        assert title is not None
        self.__synamic = synamic
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
        router = self.__synamic.get_service('router')
        return router.get_url(self.__link)

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
    def __init__(self, synamic):
        self.__synamic = synamic
        self.__is_loaded = False
        self.__menu_dir = self.__synamic.default_configs.get('dirs').get('metas.menus')

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        # for file_path in file_paths:
        self.__is_loaded = True

    def make_menu(self, name):
        path_tree = self.__synamic.get_service('path_tree')
        fn = name + '.syd'
        path = path_tree.create_file_path(self.__menu_dir, fn)
        syd = self.__synamic.object_manager.get_syd(path)

        menu_obj = _Menu(
            self.__synamic,
            title=name,
            link='__root_link__',
            children=self._process_menu(syd)
        )
        return menu_obj

    def _process_menu(self, starting_menu_syd) -> tuple:
        res_list = []
        menus = starting_menu_syd.get('menus', None)
        if menus is not None:
            for menu in menus.values():
                dict_flat = menu
                title = dict_flat.get('title', None)
                assert title is not None
                del dict_flat['title']
                link = dict_flat.get('link', None)
                if link is not None:
                    del dict_flat['link']
                res_list.append(
                    _Menu(
                        self.__synamic,
                        title=title,
                        link=link,
                        children=self._process_menu(menu),
                        other_fields=dict_flat
                    )
                )
        return tuple(res_list)

