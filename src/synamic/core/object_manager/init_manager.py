class InitManager:
    def __init__(self, synamic):
        self.__synamic = synamic

    def init_site(self, cpath):
        assert cpath.is_dir
        dir_cpaths, file_cpaths = cpath.list_cpaths()
        if dir_cpaths or file_cpaths:
            print(f'The path {cpath.abs_path} is not empty. Init\'ing failed.')
            return False
        system_settings = self.__synamic.system_settings
        contents_cdir = cpath.join(system_settings['dirs.contents.contents'], is_file=False)

        # create contents directory
        contents_cdir.makedirs()


#  metas
