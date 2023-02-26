# create a class that inherits from the scrapy.Spider class

import scrapy
import validators
from scrapy import signals

from ontology.owl_classes import Article
from scraper.scraper_utils import is_text, extract_tag_text, get_page_type, url_cleanup, get_node, get_parent_node

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

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'links.json',
        'FEED_OVERWRITE': "True",
        'FEED_EXPORT_INDENT': 2,
    }

    banned_words = ["termin", "termine"]

    visited_links = set()
    data_set = set()  # set of all pages

    def parse(self, response):
        global current_node

        check_for_webpage = is_text(response.headers.get('Content-Type', '').decode('utf-8').lower())

        current_node = get_page_type(check_for_webpage, response.url)

        # save page to set
        self.data_set.add(current_node)

        # check if current url == start url, else add parent to link_from
        if response.url in self.start_urls:
            current_node.link_from = None
        else:
            current_node.link_from.add(response.meta.get('parent'))
            current_node.link_parent = response.meta.get('parent')

        if check_for_webpage:
            # get page title
            h1_text = response.css('h1').getall()
            if len(h1_text) != 0 and h1_text is not None:
                title_set = extract_tag_text(h1_text, 'h1')
                if title_set is not None and len(title_set) != 0:
                    current_node.title = title_set
                else:
                    title_set.add("No title found")
                    current_node.title = title_set
                yield {"title": title_set}
            else:
                # fallback title from url if no h1 tag is present
                current_node.title.add(url_cleanup(response.url).split('/')[-1])

            # get all paragraphs and their corresponding header
            paragraphs = response.css('p')
            if len(paragraphs) != 0 and paragraphs is not None:
                # search for paragraph title
                for p in paragraphs:
                    # convert p tag to string
                    p_text = ''.join(p.xpath('.//text()').getall()).strip()
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
                            article.title.add(h_text)
                            break
                        parent_div = parent_div.xpath('ancestor::div[1]')
                    if article.title is None:
                        article.title.add("No title found")
                    # Add article to article_set of current_node
                    current_node.articles.add(article)
                    self.data_set.add(article)

            # h2_text = response.css('h2').getall()
            # if len(h2_text) != 0 and h2_text is not None:
            #     h2_set = extract_tag_text(h2_text, 'h2')
            #     data.h2_tags = h2_set
            #     yield {"h2": h2_set}
            #
            # h3_text = response.css('h3').getall()
            # if len(h3_text) != 0 and h3_text is not None:
            #     h3_set = extract_tag_text(h3_text, 'h3')
            #     data.h3_tags = h3_set
            #     yield {"h3": h3_set}

            links = response.css('a::attr(href)').getall()

            # get all links and visit them, also crosslink every connected link with the current page
            for link in links:
                if validators.url(link) and self.allowed_domains[
                    0] in link and not any(
                    banned_word in link for banned_word in self.banned_words):
                    if link not in self.visited_links:
                        self.visited_links.add(link)
                        yield {"link": link}
                        yield response.follow(link, callback=self.parse, meta={'parent': response.url})
                    else:
                        node = get_node(self.data_set, link)
                        if node is not None and current_node.link_from is not None and node.url not in current_node.link_from and node.url != response.url:
                            if node.link_from is None:
                                node.link_from = set()
                            node.link_from.add(response.url)
                            # self.logger.info("Link added: %s", link)
        else:

            # if not website get parent and save current node to parent
            parent_url = current_node.link_parent
            if parent_url is not None:
                parent_node = get_parent_node(self.data_set, parent_url)
                if parent_node is not None:
                    node_class = current_node.label
                    if node_class == "Image":
                        parent_node.images.add(current_node)
                    if node_class == "Video":
                        parent_node.videos.add(current_node)
                    if node_class == "Audio":
                        parent_node.audios.add(current_node)
                    if node_class == "Document":
                        parent_node.documents.add(current_node)

            self.logger.info("Response content isn't text. Skipping sub-link-search for page: %s", response.url)
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
        print("Spider finished")
