import re
import string

import pymorphy2
import nltk

_morph = pymorphy2.MorphAnalyzer()
_stop_words = set()

with open('stop_words.txt', 'r') as file:
    for stop_word in file:
        _stop_words.add(stop_word)


def _normalize_word(word):
    word = word.lower()
    word = _morph.parse(word)[0].normal_form
    return word


def _delete_punctuation(text):
    regex = re.compile('[%s]+ ' % re.escape(string.punctuation))
    return regex.sub(' ', text)


def normalize_words(words):
    return [_normalize_word(word) for word in words if word not in _stop_words]


def get_words_from_raw_text(raw_text):
    raw_text = _delete_punctuation(raw_text)
    words = normalize_words(nltk.word_tokenize(raw_text))
    return words
