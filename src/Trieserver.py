from collections import deque, Counter
import logging
import logging.config
import yaml

from nltk.corpus import words as en_corpus
from py2neo import Node, NodeSelector

from . import Database
from . import Trienode


class Trie:
    """Returns top 10 results to the user.
     Results may be outdated before calling update trie function."""
    english_words = set(en_corpus.words())
    trie_index = 0
    trie_update_frequency = 1

    def __init__(self, db_handler=Database.DatabaseHandler(), num_res_return=10):
        """
        :param db_handler: Neo4j database controller
        :param num_res_return: maximum number of results to return to user
        """
        self.root = Trienode.TrieNode(prefix='', is_word=False)
        self.vocab = set()
        self.db = db_handler
        self.node_count = 1
        self.selector = NodeSelector(self.db.graph)
        self.search_count = 0   # tracking number of search before performing trie update
        # Logging facilities
        # self.log_file = 'trie_usage_{}.log'.format(Trie._get_next_trie_index())
        with open('logging.config', 'r') as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
        self.logger = logging.getLogger('Trie_db')
        self.insertLogger = logging.getLogger('Trie_db.insert')
        self._num_res_return = num_res_return

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Trie application server with {} nodes".format(self.node_count)

    # accessor for num_res_return
    @property
    def num_res_return(self):
        return self._num_res_return

    @num_res_return.setter
    def num_res_return(self, val):
        self._set_num_res_return(val)

    def _set_num_res_return(self, val):
        self._num_res_return = val

    def app_reset(self):
        self.__init__(db_handler=Database.DatabaseHandler())

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
        # self.db.graph.run('match(n:TrieNode) detach delete n')
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
                # tx.create(Child(db_node_child, db_node))
        tx.commit()
        self.logger.info('Finished updating database. Number of nodes created is %d' % count)
        if tx.finished():
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
            db_node = self.selector.select('TrieNode', name=node.prefix).first()
            if not db_node:
                tx = g.begin()
                db_node = Node('TrieNode',
                               name=node.prefix,
                               isword=node.isWord,
                               count=0)
                tx.create(db_node)
                parent_db_node = self.selector.select('TrieNode', name=parent.prefix).first()
                tx.create(Database.Parent(parent_db_node, db_node))
                tx.commit()
            else:
                db_node['count'] += node.total_counts()
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
        root = self.selector.select('ROOT').first()
        g = self.db.graph

        def dfs(node):
            d = dict(node)
            prefix, isword, count = d['name'], d['isword'], d['count']
            if isword:
                self.insert(prefix, isword, from_db=True, count=count)
            for rel in g.match(node, rel_type='PARENT'):
                dfs(rel.end_node())
        dfs(root)
        self.update_top_results()

    def insert(self, word, isword=True, count=0, from_db=False):
        """
        This method inserts a word into the trie. This method should be hidden from user.
        Only method build_trie() and search() should call this method.
        :param word: str
        :param isword: bool
        :param count: number of times word is searched
        :param from_db: True if the method is called by build_trie()
        :return: Trie node which correspond to the word inserted
        """
        try:
            assert isinstance(word, str), "{} is not a string".format(word)
        except AssertionError as e:
            print(str(e))
            raise
        if len(word.split()) > 1:
            return None

        if word in Trie.english_words:
            self.vocab.add(word)

        cur = self.root

        for char in word:
            if char not in cur.children:
                self.node_count += 1
                cur.children[char] = Trienode.TrieNode(prefix=cur.prefix+char, parent=cur)
            cur = cur.children[char]

        cur.set_total_counts(count)
        cur.isWord = isword

        if from_db:
            cur.count = 0
        else:
            cur.count += 1

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
        last_node = None
        if search_term == '':
            last_node = self.root
        else:
            try:
                words = search_term.split()
                if len(words) == 0:
                    return []
                for word in words:
                    last_node = self.insert(word, from_db=False)
            except AttributeError as e:
                print('The search term {} is not a string'.format(search_term, str(e)))
                return

        if not from_adv_app:
            self.search_count += 1

        if self.search_count >= Trie.trie_update_frequency and not from_adv_app:
            self.search_count = 0
            self.update_top_results()

        result = {word[0] for word in last_node.top_results.most_common(self.num_res_return)}
        return list(result)

    def update_top_results(self):
        """
        This method builds top suggestion results from bottom up.
        :return: None
        """
        def dfs(node):
            if len(node.children) == 0:
                Trie.update_parent(node)
            for child in node.children:
                dfs(node.children[child])
        dfs(self.root)

    @staticmethod
    def update_parent(node):
        d = Counter()
        while node:
            if node.isWord:
                d[node.prefix] += node.count
            node.top_results.update(d)
            node.count = 0
            node = node.parent
