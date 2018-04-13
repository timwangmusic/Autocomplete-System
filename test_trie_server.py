import unittest

from src.Trieserver import Trie


class TrieServerTest(unittest.TestCase):
    def setUp(self):
        self.trie = Trie()

    def test_insert_single_word(self):
        # test if the last node on the path to the inserted is correct
        node = self.trie.insert('linux', from_db=False)
        self.assertEqual(node.prefix, 'linux')
        self.assertEqual(node.isWord, True)

    def test_insert_multiple_words(self):
        node = self.trie.insert("sweet home", from_db=False)
        self.assertEqual(node, None)

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

if __name__ == '__main__':
    unittest.main()
