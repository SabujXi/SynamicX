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
from synamic.exceptions import SynamicSydParseError, SynamicErrors, SynamicFSError


class _Menu:
    def __init__(self, site, title=None, link=None, id=None, children=None, other_fields=None):
        assert title is not None
        self.__site = site
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
        return self.__site.object_manager.getc(self.__link)

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
    def __init__(self, site):
        self.__site = site
        self.__is_loaded = False
        self.__menu_dir = self.__site.system_settings['dirs.metas.menus']

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        # for file_path in file_paths:
        self.__is_loaded = True

    def make_menu(self, name):
        path_tree = self.__site.get_service('path_tree')
        fn = name + '.syd'
        path = path_tree.create_file_cpath(self.__menu_dir, fn)
        try:
            syd = self.__site.object_manager.get_syd(path)
        except (SynamicSydParseError, SynamicFSError) as e:
            raise SynamicErrors(
                f"Synamic error during making menu object. Error occurred for menu named {name}",
                e
            )

        menu_obj = _Menu(
            self.__site,
            title=name,
            link='__root_link__',
            children=self._process_menu(syd)
        )
        return menu_obj

    def get_menu_names(self):
        menu_names = []
        path_tree = self.__site.get_service('path_tree')
        menu_cdir = path_tree.create_dir_cpath(self.__menu_dir)
        if menu_cdir.exists():
            menu_cfiles = menu_cdir.list_files(depth=1)
            for menu_cfile in menu_cfiles:
                basename = menu_cfile.basename
                if basename.lower().endswith('.syd'):
                    menu_name = basename[:-len('.syd')]
                    menu_names.append(menu_name)
        return tuple(menu_names)

    def _process_menu(self, starting_menu_syd) -> tuple:
        res_list = []
        menus = starting_menu_syd.get('menus', None)
        if menus is not None:
            for menu in menus:
                dict_flat = menu
                title = dict_flat.get('title', None)
                assert title is not None
                del dict_flat['title']
                link = dict_flat.get('link', None)
                if link is not None:
                    del dict_flat['link']
                res_list.append(
                    _Menu(
                        self.__site,
                        title=title,
                        link=link,
                        children=self._process_menu(menu),
                        other_fields=dict_flat
                    )
                )
        return tuple(res_list)

