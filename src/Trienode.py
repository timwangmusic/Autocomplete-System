from collections import Counter


class TrieNode:
    def __init__(self, prefix=None, parent=None, is_word=False):
        """

        :param prefix: prefix of this node.
        :param parent: parent node in the trie
        :param is_word: True if the path from root to this node is a word.
        # :param max_res_retain: maximum number of results in top_results
        """
        self.prefix = prefix
        self.children = dict()
        self.parent = parent
        self.count = 0      # number of times the term is searched after last trie update
        self.top_results = Counter()
        if is_word:
            self.top_results[self.prefix] = 1
        self.isWord = is_word

    def total_counts(self):
        """
        Returns the total number of searches on the prefix of the node.
        :return: int
        """
        return self.top_results[self.prefix]

    def set_total_counts(self, val):
        """
        Set the total number of searches on the prefix of the node from historical data in DB.
        :param val: int
        :return: None
        """
        self.top_results[self.prefix] = val
