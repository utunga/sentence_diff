from unittest import TestCase

from sentence_diff import SentenceDiff

def diff(actual_sentence, target_sentence):
    return SentenceDiff(actual_sentence=actual_sentence, target_sentence=target_sentence)

class TestDifferencer(TestCase):

    def test_x_v_y_wer(self):
        d = diff("I like to eat people", "I like like to eat people")
        assert d.wer() == 1/6

    def test_y_v_x_wer(self):
        d = diff("I like like to eat people", "I like  to eat people")
        assert d.wer() == 1/5

    def test_words_added(self):
        d = diff("I like Like to eat people", "I like to eat people")
        assert d.mistakes() == [
        ("Like", None, 2,'added')]

    def test_words_changed(self):
        d = diff("How do you", "how are you")
        assert d.mistakes() == [
        ("do", "are", 1, 'changed')]

    def test_words_skipped(self):
        d = diff("How see you", "how good to see you")
        assert d.mistakes() == [
        (None, "good", 1, 'skipped'), 
        (None, "to", 1, 'skipped')]

    def test_combined(self):
        d = diff("can i has 7 loaves of bread please ", "Can I have seven loaves, please?")
        assert d.mistakes() == [
        ('has', 'have', 2, 'changed'),
        ('of', None, 5, 'added'),
        ('bread', None, 6, 'added')]

    def test_no_mistakes(self):
        d = diff("my name is leaf", "My name is leaf!")
        assert d.mistakes() == []

    def test_yes_no_words(self):
        d = diff("How about a good bath", "Would you like a good bath?")
        assert d.yes_no_words() == [
        ("How", False),
        ("about", False),
        ("a", True),
        ("good", True),
        ("bath", True)]

    def test_yes_no_numbers(self):
        d = diff("can i have 7 loaves please", "Can I have seven loaves, please?")
        assert d.yes_no_words() == [
        ("can", True),
        ("i", True),
        ("have", True),
        ("7", True),
        ("loaves", True),
        ("please", True)]

    def test_numbers_mistake(self):
        d = diff("can i have 62 loaves please", "Can I have seven loaves, please?")
        assert d.mistakes() == [
        ("62", "seven", 3, "changed")]
      
    def test_numbers_mistake_logic_fail(self):
        # this shows the limitations of the current system
        # id say its not really want you want but it sort of works
        # and as long as you stick to single digits we're fine
        d = diff("can i have 27 loaves please", "Can I have twenty six loaves, please?")
        assert d.mistakes() == [
        (None, 'twenty', 3, 'skipped'), 
        ('27', 'six', 3, 'changed')]
      
    def test_scored_words(self):
        d = diff("can i has 7 loaves of bread please ", "Can I have seven loaves, please?")
        assert d.scored_words() == [
        ('can', 'Can', 0, None),
        ('i', 'I', 1, None),
        ('has', 'have', 2, 'changed'),
        ('7', 'seven', 3, None),
        ('loaves', 'loaves', 4, None),
        ('of', None, 5, 'added'),
        ('bread', None, 6, 'added'),
        ('please', 'please', 7, None)]