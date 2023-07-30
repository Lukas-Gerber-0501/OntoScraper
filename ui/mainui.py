import tkinter as tk

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from graph.neo4j_graph import generate_graph
from scraper.scraper import WebsiteScraper
from scraper.scraper_utils import trim_urls


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper")
        self.root.geometry("300x200")

        self.url_label = tk.Label(self.root, text="Website URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(self.root)
        self.url_entry.pack()

        self.username_label = tk.Label(self.root, text="Neo4j Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        self.password_label = tk.Label(self.root, text="Neo4j Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        self.start_button = tk.Button(self.root, text="Start", command=self.start_scraping)
        self.start_button.pack()

    def start_scraping(self):
        url = self.url_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        trim_res = trim_urls([url])

        process = CrawlerProcess(get_project_settings())
        process.crawl(WebsiteScraper, websites=[url], allowed=trim_res)
        process.start()

        data_set = WebsiteScraper.get_data_set()

        generate_graph(data_set, username, password)