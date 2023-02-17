"""
Use Flask to create a simple autocomplete service

To use:
    run py service_with_flask.py
"""

from src.Server import Server
from iomanagers.redis_manager import RedisManager
from flask import Flask, url_for, request, render_template
import datetime
import logging
import json

app = Flask(__name__)
server = Server(connect_to_db=False)
redis_mgr = RedisManager("localhost", "6379", 0)


@app.route('/', methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/getTime", methods=["GET"])
def getTime():
    """
    Print the time on the welcome/main page
    """
    now = datetime.date.today()
    content = f"Thanks for visiting, Time now {now}"
    return content

@app.route("/search_history", methods=["GET"])
def getSearchHistory():
    return json.dumps({"result": list(server.search_history)})

@app.route('/search', methods=["GET"])
def autocomplete():
    """
    define an autocomplete function as an end-point.
    """
    params = request.args  # parsed url args as a immutable multi-dict
    if params is None or params.get('term') is None:
        return json.dumps({"result": list()})

    term = params.get('term')        
    
    # make no distinction between empty string and a string of all spaces
    term = term.strip()

    # check autocomplete results from Redis first
    search_result = redis_mgr.get_search_results(term)
    logging.debug(f"the search result for {term} is: {search_result}")

    if not search_result:
        search_result = server.search(term)

        redis_mgr.cache_search_results(term, search_result)

    return json.dumps({"results": search_result})

with app.test_request_context():
    print(url_for('home'))
    print(url_for('autocomplete'))
    print(url_for('static', filename='js/index.js'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
