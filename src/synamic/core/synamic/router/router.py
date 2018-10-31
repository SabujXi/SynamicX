from urllib.parse import urlparse


class RouterService:
    def __init__(self, synamic):
        self.__synamic = synamic

        self.__is_loaded = False

    def load(self):
        self.__is_loaded = True

    def get_content(self, url_str):
        parsed_url = urlparse(url_str)
        url_path = parsed_url.path
        # Unused for now: url_query = parsed_url.query
        # Unused for now: url_fragment = parsed_url.fragment

        path_segments = url_path.split('/')
        # synamic must put / at the end of url unless the url ends with a file extension or it is a static file.
        if len(path_segments) > 0:
            if path_segments[0] == '':
                del path_segments[0]
                if len(path_segments) > 0:
                    if path_segments[-1] == '':
                        del path_segments[-1]

        # synamics_service = self.__synamic.get_service('synamics')
        site_ids = self.__synamic.object_manager.get_site_ids()
        # the root site id will be '' - and yes, it will be listed in get_site_ids
        sites_id_segments = [site_id.split('/') for site_id in site_ids]

        # extract out site id.
        site_id = ''
        for site_id_segments in sites_id_segments:
            if len(path_segments) < len(site_id_segments):
                continue
            if path_segments[:len(site_id_segments)] == site_id_segments:
                path_segments = path_segments[len(site_id_segments):]
                site_id = '/'.join(site_id_segments)
                break

        # extract out paginated part
        pagination_segments = []  # None?
        pagination_sep = self.__synamic.object_manager.get_site_settings()['pagination_sep']
        assert '/' not in pagination_sep
        idx = 0
        sep_idx = -1
        for segment in path_segments:
            if segment == pagination_sep:
                sep_idx = idx
                break
        if sep_idx != -1:
            pagination_segments = path_segments[idx:]
            path_segments = path_segments[0:idx]

        # if path segments got empty in all those extractions
        if len(path_segments) == 0:
            path_segments.append('')

        return self.__synamic.object_manager.get_content_by_segments(site_id, path_segments, pagination_segments)

