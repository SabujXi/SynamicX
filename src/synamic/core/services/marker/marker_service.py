from synamic.core.services.marker.marker import Marker


class MarkerService:
    def __init__(self, synamic):
        self.__synamic = synamic

        self.__is_loaded = False

    def load(self):
        self.__is_loaded = True

    def make_marker(self, marker_id):
        markers_path = self.__synamic.default_configs.get('dirs').get('metas.markers')
        syd = self.__synamic.object_manager.get_syd(markers_path + '/' + marker_id + '.syd')
        marker_type = syd['type']
        marker_title = syd.get('title', marker_type)
        marker_mark_maps = syd['marks']
        marker = Marker(self.__synamic, marker_id, marker_type, marker_title, marker_mark_maps)
        return marker
