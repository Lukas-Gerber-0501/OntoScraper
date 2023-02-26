# create a scraper with the scrapy package
# import the scrapy package
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from graph.neo4j_graph import generate_graph
from scraper.scraper import WebsiteScraper
from scraper.scraper_utils import trim_urls

print("File Main __name__ is set to: {}".format(__name__))

# testsites
WIEN = 'https://www.bhakwien22.at'  # Referenzseite
TOBI = 'https://www.sigmaiotarhoetaalpha.org'  # kleine Seite
CPX = 'https:://www.compax.at'

# testsites that are not working because of site blocks or other reasons
# MCI = 'https://www.mci.edu'
# MEDI = 'https://www.medicubus.at'


def main():
    trim_res = trim_urls([WIEN])

    process = CrawlerProcess(get_project_settings())
    process.crawl(WebsiteScraper, websites=[WIEN], allowed=trim_res)
    process.start()

    data_set = WebsiteScraper.get_data_set()

    generate_graph(data_set)

    print("Page Set: {}".format(data_set))


if __name__ == "__main__":
    main()
