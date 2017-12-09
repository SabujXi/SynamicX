class TaxonomyContent:
    pass


class TaxonomyModule:
    def __init__(self, config):
        self.__config = config

    def load(self):
        self.__config.path_tree

