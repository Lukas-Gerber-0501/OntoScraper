import uuid

import scrapy
import validators

from utils.constants import NO_TITLE
from ontology.owl_classes import Article, Webpage
from scraper.scraper_utils import is_text, extract_tag_text, create_node, url_cleanup, get_parent_node, \
    clean_text, check_content_on_matching_title, clean_title_set

current_node = None


def get_page_title(node, response):
    h1_text = response.css('h1').getall()
    if len(h1_text) != 0 and h1_text:
        title_set = extract_tag_text(h1_text, 'h1')
        if title_set and len(title_set) != 0:
            node.title = clean_title_set(title_set)
        else:
            title_set.add("No title found")
            node.title = clean_title_set(title_set)
    else:
        # fallback title from url if no h1 tag is present
        node.title.add(url_cleanup(response.url).split('/')[-1])


def get_paragraphs(node, response):
    paragraphs = response.css('p')
    if len(paragraphs) != 0 and paragraphs:
        # search for paragraph & title
        for p in paragraphs:

            # buffer to write to article after iteration
            temp_title = set()
            temp_content = ""

            # convert paragraph to string
            p_text = ''.join(p.xpath('.//text()').getall()).strip()
            # replace special chars
            temp_content = clean_text(p_text)

            get_paragraph_title(p, temp_title)

            # check if article with same title exists
            is_matching = check_content_on_matching_title(node.articles, temp_title, temp_content)

            if not is_matching:
                # if there is no matching title/article create new one
                article = Article(url=response.url, content=temp_content, title=temp_title,
                                  parent_url=node.url, uuid=str(uuid.uuid4()))
                node.articles.add(article)


def get_paragraph_title(p, temp_title):
    # Find title of paragraph in parent div
    parent_div = p.xpath('ancestor::div[1]')
    # Keep searching for parent div until a 'h' tag is found
    while parent_div:
        h_tag = parent_div.xpath('.//h1|.//h2|.//h3').get()
        if h_tag:
            h_text = scrapy.Selector(text=h_tag).xpath('string()').get().strip()
            h_text = clean_text(h_text)
            if h_text:
                temp_title.add(h_text)
            break
        parent_div = parent_div.xpath('ancestor::div[1]')
    # if there is no title found, set no title
    if len(temp_title) == 0:
        temp_title.add(NO_TITLE)


class WebsiteScraper(scrapy.Spider):
    def __init__(self, websites, allowed, *args, **kwargs):
        super(WebsiteScraper, self).__init__(*args, **kwargs)
        # set the start_urls attribute to the website argument
        self.start_urls = websites
        self.allowed_domains = allowed

    # define the name of the spider
    name = "OntoScraper"

    # events from the calendar are banned at the moment
    banned_words = ["termin", "termine", "event"]

    visited_links = set()  # set of visited links
    data_set = set()  # set of all webpages, needed for easier relationship mapping in neo4j

    def parse(self, response):
        global current_node

        # create current node
        is_webpage = is_text(response.headers.get('Content-Type', '').decode('utf-8').lower())
        current_node = create_node(is_webpage, response.url)

        # add current url to visited links
        self.visited_links.add(response.url)

        if type(current_node) == Webpage:
            # save webpage to data_set
            self.data_set.add(current_node)

        # get parent node and url
        parent_page_url = response.meta.get('parent')
        parent_node = get_parent_node(self.data_set, parent_page_url)

        # check if current url is starting url and add accordingly
        self.add_urls_to_parent(current_node, parent_node, parent_page_url, response)

        if is_webpage:
            # get page title
            get_page_title(current_node, response)

            # get all paragraphs and their corresponding header
            get_paragraphs(current_node, response)

            # get all links and visit them, also crosslink every connected link with the current page
            links = response.css('a::attr(href)').getall()
            yield from self.get_followup_links(links, response)

    def add_urls_to_parent(self, current_node, parent_node, parent_page_url, response):
        if response.url in self.start_urls:
            current_node.sibling_of_urls = None
        elif parent_page_url and parent_node:
            if type(current_node) == Webpage:
                # add current node to set of sibling nodes of parent and vice versa
                parent_node.parent_of_webpages.add(current_node)
                current_node.sibling_of_urls.add(parent_page_url)
            else:
                # if it is no webpage then add to data
                parent_node.data.add(current_node)
                current_node.sibling_of_urls.add(parent_page_url)

    def get_followup_links(self, links, response):
        for link in links:
            if validators.url(link) and self.allowed_domains[0] in link and not \
                    any(banned_word in link for banned_word in self.banned_words):
                if link not in self.visited_links:
                    yield response.follow(link, callback=self.parse, meta={'parent': response.url})

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(WebsiteScraper, cls).from_crawler(crawler, *args, **kwargs)
        return spider

    @classmethod
    def get_data_set(cls):
        return cls.data_set
