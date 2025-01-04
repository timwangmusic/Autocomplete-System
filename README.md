# Autocomplete System

Autocomplete system using Neo4j graph database for storing data and providing fault tolerance. Returns top suggestions to users.

## **Feature Support**

- Restful search API for auto-completing any phrase in English and returns top suggestions.
- Autocorrect invalid user inputs.
- Delete inappropriate phrases.
- Build new servers from Neo4j databases.
- Use advance logging techniques to track usage patterns and generate reports.
- Serialization and deserialization of servers for data exchange.

### How to use

- Ensure Python version >= 3.8
- Create a Python virtual environment with pipenv.

```
# macOS/Linux
pip install --user pipenv

```

- Run `pipenv install` to install the dependencies.
- Run `pipenv run python service_with_flask.py` to start REST service.
- Run `pipenv run python src/analytics.py` to generate usage reports.
