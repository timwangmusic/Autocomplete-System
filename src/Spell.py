# Python3 variance for classic Spelling corrector by Peter Norvig
# Ref: http://norvig.com/spell-correct.html
from collections import Counter
import re
import string


class Spell:
    def __init__(self, file='big_text.txt'):
        text = open(file).read()
        self.words = re.findall(r'\w+', text)
        self.total_words = len(self.words)
        self.words = Counter(self.words)

    def probability(self, word):
        return self.words[word] / self.total_words

    @staticmethod
    def edit_one(word):
        """ Find all words that are One edit away from word"""
        letters = string.ascii_lowercase
        splits = [(word[:i], word[i:]) for i in range(len(word))]
        insertions = [left + c + right for left, right in splits for c in letters]
        deletions = [left + right[1:] for left, right in splits if right]
        transposes = [left + right[1] + right[0] + right[2:] for left, right in splits if len(right) > 1]
        replaces = [left + c + right[1:] for left, right in splits for c in letters]
        return set(insertions + deletions + transposes + replaces)

    @staticmethod
    def edit_two(word):
        """ Find all words that are Two edits away from word"""
        return set(edit2 for edit1 in Spell.edit_one(word) for edit2 in Spell.edit_one(edit1))

    def known(self, words):
        """
        Return a list of words which are in vocabulary
        :param words: set[str]
        :return: list[str]
        """
        return [word for word in words if word in self.words]

    def candidates(self, word):
        return self.known([word]) or self.known(Spell.edit_one(word)) or self.known(Spell.edit_two(word)) or set(word)

    def correction(self, word):
        return max(self.candidates(word), key=self.probability)

    def most_likely_replacements(self, word, num_res=10):
        return sorted(self.candidates(word), key=self.probability)[:num_res]
