# Auto-complete System
Auto-complete system using Neo4j graph database for storing data and fault tolerance. Return top suggestions to user.

## **Feature Support**
* The Trie class creates basic app servers connected to a Neo4j database, which stores terms, counts and other information.
* Provides API for clients to search any phrases in English. Each search returns top 10 suggestions.
* New app servers can be built from Neo4j databases.
* The application server updates database based on latest usage with configurable update frequency.
* Tkinter GUI for search API. To use GUI, run `py app.py`.
* Use advance logging techniques to track usage patterns.
* Advanced trie classes instantiate servers that returns spell correction in case the terms are not English words.
* Serialization and deserialization of app server. Serialization encodes information prefix, if the term is word and top suggestions in the subtree.

<p align="center">
  <img src="https://github.com/weihesdlegend/Auto-complete-System/blob/master/prefix_tree.png" width="500" title = "Prefix Tree Representation in Neo4j", alt="Prefix Tree"/>
</p>
