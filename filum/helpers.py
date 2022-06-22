"""Contains helper functions for the filum application."""

import re
from collections.abc import KeysView
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter, Retry
from markdownify import markdownify as md


def bs4_to_md(soup):
    return to_md(str(soup))


def html_to_md(html):
    return to_md(html)


def to_md(content):
    return md(content, heading_style='ATX', autolinks=False)


def escape_brackets(text: str) -> str:
    """Escape brackets that otherwise result in invalid Markdown.

    If a pair of brackets do not immediately precede a pair of parentheses
    (which would denote a Markdown hyperlink), then this function escapes the
    brackets to ensure the hyperlinks adjacent to them are rendered correctly.

    e.g.\n
    [1]: [Example](https://example.com) - the hyperlink will not be rendered
    correctly unless the brackets in '[1]' are escaped.

    Args:
        text: A Markdown-formatted string

    Returns:
        The string with correctly escaped brackets
    """
    # Negative lookahead assertion to match brackets
    # that aren't immediately preceding a pair of parentheses.
    # Creates three capture groups: one for each bracket, and
    # one for whatever is within the brackets.
    # Ignore if surrounded by backticks (indicating a code block).
    pattern = re.compile(
        r'(?<!`)'   # -ve lookbehind for opening backtick
        r'(\[)'     # match opening bracket
        r'(.*)'     # match anything sandwiched by the brackets
        r'(\])'     # match closing bracket
        r'(?!\()'   # -ve lookahead for opening parenthesis
        r'(?!`)'    # -ve lookahead for closing backtick
        )

    return re.sub(pattern, r'\\\1\2\\\3', text)


def sanitise_text(text: str) -> str:
    text = str(text)
    return escape_brackets(text)


def add_comment_author_to_title(author: str, title: str) -> str:
    """Append comment author's name to title.

    If the top-level saved item is not the root node,
    then append the author's name to indicate it is a comment.
    """
    return f'{author} on: {title}'


def get_root_url(url):
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
