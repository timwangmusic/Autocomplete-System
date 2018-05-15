import pytest
import re
from src.Server import Server


@pytest.fixture(name='app')
def get_app():
    return Server(connect_to_db=False, testing=True)


def test_representation_single_word(app):
    # Insert a word and test number of nodes in the Trie
    test_word = 'Doctor strange'
    app.search(test_word)
    p = re.compile(r'.*\s(\S+)\s\w+')
    assert int(p.search(str(app)).group(1)) == len(test_word) + 1


lists = [
         (
            'linux',
            'linux',
          ),
         (
             'pneumonoultramicroscopicsilicovolcanoconiosis',
             'pneumonoultramicroscopicsilicovolcanoconiosis',
          ),
         (
             'democracy',
             'democracy',
          ),
         (
             'Beethoven-Symphony',
             'Beethoven-Symphony',
          ),
        ]


@pytest.mark.parametrize('input_str, expected', lists)
def test_insert_single_word(app, input_str, expected):
    # Test if the last node on the path to the inserted is correct
    node = app._Server__insert(input_str, from_db=False)
    assert (node.prefix, node.isWord) == (expected, True)


def test_search_with_space(app):
    # After insert a space, should return an empty list
    app.search(' ')
    app.update_top_results()
    assert app.search(' ') == []


def test_search_query_single_word(app):
    # After insert via search and update, should return the word
    app.search('testing')
    app.update_top_results()
    res = app.search('testing')
    assert res == ['testing']


def test_search_query_sentence(app):
    # After insert via search and update, should return the query
    app.search('this is a cool test')
    app.update_top_results()
    res = app.search('this is a cool test')
    assert res == ['this is a cool test']


def test_serialization(app):
    # After search a term, perform path compression and then serialize the server
    app.search('time machine is here')
    Server.path_compression(app)
    expected = [['', '0', 'time_machine_is_here 1', '1'],
                ['time machine is here', '1', 'time_machine_is_here 1', '0'],
                ]
    assert app.server_serialization() == expected


def test_server_reconstruction_similarity(app):
    app.search('simplicity is the ultimate sophistication')
    s = app.server_serialization()
    new_app = Server.server_deserialization(s, testing=True)
    assert new_app.server_serialization() == s
