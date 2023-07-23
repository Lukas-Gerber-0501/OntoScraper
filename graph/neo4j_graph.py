import logging
import spacy
from neo4j import GraphDatabase
import uuid

from generics.generics import WEBPAGE, ARTICLE, MATCHING_TITLE, PARENT_OF, NO_TITLE, ARTICLE_ID, REL_ID, \
    DATA_ID, DATA_REL_ID, MENTIONED_IN, PDF
from ontology.owl_classes import Data

# ToDo: Eingabemaske über GUI
uri = "neo4j+s://65f99491.databases.neo4j.io:7687"  # Replace with the URI for your local Neo4j instance
user = "neo4j"  # Replace with your Neo4j username
password = "9aiKUTWKd7kyfn3lPuJBRAMzddJ_Koe5qfkFu4UsnV8"  # Replace with your Neo4j password

global_counter = 0


def connect_to_neo4j(username, pw):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, pw))
        current_session = driver.session()
        return current_session
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")


def disconnect_from_neo4j(session):
    session.close()


def insert_node_and_data(session, node):
    # node = webpage with data, articles, subpages

    # create webpage node
    query_string = create_query_string_builder(node)
    print("Create: ", query_string)

    if node.label == WEBPAGE:
        # create article nodes
        if node.articles:
            query_string += multiquery_string_builder(node.articles, ARTICLE_ID, REL_ID)
            print("Article query: ", query_string)

        # create data nodes
        if node.data:
            query_string += multiquery_string_builder(node.data, DATA_ID, DATA_REL_ID)
            print("Data query: ", query_string)

    session.run(query_string)
    print(f"Created node with name '{node.label}' and url '{node.url}'")

    # if node.label == WEBPAGE:
    #     # match articles relationship
    #     if node.articles:
    #         matching_query = matching_article_builder(ARTICLE, node.url)
    #         session.run(matching_query)
    #         print("Created relationship between articles")
    #         print(matching_query)


def matching_article_builder(label, parent_url):
    relationship_query = f"MATCH (a:{label}), (b:{label}) "
    relationship_query += f"WHERE a.title = b.title and ID(a) <> ID(b) and a.parent_url = '{parent_url}' and a.title <> '' and a.title <> 'No title'"
    relationship_query += "MERGE (c:information {title: a.title}) "
    relationship_query += "WITH a,b,c "
    relationship_query += f"MERGE (a)-[r1:{MATCHING_TITLE}]->(c) "
    relationship_query += f"MERGE (b)-[r2:{MATCHING_TITLE}]->(c) "
    relationship_query += "RETURN r1, r2"
    return relationship_query


def multiquery_string_builder(dataset, node_id, rel_id):
    query_string = ","

    for idx, node in enumerate(dataset):
        label, ext = get_label(node)
        query_string += f"({node_id}{idx}: {label} {{"
        query_string += get_query_items(node)
        query_string += "}),"
        # create parent_of relationship
        query_string += f"(n)-[{rel_id}{idx}:{PARENT_OF}]->({node_id}{idx}),"

        if node_id == ARTICLE_ID or (node_id == DATA_ID and node.extension == PDF):
            entities = run_named_entity_recognition(node.content)
            query_string += create_ner_cypher_query(node_id, idx, entities)

    return query_string[:-1]


def run_named_entity_recognition(text):
    # load pretrained language model
    nlp = spacy.load("de_core_news_sm")

    # use named entity recognition on text
    doc = nlp(text)

    # filter for the main entities
    filtered_entities = [ent for ent in doc.ents if ent.label_ in ['LOC', 'ORG', 'PER', 'MISC']]

    # return filtered entities
    return filtered_entities


def create_ner_cypher_query(parent_id, parent_idx, entities):
    global global_counter
    temp = list()
    query_string = ""
    for idx, ent in enumerate(entities):
        if ent.text not in temp:
            temp.append(ent.text)
            label = get_ner_label(ent.label_)
            query_string += f"(e{global_counter}{parent_idx}{idx}:{label} {{uuid: '{str(uuid.uuid4())}', title: '{ent.text}'}}),"
            query_string += f"(e{global_counter}{parent_idx}{idx})-[er{global_counter}{parent_idx}{idx}:{MENTIONED_IN}]->({parent_id}{parent_idx}),"
            global_counter += 1

    return query_string


def get_ner_label(label):
    if label == 'PER':
        return 'person'
    if label == 'MISC':
        return 'miscellaneous'
    if label == 'LOC':
        return 'location'
    if label == 'ORG':
        return 'organization'
    else:
        return 'miscellaneous'


def create_query_string_builder(node):
    label, ext = get_label(node)
    query_string = f"CREATE (n:{label} {{"
    query_string += get_query_items(node)
    query_string += "})"
    return query_string


def get_query_items(node):
    query_string = ""
    for key, value in node.__dict__.items():
        if key == 'title':
            if type(node) == Data:
                print("Stop")
            title_text = NO_TITLE if len(node.title) == 0 else list(node.title)[0]
            query_string += f"{key}: '{str(title_text)}',"
            continue
        if value and (type(value) is str or type(value) is int):
            query_string += f"{key} : '{str(value)}',"
    return query_string[:-1]


def get_label(node):
    if node.label:
        return node.label, None
    return node.mimetype, node.extension


def delete_node(conn_session, node):
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("MATCH (n:Greeting {name: $name}) DELETE n",
                                 name='test')
            greeting_node = result.single()[0]
            print(f"Deleted node with name '{greeting_node['name']}'")
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
    finally:
        # Close the driver when done
        driver.close()


def delete_all_nodes_and_relationships(session):
    result = session.run("MATCH (n) DETACH DELETE n")
    print(f"Deleted all nodes. {result}")


def check_for_relationship(session, page_set):
    for current_page in page_set:
        if current_page.parent_of_webpages:
            relationship_query = f"MATCH (a:{current_page.label} {{url: '{current_page.url}'}}), "
            merge_query = ""
            for idx, sibling_page in enumerate(current_page.parent_of_webpages):
                relationship_query += f"(b{idx}:{sibling_page.label} {{url: '{sibling_page.url}'}}), "
                merge_query += f"MERGE (a) -[r{idx}:{PARENT_OF}]->(b{idx}) "

            relationship_query = relationship_query[:-2]
            relationship_query += merge_query
            session.run(relationship_query)
            print(f"Inserted parent_of relationship for node {current_page.url} \n with query: {relationship_query}")


def process_data(session, page_set):
    # delete all nodes
    delete_all_nodes_and_relationships(session)

    # insert nodes
    for node in page_set:
        insert_node_and_data(session, node)

    # generate webpage relationships
    check_for_relationship(session, page_set)


def generate_graph(session, page_set):
    print("Starting data processing....")
    process_data(session, page_set)
    print("Finished data processing!")
