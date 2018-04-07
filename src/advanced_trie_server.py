from . import Trieserver
from . import Spell


class AdvTrie(Trieserver.Trie):
    """This class provides advanced functionality such as providing auto-corrections as suggestions."""
    NUM_CORRECTIONS_TO_INSERT = 3
    MAX_BASIC_RESULTS = 15
    MAX_CORRECTIONS = 10

    def __init__(self, num_corrections=5, num_basic_results=5):
        super().__init__()
        self.checker = Spell.Spell()
        self.num_corrections = num_corrections
        self.num_basic_search_results = num_basic_results

    def search(self, search_term, from_adv_app=True):
        """
        This search method not only returns results from basic class count-based search,
        but also returns top phrases from Bayes predictions.
        :param search_term: same as in base class.
        :param from_adv_app: bool. True if the search call is from AdvTrie servers.
        :return: List[str]
        """
        basic_results = super().search(search_term, from_adv_app=from_adv_app)
        corrections = self.checker.most_likely_replacements(search_term.split()[-1],
                                                            self.num_corrections)
        corrections = [word for word in corrections if word not in basic_results]

        for word in corrections[:AdvTrie.NUM_CORRECTIONS_TO_INSERT]:
            super().insert(word, isword=True, from_db=False)

        self.search_count += 1
        if self.search_count >= AdvTrie.trie_update_frequency:
            self.search_count = 0
            self.update_top_results()

        return list(set(corrections + basic_results[:self.num_basic_search_results]))

    @property
    def num_corrections(self):
        return self._num_corrections

    @num_corrections.setter
    def num_corrections(self, num_corrections):
        self._set_num_corrections(num_corrections)

    def _set_num_corrections(self, num_corrections):
        if num_corrections < 0:
            raise ValueError('Number of corrections cannot be negative')
        elif num_corrections > AdvTrie.MAX_CORRECTIONS:
            raise ValueError('Too many corrections.')
        self._num_corrections = num_corrections

    @property
    def num_basic_search_results(self):
        return self._num_basic_search_results

    @num_basic_search_results.setter
    def num_basic_search_results(self, num_results):
        self._set_num_basic_search_results(num_results)

    def _set_num_basic_search_results(self, num_results):
        if num_results < 0:
            raise ValueError('Number of basic results cannot be negative')
        elif num_results > AdvTrie.MAX_BASIC_RESULTS:
            raise ValueError('Too many basic results.')
        self._num_basic_search_results = num_results
