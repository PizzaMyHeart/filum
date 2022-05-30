from datetime import datetime
import re
from markdownify import markdownify as md

def bs4_to_md(soup):
    return md(str(soup))

def html_to_md(html):
    # TODO: Show full hyperlinks (hn truncates these)
    return md(md(html))

def root_url(url):
    p = re.compile(r'https://.+\.com')
    return p.search(url).group(0)

def current_timestamp():
    return datetime.timestamp(datetime.now())

def iso_to_timestamp(time):
    return datetime.fromisoformat(time).timestamp()

def timestamp_to_iso(timestamp):
    return datetime.fromtimestamp(timestamp).isoformat(sep=' ', timespec='seconds')