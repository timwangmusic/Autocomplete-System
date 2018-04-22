from . import Trieserver
from . import Spell
from sklearn.neighbors import BallTree
import numpy as np
import json
from os import path


class AdvTrie(Trieserver.Trie):
    """This class provides advanced functionality such as providing auto-corrections as suggestions."""
    MAX_CORRECTIONS = 10
    NUM_CORRECTIONS_TO_INSERT = MAX_CORRECTIONS // 2
    MAX_BASIC_RESULTS = 15

    def __init__(self, num_corrections=10, num_basic_results=10,
                 home_dir="/Users/Weihe/Dropbox/Auto_complete_system/src",
                 embedding_json="embedding_res.json",
                 vocab_int_json="vocab_to_int.json"):
        super().__init__(num_res_return=num_basic_results)

        embedding_json = path.join(home_dir, embedding_json)
        vocab_int_json = path.join(home_dir, vocab_int_json)

        self.checker = Spell.Spell()
        self.num_corrections = num_corrections
        self.num_basic_search_results = num_basic_results
        self.max_total_res = min(10, num_basic_results+num_corrections)

        # load json files
        print ("Loading JSON files, may take a while.")
        with open(embedding_json, 'r') as read_file:
            self.embeddings = np.array(json.load(read_file))
        with open(vocab_int_json, 'r') as read_file:
            self.vocab_int = json.load(read_file)
        self.int_vocab = {i: word for word, i in self.vocab_int.items()}

        # train k nearest neighbor model
        print ("Training BallTree k-nearest neighbor searcher...")
        self.searcher = BallTree(self.embeddings, leaf_size=10)
        print ("Ready to use.")

    def _next_words(self, word):
        """
        Given an input return the next most relevant words contextually.
        :param word: str
        :return: List[str]
        """
        if word not in self.vocab_int:
            return []
        index = self.vocab_int[word]
        neighbors = self.searcher.query([self.embeddings[index]], k=10, return_distance=False)
        res = []
        for neighbor in list(neighbors.flatten()):
            res.append(self.int_vocab[neighbor])
        return res[1:]

    def search(self, search_term, from_adv_app=True):
        """
        This search method not only returns results from basic class count-based search,
        but also returns top phrases from Bayes predictions.
        :param search_term: same as in base class.
        :param from_adv_app: bool. True if the search call is from AdvTrie servers.
        :return: List[str]
        """
        basic_results = super().search(search_term, from_adv_app=from_adv_app)
        corrections = []
        if len(search_term) > 0:
            target = search_term.split()[-1]
            corrections = self.checker.most_likely_replacements(target, self.num_corrections)
            next_words = self._next_words(target)
        self.insertLogger.debug('basic results are {}'.format(str(basic_results)))
        corrections = [word for word in corrections if word not in basic_results]
        next_words = [word for word in next_words if word not in basic_results and word not in corrections]

        for word in corrections[:AdvTrie.NUM_CORRECTIONS_TO_INSERT]:
            super().insert(word, isword=True, from_db=False)

        self.search_count += 1
        if self.search_count >= AdvTrie.trie_update_frequency:
            self.search_count = 0
            self.update_top_results()

        return list(set(corrections + basic_results))[:self.max_total_res] + next_words[:2]

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
