from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "supersecret"

def connection():
    driver = GraphDatabase.driver(uri=uri, auth=(username, password))
    return driver