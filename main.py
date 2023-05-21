# create a scraper with the scrapy package
# import the scrapy package
import logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import graph_db_test
from generics.generics import WEBPAGE
from graph.neo4j_graph import generate_graph
from ontology.owl_classes import Webpage, Article, Data
from scraper.scraper import WebsiteScraper
from scraper.scraper_utils import trim_urls

print("File Main __name__ is set to: {}".format(__name__))

# testsites
WIEN = 'https://www.bhakwien22.at'  # reference site with deep structure
TOBI = 'https://www.sigmaiotarhoetaalpha.org'  # small website
CPX = 'https:://www.compax.at'  # website with flat structure


# testsites that are not working because of site blocks or other reasons
# MCI = 'https://www.mci.edu'
# MEDI = 'https://www.medicubus.at'


def main():
    logging.basicConfig(filename='ontoScraper_info.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    logging.basicConfig(filename='ontoScraper.log', level=logging.WARN,
                        format='%(asctime)s %(levelname)s %(message)s')

    trim_res = trim_urls([WIEN])

    process = CrawlerProcess(get_project_settings())
    process.crawl(WebsiteScraper, websites=[WIEN], allowed=trim_res)
    process.start()

    data_set = WebsiteScraper.get_data_set()

    generate_graph(data_set)

    print("Page Set: {}".format(data_set))


def test_main():
    test_data_set = set()

    node = Webpage(url="testurl.com")
    node2 = Webpage(url="testurl2.com")
    node3 = Webpage(url="testurl3.com")
    node4 = Webpage(url="testurl4.com")

    pdf = Data(label="application", url="testdokument1.pdf")
    video = Data(label="video", url="testvideo1.mp4")
    audio = Data(label="audio", url="testaudio1.mp3")

    node.data.add(pdf)
    node.data.add(video)
    node.data.add(audio)

    image = Data()
    image.title.add("testimage")
    image.label = "image"
    image.extension = ".jpg"
    node2.data.add(image)

    article = Article(url="testurl.com", content="testcontent")
    article2 = Article(url="testurl2.com", content="testcontent2")
    article.title.add("testarticle")
    article2.title.add("testarticle")

    article.matching_title_urls.add(article2.url)
    article2.matching_title_urls.add(article.url)

    node.title.add("test")
    node.articles.add(article)
    node.articles.add(article2)
    node.parent_of_nodes.add(node2)
    node.parent_of_nodes.add(node3)

    node2.title.add("test2")
    node3.title.add("test3")
    node4.title.add("test4")

    node2.parent_of_nodes.add(node4)
    node2.parent_of_nodes.add(article)
    node2.parent_of_nodes.add(article2)
    test_data_set.add(node)
    test_data_set.add(node2)
    test_data_set.add(article)
    test_data_set.add(image)
    test_data_set.add(article2)
    test_data_set.add(node3)
    test_data_set.add(node4)

    graph_db_test.generate_graph(test_data_set)


if __name__ == "__main__":
    # main()
    test_main()
