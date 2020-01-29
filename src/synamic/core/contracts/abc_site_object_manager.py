import abc
from abc import abstractmethod
from synamic.core.models.site import Site


class AbcSiteObjectManager(metaclass=abc.ABCMeta):
    def __init__(self, parent_site: Site):
        """
        Site can be root site.
        """
        self._parent_site: Site = parent_site

