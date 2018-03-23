from collections import Counter


class TrieNode:
    def __init__(self, prefix=None, parent=None, is_word=False):
        """

        :param prefix: prefix of this node.
        :param parent: parent node in the trie
        :param is_word: True if the path from root to this node is a word.
        """
        self.prefix = prefix
        self.children = dict()
        self.parent = parent
        self.count = 0      # number of times the whole term is searched after last update
        self.top_results = Counter({"{}".format(prefix): 0})
        self.isWord = is_word
