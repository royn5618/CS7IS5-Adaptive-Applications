from application.config_import import get_private_config
from application.retrieval.data_retrieval import NewsRetrieval
import requests
import logging
import textrazor
import operator

class TextExtractor(object):
    """Wrapper for data retrieval functionality."""

    def __init__(self):
        """Empty, to be implemented by sub class."""
        pass

    def get_json_from_url(self, url):
        """Get the json response from a url, log if error."""
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(
                "Response {} from server "
                "when accessing url {}".format(
                    response.status_code, url))
            return None
        return response.json(encoding='utf-8')

    def get_news_statistics(self, text):
        """Retrieve the list of topics(keywords) from the API for the given text."""
        textrazor.api_key = self.textrazor_apikey
        client = textrazor.TextRazor(extractors=["topics","entities"])
        client.set_classifiers(["textrazor_newscodes"])
        response = client.analyze(text)
        if len(response.topics())==0 and len(response.entities())==0 and len(response.categories())==0:
            return None
        return response

    def get_news_categories(self, response):
        categories = ["economy, business and finance", "politics", "science and technology",
                     "arts, culture and entertainment", "sport", "misc"]
        news_type = []
        for category in response.categories():
            if ("general" in category.label or "sport" in category.label):
                for cat in categories:
                    if cat in category.label:
                        news_type.append(cat)
        if not news_type:
            news_type.append("misc")
        return(set(news_type))

    def get_news_topics(self, response):
        dict_topics = {}
        for topic in response.topics():
            dict_topics[topic.label] = topic.score
        top_topics = sorted(dict_topics, key=dict_topics.get, reverse=True)[:10]
        return(top_topics)

    def get_news_entities(self, response):
        dict_entities = {}
        for entity in response.entities():
            dict_entities[entity.id] = entity.relevance_score
        top_entities = sorted(dict_entities, key=dict_entities.get, reverse=True)[:10]
        return(top_entities)

    # def get_news_topics(self, text):
    #     """Retrieve the list of topics(keywords) from the API for the given text."""
    #     textrazor.api_key = self.textrazor_apikey
    #     client = textrazor.TextRazor(extractors=["topics"])
    #     client.set_classifiers(["textrazor_newscodes"])
    #     response = client.analyze(text)
    #     return response.categories()
    #
    # def get_news_entities(self, text):
    #     """Retrieve the list of topics(keywords) from the API for the given text."""
    #     textrazor.api_key = self.textrazor_apikey
    #     client = textrazor.TextRazor(extractors=["topics"])
    #     client.set_classifiers(["textrazor_newscodes"])
    #     response = client.analyze(text)
    #     return response.categories()

class Extraction(TextExtractor):
    """Class Responsible to do analysis on news data."""

    def __init__(self):
        """Retrieve text razor api key."""
        super(TextExtractor, self).__init__()
        self.textrazor_apikey = get_private_config()["textrazorapi_key2"]

    def check_extraction_using_key(self):
        """
        Verify that the key is working by listing.

        the keywords information. It takes the second news from the news fetched
        from NewsApi and do extraction on News Description. Only topics with high
        relevance scores are listed. This should be stored in db.
        """
        news = NewsRetrieval()
        news_headline = news.get_news_headlines()
        print(news_headline['articles'][1]['description'])
        keywords = super().get_news_topics(news_headline['articles'][1]['description'])
        for keyword in sorted(keywords,key=operator.attrgetter('score'), reverse=True)[:5]:
                print(keyword.label)
        if keywords is None:
            return False
        return True