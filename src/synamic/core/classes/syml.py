"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import re


class Syml:
    def __init__(self, text):
        self.__text = text
        self.__syml_map = None
        self.__parse()

    def __parse(self):
        assert self.__syml_map is None
        tab_size = 4

        text = self.__text.strip()
        start_pos = 0
        end_pos = len(text) - 1
        if text == '':
            self.__syml_map = {}
            return

        name_value = {}

        name_pat = re.compile('^(?P<name>[a-z]+)\s*:', re.I)
        newline_pat = re.compile(r'\n\r|\n|\r')

        line_no = 1
        while start_pos <= end_pos + 1:


            line_no += 1

