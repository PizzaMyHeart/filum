import re

from filum.exceptions import InvalidThreadId, InvalidUrl
from filum.controller import Controller

c = Controller()

url_pattern_reddit = re.compile(r'https:\/\/www.reddit.com\/r\/.+\/comments\/')
url_pattern_so = re.compile(r'https:\/\/stackoverflow.com\/((questions)|(q)|(a))')
url_pattern_se = re.compile(r'https:\/\/.+\.stackexchange.com\/((questions)|(q)|(a))')
url_pattern_hn = re.compile(r'https:\/\/news.ycombinator.com\/item')

# TODO: Add patterns for other SE sites such as Ask Ubuntu, Server Fault,
# Super User

url_patterns = [
    re.compile(r'https:\/\/www.reddit.com\/r\/.+\/comments\/'),
    re.compile(r'https:\/\/news.ycombinator.com\/item'),
    re.compile(r'https:\/\/.+\.stackexchange.com\/((questions)|(q)|(a))'),
    re.compile(
        r'https:\/\/((stackoverflow)'
        r'|(serverfault)'
        r'|(askubuntu)'
        r'|(superuser)'
        r').com\/((questions)|(q)|(a))'),
]


# Validation functions


def is_valid_url(url: str) -> bool:
    '''Checks whether the user-supplied URL belongs to
    Reddit, HN, or SE.
    '''
    for pattern in url_patterns:
        if pattern.match(url.strip().lower()):
            return True
    raise InvalidUrl


def is_valid_id(id: int) -> bool:
    '''Checks whether the user-supplied thread ID is
    valid'''
    if type(id) == int:
        if id > 0:
            return True
    raise InvalidThreadId


def id_exists(id: int) -> bool:
    valid_id_message = 'Please enter a valid thread label (+ve int). Run `filum show` to see a list of thread labels.'
    ancestors_length = c.get_ancestors_length()
    if id <= ancestors_length:
        return True
    print(f'Thread no. {id} does not exist.\n{valid_id_message}')
    return False
