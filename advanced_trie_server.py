from Trieserver import Trie
from Spell import Spell


class AdvTrie(Trie):
    """This class provides advanced functionality such as providing auto-corrections as suggestions."""
    NUM_CORRECTIONS = 5
    NUM_BASIC_RESULTS = 5
    NUM_CORRECTIONS_TO_INSERT = 3

    def __init__(self):
        super().__init__()
        self.checker = Spell()

    def search(self, search_term):
        """
        This search method not only returns results from basic class count-based search,
        but also returns top phrases from Bayes predictions.
        :param search_term: same as in base class
        :return:
        """
        basic_results = super().search(search_term)
        corrections = self.checker.most_likely_replacements(search_term.split()[-1],
                                                            AdvTrie.NUM_CORRECTIONS)
        for word in corrections[:AdvTrie.NUM_CORRECTIONS_TO_INSERT]:
            super().insert(word, isword=True, from_db=False)
        return set(corrections + basic_results[:AdvTrie.NUM_BASIC_RESULTS])

    @property
    def num_search_results(self):
        return AdvTrie.NUM_CORRECTIONS + AdvTrie.NUM_BASIC_RESULTS
