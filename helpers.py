from datetime import datetime
import re

def root_url(url):
    p = re.compile(r'https:\/\/.+\.com\/')
    return p.search(url).group(0)

def current_timestamp():
    return datetime.timestamp(datetime.now())