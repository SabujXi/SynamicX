import os
import sys
import codecs
from synamic.shell.synamic_shell import start_shell
from synamic.core.synamic import Synamic

# sys.stdout = codecs.getwriter('utf8')(sys.stdout)
# sys.stderr = codecs.getwriter('utf8')(sys.stderr)


def main():
    start_shell(Synamic, os.getcwd())
