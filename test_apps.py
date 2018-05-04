import pytest
from src.Trieserver import Trie


@pytest.fixture
def app():
    return Trie(connect_to_db=False, testing=True)


def test_insert_single_word(app):
    # test if the last node on the path to the inserted is correct
    node = app.insert('linux', from_db=False)
    assert node.prefix == 'linux'
    assert node.isWord is True


def test_insert_multiple_words(app):
    node = app.insert("sweet home", from_db=False)
    assert node is None


def test_search_with_empty_input(app):
    # After insert via search and update, should return overall top results
    app.search('probing')
    app.update_top_results()
    res = app.search("")
    assert res[0] == 'probing'


def test_search_with_space(app):
    # After insert a space, should return an empty list
    app.search(' ')
    app.update_top_results()
    assert app.search(' ') == []


def test_search_query_single_word(app):
    # After insert via search and update, should return the word
    app.search('testing', from_adv_app=False)
    app.update_top_results()
    res = app.search("")
    assert res[0] == 'testing'


def test_search_query_sentence(app):
    # After insert via search and update, should a list containing all words in the query
    app.search('this is a cool test')
    app.update_top_results()
    search_results = set(app.search(""))
    search_term = 'this is a cool test'.split()
    for word in search_term:
        assert word in search_results


def test_search_prefix_chain_creation(app):
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

def same_tree(app, new_app):
    def check_property(x, y):
        return x.prefix == y.prefix and x.children.keys() == y.children.keys() and \
               x.total_counts() == y.total_counts()

    if app is None and new_app is None:
        return True
    elif app is None or new_app is None:
        return False
    if not check_property(app, new_app):
        return False
    for child_x, child_y in zip(app.children.keys(), new_app.children.keys()):
        if not same_tree(app.children[child_x], new_app.children[child_y]):
            return False
    return True