import os

import validators
from bs4 import BeautifulSoup

from ontology.enums import ImageTypes, AudioTypes, VideoTypes, DocumentTypes, OtherTypes
from ontology.owl_classes import Webpage, Image, Document, Other, Video, Audio

enum_dict = {
    DocumentTypes: Document,
    ImageTypes: Image,
    VideoTypes: Video,
    AudioTypes: Audio
}


def get_page_type(is_webpage, url):
    print(is_webpage, url)

    current_node = None

    # check if url is a webpage
    if is_webpage:
        current_node = Webpage(title=set(), url=url, link_from=set(), documents=set(), images=set(), articles=set())
    else:

        extension = url.split('.')[-1]
        file_name = os.path.basename(url)
        file_name = file_name.split('.')
        file_name = file_name[-2]

        for enum_class, obj_class in enum_dict.items():
            if any(url.endswith(ext) for ext in [m.value for m in enum_class]):
                current_node = obj_class(url=url, **{obj_class.__name__.lower() + '_extension': extension},
                                         link_from=set(), title=set())
                break
            else:
                current_node = Other(url=url, link_from=set())

        # add title if not webpage
        current_node.title.add(file_name)

    parent = get_parent(url)
    if validators.url(parent):
        current_node.direct_parent = parent

    return current_node


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


def get_parent(url):
    if url[-1] == '/':
        url = url[:-1]
    url_parts = url.split('/')
    return '/'.join(url_parts[:-1])


def is_text(content_type):
    return 'text' in content_type


def get_node(data_set, url):
    for node in data_set:
        if node.url == url:
            return node
    return None


def get_parent_node(data_set, url):
    for node in data_set:
        if node.url == url and node.label == "Webpage":
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
