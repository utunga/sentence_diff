import re
import string
import numpy as np
import inflect
import difflib
from better_profanity import profanity
from sentence_diff import SentenceDiff

THRESHOLD_PASS = .4
THRESHOLD_SUPER_PASS = .7

class WordDiff:

    def __init__(self, actual, target):
        SentenceDiff._assert_not_empty(actual,target)
        self.actual = actual
        self.target = target
        self.actual_lower = self.normalize(actual)
        self.target_lower = self.normalize(target)

    def chatterize_score(self):
        similarity = self.similarity(self.actual_lower, self.target_lower)
        pass_fail = "SUPER PASS" if similarity > THRESHOLD_SUPER_PASS \
                    else "PASS" if similarity > THRESHOLD_PASS \
                    else "FAIL"
        return pass_fail, similarity

    def normalize(self, text):
        return \
            SentenceDiff._remove_punctuation(
                SentenceDiff._single_word_sub(
                    SentenceDiff._spell_out_numbers_in_word(
                        SentenceDiff._sound_out_dollars(
                            profanity.censor(text.lower(), 'x')))))

    def similarity(self, wordA, wordB):
        # work substitution cost
        # similar words cost close to 0 different words cost 1
        denominator = 0
        numerator = 0
        for i, s in enumerate(difflib.ndiff(wordA, wordB)):
            denominator += 1
            if s[0] == '-' or s[0] == '+':
                numerator += 1
        return 1 - numerator/denominator


