import re
import string
import numpy as np
import inflect


class SentenceDiff:

    def __init__(self, actual_sentence, target_sentence):
        self.__assert_not_empty(actual_sentence,target_sentence)
        
        # lowercase, normalize, tokenize
        self.actual = self._tokenize(actual_sentence)
        self.target = self._tokenize(target_sentence)

        # split words without lower casing
        self.actual_words = self._normalize(actual_sentence).split()
        self.target_words = self._normalize(target_sentence).split()

        # initialize the matrix per levenshtein distance
        shape = (len(self.target) + 1, len(self.actual) + 1)
        self.matrix = np.zeros(shape, dtype=np.uint32)
        self.matrix[0, :] = np.arange(shape[1])
        self.matrix[:, 0] = np.arange(shape[0])
      
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

    def print_debug(self):
        self._compare()
        self._backtrace()
        print("actual")
        print(self.actual)
        print("target")
        print(self.target)
        print("wer")
        print(self.error)
        # print(self.matrix)
        # print(self.path)
        print(self.alignment)
        print("")
        print(self.scored_words)
        print("")
        print(self.insertions)
        print(self.deletions)
        print(self.substitutions)

    # private methods 
    def _compare(self):
        matrix = self.matrix
        for trgt_pos, rw in enumerate(self.target):
            for actual_pos, hw in enumerate(self.actual):
                insert = matrix[trgt_pos + 1, actual_pos] + 1
                delete = matrix[trgt_pos, actual_pos + 1] + 1
                if rw != hw:
                    subst = matrix[trgt_pos, actual_pos] + 1
                else:
                    subst = matrix[trgt_pos, actual_pos]

                best = min(insert, delete, subst)
                matrix[trgt_pos + 1, actual_pos + 1] = best

        self.cost = matrix[-1, -1]
        self.error = self.cost / len(self.target)

    def _backtrace(self):
        trgt_pos = len(self.target) - 1
        actual_pos = len(self.actual) - 1
        alignment = []
        path = []
        inserts = 0
        deletions = 0
        substitns = 0
        match = 0

        while trgt_pos >= 0 or actual_pos >= 0:
            path.append((trgt_pos + 1, actual_pos + 1))
            start = self.matrix[trgt_pos + 1, actual_pos + 1]
            insert = self.matrix[trgt_pos + 1, actual_pos]
            delete = self.matrix[trgt_pos, actual_pos + 1]
            subst = self.matrix[trgt_pos, actual_pos]
            best = min(start, subst)

            if insert < best:
                alignment.append((None, self.actual[actual_pos]))
                inserts += 1
                actual_pos -= 1
            elif delete < best:
                alignment.append((self.target[trgt_pos], None))
                deletions += 1
                trgt_pos -= 1
            else:
                if start == subst: # no change
                    match += 1
                else:
                    substitns += 1

                if actual_pos < 0:
                    # shouldn't happen
                    raise Exception("error during _backtrace")

                alignment.append((self.target[trgt_pos], self.actual[actual_pos]))
                actual_pos -= 1
                trgt_pos -= 1

        alignment.reverse()
        path.reverse()

        scored_words = []
        actuals = self.actual_words
        targets = self.target_words

        # the index returned in scored_words is relative to the *actual* sentence 
        # but we need to keep track of both so we can look up untokenized form of word
        a_idx = 0
        t_idx = 0    
        for pair in alignment:

            if pair[0] == pair[1]:
                actual = actuals[a_idx]
                target = targets[t_idx]
                scored_words.append((actual, target, a_idx, None))
                a_idx += 1
                t_idx += 1

            elif pair[0] is None:
                actual = actuals[a_idx]
                scored_words.append((actual, None, a_idx, "added"))
                a_idx += 1

            elif pair[1] is None:
                target = targets[t_idx]
                scored_words.append((None, target, a_idx, "skipped"))
                t_idx += 1

            else:
                actual = actuals[a_idx]
                target = targets[t_idx]
                scored_words.append((actual, target, a_idx, "changed"))
                a_idx += 1
                t_idx += 1

        self.scored_words = scored_words
        self.path = path
        self.alignment = alignment
        self.insertions = inserts
        self.deletions = deletions
        self.substitutions = substitns
        self.matched = match

    def _tokenize(self, sentence):
        normalized_lower = self._normalize(sentence)
        words = normalized_lower.lower().split()
        words = self._spell_out_numbers(words)
        return words

    def _normalize(self, text):
        return \
            self._remove_punctuation(
                str(text).strip())

    @staticmethod
    def __assert_not_empty(actual_sentence, target_sentence):
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
    def _check_int(s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    @staticmethod
    def _remove_punctuation(text):
        return text.translate(str.maketrans('', '', string.punctuation))

