# Auto-complete System
[![Build Status](https://travis-ci.org/weihesdlegend/Auto-complete-System.svg?branch=master)](https://travis-ci.org/weihesdlegend/Auto-complete-System)

Auto-complete system using Neo4j graph database for storing data and providing fault tolerance. Return top suggestions to user.

## **Feature Support**
* Establish connection of app servers to Neo4j databases, which store terms, counts and other information.
* API to search any phrase in English and returns top suggestions. Auto-correct invalid user inputs.
* API to delete inappropriate phrases.
* API to build new servers from Neo4j databases.
* Use advance logging techniques to track usage patterns.
* Serialization and deserialization of servers.

### How to use
* Run `py app.py` to trigger Tkinter UI.
* Run `py analytics.py` to generate usage reports.
