import re
import string
import numpy as np
import inflect
import difflib
import itertools
import functools
from better_profanity import profanity


class SentenceDiff:

    def __init__(self, actual_sentence, target_sentence):
        self._assert_not_empty(actual_sentence, target_sentence)
        
        # lowercase, normalize, tokenize
        self.actual_sentence = actual_sentence
        self.actual_tokenized = self._tokenize(actual_sentence)
        self.target_tokenized = self._tokenize(target_sentence)

        # split words without lower casing
        self.actual_words = self._tokenize_for_end_user(actual_sentence)
        self.target_words = self._tokenize_for_end_user(target_sentence)

    # public methods 
    def wer(self):
        self._compare()
        return self.error

    def scored_words(self):
        self._compare()
        self._backtrace()
        return self.scored_words

    def mistakes(self):
        self._compare()
        self._backtrace()
        return [tupl for tupl in self.scored_words if tupl[3]]

    def yes_no_words(self):
        self._compare()
        self._backtrace()
        res = []
        for scored in self.scored_words:
            if scored[0]:
                res.append((scored[0], scored[3] is None))
        return res

    def chatterize_score(self):

        actual_homonyms = SentenceDiff._homonyms(self.actual_sentence)

        wer1 = 99
        matrix1 = None
        actual_tokenized1 = None
        actual_words1 = None
        for tmp_actual in actual_homonyms:
            tmp_actual_tokenized = self._tokenize(tmp_actual)
            tmp_wer, tmp_matrix = self._do_compare(tmp_actual_tokenized, self.target_tokenized)
            if tmp_wer < wer1:
                wer1 = tmp_wer
                matrix1 = tmp_matrix
                actual_tokenized1 = tmp_actual_tokenized
                actual_words1 = self._tokenize_for_end_user(tmp_actual)

        wer2 = 99
        matrix2 = None
        actual_tokenized2 = None
        actual_words2 = None
        for tmp_actual in actual_homonyms:
            tmp_actual_tokenized = self._tokenize(tmp_actual)
            tmp_wer, tmp_matrix = self._do_compare(self.target_tokenized, tmp_actual_tokenized)
            if tmp_wer < wer2:
                wer2 = tmp_wer
                matrix2 = tmp_matrix
                actual_tokenized2 = tmp_actual_tokenized
                actual_words2 = self._tokenize_for_end_user(tmp_actual)

        if wer1 <= wer2:
            scored_words, alignment = \
                self._do_backtrace(actual_tokenized1, self.target_tokenized, matrix1, actual_words1, self.target_words)
        else:
            scored_words, alignment = \
                self._do_backtrace(self.target_tokenized, actual_tokenized2, matrix2, self.target_words, actual_words2)

        cost = 0
        word_count = 0
        for tuple in scored_words:
            word_count += 1
            actual = SentenceDiff._remove_punctuation(tuple[0])
            target = SentenceDiff._remove_punctuation(tuple[1])
            action = tuple[3]
            if action is None:
                cost += 0  # correct
            elif action== 'changed':
                cost += SentenceDiff._word_diff_cost(tuple[0], tuple[1])  # substitution cost
            else:
                cost += SentenceDiff._word_add_rm_cost(tuple[0], tuple[1])  # substitution cost

        return (word_count - cost) / word_count

    def print_debug(self):
        self._compare()
        self._backtrace()
        print("actual")
        print(self.actual_tokenized)
        print("target")
        print(self.target_tokenized)
        print("wer")
        print(self.error)
        # print(self.matrix)
        # print(self.path)
        print(self.alignment)
        print("")
        print(self.scored_words)
        print("")
        # print(self.insertions)
        # print(self.deletions)
        # print(self.substitutions)

    def _init_matrix(self, actual, target):
        # initialize the matrix per levenshtein distance
        shape = (len(target) + 1, len(actual) + 1)
        matrix = np.zeros(shape, dtype=np.uint32)
        matrix[0, :] = np.arange(shape[1])
        matrix[:, 0] = np.arange(shape[0])
        return matrix

    def _find_best_actual_homonyms(self):
        homonyms = SentenceDiff._homonyms(self.actual_sentence)
        wer1 = 999
        actual_tokenized = None
        actual_words = None
        for tmp in homonyms:
            tmp_tokenized = self._tokenize(tmp)
            tmp_wer, tmp_matrix = self._do_compare(tmp_tokenized, self.target_tokenized)
            if tmp_wer < wer1:
                wer1 = tmp_wer
                actual_words = self._tokenize_for_end_user(tmp)
                actual_tokenized = tmp_tokenized
        self.actual_tokenized = actual_tokenized
        self.actual_words = actual_words


    def _compare(self):
        self._find_best_actual_homonyms()
        wer, matrix = self._do_compare(self.actual_tokenized, self.target_tokenized)
        self.error = wer
        self.matrix = matrix

    def _do_compare(self, actual, target):
        matrix = self._init_matrix(actual, target)
        for trgt_pos, rw in enumerate(target):
            for actual_pos, hw in enumerate(actual):
                insert = matrix[trgt_pos + 1, actual_pos] + 1
                delete = matrix[trgt_pos, actual_pos + 1] + 1
                if rw != hw:
                    subst = matrix[trgt_pos, actual_pos] + 1
                else:
                    subst = matrix[trgt_pos, actual_pos]

                best = min(insert, delete, subst)
                matrix[trgt_pos + 1, actual_pos + 1] = best

        cost = matrix[-1, -1]
        if len(target)==0:
            return 1
        wer = cost / len(target)
        return wer, matrix

    def _do_backtrace(self, actuals, targets, matrix, actual_words, target_words, safe_mode=False):
        i = len(targets) - 1
        j = len(actuals) - 1

        alignment = []
        path = []
        inserts = 0
        deletions = 0
        substitns = 0
        matched = 0

        while i >= 0 or j >= 0:
            path.append((i + 1, j + 1))
            start = matrix[i + 1, j + 1]
            insert = matrix[i + 1, j]
            delete = matrix[i, j + 1]
            subst = matrix[i, j]
            best = min(start, subst)

            if j < 0:
                return self._do_backtrace(actuals, targets, matrix,
                                          actual_words, target_words, safe_mode=True)

            if insert < best:
                alignment.append((None, actuals[j]))
                inserts += 1
                j -= 1

            elif delete < best or (safe_mode and delete==best):
                alignment.append((targets[i], None))
                deletions += 1
                i -= 1

            else:
                if start == subst: # no change
                    matched += 1
                else:
                    substitns += 1

                alignment.append((targets[i], actuals[j]))
                j -= 1
                i -= 1

        alignment.reverse()
        path.reverse()
        scored_words = []

        # the index returned in scored_words is relative to the *actual* sentence 
        # but we need to keep track of both so we can look up the un-messed-with form of word
        a_idx = 0
        t_idx = 0    
        for pair in alignment:

            if pair[0] == pair[1]:
                actual = actual_words[a_idx]
                target = target_words[t_idx]
                scored_words.append((actual, target, a_idx, None))
                a_idx += 1
                t_idx += 1

            elif pair[0] is None:
                actual = actual_words[a_idx]
                scored_words.append((actual, None, a_idx, "added"))
                a_idx += 1

            elif pair[1] is None:
                target = target_words[t_idx]
                scored_words.append((None, target, a_idx, "skipped"))
                t_idx += 1

            else:

                actual = actual_words[a_idx]
                target = target_words[t_idx]
                scored_words.append((actual, target, a_idx, "changed"))
                a_idx += 1
                t_idx += 1

        return scored_words, alignment

    def _backtrace(self):
        scored_words, alignment =\
            self._do_backtrace(self.actual_tokenized, self.target_tokenized, self.matrix, self.actual_words, self.target_words)
        self.scored_words = scored_words
        self.alignment = alignment

    def _tokenize(self, sentence):
        normalized_lower = self._normalize(sentence).lower()
        words = normalized_lower.split()
        words = SentenceDiff._single_word_subs(words)
        words = self._spell_out_numbers(words)
        return words

    def _tokenize_for_end_user(self, text):
        text = SentenceDiff._sound_out_dollars(
                    profanity.censor(text, 'x'))
        words = str(text).strip().split()
        return [word for word in words if len(self._remove_punctuation(word).strip())>0]

    def _normalize(self, text):
        return \
            self._remove_punctuation(
                SentenceDiff._sound_out_dollars(
                    profanity.censor(text, 'x')))

    @staticmethod
    def _assert_not_empty(actual_sentence, target_sentence):
        assert target_sentence is not None
        assert actual_sentence is not None
        t = len(target_sentence)
        a = len(actual_sentence)
        if t == 0 or a == 0\
           and a == t:
            raise Exception("cannot compare empty sentences")

    @staticmethod
    def _spell_out_numbers(words):
        p = inflect.engine()
        result = []
        for word in words:
            if SentenceDiff._check_int(word):
                result.append(p.number_to_words(int(word)))
            else:
                result.append(word)
        return result

    @staticmethod
    def _spell_out_numbers_in_word(word):
        if SentenceDiff._check_int(word):
            p = inflect.engine()
            return p.number_to_words(int(word))
        else:
            return word

    @staticmethod
    def _check_int(s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    @staticmethod
    def _remove_punctuation(text):
        if text is None:
            return None
        return text.translate(str.maketrans('', '', string.punctuation))

    @staticmethod
    def _sound_out_dollars(text):
        text = re.sub(r"\$1\b", "1 dollar", text)
        _subst = "\\2 dollars"
        _regex = r"(\$)(\d*)\b"
        return re.sub(_regex, _subst, text)

    @staticmethod
    def _single_word_subs(words):
        return [SentenceDiff._single_word_sub(word) for word in words]

    @staticmethod
    def _single_word_sub(word):
            # specific
        word = re.sub(r"mr", "mister", word, flags=re.IGNORECASE)
        word = re.sub(r"ms", "miss", word, flags=re.IGNORECASE)
        word = re.sub(r"mrs", "mrs", word, flags=re.IGNORECASE)
        word = re.sub(r"dr", "doctor", word, flags=re.IGNORECASE)
        return word

    @staticmethod
    def _word_diff_cost(wordA, wordB):
        #substitution cost, similar words cost close to 0 different words cost 1
        denominator = 0
        numerator = 0
        for i, s in enumerate(difflib.ndiff(wordA, wordB)):
            denominator += 1
            if s[0] == '-' or s[0] == '+':
                numerator += 1

        cost = numerator/denominator
        # a little hack to cost zero when its really a random
        # coincidence eg 'hydra' vs 'girl' share one letter -r
        if cost>=0.85 and numerator>2:
            return 1
        else:
            return cost

    @staticmethod
    def _word_add_rm_cost(wordA, wordB):
        #addition or removal cost, small words dont cost so much
        word = wordA if wordA is not None else wordB
        if word == "a" or word == "the" or len(word) <= 2:
            return 0.6
        else:
            return 1

    @staticmethod
    def _all_substitutions(list_of_lists):
        rslt = []
        for lst in list_of_lists:
            for pair in itertools.permutations(lst, 2):
                rslt.append(pair)
        return rslt

    @staticmethod
    @functools.lru_cache()
    def _homonyms(sentence):
        result = [sentence]
        for pair in SentenceDiff._all_word_subs():
            test_sentence = sentence.replace(pair[0], pair[1])
            if test_sentence != sentence:
                result.append(test_sentence)
        return result

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def _all_word_subs():
        return SentenceDiff._all_substitutions(
                SentenceDiff._all_word_homonyms())

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def _all_word_homonyms():
        return \
        [["there", "their", "they’re"],
         ["see", "sea"],
         ["for", "four", "4"],
         ["by", "buy", "bye"],
         ["passed", "past"],
         ["which", "witch"],
         ["son", "sun"],
         ["who’s", "whose"],
         ["hole", "whole"],
         ["write", "right"],
         ["to", "too", "two", "2"],
         ["threw", "through"],
         ["cereal", "serial"],
         ["desert", "dessert"],
         ["meat", "meet"],
         ["flower", "flour"],
         ["cooking", "cookin"],
         ["jumping", "jumpin"],
         ["principal", "principle"],
         ["blue bell", "bluebell"],
         ["talk town", "talktown"],
         ["silverware", "silver ware"],
         ["majong", "mah jong"],
         ["rock wall", "rockwall"],
         ["chicken soup", "chickensoup"],
         ["tomato soup", "tomatosoup"],
         ["hi tim", "hawaii team"],
         ["hi tim", "hi team"],
         ["hi", "hawaii"],
         ["hi tim", "hawaii team"],
         ["hi tim", "hi team"],
         ["hi", "hawaii"]
         ]