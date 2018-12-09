from synamic.core.services.marker.marker import Marker
from .marker import _Mark


class MarkerService:
    def __init__(self, site):
        self.__site = site

        self.__is_loaded = False

    def load(self):
        self.__is_loaded = True

    def make_marker(self, marker_id):
        markers_cdir = self.__site.cpaths.markers_cdir
        syd = self.__site.object_manager.get_syd(markers_cdir.join_as_cfile(marker_id + '.syd'))
        marker_type = syd['type']
        marker_title = syd.get('title', marker_type)
        marker_mark_maps = syd['marks']
        marker = Marker(self.__site, marker_id, marker_type, marker_title, marker_mark_maps, syd)
        return marker

    def get_marker_ids(self):
        markers_cdir = self.__site.cpaths.markers_cdir

        _ = []
        if markers_cdir.exists():
            marker_cpaths = markers_cdir.list_files(checker=lambda cp: cp.basename.endswith('.syd'))
            for cp in marker_cpaths:
                _.append(cp.basename[:-len('.syd')])
        ids = tuple(_)
        return ids

    def is_type_mark(self, other):
        return isinstance(other, _Mark)
