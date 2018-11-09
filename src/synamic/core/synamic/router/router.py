from synamic.core.synamic.router.url import ContentUrl
from synamic.core.contracts import CDocType


class RouterService:
    def __init__(self, synamic):
        self.__synamic = synamic
        self.__is_loaded = False

    def load(self):
        self.__is_loaded = True

    def get_content(self, url_str: str):
        site_id, path_components, special_components = ContentUrl.parse_requested_url(self.__synamic, url_str)
        try:
            site = self.__synamic.sites.get_by_id(site_id)
        except KeyError:
            site = None

        if site is None:
            content = None
        else:
            # step 1: search for static/binary file in file system with the path components : TODO: do for static.
            # step 2 if 1 fails: search for non-static content and in this case the url is already cached.
            curl = self.make_url(site, path_components, CDocType.NONE)
            content = self.get_content_by_url(site, curl)
            if content is None:
                curl = self.make_url(site, path_components, CDocType.HTML_DOCUMENT)
                content = self.get_content_by_url(site, curl)
        return content

    def get_content_by_url(self, site, curl):
        """Forgiving function that returns None"""
        if CDocType.is_text(curl.for_cdoctype):
            content_cpath = site.object_manager.get_marked_cpath_by_curl(curl)
            if content_cpath is not None:
                return site.object_manager.get_marked_content(content_cpath)
            else:
                return None
        else:
            # TODO: fix bug: a.txt /a.txt/ and /a.txt work the same - /a.txt/ is most weird
            contents_dir = self.__synamic.default_data.get_syd('dirs')['contents.contents']
            contents_dir_cpath = site.object_manager.get_path_tree().create_dir_cpath(contents_dir)
            fs_path = curl.to_file_system_path
            fs_path = fs_path.rstrip('/\\')
            file_cpath = contents_dir_cpath.join(fs_path, is_file=True)

            if file_cpath.exists():
                return site.object_manager.get_binary_content(file_cpath)
            else:
                return None

    @classmethod
    def make_url(cls, site, url_path_comps, for_cdoctype=None):
        return ContentUrl(site, url_path_comps, for_cdoctype=for_cdoctype)
