import logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from graph.neo4j_graph import generate_graph, connect_to_neo4j, disconnect_from_neo4j
from scraper.scraper import WebsiteScraper
from scraper.scraper_utils import trim_urls

# ToDo: Move to UI
uri = "neo4j+s://65f99491.databases.neo4j.io:7687"  # Replace with the URI for your local Neo4j instance
user = "neo4j"  # Replace with your Neo4j username
password = "9aiKUTWKd7kyfn3lPuJBRAMzddJ_Koe5qfkFu4UsnV8"  # Replace with your Neo4j password


# testsites
WIEN = 'https://www.bhakwien22.at'  # reference site with deep structure and multiple nodes
SIA = 'https://www.sigmaiotarhoetaalpha.org'  # small website with deep structure
CPX = 'https://www.compaxdigital.com'  # big website with flat structure
OEH = 'https://www.oeh-mci.at' #

# testsites that are not working because of site blocks or other reasons
# MCI = 'https://www.mci.edu' (Website split into multiple urls like edu, de, at, ...)
# MEDI = 'https://www.medicubus.at' (Scraper blocking)


def main():

    # trim input url for use
    trim_url = trim_urls([OEH])

    # information retrieval and structuring
    data_set = retrieve_information(trim_url, OEH)
    write_data(data_set)
    print("Information Retrieval System completed!")

def retrieve_information(trim_url, website):
    # start scraper/crawler with given url
    process = CrawlerProcess(get_project_settings())
    process.crawl(WebsiteScraper, websites=[website], allowed=trim_url)
    process.start()

    # get dataset from retrieval operation
    return WebsiteScraper.get_data_set()


def write_data(data_set):
    # connect to neo4j database
    session = connect_to_neo4j(user, password)
    print("Connected to Neo4j (" + uri + ") with user: " + user)

    # generate cypher queries and fill database
    generate_graph(session, data_set)

    # close connection
    disconnect_from_neo4j(session)
    print("Disconnected from Neo4j")


if __name__ == "__main__":
    main()
