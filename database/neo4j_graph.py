import uuid

import spacy
from neo4j import GraphDatabase

from utils.constants import WEBPAGE, PARENT_OF, NO_TITLE, ARTICLE_ID, REL_ID, \
    DATA_ID, DATA_REL_ID, MENTIONED_IN, PDF
from scraper.scraper_utils import clean_text

global_counter = 0


def connect_to_neo4j(username, pw, uri):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, pw))
        current_session = driver.session()
        return current_session
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")


def disconnect_from_neo4j(session):
    print("Disconnected from Neo4J")
    session.close()


def insert_node_and_data(session, node):
    # create node
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


def create_query_string_builder(node):
    # node creation string and concat all the necessary nodes together
    label, ext = get_node_label(node)
    query_string = f"CREATE (n:{label} {{"
    query_string += get_query_items(node)
    query_string += "})"
    return query_string


def multiquery_string_builder(dataset, node_id, rel_id):
    # this cypher query builder generates a node for the given information and
    # adds the corresponding relationships at the same time
    query_string = ","

    for idx, node in enumerate(dataset):
        label, ext = get_node_label(node)
        query_string += f"({node_id}{idx}: {label} {{"
        query_string += get_query_items(node)
        query_string += "}),"
        # create parent_of relationship
        query_string += f"(n)-[{rel_id}{idx}:{PARENT_OF}]->({node_id}{idx}),"

        # when the node is an article or a pdf, run the named entity recognition
        if node_id == ARTICLE_ID or (node_id == DATA_ID and node.extension == PDF):
            entities = run_named_entity_recognition(node.content)
            query_string += create_ner_cypher_query(node_id, idx, entities)

    return query_string[:-1]


def get_query_items(node):
    # iterate over all variables in the class and
    # create parameters with the same names and the corresponding values
    # to create a cyper node
    query_string = ""
    for key, value in node.__dict__.items():
        if key == 'title':
            title_text = NO_TITLE if len(node.title) == 0 else list(node.title)[0]
            query_string += f"{key}: '{str(title_text)}',"
            continue
        if value and (type(value) is str or type(value) is int):
            query_string += f"{key} : '{str(value)}',"
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
    # create node and relationship for the extracted entities of the named entity recognition
    global global_counter
    temp = list()
    query_string = ""
    for idx, ent in enumerate(entities):
        if ent.text not in temp:
            temp.append(ent.text)
            label = get_ner_label(ent.label_)
            query_string += f"(e{global_counter}{parent_idx}{idx}:{label} {{uuid: '{str(uuid.uuid4())}', title: '{clean_text(ent.text)}'}}),"
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


def get_node_label(node):
    if node.label:
        return node.label, None
    return node.mimetype, node.extension


def delete_all_nodes_and_relationships(session):
    # function to clean the database before a run
    result = session.run("MATCH (n) DETACH DELETE n")
    print(f"Deleted all nodes. {result}")


def check_for_relationship(session, page_set):
    # function to check for relationships between nodes in the given set
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

    # generate relationships
    check_for_relationship(session, page_set)

    disconnect_from_neo4j(session)



