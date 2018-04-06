# Auto-complete System
Auto-complete system using Neo4j graph database for storing data and fault tolerance. Return top suggestions to user.

## **Feature Support**
* The Trie applications class creates servers connected to a Neo4j database, which stores terms, counts and other information. Provides API for clients to search any phrases in English. Each search returns top 10 suggestions. 
* New Trie servers can be built from connected Neo4j databases. See the `build_trie()` method for details.
* The application server updates database based on latest usage with configurable update frequency. See the `search()` method for details.
* Tkinter GUI for search API. To use GUI, run `py app.py`.
* Use advance logging techniques to track usage patterns.


<p align="center">
  <img src="https://github.com/weihesdlegend/Auto-complete-System/blob/master/prefix_tree.png" width="500" title = "Prefix Tree Representation in Neo4j", alt="Prefix Tree"/>
</p>
