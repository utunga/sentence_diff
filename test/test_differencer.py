from unittest import TestCase
from sentence_diff import SentenceDiff


def diff(actual_sentence, target_sentence):
    return SentenceDiff(actual_sentence=actual_sentence, target_sentence=target_sentence)


def chatterize_score(actual_sentence, target_sentence):
    diff = SentenceDiff(actual_sentence, target_sentence)
    return diff.chatterize_score()


def assert_chatterize_score(actual_sentence, target_sentence, expected):
    score = chatterize_score(actual_sentence, target_sentence)
    assert score == expected


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
        assert d.mistakes() == \
            [('has', 'have', 2, 'changed'),
            ('of', None, 5, 'added'),
            ('bread', None, 6, 'added')]

    def test_no_mistakes(self):
        d = diff("my name is leaf", "My name is leaf!")
        assert d.mistakes() == []

    def test_yes_no_words(self):
        d = diff("How about a good bath", "Would you like a good bath?")
        print(d.scored_words())
        assert d.yes_no_words() == [
        ("How", False),
        ("about", False),
        ("a", False),
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
        d = diff("can i has 7 Loaves of bread please ", "Can I have seven Loaves, please?")
        assert d.scored_words() == [
        ('can', 'Can', 0, None),
        ('i', 'I', 1, None),
        ('has', 'have', 2, 'changed'),
        ('7', 'seven', 3, None),
        ('Loaves', 'Loaves,', 4, None),
        ('of', None, 5, 'added'),
        ('bread', None, 6, 'added'),
        ('please', 'please?', 7, None)]

    def test_ex_miss_mary(self):
        d = diff("Nice to meet you Miss Mary.", "nice to meet you, Ms Mary!")
        print(d.mistakes())
        assert d.wer() == 0

    def test_ex_meet_at_church(self):
        d = chatterize_score("Let's meat at the church.", "lets meet at the church")
        assert d == 1

    def test_ex_wow_100(self):
        d = chatterize_score("wow, 100 dollars", "Wow, $100?")
        assert d == 1

    def test_backtrace_ex(self):
        d = diff("Hi.", "hello tim my name is scott")
        assert d.wer() == 1

    def test_backtrace_ex2(self):
        d = chatterize_score("let's climb the rockwall", "Let's climb the rock wall.")
        #print(d.mistakes())
        assert d == 1

    def test_normalize_100_dollars(self):
        d = SentenceDiff("xx","xx")
        assert d._normalize("$100") == "100 dollars"

    def test_normalize_1_dollar(self):
        d = SentenceDiff("xx","xx")
        assert d._normalize("here is $1 for you") == "here is 1 dollar for you"

    def test_ex_silverware(self):
        d = chatterize_score(actual_sentence="i need silver ware", target_sentence="I need silverware.")
        assert d == 1

    def test_ex_dog_house(self):
        d = chatterize_score("hawaii tim", "Hi Tim.")
        assert d == 1

    def test_ex_miss_mary(self):
        d = diff("hi miss mary", "Hi Ms. Mary!")
        assert d.wer() == 0

    def test_chatterize_score_dont_drop_apostrophe(self):
        score = chatterize_score("You're welcome","You're welcome")
        assert score == 1
        d = diff("You're welcome","You're welcome")
        scored = d.scored_words()
        assert scored[0][0] == "You're"

    def test_chatterize_score_dont_mess_up_lets(self):
        score = chatterize_score("Let's pretend we're pirates.", "Let's pretend we're pirates.")
        assert score == 1
        d = diff("Let's pretend we're pirates.", "Let's pretend we're pirates.")
        scored = d.scored_words()
        print(scored)
        assert scored[0][0] == "Let's"

    def test_complex_backtrace_ex(self):
        actual = "Do you want to have a sleepover?"
        target = "want to have a sleep over you want to have a sleepover"
        d = diff(actual, target)
        print(d.scored_words())
        assert d.chatterize_score() == 0.4708333333333334

    def test_complex_backtrace_ex_2(self):
        actual = "where i like to dress as a superhero"
        target = "I like to dress as a superhero."
        d = diff(actual, target)
        assert d.chatterize_score() == 0.8

    def test_complex_backtrace_ex_test(self):
        actual = "x a b"
        target = "a b c a b"
        d = diff(actual, target)
        print(d.scored_words())
        assert d.chatterize_score() == 0.6

    def test_profanity(self):
        d = diff("two fucking loaves", "two more loaves")
        assert d.mistakes() == [
        ("xxxx", 'more', 1, 'changed')]

    def test_i_want_water(self):
        actual = "I want water, please"
        target = "I want please"
        d = diff(actual, target)
        assert d.yes_no_words() ==[
            ('I', True), 
            ('want', True), 
            ('water,', False), 
            ('please', True)]
        assert d.chatterize_score() == .75

    def test_chatterize_score_partial_word(self):
        assert_chatterize_score("I like superheroes.", "i like superhero", 0.9166666666666666)

    def test_chatterize_score_partial_word_round_up(self):
        assert_chatterize_score("superhero", "superheros", 0.9)

    def test_chatterize_score_fail(self):
        assert_chatterize_score("how you gorger hydra","I am a girl.", 0)

    def test_chatterize_score_pass(self):
        assert_chatterize_score("i want corn please","I want corn, please.", 1)

    def test_dad_birthday(self):
        assert_chatterize_score("it's my dad's birthday", "It's my dad's birthday", 1)

    def test_mom_birthday(self):
        assert_chatterize_score("is my mom's birthday", "It's my mom's birthday", .8)

    def test_some_flower(self):
        assert_chatterize_score("some flower please", "Some flour, please.", 1)

    def test_I_love_desert(self):
        assert_chatterize_score("I love desert", "I love dessert!", 1)

    def test_blue_bell(self):
        assert_chatterize_score("I like the name blue bell", "I like the name Bluebell", 1)

    def test_whats_jumpin(self):
        assert_chatterize_score("what's jumping", "Whats jumpin?", 1)

    def test_whats_cookin(self):
        assert_chatterize_score("what's cooking", "Whats cookin?", 1)

    def test_meat_meet(self):
        assert_chatterize_score("chickens give us meet", "Chickens give us meat.", 1)

    def test_merry_marry(self):
        assert_chatterize_score("hi miss marry", "Hi, Ms. Marry", 1)

    def test_talk_town(self):
        assert_chatterize_score("talk town school is great", "TalkTown school is great", 1)

    def test_to_please(self):
        assert_chatterize_score("I'd like to please", "I'd like 2 please", 1)

    def test_for_please(self):
        assert_chatterize_score("I'd like for please", "I'd like 4 please", 1)

    def test_chefs(self):
        assert_chatterize_score("can I have a chefs hat", "can I have a chef's hat", 1)

    def test_hi_sally(self):
        assert_chatterize_score("hi sally", "Hi, Sally", 1)
