# Auto_complete_system
Auto-complete system using Neo4j graph database for storing data and fault tolerance. Return top suggestions to user.

## Functionalities
* The Trie class creates an application server that connected to a Neo4j database, supporting insertion, search and delete of terms from clients. 
* Trie server can be constructed from Neo4j database.
* The application server can update database based on latest usage.
* Each search with a term returns top 10 suggestions with the term as prefix.
