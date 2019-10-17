"""
    Main module for auto-complete server
"""
from collections import deque, Counter
import logging
import logging.config
import yaml
import csv

# from nltk.corpus import words as en_corpus
from py2neo import Node
from src.Trienode import TrieNode
from src.Spell import Spell

from . import Database
from src.Errors import ReturnResultValueLessThanOne


class Server:
    """Server class for auto-complete system

    This class defines application server for performing auto-complete functionality.
    The main API search(str) searches a term in server and returns top results to the user.
    New servers can be established from Neo4j database which stores search history.

    Attributes:
        Server.server_index: int
            index for the application server created
        Server.server_update_frequency: int
            frequency for controlling how often servers write to database
    """

    server_index = 0
    server_update_frequency = 1

    def __init__(self, *, num_res_return: int = 10, root: TrieNode = None, connect_to_db: bool = True,
                 testing: bool = False, node_count: int = 1):
        """
        :param num_res_return: maximum number of results to return to user
        :param root: Trienode
        :param connect_to_db: True if server is connected to a database
        :param testing: True if server constructed in test scripts
        """
        self.__class__.server_index += 1
        if connect_to_db:
            self.db = Database.DatabaseHandler()
            self._selector = self.db.graph.nodes  # get node matcher

        if root is None:
            self.__root = TrieNode(prefix='', is_word=False)
        else:
            self.__root = root

        self.vocab = set()
        self.node_count = node_count
        self.search_count = 0  # tracking number of search before performing trie update

        self.testing = testing

        # Logging facilities
        if not testing:
            with open('logging.config', 'r') as f:
                config = yaml.safe_load(f)
            logging.config.dictConfig(config)
            self.logger = logging.getLogger('Trie_db')
            self.insertLogger = logging.getLogger('Trie_db.insert')

            with open('data/5000_most_freq_words.csv') as csv_file:
                words_reader = csv.reader(csv_file)
                for row in words_reader:
                    _, rank, word, freq, _ = row
                    freq = int(freq)
                    self.__insert(word, isword=True, count=freq, from_db=True)
        else:
            self.word_dictionary = set()

        self._num_res_return = num_res_return
        self.spell_checker = Spell()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Trie application server with {self.node_count} nodes"

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
        self.__set_num_res_return(val)

    def __set_num_res_return(self, val):
        if val < 1:
            raise ReturnResultValueLessThanOne('should return at least 1 result.')
        self._num_res_return = val

    def app_reset(self):
        self.__init__()

    @classmethod
    def _get_num_server_instances(cls):
        return cls.server_index

    def top_results(self, num_results=10):
        res = self.__root.top_results.most_common(num_results)
        return [word for word, count in res]

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
        node['count'] = self.__root.total_counts()
        tx.create(node)  # create root in neo4j
        queue.append((node, self.__root))
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
            # self.logger.info('Finished building database. Number of nodes created is {count}'.format(count=count))
            self.logger.info(f'Finished building database. Number of nodes created is {count}')

        if self.testing and tx.finished():
            self.logger.info('Transaction finished.')

    def update_db(self):
        """
        Update database with latest application server usage
        :return: None
        """
        root = self.__root
        g = self.db.graph

        def dfs(node, parent):
            """update node info to database"""
            if not node:
                return
            db_node = self._selector.match('TrieNode', name=node.prefix).first()
            if not db_node:
                tx = g.begin()
                db_node = Node('TrieNode',
                               name=node.prefix,
                               isword=node.isWord,
                               count=node.total_counts())
                tx.create(db_node)
                parent_db_node = self._selector.match('TrieNode', name=parent.prefix).first()
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
        Improves run-time by only insert complete words.
        :return: None
        """
        self.app_reset()
        root = self._selector.match('ROOT').first()
        graph = self.db.graph

        def dfs(node):
            prefix, isword, count = node['name'], node['isword'], node['count']
            if isword:
                self.__insert(prefix, isword, from_db=True, count=count)
            # find all parent-children relationships
            for rel in graph.match(nodes=[node], r_type=Database.Parent):
                if rel is not None:
                    dfs(rel.nodes[1])

        dfs(root)
        self.update_top_results()

    def __insert(self, word: str, *, isword: bool = True, count: int = 0, from_db: bool = False) -> TrieNode:
        """
        This method inserts a word into the trie. This method should be hidden from user.
        Only method build_trie() and search() should call this method. So we make it internal.
        :param word: str
        :param isword: bool
        :param count: number of times word is searched
        :param from_db: True if the method is called by build_trie()
        :return: Trie node which correspond to the word inserted
        """

        # if word in Trie.english_words:
        # self.vocab.add(word)
        cur = self.__root

        for char in word:
            if char not in cur.children:
                self.node_count += 1
                cur.children[char] = TrieNode(prefix=cur.prefix + char, parent=cur)
            cur = cur.children[char]

        cur.isWord = isword

        if from_db:
            cur.count = 0
            cur.set_total_counts(count)
        else:
            cur.count += 1

        if not self.testing:
            # self.insertLogger.debug('Insert used for {word}'.format(word=word))
            self.insertLogger.debug(f'Insert used for {word}')

        return cur

    def delete(self, term):
        """
        Search the specified term and delete the node if found.
        Also delete nodes in the subtree.
        :param term: str
        :return: None
        """
        target_node = self.__root
        for letter in term:
            if letter not in target_node.children:
                return
            target_node = target_node.children[letter]

        # if target node is not a word, meaning that the term does not exist
        if not target_node.isWord:
            return

        words_to_del, total_deleted = Server.__delete_helper(target_node)

        self.node_count -= total_deleted

        # delete subtree rooted at the node contains the term
        last_letter = term[-1]
        target_node.parent.children.pop(last_letter)

        # delete parent nodes that do not contain whole term
        start_node = target_node.parent
        while start_node and start_node.parent and not start_node.isWord:
            last_letter = start_node.prefix[-1]
            start_node.parent.children.pop(last_letter)
            self.node_count -= 1
            start_node = start_node.parent

        # remove all deleted terms from the top results of parent nodes of the target node
        while start_node:
            for word in words_to_del:
                start_node.top_results.pop(word, None)
            start_node = start_node.parent

    @staticmethod
    def __delete_helper(node):
        """
        Breadth-first search to find all children nodes that are words
        :param node: TrieNode
            root of subtree
        :return: set(str), int
            terms delete and total number of nodes deleted
        """
        q = deque([node])
        res = set()
        node_count = 0
        while q:
            cur = q.popleft()
            node_count += 1
            if cur.isWord:
                res.add(cur.prefix)
            for _, child in cur.children.items():
                q.append(child)
        return res, node_count

    def search(self, search_term: str) -> list:
        """
        API for clients to get a list of top suggestions.
        The input may be a sentence, with words separated by space.
        Search top results for entire sentence may not make sense.
        Current design returns top results only based on last word in a sentence.
        :param search_term: str
        :return: List[str]
        """
        if not isinstance(search_term, str):
            raise TypeError("{} is not a string".format(search_term))

        _words = search_term.lower().split()
        if len(_words) == 0:
            return []

        _word_lists = []
        for word in _words:
            # The replacement takes care of cases of both valid and invalid words
            replacements = self.spell_checker.most_likely_replacements(word, num_res=2)
            _word_lists.append(replacements)

        replacement_list = []
        Server.__search_helper(_word_lists, 0, [], replacement_list)

        result = []
        candidates = []
        for words in replacement_list:
            last_node = self.__insert(' '.join(words), from_db=False)
            candidates.append(last_node)
            self.search_count += 1

        if self.search_count >= Server.server_update_frequency:
            self.search_count = 0
            self.update_top_results()

        # result = [word[0] for word in last_node.top_results.most_common(self.num_res_return)]
        for node in candidates:
            result.extend(node.top_results.most_common(self.num_res_return))

        res = [word_freq[0] for word_freq in sorted(result, key=lambda x: x[1])]
        return res[:self.num_res_return]

    @staticmethod
    def __search_helper(word_list, idx, path, res):
        if idx == len(word_list):
            res.append(list(path))
            return
        for word in word_list[idx]:
            path.append(word)
            Server.__search_helper(word_list, idx + 1, path, res)
            path.pop()

    def update_top_results(self):
        """
        This method builds top suggestion results from bottom up.
        :return: None
        """

        def dfs(node):
            if len(node.children) == 0:
                Server.update_parent_new(node, Counter())
                return
            for child in node.children:
                dfs(node.children[child])

        dfs(self.__root)

    @staticmethod
    def update_parent_new(node, d):
        if node.isWord:
            d[node.prefix] = node.count
            node.count = 0
        # temp = node.total_counts()
        node.top_results.update(d)
        # node.set_total_counts(temp)
        if node.parent:
            Server.update_parent_new(node.parent, d)

    @classmethod
    def path_compression(cls, server):
        """
        Compress redundant paths by finding nodes having single child node
        :param server: Server
        :return: None
        """
        root = server.__root
        for child, node in root.children.items():
            Server.__compress(node)

    @staticmethod
    def __combine(parent):
        for child, node in parent.children.items():
            parent.prefix = node.prefix
            parent.children = node.children
            parent.isWord = node.isWord
        return parent

    @staticmethod
    def __compress(node):
        if len(node.children) == 0:
            return
        while not node.isWord and len(node.children) == 1:
            node = Server.__combine(node)
        for child, child_node in node.children.items():
            Server.__compress(child_node)

    @staticmethod
    def __counter_serialization(cnt, num_results_to_serialize=10):
        """
        Serialize top 10 results from counter to string
        :param cnt: collections.Counter
        :param num_results_to_serialize: number of top results to serialize
        :return: str
        """
        top_res = cnt.most_common(num_results_to_serialize)
        res = []
        for term, cnt in top_res:
            term = '_'.join(term.split())
            res.extend([term, str(cnt)])
        return " ".join(res)

    @staticmethod
    def __counter_deserialization(s):
        """
        Convert serialized Counter to object
        :param s: str
        :return: collections.Counter
        """
        counts = s.split()
        idx = 0
        counter = Counter()
        while idx < len(counts):
            term = ' '.join(counts[idx].split('_'))
            counter[term] = int(counts[idx + 1])
            idx += 2
        return counter

    def server_serialization(self, num_results_to_serialize=10):
        """
        Serialize the trie server.
        Records information such as prefix, isWord, number of child nodes and serialized top results.
        The purpose of this function is for rebuilding Trie in case of server failure.
        :return: List[List[str]]
        """

        def dfs(node):
            nonlocal data
            if node is None:
                return
            top_results = Server.__counter_serialization(
                node.top_results,
                num_results_to_serialize=num_results_to_serialize,
            )
            isword = '1' if node.isWord else '0'
            data.append([node.prefix, isword, top_results, str(len(node.children))])
            for child in node.children:
                dfs(node.children[child])

        data = []
        dfs(self.__root)
        return data

    @staticmethod
    def server_deserialization(s, connect_to_db=False, testing=False):
        """
        Trie server deserialization
        :param s: List[List[str]], serialized Trie server
        :param connect_to_db: True if connect to database
        :param testing: True if in testing mode
        :return: Server
        """
        node_count = 0

        def build_trie(node, num_children, index):
            nonlocal root, node_count
            if num_children == 0:
                return index
            for _ in range(num_children):
                _prefix, _isword, _top_results, _num_children_str = s[index]
                # create new TrieNode
                _isword = True if _isword == '1' else False
                _top_results = Server.__counter_deserialization(_top_results)
                new_node = TrieNode(prefix=_prefix, is_word=_isword)
                new_node.top_results = _top_results
                new_node.parent = node
                if node:
                    node.children[_prefix[-1]] = new_node
                if index == 0:
                    root = new_node
                node_count += 1
                index = build_trie(new_node, int(_num_children_str), index + 1)
            return index

        root = None
        build_trie(None, 1, 0)
        return Server(root=root, connect_to_db=connect_to_db, testing=testing, node_count=node_count)
