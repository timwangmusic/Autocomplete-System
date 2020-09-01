"""
Use Flask to create simple auto-complete service

To use:
    run py service_with_flask.py
    in browser: http://localhost:5000/autocomplete?term=search_term
"""

from src.Server import Server
from iomanagers.redis_manager import RedisManager
from flask import Flask, url_for, request, render_template
import datetime
import logging

app = Flask(__name__)
server = Server(connect_to_db=False)
redis_mgr = RedisManager("localhost", "6379", 0)


@app.route('/', methods=["GET"])
def welcome():
    return render_template("welcome_page.html")


@app.route("/getTime", methods=["GET"])
def getTime():
    """
    Print the time on the welcome/main page
    """
    now = datetime.date.today()
    content = f"Thanks for visiting, Time now {now}"
    return content


@app.route('/search', methods=["GET"])
def autocomplete():
    """
    define an autocomplete function as an end-point.
    """
    params = request.args  # parsed url args as a immutable multi-dict
    if params is None or params.get('term') is None:
        return render_template("error_input.html")

    term = params.get('term')        
    
    # make no distinction between empty string and a string of all spaces
    term = term.strip()

    # check autocomplete results from Redis first
    search_result = redis_mgr.get_search_results(term)
    logging.debug(f"the search result for {term} is: {search_result}")

    if not search_result:
        search_result = server.search(term)

        redis_mgr.cache_search_results(term, search_result)

    return render_template("search_results.html", term=term, results=search_result)


with app.test_request_context():
    print(url_for('welcome'))
    print(url_for('autocomplete'))

if __name__ == '__main__':
    app.run(host='127.0.0.1')
