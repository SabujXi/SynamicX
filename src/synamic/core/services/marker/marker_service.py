from synamic.core.services.marker.marker import Marker


class MarkerService:
    def __init__(self, site):
        self.__site = site

        self.__is_loaded = False

    def load(self):
        self.__is_loaded = True

    def make_marker(self, marker_id):
        markers_path = self.__site.default_data.get_syd('dirs').get('metas.markers')
        syd = self.__site.object_manager.get_syd(markers_path + '/' + marker_id + '.syd')
        marker_type = syd['type']
        marker_title = syd.get('title', marker_type)
        marker_mark_maps = syd['marks']
        marker = Marker(self.__site, marker_id, marker_type, marker_title, marker_mark_maps)
        return marker

    def get_marker_ids(self):
        path_tree = self.__site.get_service('path_tree')
        markers_path = self.__site.default_data.get_syd('dirs').get('metas.markers')
        marker_cpaths = path_tree.list_file_cpaths(markers_path, checker=lambda cp: cp.basename.endswith('.syd'))
        _ = []
        for cp in marker_cpaths:
            _.append(cp.basename[:-len('.syd')])
        ids = tuple(_)
        return ids

