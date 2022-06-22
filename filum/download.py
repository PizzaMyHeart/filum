"""Contains the Download class that returns content in a dict given a URL."""

import traceback

from bs4 import BeautifulSoup

from filum.helpers import get_http_response

from filum.parsers.parse_hn import parse_hn
from filum.parsers.parse_reddit import parse_reddit
from filum.parsers.parse_se import parse_se


class Download:
    def __init__(self, url):
        self.url = url
        self.reddit_url = None

    def process_url(self):
        """Given a URL, sets the .site attribute."""

        # Reddit's unofficial API - add a '.json' suffix to any url
        if 'reddit.com' in self.url:
            self.reddit_url = self.url  # Save a copy of the original Reddit URL
            self.url += '.json'
            self.site = 'reddit'
        elif 'news.ycombinator.com' in self.url:
            self.site = 'hn'
        else:
            self.site = 'se'

        return self

    def get_response(self):
        """Makes an HTTP GET request and saves the response object as an attribute."""

        self.response = get_http_response(self.url)
        # Unlike self.url, self.item_permalink will not be mutated.
        # Also to ensure the final redirected url is saved to the database.
        if self.reddit_url:
            self.item_permalink = self.reddit_url
        else:
            self.item_permalink = self.response.url
        return self

    def parse_html(self, raw: str):
        """Creates a BeautifulSoup object from HTML content."""
        # Use the html5lib parser to handle mangled HTML e.g. HN posts.
        self.soup = BeautifulSoup(raw, features='html5lib')
        return self

    def prepare_response(self):
        """Convert Reddit responses to JSON objects, and HN and SE responses to BeautifulSoup objects."""
        if self.site == 'reddit':
            self.response = self.response.json()
        else:
            self.response = self.parse_html(self.response.text)
        return self

    def get_thread(self):
        """Call the corresponding parser for each website."""
        if self.site == 'reddit':
            return parse_reddit(self.response, self.site, self.item_permalink)
        elif self.site == 'hn':
            return parse_hn(self.soup, self.site, self.item_permalink)
        elif self.site == 'se':
            return parse_se(self.soup, self.site, self.url, self.item_permalink)

    def run(self):
        """Wrapper function to run the Download methods in order. Returns a dict."""
        return self.process_url().get_response().prepare_response().get_thread()


hn_url_root = 'https://news.ycombinator.com/item?id=27336584'
hn_url_comment = 'https://news.ycombinator.com/item?id=31451536'
se_url_root = 'https://stats.stackexchange.com/questions/6/the-two-cultures-statistics-vs-machine-learning'
se_url_answer = 'https://stackoverflow.com/questions/15340582/python-extract-pattern-matches/15340666#15340666'
reddit_url_root = 'https://www.reddit.com/r/Python/comments/vhabnp/pep_671_syntax_for_late_bound_function_default/'


def main():
    Download(reddit_url_root).process_url() \
                         .get_response() \
                         .prepare_response() \
                         .get_thread()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
