# Sentence Differences - sentence_diff
Package to difference English sentences via Liechtenstein distance, calculate word error rate, and list out word by word differences

# Basic usage

```python

from sentence_diff import SentenceDiff

d = SentenceDiff("can i has 7 loaves of bread please ", "Can I have seven loaves, please?")
assert d.mistakes() == [
  ('has', 'have', 2, 'changed'),
  ('of', None, 5, 'added'),
  ('bread', None, 6, 'added')]

```

### Word Error Rate - wer()

```python
d = SentenceDiff("I like to meet people", "I really like to meet people")
assert d.wer() == 1/6
```

```python
d = SentenceDiff("I really like to meet people", "I like to meet people")
assert d.wer() == 1/5
```

### Changes - mistakes()

Added words
```python
d = SentenceDiff("I like Like to eat people", "I like to eat people")
assert d.mistakes() == [
("Like", None, 2,'added')]
```

Changed words 
```python
d = SentenceDiff("How do you", "how are you")
assert d.mistakes() == [
("do", "are", 1, 'changed')]
```

Skipped words
```python
d = SentenceDiff("How see you", "how good to see you")
assert d.mistakes() == [
(None, "good", 1, 'skipped'), 
(None, "to", 1, 'skipped')]
```

No differences (ignores punctuation and case)
```python
d = SentenceDiff("my name is joe", "My name is Joe!")
assert d.mistakes() == []
```

### What words from original are OK - yes_no_words()

```python
d = SentenceDiff("can i have 7 loaves please", "Can I have seven loaves, please?")
assert d.yes_no_words() == [
("can", True),
("i", True),
("have", True),
("7", True),
("loaves", True),
("please", True)]
```

### What words from original are OK or not? - yes_no_words()

```python
d = SentenceDiff("can i have 7 loaves please", "Can I have seven loaves, please?")
assert d.yes_no_words() == [
("can", True),
("i", True),
("have", True),
("7", True),
("loaves", True),
("please", True)]
```

### Full list of changes - scored_words()

```python
d = SentenceDiff("can i has 7 loaves of bread please ", "Can I have seven loaves, please?")
assert d.scored_words() == [
('can', 'Can', 0, None),
('i', 'I', 1, None),
('has', 'have', 2, 'changed'),
('7', 'seven', 3, None),
('loaves', 'loaves', 4, None),
('of', None, 5, 'added'),
('bread', None, 6, 'added'),
('please', 'please', 7, None)]
```
