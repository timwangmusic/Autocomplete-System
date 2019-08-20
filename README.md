# Auto-complete System
[![Build Status](https://travis-ci.org/weihesdlegend/Auto-complete-System.svg?branch=master)](https://travis-ci.org/weihesdlegend/Auto-complete-System)

Auto-complete system using Neo4j graph database for storing data and providing fault tolerance. Returns top suggestions to users.

## **Feature Support**
* Restful search API for auto-completing any phrase in English and returns top suggestions. Auto-correct invalid user inputs.
* Delete inappropriate phrases.
* Build new servers from Neo4j databases.
* Use advance logging techniques to track usage patterns and generate reports.
* Serialization and deserialization of servers for data exchange.

### How to use

#### Install pip first
	* Run `sudo apt-get install python3-pip`

#### Then install virtualenv using pip3
	* Run `virtualenv -p python3 env`

#### Now create a virtual environment
	* Run `virtualenv -p python3 env`

#### Active your virtual environment:
	* Run `source env/bin/activate`

#### Install the project requirements
	* Run `pip install -r requirements.txt`

#### Run the project
	* Run `python service_flask.py` to start REST service.
	* Run `python analytics.py` to generate usage reports.