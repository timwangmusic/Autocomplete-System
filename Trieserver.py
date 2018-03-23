from Trienode import TrieNode
from py2neo import Graph, Node, Relationship
from collections import deque, Counter
from nltk.corpus import words as en_corpus


class Parent(Relationship):
    pass


class Child(Relationship):
    pass


class DatabaseHandler:
    def __init__(self, username='admin', password='admin'):
        self.username = username
        self.password = password
        self.graph = Graph(password=password)


class Trie:
    english_words = set(en_corpus.words())

    def __init__(self, db_handler=None):
        self.root = TrieNode(prefix='', is_word=True)
        self.vocab = set()
        self.db = db_handler

    def update_db(self):
        """
        This method updates database with in-memory data in application server.
        :return: None
        """
        queue = deque()
        tx = self.db.graph.begin()
        node = Node('TrieNode', 'root', prefix=self.root.prefix, isword=self.root.isWord, count=self.root.count)
        tx.create(node)     # create root in neo4j
        queue.append((node, self.root))
        while queue:
            db_node, cur = queue.popleft()
            for child in cur.children:
                db_node_child = Node('TrieNode', prefix=cur.children[child].prefix,
                                     isword=cur.children[child].isWord,
                                     count=cur.children[child].count)
                queue.append((db_node_child, cur.children[child]))
                tx.create(db_node_child)
                tx.create(Parent(db_node, db_node_child))
                tx.create(Child(db_node_child, db_node))
        tx.commit()

    def build_trie(self):
        """
        This method builds trie server with TrieNode-labeled nodes from the database.
        :return: None
        """
        data_cursor = self.db.graph.run("MATCH(n:TrieNode)-[:PARENT]->(m) RETURN m.prefix, m.isword, m.count")
        for record in data_cursor:
            prefix, isword, count = record['m.prefix'], record['m.isword'], record['m.count']
            self.insert(prefix, isword=isword, count=count)

    def insert(self, word, isword=True, count=0):
        """
        Insert word into the trie.
        :param word: str
        :return: None
        """
        if word not in self.vocab:
            if word in Trie.english_words:
                self.vocab.add(word)
            cur = self.root
            for char in word:
                if char not in cur.children:
                    cur.children[char] = TrieNode(prefix=cur.prefix+char, parent=cur)
                cur = cur.children[char]
            cur.isWord = isword
            cur.count = count

    def search(self, word):
        """
        API for clients to get a list of top suggestions.
        :param word: str
        :return: List[str]
        """
        cur = self.root
        for char in word:
            if char not in cur.children:
                cur.children[char] = TrieNode(prefix=cur.prefix+char, parent=cur)
            cur = cur.children[char]
        cur.count += 1
        cur.top_results[cur.prefix] += 1
        if cur.prefix not in self.vocab and cur.prefix in Trie.english_words:
            self.vocab.add(cur.prefix)
            cur.isWord = True
        return cur.top_results.most_common(10)

    def build_top_results(self):
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
            d[node.prefix] += node.count
            node.top_results.update(d)
            node.count = 0
            node = node.parent
