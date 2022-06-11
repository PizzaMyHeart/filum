import pathlib
import unittest

from bs4 import BeautifulSoup
from filum.download import Download

html_fp = pathlib.Path(__file__).parent.resolve() / 'test_se.html'

with open(html_fp) as f:
    html_se = f.read()


class TestDownload(unittest.TestCase):
    def test_process_url_reddit(self):
        url = 'https://www.reddit.com/r/programming/comments/2jb24/ask_reddit_unit_testing_is_great_but_how_do_you/'
        d = Download(url)
        d.process_url()
        self.assertEqual(
            d.url,
            'https://www.reddit.com/r/programming/comments/2jb24/ask_reddit_unit_testing_is_great_but_how_do_you/.json'
            )
        self.assertEqual(d.site, 'reddit')

    def test_process_url_hn(self):
        url = 'https://news.ycombinator.com/item?id=31707163'
        d = Download(url)
        d.process_url()
        self.assertEqual(d.url, url)
        self.assertEqual(d.site, 'hn')

    def test_process_url_se(self):
        url = 'https://stackoverflow.com/questions/46098852/best-practices-python-classes'
        d = Download(url)
        d.process_url()
        self.assertEqual(d.url, url)
        self.assertEqual(d.site, 'se')

    def test_parse_html_creates_soup_from_html(self):
        d = Download('test')
        d.parse_html(html_se)
        self.assertIsInstance(d.soup, BeautifulSoup)


if __name__ == '__main__':
    unittest.main()
