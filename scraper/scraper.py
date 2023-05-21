# create a class that inherits from the scrapy.Spider class
import logging

import scrapy
import validators
from scrapy import signals

from ontology.owl_classes import Article
from scraper.scraper_utils import is_text, extract_tag_text, get_page_type, url_cleanup, get_parent_node, \
    handle_matchting_articles, clean_text

current_node = None


class WebsiteScraper(scrapy.Spider):

    # create a constructor for this class with the arguments website
    def __init__(self, websites, allowed, *args, **kwargs):
        super(WebsiteScraper, self).__init__(*args, **kwargs)
        # set the start_urls attribute to the website argument
        self.start_urls = websites
        self.allowed_domains = allowed

    # define the name of the spider
    name = "ontowebCrawler"

    banned_words = ["termin", "termine"]

    visited_links = set()
    data_set = set()  # set of all pages

    def parse(self, response):

        # ToDo: for testing purpose, remove later
        if len(self.visited_links) > 10:
            return

        global current_node

        # create current node
        check_if_webpage = is_text(response.headers.get('Content-Type', '').decode('utf-8').lower())
        current_node = get_page_type(check_if_webpage, response.url)

        self.visited_links.add(response.url)

        # save page to data_set
        self.data_set.add(current_node)

        # get parent node / url
        parent_page_url = response.meta.get('parent')
        parent_node = get_parent_node(self.data_set, parent_page_url)

        # check if current url is starting url and add accordingly
        if response.url in self.start_urls:
            current_node.sibling_of_urls = None
        elif parent_page_url and parent_node:
            parent_node.parent_of_nodes.add(current_node)
            current_node.sibling_of_urls.add(parent_page_url)

        if check_if_webpage:
            # get page title
            h1_text = response.css('h1').getall()
            if len(h1_text) != 0 and h1_text:
                title_set = extract_tag_text(h1_text, 'h1')
                if title_set and len(title_set) != 0:
                    current_node.title = title_set
                else:
                    title_set.add("No title found")
                    current_node.title = title_set
                yield {"title": title_set}
            else:
                # fallback title from url if no h1 tag is present
                current_node.title.add(url_cleanup(response.url).split('/')[-1])

            # get all paragraphs and their corresponding header
            # ToDo: find articles with same title and link them together matching_title
            # ToDo: ' auskommentiern mit \'
            paragraphs = response.css('p')
            if len(paragraphs) != 0 and paragraphs:
                # search for paragraph & title
                for p in paragraphs:
                    # convert p tag to string
                    p_text = ''.join(p.xpath('.//text()').getall()).strip()
                    p_text = clean_text(p_text)
                    # Article class for every paragraph on page
                    article = Article(url=response.url, content=p_text, title=set())
                    # Find title of paragraph
                    # Get the parent div of the paragraph
                    parent_div = p.xpath('ancestor::div[1]')
                    # Keep searching for parent div until any 'h' tag is found
                    while parent_div:
                        h_tag = parent_div.xpath('.//h1|.//h2|.//h3').get()
                        if h_tag:
                            h_text = scrapy.Selector(text=h_tag).xpath('string()').get().strip()
                            h_text = clean_text(h_text)
                            article.title.add(h_text)
                            handle_matchting_articles(self.data_set, article)
                            break
                        parent_div = parent_div.xpath('ancestor::div[1]')
                    if article.title is None or len(article.title) == 0:
                        article.title.add("No title found")
                    # Add article to article_set of current_node
                    current_node.articles.add(article)
                    self.data_set.add(article)

            links = response.css('a::attr(href)').getall()

            # get all links and visit them, also crosslink every connected link with the current page
            for link in links:
                if validators.url(link) and self.allowed_domains[0] in link and not \
                        any(banned_word in link for banned_word in self.banned_words):
                    if link not in self.visited_links:
                        yield {"link": link}
                        yield response.follow(link, callback=self.parse, meta={'parent': response.url})
                    else:
                        if parent_node:
                            parent_node.parent_of_nodes.add(current_node)
                            current_node.sibling_of_urls.add(parent_node.url)
                            self.logger.info("Sibling: %s added to Parent: %s", current_node.url, parent_node.url)
        yield self.data_set

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(WebsiteScraper, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_finished, signal=signals.spider_closed)
        return spider

    @classmethod
    def get_data_set(cls):
        return cls.data_set

    def spider_finished(self, spider):
        logging.info("Spider finished")
        print("Spider finished")
