import mimetypes
import os
import uuid

import pdfplumber
import requests
import validators
from bs4 import BeautifulSoup

from generics.constants import WEBPAGE, ARTICLE, NO_TITLE, PDF
from ontology.owl_classes import Webpage, Data


def create_node(is_webpage, url):
    if is_webpage:
        current_node = Webpage(url=url, uuid=str(uuid.uuid4()))
    else:
        mime_type, extension = get_mime_type(url)
        file_name = get_file_name(url)
        current_node = Data(label=mime_type, url=url, extension=extension, uuid=str(uuid.uuid4()))
        current_node.title.add(clean_text(file_name))

        if extension == PDF and mime_type == "application":
            current_node.content = fetch_pdf_content(url)

    return current_node


def fetch_pdf_content(url):
    # fetch pdf and open
    response = requests.get(url, stream=True)
    with open('temp.pdf', 'wb') as f:
        f.write(response.content)

    # read pdf text content
    content = ""
    with pdfplumber.open('temp.pdf') as pdf:
        for page in pdf.pages:
            page_content = page.extract_text()
            content += page_content + "\n"

    # remove empty lines
    content = '\n'.join(line for line in content.splitlines() if line)

    return clean_text(content)


def extract_tag_text(html_array, tag_type):
    result_set = set()

    for html in html_array:
        soup = BeautifulSoup(html, 'html.parser')
        h = soup.find(tag_type)
        result_set.add(h.get_text().replace('\n', ' '))

    return result_set


def trim_urls(urls):
    # trim urls to domain name
    trimmed_urls = []
    for url in urls:
        trimmed_urls.append(url.split('www.')[1])
    return trimmed_urls


def get_url_parent(url):
    if url[-1] == '/':
        url = url[:-1]
    url_parts = url.split('/')
    result = '/'.join(url_parts[:-1])
    if validators.url(result):
        return result
    return None


def is_text(content_type):
    return 'text' in content_type


def get_node(data_set, url):
    for node in data_set:
        if node.url == url:
            return node
    return None


def get_parent_node(data_set, url):
    for node in data_set:
        if node.url == url and node.label == WEBPAGE:
            return node
    return None


def url_cleanup(url):
    if url and url.endswith("/"):
        return url[:-1]
    return url


def url_builder(sub_url, url, parent_url):
    if sub_url and sub_url.startswith("/") and len(sub_url) > 1 and not url.startswith(parent_url):
        return url + sub_url
    return sub_url


def get_mime_type(filename):
    mime_type, encoding = mimetypes.guess_type(filename)
    if mime_type is not None:
        extension = mimetypes.guess_extension(mime_type)
        return mime_type.split("/")[0], extension
    return None, None


def get_file_name(url):
    file_name = os.path.basename(url)
    file_name = file_name.split('.')
    file_name = file_name[-2]
    return file_name


def handle_matchting_articles(data_set, article):
    for node in data_set:
        if node.title == NO_TITLE or node.label != ARTICLE:
            continue
        if node.title == article.title and node.parent_url == article.parent_url:
            node.matching_title_urls.add(article.url)
            article.matching_title_urls.add(node.url)


def check_content_on_matching_title(data_set, title, content):
    if not title or NO_TITLE in title:
        return False

    # iterate over all articles already in set and check for same title
    for node in data_set:
        if node.title == title:
            if len(content) > 0:
                node.content = " ".join([node.content, content])
            return True
    return False


def clean_text(text):
    res = text.replace("'", "")
    res = res.replace('"', '')
    return res
