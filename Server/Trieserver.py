from Trienode import TrieNode
from py2neo import Node
from collections import deque, Counter
from nltk.corpus import words as en_corpus
from logging import getLogger, FileHandler, INFO, Formatter
from Database import DatabaseHandler, Parent, Child


class Trie:
    """Returns top 10 results to the user. Results may be outdated before calling update trie function."""
    english_words = set(en_corpus.words())
    trie_index = 0

    def __init__(self, db_handler=DatabaseHandler(), logger=None):
        self.root = TrieNode(prefix='', is_word=True)
        self.vocab = set()
        self.db = db_handler
        # Logging facilities
        self.log_file = 'trie_usage_{}.log'.format(Trie._get_next_trie_index())
        self.logger = logger or getLogger('__main__')
        self.logger.setLevel(INFO)
        f_handler = FileHandler(self.log_file)
        f_handler.setLevel(INFO)
        formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(formatter)
        self.logger.addHandler(f_handler)
        self.searchLogger = getLogger('root.search')
        self.insertLogger = getLogger('root.insertion')
        self.searchLogger.addHandler(f_handler)
        self.insertLogger.addHandler(f_handler)

    @classmethod
    def _get_next_trie_index(cls):
        result = Trie.trie_index
        Trie.trie_index += 1
        return result

    def update_db(self):
        """
        This method updates database with in-memory data in application server.
        :return: None
        """
        queue = deque()
        tx = self.db.graph.begin()
        self.logger.debug('Start updating database.')
        node = Node('TrieNode', 'root', prefix=self.root.prefix, isword=self.root.isWord, count=self.root.count)
        tx.create(node)     # create root in neo4j
        queue.append((node, self.root))
        count = 0
        while queue:
            db_node, cur = queue.popleft()
            for child in cur.children:
                db_node_child = Node('TrieNode', prefix=cur.children[child].prefix,
                                     isword=cur.children[child].isWord,
                                     count=cur.children[child].count)
                queue.append((db_node_child, cur.children[child]))
                tx.create(db_node_child)
                count += 1
                tx.create(Parent(db_node, db_node_child))
                tx.create(Child(db_node_child, db_node))
        tx.commit()
        self.logger.info('Finished updating database. Number of nodes created is %d' % count)
        if tx.finished():
            self.logger.debug('Transaction finished.')

    def build_trie(self):
        """
        This method builds trie server with TrieNode-labeled nodes from the database.
        :return: None
        """
        data_cursor = self.db.graph.run("MATCH(n:TrieNode)-[:PARENT]->(m) RETURN m.prefix, m.isword, m.count")
        for record in data_cursor:
            prefix, isword, count = record['m.prefix'], record['m.isword'], record['m.count']
            self.insert(prefix, isword=isword, count=count, from_db=True)
        self.update_top_results()

    def insert(self, word, isword=True, count=0, from_db=False):
        """
        Insert a word into the trie. This method should be hidden from user.
        Only method build_trie() and search() should call this method.
        :param word: str
        :param isword: bool
        :param count: number of times word is searched
        :param from_db: True if the method is called by build_trie()
        :return: Trie node which correspond to the word inserted
        """
        if word in Trie.english_words:
            self.vocab.add(word)
        cur = self.root
        for char in word:
            if char not in cur.children:
                cur.children[char] = TrieNode(prefix=cur.prefix+char, parent=cur)
            cur = cur.children[char]
        cur.isWord = isword
        if from_db:
            cur.count = count
        else:
            cur.count += 1
        self.insertLogger.debug('{} is inserted to vocabulary'.format(word))
        return cur

    def search(self, search_term):
        """
        API for clients to get a list of top suggestions.
        The input may be a sentence, with words separated by space.
        Search top results for entire sentence may not make sense.
        Current design returns top results only based on last word in a sentence.
        :param search_term: str
        :return: List[str]
        """
        words = search_term.split()
        last_node = None
        for word in words:
            last_node = self.insert(word, from_db=False)
        return [word[0] for word in last_node.top_results.most_common(10)]

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
        while node.parent:
            if node.isWord:
                d[node.prefix] += node.count
            node.top_results.update(d)
            node.count = 0
            node = node.parent
