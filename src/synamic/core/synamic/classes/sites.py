class Sites:
    def __init__(self, synamic, sites_dict):
        self.__synamic = synamic
        self.__sites_dict = sites_dict

    def __getitem__(self, item):
        return self.__sites_dict.get(item)

    def __getattr__(self, item):
        return self.__sites_dict.get(item)

    @property
    def synamic(self):
        return self.__synamic

    @property
    def root_synamic(self):
        res = self.synamic

        while res is not None:
            res = res.parent
        return res