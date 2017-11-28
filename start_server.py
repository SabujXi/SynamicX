import os
from synamic.core.synamic import Synamic
from synamic.dev_server.server import serve

site_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_site")

print("SITE-ROOT: %s" % site_root)

syn = Synamic(site_root)
syn.load()
serve(syn, 8000)
