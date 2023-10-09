import re
import tkinter as tk
from time import sleep
from tkinter import ttk, messagebox

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from database.neo4j_graph import connect_to_neo4j, process_data
from scraper.scraper import WebsiteScraper
from scraper.scraper_utils import trim_urls


class Application:
    def __init__(self, window):
        self.window = window

        # create form elements
        self.url_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.neo4j_uri_var = tk.StringVar()
        self.status_var = tk.StringVar()

        ttk.Label(window, text='Website-URL', anchor='w').grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        ttk.Entry(window, textvariable=self.url_var).grid(row=0, column=1, sticky='ew', padx=10, pady=10)

        ttk.Label(window, text='Neo4j-Username', anchor='w').grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        ttk.Entry(window, textvariable=self.username_var).grid(row=1, column=1, sticky='ew', padx=10, pady=10)

        ttk.Label(window, text='Neo4j-Password', anchor='w').grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        ttk.Entry(window, textvariable=self.password_var, show='*').grid(row=2, column=1, sticky='ew', padx=10, pady=10)

        ttk.Label(window, text='Neo4j-Uri', anchor='w').grid(row=3, column=0, sticky='ew', padx=10, pady=10)
        ttk.Entry(window, textvariable=self.neo4j_uri_var).grid(row=3, column=1, sticky='ew', padx=10, pady=10)

        self.submit_button = ttk.Button(window, text='Submit', command=self.submit)
        self.submit_button.grid(row=4, columnspan=2, column=0, pady=10)

        close_button = ttk.Button(window, text='Close', command=self.close)
        close_button.grid(row=5, columnspan=2, column=0, pady=10)

        status_label = tk.Label(window, textvariable=self.status_var)
        status_label.grid(row=7, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

    def submit(self):
        self.submit_button.config(state='disabled')

        url = self.url_var.get()
        username = self.username_var.get()
        password = self.password_var.get()
        neo4j_uri = self.neo4j_uri_var.get()

        # validate input
        if not url or not username or not password or not neo4j_uri:
            messagebox.showerror("Error", "All fields are required")
            self.submit_button.config(state='normal')
            return

        # validate URL
        if not re.match(r'^https?://www\.[^/]+$', url):
            messagebox.showerror("Error",
                                 "Invalid URL, has to start with http://www or https://www, no trailing / allowed")
            self.submit_button.config(state='normal')
            return

        self.status_var.set("OntoScraper starting!")

        self.run_scraper(url, username, password, neo4j_uri)

    def run_scraper(self, url, username, password, neo4j_uri):
        # trim input url for use
        trim_url = trim_urls([url])

        # information retrieval and structuring
        data_set = retrieve_information(trim_url, url)
        write_data(data_set, username, password, neo4j_uri)
        self.submit_button.config(state='normal')
        self.status_var.set("OntoScraper finished!")

    def close(self):
        self.window.destroy()


def retrieve_information(trim_url, website):
    # start scraper/crawler with given url
    process = CrawlerProcess(get_project_settings())
    process.crawl(WebsiteScraper, websites=[website], allowed=trim_url)
    process.start()
    data = WebsiteScraper.get_data_set()
    process.stop()
    # get dataset from retrieval operation
    return data


def write_data(data_set, user, pw, uri):
    # connect to neo4j database
    session = connect_to_neo4j(user, pw, uri)
    print("Connected to Neo4j (" + uri + ") with user: " + user)

    # generate cypher queries and fill database
    process_data(session, data_set)


def main():
    # create window
    window = tk.Tk()
    window.title("OntoScraper")
    window.geometry("600x300")
    window.grid_columnconfigure(1, weight=1)
    style = ttk.Style(window)
    style.theme_use('clam')
    app = Application(window)
    # start the tkinter main loop
    window.mainloop()


if __name__ == "__main__":
    main()
