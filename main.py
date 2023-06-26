import logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from graph.neo4j_graph import generate_graph
from scraper.scraper import WebsiteScraper
from scraper.scraper_utils import trim_urls

print("File Main __name__ is set to: {}".format(__name__))

# testsites
WIEN = 'https://www.bhakwien22.at'  # reference site with deep structure and multiple nodes
SIA = 'https://www.sigmaiotarhoetaalpha.org'  # small website
CPX = 'https:://www.compax.at'  # website with flat structure


# testsites that are not working because of site blocks or other reasons
# MCI = 'https://www.mci.edu' (Website split into multiple urls like edu, de, ...)
# MEDI = 'https://www.medicubus.at' (Scraper blocking)


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


if __name__ == "__main__":
    main()
    # test_main()
