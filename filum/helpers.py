import re
from collections.abc import KeysView
from datetime import datetime

from markdownify import markdownify as md


def bs4_to_md(soup):
    return md(str(soup), heading_style='ATX')


def html_to_md(html):
    # TODO: Show full hyperlinks (hn truncates these)
    return md(md(html, heading_style='ATX'), heading_style='ATX')


def root_url(url):
    '''Return the first part of the URL until and including ".com"
    '''
    p = re.compile(r'https://.+\.com')
    return p.search(url).group(0)


def current_timestamp():
    return datetime.timestamp(datetime.now())


def iso_to_timestamp(time):
    return datetime.fromisoformat(time).timestamp()


def timestamp_to_iso(timestamp):
    return datetime.fromtimestamp(timestamp).isoformat(sep=' ', timespec='seconds')


def qmarks(sequence: KeysView) -> str:
    'Get a qmark SQL placeholder of arbitrary length.'
    return ', '.join(['?']*len(sequence))
