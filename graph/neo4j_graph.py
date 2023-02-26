from neo4j import GraphDatabase

uri = "bolt://localhost:7687"  # Replace with the URI for your local Neo4j instance
u = "neo4j"  # Replace with your Neo4j username
p = "password"  # Replace with your Neo4j password


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
    # ToDo: Check what type node is, add extra properties for some articles
    # ToDo: Article, add paragraph
    # ToDo: Error AttributeError: 'str' object has no attribute 'pop' fixen...
    # print(node.title)
    result = session.run(
        "CREATE (n:" + node.label + " {title: $title, url: $url}) RETURN n",
        title="No title found" if len(node.title) == 0 else node.title.pop(),
        url=node.url,
    )
    current_node = result.single()[0]
    print(f"Created node with name '{current_node['title']}' and url '{current_node['url']}'")


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


def generate_relationship(from_node, to_node, session):
    # generate a relationship from_node -> to_node
    pass


def process_data(session, page_set):
    # insert nodes

    for node in page_set:
        insert_node(session, node)

    # generate relationships
    pass


def generate_graph(page_set):
    session = connect_to_neo4j(u, p)

    process_data(session, page_set)

    disconnect_from_neo4j(session)

    # ToDo: connection to graph goes here and data is written to the database

    # ToDo: interpret paragraphs with nlp library to get meaning of the text, maybe set text title in class data

# if __name__ == "__main__":
#     insert_node()
#     delete_node()
