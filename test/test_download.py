import pathlib
import unittest

from bs4 import BeautifulSoup
from filum.download import Download

html_fp = pathlib.Path(__file__).parent.resolve() / 'test_se.html'

with open(html_fp) as f:
    html_se = f.read()


class TestDownload(unittest.TestCase):
    def setUp(self):
        self.url_reddit = 'https://www.reddit.com/r/boardgames/comments/utkslk/tiny_epic_which_one_would_you_recommend/'
        self.url_hn = 'https://news.ycombinator.com/item?id=31707163'
        self.url_se = 'https://stackoverflow.com/questions/46098852/best-practices-python-classes'

    def test_process_url_reddit(self):
        d = Download(self.url_reddit)
        d.process_url()
        self.assertEqual(
            d.url,
            'https://www.reddit.com/r/boardgames/comments/utkslk/tiny_epic_which_one_would_you_recommend/.json'
            )
        self.assertEqual(d.site, 'reddit')

    def test_process_url_hn(self):
        d = Download(self.url_hn)
        d.process_url()
        self.assertEqual(d.url, self.url_hn)
        self.assertEqual(d.site, 'hn')

    def test_process_url_se(self):
        d = Download(self.url_se)
        d.process_url()
        self.assertEqual(d.url, self.url_se)
        self.assertEqual(d.site, 'se')

    def test_parse_html_creates_soup_from_html(self):
        d = Download('test')
        d.parse_html(html_se)
        self.assertIsInstance(d.soup, BeautifulSoup)


if __name__ == '__main__':
    unittest.main()
