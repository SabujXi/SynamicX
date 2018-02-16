"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import os
from synamic.core.synamic import Synamic
site_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), "experiment_dir")

print("SITE-ROOT: %s" % site_root)

syn = Synamic(site_root)
syn.initialize_site()

syn.load()
syn.build()
