import unittest
from synamic.frontmatter.front_matter import parse_front_matter


class TestFrontMatterParser(unittest.TestCase):
    def setUp(self):
        self.invalid_frontmatter1 = """---
        u:ttt
        hhhs-----
        """
        self.empty_frontmatter = """
        the content is here, no front matter around here.
        """
        self.valid_frontmatter = """----
name: My name
url: somehow/url
----
        """
        self.empty_text = ""

    def test_invalid(self):
        res = parse_front_matter(self.invalid_frontmatter1)
        self.assertTupleEqual(res, (None, None, None), "This should not be considered as a valid frontmattered text")

    def test_valid(self):
        res = parse_front_matter(self.valid_frontmatter)
        self.assertEqual(res[0], True)
        self.assertEqual(res[1], """name: My name
url: somehow/url""")
        self.assertEqual(res[2], """        """)

    def test_empty_frontmatter(self):
        res = parse_front_matter(self.empty_frontmatter)
        self.assertEqual(res[0], False, "No frontmatter must return False")
        self.assertEqual(res[2], self.empty_frontmatter)

    def test_empty_text(self):
        res = parse_front_matter(self.empty_text)
        self.assertTupleEqual(res[:2], (False, None), "the frontmatter is empty")
        self.assertEqual(res[2], "", "Body must be empty as the text is")
