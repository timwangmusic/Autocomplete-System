import pytest
from src.Trieserver import Trie


@pytest.fixture
def app():
    return Trie(connect_to_db=False, testing=True)


def test_insert_single_word():
    # test if the last node on the path to the inserted is correct
    node = app.insert('linux', from_db=False)
    assert node.prefix == 'linux'
    assert node.isWord is True


def test_insert_multiple_words():
    node = app.insert("sweet home", from_db=False)
    assert node is None


def test_search_with_empty_input():
    # After insert via search and update, should return overall top results
    app.search('probing')
    app.update_top_results()
    res = app.search("")
    assert res[0] == 'probing'


def test_search_with_space():
    # After insert a space, should return an empty list
    app.search(' ')
    app.update_top_results()
    assert app.search(' ') == []


def test_search_query_single_word():
    # After insert via search and update, should return the word
    app.search('testing', from_adv_app=False)
    app.update_top_results()
    res = app.search("")
    assert res[0] == 'testing'


def test_search_query_sentence():
    # After insert via search and update, should a list containing all words in the query
    app.search('this is a cool test')
    app.update_top_results()
    search_results = set(app.search(""))
    search_term = 'this is a cool test'.split()
    for word in search_term:
        assert word in search_results


def test_search_prefix_chain_creation():
    # insert a word and all prefix nodes should be correctly created
    test_word = "Spectacular"
    prefixes = [test_word[:i] for i in range(len(test_word))]
    app.search(test_word)
    node = app.root
    for i in range(len(test_word)):
        assert node.prefix == prefixes[i]
        node = node.children[test_word[i]]


"""
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
