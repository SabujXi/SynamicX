class BuilderService:
    def __init__(self, site):
        self.__site = site

    def __build_contents(self, content_paths):
        pass

    def __build_paginated_contents(self):
        pass

    def __build_statics(self, static_paths):
        pass

    def __build_root_files(self, root_file_paths):
        pass

    def build(self):
        site_ids = self.__site.object_manager.get_site_ids()
        for site_id in site_ids:
            content_paths = self.__site.object_manager.get_all_content_paths(site_id)
            self.__build_contents(content_paths)
            self.__build_paginated_contents()
            static_paths = self.__site.object_manager.get_all_static_paths(site_id)
            self.__build_statics(static_paths)


