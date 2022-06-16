"""Contains helper functions for the filum application."""

import re
from collections.abc import KeysView
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter, Retry
from markdownify import markdownify as md


def bs4_to_md(soup):
    return md(str(soup), heading_style='ATX')


def html_to_md(html):
    # TODO: Show full hyperlinks (hn truncates these)
    return md(md(html, heading_style='ATX'), heading_style='ATX')


def root_url(url):
    """Return the first part of the URL until and including '.com'"""
    p = re.compile(r'https://.+\.com')
    return p.search(url).group(0)


def current_timestamp():
    return datetime.timestamp(datetime.now())


def iso_to_timestamp(time):
    return datetime.fromisoformat(time).timestamp()


def timestamp_to_iso(timestamp):
    return datetime.fromtimestamp(timestamp).isoformat(sep=' ', timespec='seconds')


def qmarks(sequence: KeysView) -> str:
    """Get a qmark SQL placeholder of arbitrary length."""
    return ', '.join(['?']*len(sequence))


def get_http_response(url: str) -> requests.Response:
    """Makes an HTTP GET request and returns the response object.

    Retries a total of 5 times if unsuccessful.

    Args:
        url: A URL string

    Returns:
        A requests.Response object
    """

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0',
        'dnt': '1',
        'accept-encoding': 'gzip, deflate, br',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.5'}

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=5)
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    return session.get(url, headers=headers)
