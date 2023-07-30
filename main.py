import re
import tkinter as tk
from tkinter import ttk, messagebox

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from graph.neo4j_graph import generate_graph, connect_to_neo4j, disconnect_from_neo4j
from scraper.scraper import WebsiteScraper
from scraper.scraper_utils import trim_urls

uri = "neo4j+s://65f99491.databases.neo4j.io:7687"  # Replace with the URI for your local Neo4j instance
user = "neo4j"  # Replace with your Neo4j username
password = "9aiKUTWKd7kyfn3lPuJBRAMzddJ_Koe5qfkFu4UsnV8"  # Replace with your Neo4j password

# testsites
WIEN = 'https://www.bhakwien22.at'  # reference site with deep structure and multiple nodes
SIA = 'https://www.sigmaiotarhoetaalpha.org'  # small website with deep structure
CPX = 'https://www.compaxdigital.com'  # big website with flat structure
OEH = 'https://www.oeh-mci.at'  #


# testsites that are not working because of site blocks or other reasons
# MCI = 'https://www.mci.edu' (Website split into multiple urls like edu, de, at, ...)
# MEDI = 'https://www.medicubus.at' (Scraper blocking)


def main():
    # create a new tkinter window
    window = tk.Tk()
    window.title("OntoScraper")
    window.geometry("600x300")
    window.grid_columnconfigure(1, weight=1)  # make column stretchable

    # apply the default ttk theme
    style = ttk.Style(window)
    style.theme_use('default')

    # create tkinter variables for form fields
    url_var = tk.StringVar()
    username_var = tk.StringVar()
    password_var = tk.StringVar()
    banned_words_var = tk.StringVar()

    # create form fields with padding and left alignment
    ttk.Label(window, text='Website-URL', anchor='w').grid(row=0, column=0, sticky='ew', padx=10, pady=10)
    ttk.Entry(window, textvariable=url_var).grid(row=0, column=1, sticky='ew', padx=10, pady=10)

    ttk.Label(window, text='Neo4j-Username', anchor='w').grid(row=1, column=0, sticky='ew', padx=10, pady=10)
    ttk.Entry(window, textvariable=username_var).grid(row=1, column=1, sticky='ew', padx=10, pady=10)

    ttk.Label(window, text='Neo4j-Password', anchor='w').grid(row=2, column=0, sticky='ew', padx=10, pady=10)
    ttk.Entry(window, textvariable=password_var, show='*').grid(row=2, column=1, sticky='ew', padx=10, pady=10)

    def submit():
        # get form values
        url = url_var.get()
        username = username_var.get()
        password = password_var.get()
        banned_words = banned_words_var.get().split(',')  # assuming banned words are comma-separated

        # validate form values
        if not url or not username or not password or not banned_words:
            messagebox.showerror("Error", "All fields are required")
            return

        # validate URL
        if not re.match(r'^https?://www\.[^/]+$', url):
            messagebox.showerror("Error", "Invalid URL, has to start with http://www or https://www, no trailing / allowed")
            return

        # run your main logic here
        run_scraper(url, username, password, banned_words)

    # create submit button
    ttk.Button(window, text='Submit', command=submit).grid(row=4, column=1)

    # start the tkinter main loop
    window.mainloop()


def run_scraper(url, username, password, banned_words):
    # trim input url for use
    trim_url = trim_urls([url])

    # information retrieval and structuring
    data_set = retrieve_information(trim_url, url)
    write_data(data_set, username, password)
    print("Information Retrieval System completed!")


def retrieve_information(trim_url, website):
    # start scraper/crawler with given url
    process = CrawlerProcess(get_project_settings())
    process.crawl(WebsiteScraper, websites=[website], allowed=trim_url)
    process.start()

    # get dataset from retrieval operation
    return WebsiteScraper.get_data_set()


def write_data(data_set, user, pw):
    # connect to neo4j database
    session = connect_to_neo4j(user, pw)
    print("Connected to Neo4j (" + uri + ") with user: " + user)

    # generate cypher queries and fill database
    generate_graph(session, data_set)

    # close connection
    disconnect_from_neo4j(session)
    print("Disconnected from Neo4j")


if __name__ == "__main__":
    main()
