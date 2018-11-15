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
            cdoctype = CDocType.UNSPECIFIED
            curl = self.make_url(site, path_components, cdoctype)
            if special_components:
                print(f'Special Components: {special_components}')
                pagination_url_comp = self.__synamic.system_settings['pagination_url_comp']
                mark_url_comp = self.__synamic.system_settings['mark_url_comp']
                user_url_comp = self.__synamic.system_settings['user_url_comp']

                if special_components[0] == user_url_comp:
                    if len(special_components) < 2:
                        return None
                    else:
                        user_id = special_components[1]
                        user = site.object_manager.get_user(user_id)
                        if user is None:
                            return None
                        else:
                            return user.content
                elif special_components[0] == mark_url_comp:
                    if len(special_components) < 3:
                        return None
                    else:
                        marker_id_or_slug = special_components[1]
                        mark_id = special_components[2]
                        marker = site.object_manager.get_marker(marker_id_or_slug, default=None)
                        if marker is None:
                            marker = site.object_manager.get_marker_by_slug(marker_id_or_slug)
                        if marker is None:
                            return None
                        mark = marker.get_mark_by_id(mark_id)
                        if mark is None:
                            return None
                        else:
                            return mark.content
                elif special_components[0] == pagination_url_comp:
                    if len(special_components) < 2:
                        return None
                    else:
                        page_no = special_components[1]
                        if page_no.isdigit():
                            page_no = int(page_no)
                        else:
                            return None

                        root_content = self.get_content_by_url(site, curl)
                        if root_content is None:
                            return None
                        else:
                            sub_page = root_content.pagination.get_sub_page(page_no)
                            if sub_page is None:
                                return None
                            else:
                                return sub_page.host_content
            content = self.get_content_by_url(site, curl)
        return content

    def get_content_by_url(self, site, curl):
        """Forgiving function that returns None"""
        print(f'Querying {curl.path_components} - doctype {curl.for_cdoctype} on site {site.id}')
        # try for text doc
        marked_content = site.object_manager.get_marked_content_by_curl(curl)
        if marked_content is not None:
            return marked_content

        pre_processed_content = site.object_manager.get_pre_processed_content_by_curl(curl)
        if pre_processed_content is not None:
            return pre_processed_content
        else:
            # TODO: fix bug: a.txt /a.txt/ and /a.txt work the same - /a.txt/ is most weird
            contents_dir = self.__synamic.system_settings['dirs.contents.contents']
            contents_dir_cpath = site.path_tree.create_dir_cpath(contents_dir)

            curl = curl.clone(CDocType.GENERATED_BINARY_DOCUMENT)

            fs_path = curl.to_file_system_path
            fs_path = fs_path.rstrip('/\\')
            file_cpath = contents_dir_cpath.join(fs_path, is_file=True)

            if file_cpath.exists():
                return site.object_manager.get_binary_content(file_cpath)
            else:
                return None

    @classmethod
    def make_url(cls, site, url_path_comps, for_cdoctype=CDocType.UNSPECIFIED):
        return ContentUrl(site, url_path_comps, for_cdoctype=for_cdoctype)
