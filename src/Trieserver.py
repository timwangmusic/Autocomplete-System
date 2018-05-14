from collections import deque, Counter
import logging
import logging.config
import yaml

from nltk.corpus import words as en_corpus
from py2neo import Node, NodeSelector
from src.Trienode import TrieNode
from src.Spell import Spell

from . import Database


class Trie:
    """Returns top results to the user.
     Results may be outdated before calling update trie function."""
    # english_words = set(en_corpus.words())
    trie_index = 0
    trie_update_frequency = 1

    def __init__(self, num_res_return=10, connect_to_db=True, testing=False):
        """
        :param num_res_return: maximum number of results to return to user
        :param connect_to_db: True if server is connected to a database
        """
        if connect_to_db:
            self.db = Database.DatabaseHandler()
            self._selector = NodeSelector(self.db.graph)

        self.root = TrieNode(prefix='', is_word=False)
        self.vocab = set()
        self.node_count = 1
        self.search_count = 0   # tracking number of search before performing trie update

        # Logging facilities
        if not testing:
            self.word_dictionary = set(en_corpus.words())
            with open('logging.config', 'r') as f:
                config = yaml.safe_load(f)
            logging.config.dictConfig(config)
            self.logger = logging.getLogger('Trie_db')
            self.insertLogger = logging.getLogger('Trie_db.insert')
        else:
            self.word_dictionary = set()

        self.testing = testing
        self._num_res_return = num_res_return
        self.spell_checker = Spell()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Trie application server with {} nodes".format(self.node_count)

    def __len__(self):
        """
        Return number of nodes in the Trie
        :return: int
        """
        return self.node_count

    def __bool__(self):
        """
        Return True if Trie is non-empty
        :return: bool
        """
        return self.node_count > 1

    def __getitem__(self, item):
        return self.search(item)

    # accessor for num_res_return
    @property
    def num_res_return(self):
        return self._num_res_return

    @num_res_return.setter
    def num_res_return(self, val):
        self._set_num_res_return(val)

    def _set_num_res_return(self, val):
        if val < 1:
            raise ValueError('should return at least 1 result.')
        self._num_res_return = val

    def app_reset(self):
        self.__init__()

    @classmethod
    def _get_next_trie_index(cls):
        result = Trie.trie_index
        Trie.trie_index += 1
        return result

    def build_db(self):
        """
        This method removes data from database and build new graph with in-memory data in application server.
        :return: None
        """
        self.db.graph.delete_all()  # delete all existing nodes and relationships
        queue = deque()
        tx = self.db.graph.begin()
        self.logger.info('Start updating database.')
        node = Node('TrieNode', 'ROOT',
                    isword=False,
                    name='',
                    )
        node['count'] = self.root.total_counts()
        tx.create(node)     # create root in neo4j
        queue.append((node, self.root))
        count = 0

        while queue:
            db_node, cur = queue.popleft()
            for child in cur.children:
                prefix = cur.children[child].prefix
                db_node_child = Node('TrieNode',
                                     name=prefix,
                                     isword=cur.children[child].isWord,
                                     count=cur.children[child].total_counts()
                                     )
                queue.append((db_node_child, cur.children[child]))
                tx.create(db_node_child)
                count += 1
                tx.create(Database.Parent(db_node, db_node_child))

        tx.commit()
        if not self.testing:
            self.logger.info('Finished building database. Number of nodes created is %d' % count)

        if self.testing and tx.finished():
            self.logger.info('Transaction finished.')

    def update_db(self):
        """
        Update database with latest application server usage
        :return: None
        """
        root = self.root
        g = self.db.graph

        def dfs(node, parent):
            """update node info to database"""
            if not node:
                return
            db_node = self._selector.select('TrieNode', name=node.prefix).first()
            if not db_node:
                tx = g.begin()
                db_node = Node('TrieNode',
                               name=node.prefix,
                               isword=node.isWord,
                               count=node.total_counts())
                tx.create(db_node)
                parent_db_node = self._selector.select('TrieNode', name=parent.prefix).first()
                tx.create(Database.Parent(parent_db_node, db_node))
                tx.commit()
            else:
                db_node['count'] = node.total_counts()
                g.push(db_node)
            for child in node.children:
                dfs(node.children[child], node)

        dfs(root, None)

    def build_trie(self):
        """
        This method builds trie server with TrieNode-labeled nodes from the database.
        Compared to previous version, significantly improves run-time by only insert complete words.
        Runtime reduction: O(NK^2) -> O(NK), where N is number of words and K is average word length.
        :return: None
        """
        self.app_reset()
        root = self._selector.select('ROOT').first()
        g = self.db.graph

        def dfs(node):
            d = dict(node)
            prefix, isword, count = d['name'], d['isword'], d['count']
            if isword:
                self._insert(prefix, isword, from_db=True, count=count)
            for rel in g.match(node, rel_type='PARENT'):
                dfs(rel.end_node())
        dfs(root)
        self.update_top_results()

    def _insert(self, word, isword=True, count=0, from_db=False):
        """
        This method inserts a word into the trie. This method should be hidden from user.
        Only method build_trie() and search() should call this method.
        :param word: str
        :param isword: bool
        :param count: number of times word is searched
        :param from_db: True if the method is called by build_trie()
        :return: Trie node which correspond to the word inserted
        """

        # if word in Trie.english_words:
        # self.vocab.add(word)
        cur = self.root

        for char in word:
            if char not in cur.children:
                self.node_count += 1
                cur.children[char] = TrieNode(prefix=cur.prefix+char, parent=cur)
            cur = cur.children[char]

        cur.isWord = isword

        if from_db:
            cur.count = 0
            cur.set_total_counts(count)
        else:
            cur.count += 1

        if not self.testing:
            self.insertLogger.debug('Insert used for {}'.format(word))
        return cur

    def search(self, search_term, from_adv_app=False):
        """
        API for clients to get a list of top suggestions.
        The input may be a sentence, with words separated by space.
        Search top results for entire sentence may not make sense.
        Current design returns top results only based on last word in a sentence.
        :param search_term: str
        :param from_adv_app: bool
        :return: List[str]
        """
        if not isinstance(search_term, str):
            raise TypeError("{} is not a string".format(search_term))

        # last_node = None
        # if search_term == '':
        #     last_node = self.root

        _words = search_term.split()
        if len(_words) == 0:
            return []
        # for word in _words:
        #     last_node = self._insert(word, from_db=False)
        _word_lists = []
        for word in _words:
            replacements = None
            if word not in self.word_dictionary:
                replacements = self.spell_checker.most_likely_replacements(word, num_res=2)
            _word_lists.append(replacements)

        replacement_list = []
        Trie.search_helper(_word_lists, 0, [], replacement_list)

        result = []
        candidates = []
        for words in replacement_list:
            last_node = self._insert(' '.join(words), from_db=False)
            candidates.append(last_node)

        if not from_adv_app:
            self.search_count += 1

        if self.search_count >= Trie.trie_update_frequency and not from_adv_app:
            self.search_count = 0
            self.update_top_results()

        # result = [word[0] for word in last_node.top_results.most_common(self.num_res_return)]
        for node in candidates:
            result.extend(node.top_results.most_common(self.num_res_return))
        result.sort(key=lambda x: x[1])
        res = [word_freq[0] for word_freq in result]
        return res[:self.num_res_return]

    @staticmethod
    def search_helper(word_list, idx, path, res):
        if idx == len(word_list):
            res.append(list(path))
            return
        for word in word_list[idx]:
            path.append(word)
            Trie.search_helper(word_list, idx+1, path, res)
            path.pop()

    def update_top_results(self):
        """
        This method builds top suggestion results from bottom up.
        :return: None
        """
        def dfs(node):
            if len(node.children) == 0:
                Trie.update_parent_new(node, Counter())
                return
            for child in node.children:
                dfs(node.children[child])
        dfs(self.root)

    @staticmethod
    def update_parent(node):
        d = Counter()
        while node:
            if node.isWord:
                d[node.prefix] = node.count
                node.count = 0      # reset count on the term
            node.top_results.update(d)
            node = node.parent

    @staticmethod
    def update_parent_new(node, d):
        if node.isWord:
            d[node.prefix] = node.count
            node.count = 0
        node.top_results.update(d)
        if node.parent:
            Trie.update_parent_new(node.parent, d)

    @classmethod
    def path_compression(cls, trie):
        """
        Compress redundant paths by finding nodes having single child node
        :param trie: Trie
        :return: Trie
        """
        root = trie.root
        for child, node in root.children.items():
            Trie.compress(node)
        return trie

    @staticmethod
    def combine(parent):
        for child, node in parent.children.items():
            parent.prefix = node.prefix
            parent.children = node.children
            parent.isWord = node.isWord
        return parent

    @staticmethod
    def compress(node):
        if len(node.children) == 0:
            return
        while not node.isWord and len(node.children) == 1:
            node = Trie.combine(node)
        for child, child_node in node.children.items():
            Trie.compress(child_node)

    @staticmethod
    def counter_to_str(cnt):
        """
        Serialize top 10 results from counter to string
        :param cnt: collections.Counter
        :return: str
        """
        top_res = cnt.most_common(10)
        res = []
        for term, cnt in top_res:
            res.extend([term, str(cnt)])
        return " ".join(res)

    @staticmethod
    def counter_deserialization(s):
        """
        Convert serialized Counter to object
        :param s: str
        :return: collections.Counter
        """
        counts = s.split()
        idx = 0
        counter = Counter()
        while idx < len(counts):
            counter[counts[idx]] = int(counts[idx+1])
            idx += 2
        return counter

    def server_serialization(self):
        """
        Serialize the trie server.
        Records information such as prefix, isWord, number of child nodes and serialized top 10 results.
        The purpose of this function is for rebuilding Trie in case of server failure.
        :return: List[List[str]]
        """
        def dfs(node):
            nonlocal data
            if node is None:
                return
            top_results = Trie.counter_to_str(node.top_results)
            isword = '1' if node.isWord else '0'
            data.append([node.prefix, isword, top_results, str(len(node.children))])
            for child in node.children:
                dfs(node.children[child])
        data = []
        dfs(self.root)
        return data

    @staticmethod
    def server_deserialization(s):
        """
        Trie server deserialization
        :param s: List[List[str]], serialized Trie server
        :return: TrieNode
        """
        def build_trie(node, num_children, index):
            if num_children == 0:
                return index
            for _ in range(num_children):
                _prefix, _isword, _top_results, _num_children_str = s[index]
                # create new TrieNode
                _isword = True if _isword == '1' else False
                _top_results = Trie.counter_deserialization(_top_results)
                new_node = TrieNode(prefix=_prefix, is_word=_isword)
                new_node.top_results = _top_results
                new_node.parent = node
                node.children[_prefix[-1]] = new_node
                index = build_trie(new_node, int(_num_children_str), index+1)
            return index

        prefix, isword, top_results, num_children_str = s[0]
        isword = True if isword == '1' else False
        top_results = Trie.counter_deserialization(top_results)
        root = TrieNode(prefix=prefix, is_word=isword)
        root.top_results = top_results
        build_trie(root, int(num_children_str), 1)
        return root
