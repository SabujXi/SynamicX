import os
from synamic.entry_points.shell import start_shell
from synamic.core.synamic import Synamic


def main():
    start_shell(Synamic, os.getcwd())


if __name__ == '__main__':
    main()
