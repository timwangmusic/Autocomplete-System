from src.Trieserver import Trie


def test_insert_single_word():
    # test if the last node on the path to the inserted is correct
    app = Trie(connect_to_db=False, testing=True)
    node = app.insert('linux', from_db=False)
    assert node.prefix == 'linux'
    assert node.isWord == True


def test_insert_multiple_words():
    app = Trie(connect_to_db=False, testing=True)
    node = app.insert("sweet home", from_db=False)
    assert node == None

"""
    def test_search_with_empty_input(self):
        # After insert via search and update, should return overall top results
        self.trie.search('probing')
        self.trie.update_top_results()
        res = self.trie.search("")
        self.assertTrue(len(res) > 0)

    def test_search_with_space(self):
        # After insert a space, should return an empty list
        self.trie.search(' ')
        self.trie.update_top_results()
        res = self.trie.search(' ')
        self.assertTrue(len(res) == 0)

    def test_search_query_single_word(self):
        # After insert via search and update, should return the word
        self.trie.search('testing', from_adv_app=False)
        self.trie.update_top_results()
        res = self.trie.search("")
        self.assertEqual(res[0], 'testing')

    def test_search_query_sentence(self):
        # After insert via search and update, should a list containing all words in the query
        self.trie.search('this is a cool test')
        self.trie.update_top_results()
        search_results = set(self.trie.search(""))
        search_term = 'this is a cool test'.split()
        for word in search_term:
            self.assertIn(word, search_results)

    def test_search_prefix_chain_creation(self):
        # insert a word and all prefix nodes should be correctly created
        test_word = "Spectacular"
        prefixes = [test_word[:i] for i in range(len(test_word))]
        self.trie.search(test_word)
        node = self.trie.root
        for i in range(len(test_word)):
            self.assertEqual(node.prefix, prefixes[i])
            node = node.children[test_word[i]]



   # the following set of tests verifies database functionality
    def update_database_same_word(self):

        1) Search a new word 2 times ans update trie
        2) Build database
        3) Search the same word 5 times and update trie
        4) update database
        5) Verify the count of the word equals 7

        term = "disneyland"
        for _ in range(2):
            self.trie.search(term)
        self.trie.update_top_results()
        self.trie.build_db()
        for _ in range(5):
            self.trie.search(term)
        self.trie.update_top_results()
        self.trie.update_db()
        count = self.trie.selector.select('TrieNode', name=term).first()['count']
        self.assertEqual(count, 7)

    def test_same_tree(self):

        1) Search a word or couple of words and update trie
        2) Build database
        3) Bring up a new server with data from database
        4) verify both trees are same

        test_term = "test term"
        self.trie.search(test_term)
        self.trie.update_top_results()
        self.trie.build_db()
        self.new_server.build_trie()
        self.assertTrue(same_tree(self.trie.root, self.new_server.root))

"""
