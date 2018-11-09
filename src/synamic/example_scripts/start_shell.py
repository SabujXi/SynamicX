"""
This script will be used when the installed synamic shell is not being used and 
the source is in use, for example, during development.
"""
import os
import sys

SYNAMIC_LIBRARY_ROOT = "C:\\...."  # full path to synamic library/src
sys.path.insert(0, SYNAMIC_LIBRARY_ROOT)

from synamic.core.synamic import Synamic
from synamic.entry_points.shell import start_shell


SITE_ROOT_DIR = "test_site"  # put the relative directory name of the site (relative to this script)

site_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), SITE_ROOT_DIR)

print("SITE-ROOT: %s" % site_root)

start_shell(Synamic, site_root)
