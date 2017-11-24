from synamic.core import synamic_config


class Synamic(synamic_config.SynamicConfig):
    def __init__(self, site_root):
        super().__init__(site_root)

    # def render(self):
    #     # load
    #     for mod in self.get_meta_content_modules():
    #         mod.load(self)
    #
    #     for mod in self.get_content_modules():
    #         mod.load(self)
    #
    #     for mod in self.get_templates_modules():
    #         mod.load(self)
    #
    #     # run: as mentioned - only content runs
    #     for mod in self.get_content_modules():
    #         mod.run(self)
