from datetime import datetime
import re
from markdownify import markdownify as md

def bs4_to_md(soup):
    return md(str(soup)).replace('\n', '')

def html_to_md(html):
    return md(html).replace('\n', '')

def root_url(url):
    p = re.compile(r'https:\/\/.+\.com\/')
    return p.search(url).group(0)

def current_timestamp():
    return datetime.timestamp(datetime.now())