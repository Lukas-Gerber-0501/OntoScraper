from dataclasses import dataclass, field
from typing import Optional

from generics.constants import WEBPAGE, ARTICLE


# parent class for all pages
@dataclass(kw_only=True)
class Information:
    uuid: Optional[str] = None
    title: set = field(default_factory=set)
    url: Optional[str] = None
    sibling_of_urls: set = field(default_factory=set)

    def __hash__(self):
        return hash(self.url)


# generic class for data on webpage
@dataclass(kw_only=True)
class Data(Information):
    label: Optional[str] = None
    extension: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    file_size: Optional[str] = None
    other_information: Optional[str] = None

    def __hash__(self):
        return super().__hash__()


# class for articles on webpage
@dataclass(kw_only=True)
class Article(Information):
    mimetype: str = "text"
    label: str = ARTICLE
    content: Optional[str] = None
    matching_title_urls: set[str] = field(default_factory=set)
    parent_url: Optional[str] = None

    def __hash__(self):
        return super().__hash__()


# class for webpage
@dataclass(kw_only=True)
class Webpage(Information):
    label: str = WEBPAGE
    parent_of_webpages: set = field(default_factory=set)
    articles: set[Article] = field(default_factory=set)
    data: set[Data] = field(default_factory=set)

    def __hash__(self):
        return super().__hash__()
