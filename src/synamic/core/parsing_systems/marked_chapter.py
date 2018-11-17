"""
Limited markdown parser only to parse chapters, nothing more nothing less.
"""
import re


class _Patterns:
    list_item = re.compile(r'(?P<white_spaces>\s*)(?P<item_marker>[*+-])(?P<item_data>.+)')
    blanks = re.compile(r'^\s*$')


def convert_tabs(text: str):
    """1 tab is considered four spaces"""
    return text.replace('\t', '    ')


class MarkedChapterParser:
    def __init__(self):
        pass

    def parse(self, text: str):
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            blank_line_match = _Patterns.blanks.match(line)
            list_item_match = _Patterns.list_item.match(line)

            # skip blank lines
            if blank_line_match:
                continue
            if list_item_match:
                white_spaces = convert_tabs(list_item_match.group('white_spaces'))
                item_marker = list_item_match.group('item_marker')
                item_data = list_item_match.group('item_data')
            else:
                ...
