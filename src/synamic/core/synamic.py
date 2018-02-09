"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

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
