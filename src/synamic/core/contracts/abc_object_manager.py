import abc
from abc import abstractmethod
from typing import Sequence
from synamic.core.models.site import Site


class AbcObjectManager(metaclass=abc.ABCMeta):

    # Site
    @abstractmethod
    async def save_site(self, site: Site):
        """
        Depending on the site it set or None update or save.
        :param site:
        :return:
        """

    @abstractmethod
    async def get_sites(self, parent_site: Site = None) -> Sequence[Site]:
        pass

    @abstractmethod
    async def get_site(self, site_id: str) -> Site:
        pass

    @abstractmethod
    async def save_cfield(self, cfield):
        pass

    @abstractmethod
    async def get_content_field(self, site: Site, path: str):
        pass

    @abstractmethod
    async def get_content_fields(self, site: Site, path: str, default=None):
        pass

    @abstractmethod
    async def get_marked_content(self, site, path):
        # create content, meta, set meta with converters. Setting it from here will help caching.
        pass

    @abstractmethod
    async def get_marked_content_paths(self, site):
        pass

    @abstractmethod
    async def get_static_content_paths(self, site):
        pass

    @abstractmethod
    async def get_syd(self, site: Site, path):
        pass

    @abstractmethod
    async def get_model(self, site, model_name):
        pass

    @abstractmethod
    async def get_site_settings(self, site):
        pass

    @abstractmethod
    async def get_menu(self, site, menu_name, default=None):
        pass

    @abstractmethod
    async def get_menus(self, site):
        pass

    @abstractmethod
    async def get_data(self, site, data_name, default=None):
        pass

    @abstractmethod
    async def get_book_tocs(self, site):
        pass

    @abstractmethod
    async def get_user(self, starting_site, user_id):
        pass

    @abstractmethod
    async def get_users(self, site):
        pass
