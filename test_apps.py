import pytest
import re
from src.Trieserver import Trie


@pytest.fixture(name='app')
def get_app():
    return Trie(connect_to_db=False, testing=True)


lists = [('linux', 'linux'),
         ('pneumonoultramicroscopicsilicovolcanoconiosis', 'pneumonoultramicroscopicsilicovolcanoconiosis'),
         ('democracy', 'democracy'),
         ('Beethoven-Symphony', 'Beethoven-Symphony'),
         ]


@pytest.mark.parametrize('input_str, expected', lists)
def test_insert_single_word(app, input_str, expected):
    # test if the last node on the path to the inserted is correct
    node = app._insert(input_str, from_db=False)
    assert (node.prefix, node.isWord) == (expected, True)


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


def test_representation_singleword(app):
    # insert a word and test number of nodes in the Trie
    test_word = 'stranger'
    app.search(test_word)
    p = re.compile(r'.*\s(\S+)\s\w+')
    assert int(p.search(str(app)).group(1)) == len(test_word) + 1
