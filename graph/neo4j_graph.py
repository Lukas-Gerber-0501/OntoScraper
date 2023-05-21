import logging

from neo4j import GraphDatabase

from generics.generics import WEBPAGE, ARTICLE, MATCHING_TITLE, PARENT_OF, SIBLING_OF
from ontology.owl_classes import Article

import numpy as n

# ToDo: Eingabemaske über GUI
uri = "neo4j+s://fa3805f7.databases.neo4j.io:7687"  # Replace with the URI for your local Neo4j instance
u = "neo4j"  # Replace with your Neo4j username
p = "7fGG9vComLeggEYMBSqvqvwWWmPwuyxuDV1e2ec-2rc"  # Replace with your Neo4j password


def connect_to_neo4j(username, password):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        current_session = driver.session()
        print("Connected to Neo4j")
        return current_session
    except Exception as e:
        # Handle the exception here
        print(f"Failed to connect to Neo4j: {e}")


def disconnect_from_neo4j(session):
    session.close()


def insert_node(session, node):
    query_string = create_query_string_builder(node)
    session.run(query_string)
    print(f"Created node with name '{node.label}' and url '{node.url}'")


def create_query_string_builder(node):
    label, ext = get_label(node)
    query_string = "CREATE (n:" + label + "{"
    for key, value in node.__dict__.items():
        if key == 'title':
            title_text = "No title found" if len(node.title) == 0 else list(node.title)[0]
            query_string += key + ": '" + str(title_text) + "',"
            continue
        if value and (type(value) is str or type(value) is int):
            query_string += key + ": '" + str(value) + "',"

    query_string = query_string[:-1]
    query_string += "})"
    return query_string


def relationship_query_string_builder(label_from, label_to, matcher_from, matcher_to):
    relationship_query = f"MATCH (a:{label_from}), (b:{label_to}) "
    if label_from == WEBPAGE:
        relationship_query += f"WHERE a.url = '{matcher_from}' and b.url = '{matcher_to}' "
        relationship_query += f"MERGE (a)-[r:{PARENT_OF}]->(b) "
        relationship_query += f"MERGE (b)-[s:{SIBLING_OF}]->(a) "
        relationship_query += "RETURN r, s"
        return

    if label_from == ARTICLE:
        relationship_query += f"WHERE a.{matcher_from} = b.{matcher_to} and ID(a) <> ID(b) "
        relationship_query += f"MERGE (a)-[r:{MATCHING_TITLE}]->(b)"
        relationship_query += "RETURN r"
        return

    return relationship_query


def get_label(node):
    if node.label:
        return node.label, None
    return node.mimetype, node.extension


def delete_node(session, node):
    try:
        driver = GraphDatabase.driver(uri, auth=(u, p))
        with driver.session() as session:
            result = session.run("MATCH (n:Greeting {name: $name}) DELETE n",
                                 name='test')
            greeting_node = result.single()[0]
            print(f"Deleted node with name '{greeting_node['name']}'")
    except Exception as e:
        # Handle the exception here
        print(f"Failed to connect to Neo4j: {e}")
    finally:
        # Close the driver when done
        driver.close()


def delete_all_nodes(session):
    result = session.run("MATCH (n) DETACH DELETE n")
    print(f"Deleted all nodes. {result}")


def check_for_relationship(session, page_set, current_node):
    # generate a relationship from_node -> to_node
    if current_node.label == WEBPAGE:
        if len(current_node.parent_of_nodes) > 0:
            create_parent_sibling_relationships(current_node, current_node.parent_of_nodes, session)

        if len(current_node.articles) > 0:
            create_parent_sibling_relationships(current_node, current_node.articles, session)

        if len(current_node.data) > 0:
            create_parent_sibling_relationships(current_node, current_node.data, session)

    if current_node.label == ARTICLE:
        # then we have the matching titles of the articles
        for node in page_set:
            if node.url in current_node.matching_title_urls and type(node) == Article:
                # create relationship
                if len(current_node.parent_of_nodes) > 0:
                    print("Stop")
                query = relationship_query_string_builder(current_node.label, node.label, "title", "title")

                session.run(query)
                print(f"Created relationship {MATCHING_TITLE} between {current_node.title} and {node.title}")


def create_parent_sibling_relationships(node, data_set, session):
    for data in data_set:
        parent_query = relationship_query_string_builder(node.label, data.label, node.url, data.url)
        session.run(parent_query)
        print(
            f"Created relationships {PARENT_OF} & {SIBLING_OF} between {node.title} and {data.title}")


# MATCH (a:article), (b:article)
# WHERE a.title = b.title and ID(a) <> ID(b)
# CREATE (a)-[r:matching_title]->(b)
# RETURN a,b,r


# MATCH p=()-[:matching_title]->() RETURN p LIMIT 25;

# show all nodes and relationships
# MATCH (n)
# OPTIONAL MATCH (n)-[r]->(m)
# RETURN n, r, m

def process_data(session, page_set):
    # fortesting: delete all nodes before starting fresh
    delete_all_nodes(session)

    # insert nodes
    for node in page_set:
        insert_node(session, node)

    # generate relationships
    for node in page_set:
        check_for_relationship(session, page_set, node)


def generate_graph(page_set):
    logging.basicConfig(filename='neo4j_logger.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    session = connect_to_neo4j(u, p)

    process_data(session, page_set)

    disconnect_from_neo4j(session)

    # ToDo: connection to graph goes here and data is written to the database

    # ToDo: interpret paragraphs with nlp library to get meaning of the text, maybe set text title in class data?

# if __name__ == "__main__":
#     insert_node()
#     delete_node()
