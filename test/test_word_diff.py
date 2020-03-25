from unittest import TestCase
from sentence_diff import WordDiff

def diff(actual, target):
    d = WordDiff(actual,target)
    return d.chatterize_score()

class TestDifferencer(TestCase):

    def test_big(self):
        target = "big"
        actual = "big"
        pass_fail, score = diff(actual, target)
        assert score == 1
        assert pass_fail == "SUPER PASS"

    def test_food(self):
        target = "order food"
        actual = "all the food i ate food"
        pass_fail, score = diff(actual, target)
        assert score == .2222222222222222
        assert pass_fail == "FAIL"

    def test_dog(self):
        target = "dog"
        actual = "tall dog poke bo suck my mother nature"
        pass_fail, score = diff(actual, target)
        assert score == .07894736842105265
        assert pass_fail == "FAIL"

    def test_superhero(self):
        target = "superhero"
        actual = "superheroes"
        pass_fail, score = diff(actual, target)
        assert score == .8181818181818181
        assert pass_fail == "SUPER PASS"

    def test_shirt(self):
        target = "shirt"
        actual = "sharks"
        pass_fail, score = diff(actual, target)
        assert score == .375
        assert pass_fail == "FAIL"

    def test_pirates(self):
        target = "shirt"
        actual = "shut"
        pass_fail, score = diff(actual, target)
        assert score == .5
        assert pass_fail == "PASS"

    def test_number(self):
        target = "one"
        actual = "1"
        pass_fail, score = diff(actual, target)
        assert score == 1
        assert pass_fail == "SUPER PASS"

    def test_dollars(self):
        target = "100 dollars"
        actual = "$100"
        pass_fail, score = diff(actual, target)
        assert score == 1
        assert pass_fail == "SUPER PASS"


