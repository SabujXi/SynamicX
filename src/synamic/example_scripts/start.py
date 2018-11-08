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
site_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_site")

print("SITE-ROOT: %s" % site_root)

syn = Synamic(site_root)
syn.load()
# a_cnt = syn.filter_content("(text:: tags in x, y)")[0]
# print(a_cnt.cpath.relative_path)
# syn.paginate(a_cnt, "(texts)", per_page=1)
syn.build()
