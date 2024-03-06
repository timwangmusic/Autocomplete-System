# Autocomplete System
Autocomplete system using Neo4j graph database for storing data and providing fault tolerance. Returns top suggestions to users.

## **Feature Support**
* Restful search API for auto-completing any phrase in English and returns top suggestions.
* Autocorrect invalid user inputs.
* Delete inappropriate phrases.
* Build new servers from Neo4j databases.
* Use advance logging techniques to track usage patterns and generate reports.
* Serialization and deserialization of servers for data exchange.

### How to use
* Ensure Python version >= 3.8
* Create a Python virtual environment.
```
# macOS/Linux
sudo apt-get install python3-venv # If needed
python3 -m venv env
source env/bin/activate

# Windows
python -m venv env
```
* Run `pip3 install -r requirements.txt` to install the python3 requirements.
* Run `python service_flask.py` to start REST service.
* Run `python analytics.py` to generate usage reports.
