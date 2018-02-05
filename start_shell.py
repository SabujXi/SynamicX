import os
from synamic.core.synamic import Synamic
from synamic.shell.synamic_shell import start_shell

site_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_site")

print("SITE-ROOT: %s" % site_root)

syn = Synamic(site_root)


start_shell(syn)
