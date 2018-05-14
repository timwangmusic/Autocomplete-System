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


def test_search_with_space(app):
    # After insert a space, should return an empty list
    app.search(' ')
    app.update_top_results()
    assert app.search(' ') == []


def test_search_query_single_word(app):
    # After insert via search and update, should return the word
    app.search('testing', from_adv_app=False)
    app.update_top_results()
    res = app.search('testing')
    assert res[0] == 'testing'


def test_search_query_sentence(app):
    # After insert via search and update, should return the query
    app.search('this is a cool test')
    app.update_top_results()
    search_results = app.search('this is a cool test')
    assert search_results[0] == 'this is a cool test'


def test_representation_singleword(app):
    # insert a word and test number of nodes in the Trie
    test_word = 'stranger'
    app.search(test_word)
    p = re.compile(r'.*\s(\S+)\s\w+')
    assert int(p.search(str(app)).group(1)) == len(test_word) + 1
