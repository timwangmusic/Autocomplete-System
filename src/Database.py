from py2neo import Graph, Relationship


class Parent(Relationship):
    pass


class DatabaseHandler:
    def __init__(self, username='admin', password='admin'):
        self.username = username
        self.password = password
        self.graph = Graph(password=password)
