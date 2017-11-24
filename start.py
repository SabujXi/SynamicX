import os
import sys
from synamic.core.synamic import Synamic
site_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_site")
print("SITE-ROOT: %s" %site_root)
# synamic_module_path = os.path.join(site_root, "src")
# print(sys.path)
# sys.path.append(synamic_module_path)
# print(sys.path)
syn = Synamic(site_root)
syn.initialize_site_dirs()
syn.load()
syn.render()
