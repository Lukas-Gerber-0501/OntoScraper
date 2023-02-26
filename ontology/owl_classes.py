# class Data:
#     def __init__(self,
#                  link_from=None,
#                  direct_parent=None,
#                  url=None,
#                  title=None,
#                  h2_tags=None,
#                  h3_tags=None,
#                  paragraphs=None,
#                  documents=None
#                  ):
#         self.link_from = link_from
#         self.direct_parent = direct_parent
#         self.url = url
#         self.title = title
#         self.h2_tags = h2_tags
#         self.h3_tags = h3_tags
#         self.paragraphs = paragraphs
#         self.documents = documents


# parent class for all pages
class Page:
    def __init__(self,
                 title=None,
                 url=None,
                 direct_parent=None,
                 link_from=None,
                 link_parent=None
                 ):
        self.title = title
        self.url = url
        self.direct_parent = direct_parent
        self.link_from = link_from
        self.link_parent = link_parent


# class for webpage
class Webpage(Page):
    label = "Webpage"

    def __init__(self,
                 title=None,
                 url=None,
                 direct_parent=None,
                 articles=None,
                 images=None,
                 documents=None,
                 link_from=None,
                 link_parent=None
                 ):
        super().__init__(title, url, direct_parent, link_from, link_parent)
        self.articles = articles
        self.images = images
        self.documents = documents


# class for images on webpage
class Image(Page):
    label = "Image"

    def __init__(self,
                 title=None,
                 url=None,
                 direct_parent=None,
                 image_extension=None,
                 link_from=None,
                 link_parent=None
                 ):
        super().__init__(title, url, direct_parent, link_from, link_parent)
        self.image_extension = image_extension


# class for documents on webpage
class Document(Page):
    label = "Document"

    def __init__(self,
                 title=None,
                 url=None,
                 direct_parent=None,
                 document_extension=None,
                 link_from=None,
                 link_parent=None
                 ):
        super().__init__(title, url, direct_parent, link_from, link_parent)
        self.document_extension = document_extension


# class for articles on webpage
class Article(Page):
    label = "Article"

    def __init__(self,
                 title=None,
                 url=None,
                 direct_parent=None,
                 content=None,
                 link_from=None,
                 link_parent=None
                 ):
        super().__init__(title, url, direct_parent, link_from, link_parent)
        self.content = content


# class for videos on webpage
class Video(Page):
    label = "Video"

    def __init__(self,
                 title=None,
                 url=None,
                 direct_parent=None,
                 video_extension=None,
                 link_from=None,
                 link_parent=None
                 ):
        super().__init__(title, url, direct_parent, link_from, link_parent)
        self.video_extension = video_extension


# class for audio on webpage
class Audio(Page):
    label = "Audio"

    def __init__(self,
                 title=None,
                 url=None,
                 direct_parent=None,
                 audio_extension=None,
                 link_from=None,
                 link_parent=None
                 ):
        super().__init__(title, url, direct_parent, link_from, link_parent)
        self.audio_extension = audio_extension


# class for everything else on webpage
class Other(Page):
    label = "Other"

    def __init__(self,
                 title=None,
                 url=None,
                 direct_parent=None,
                 link_from=None,
                 link_parent=None
                 ):
        super().__init__(title, url, direct_parent, link_from, link_parent)
