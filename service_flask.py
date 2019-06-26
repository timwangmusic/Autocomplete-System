"""
Use Flask to create simple auto-complete service

To use:
    run py service_flask.py
    in browser: http://localhost:5000/autocomplete?term=search_term
"""

from src.Server import Server
import flask

app = flask.Flask(__name__)
server = Server(connect_to_db=False)


@app.route('/search', methods=["GET", "POST"])
def autocomplete():
    """
    define an autocomplete function as an end-point.
    """
    data = {'success': False}

    params = flask.request.json
    if params is None:
        params = flask.request.args

    if params is not None:
        search_result = server.search(params.get('term'))
        data['result'] = search_result
        data['success'] = True

    return flask.jsonify(data)


if __name__ == '__main__':
    app.run(host='127.0.0.1')
