# Auto-complete System
Auto-complete system using Neo4j graph database for storing data and fault tolerance. Return top suggestions to user.

## **Feature Support**
* The Trie class creates an application server connected to a Neo4j database, which stores terms, counts and other associated information. Trie servers support insertion, search and deletion of terms. 
* New Trie servers can be built from Neo4j database. See the `build_trie()` method for details.
* The application server can update database based on latest usage. See the `update_db()` method for details.
* Each search returns top 10 suggestions with the term as prefix.
* Use advance logging techniques to track usage patterns.
