from unittest import TestCase
from sentence_diff import SentenceDiff

class TestHomonyms(TestCase):

    def test_sentence_homonymsdeserts(self):
        result = SentenceDiff._homonyms("I love desert")
        assert result == ["I love desert", "I love dessert"]

    def test_substitutions(self):
        list_of_lists = [["a","b"],
                         ["x","y","z"]]
        result = SentenceDiff._all_substitutions(list_of_lists)
        assert result == \
           [("a","b"),
            ("b","a"),
            ("x", "y"),
            ("x", "z"),
            ("y", "x"),
            ("y", "z"),
            ("z", "x"),
            ("z", "y")]

