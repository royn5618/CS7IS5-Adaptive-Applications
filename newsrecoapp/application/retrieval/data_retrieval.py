from application.config_import import get_private_config
import requests
import logging

class DataRetrieval(object):
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

    def get_news_headlines(self):
        """Retrieve the list of news headlines from the API."""
        url = self.NEWS_URL["headlines"].format(api_key=self.news_apikey)
        return self.get_json_from_url(url)


class NewsRetrieval(DataRetrieval):
    """Class Responsible to retrieve news data."""

    NEWS_URL = dict(
        headlines="https://newsapi.org/v2/top-headlines?"
                "country=ie&"
                "apiKey={api_key:}")

    def __init__(self):
        """Retrieve news api key."""
        super(NewsRetrieval, self).__init__()
        self.news_apikey = get_private_config()["newsapi_key"]

    def check_connectivity_using_key(self):
        """
        Verify that the key is working by listing.

        the news information.
        """
        news = self.get_news_headlines()
        print (news)
        if news is None:
            return False
        return True