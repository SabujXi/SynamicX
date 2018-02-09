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
cnts = syn.filter_content("(texts:: tags in 'x') // (texts:: tags not in z)")

for cnt in cnts:
    print(cnt.path_object.relative_path)
