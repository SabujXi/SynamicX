import os
from synamic.shell.synamic_shell import start_shell
from synamic.core.synamic import Synamic


def main():
    cfg = Synamic(os.getcwd())
    start_shell(cfg)
