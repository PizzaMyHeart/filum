import re

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

# Custom exceptions for input validation


class InvalidInputError(Exception):
    '''Exception for errors due to invalid user input'''


class InvalidUrl(InvalidInputError):
    '''Invalid URL'''
    def __init__(self):
        self.message = ('Please enter a URL prefixed with "https://".\n'
                        'Supported sites: Reddit, Hacker News, Stack Exchange')
        super().__init__(self.message)


class InvalidThreadId(InvalidInputError):
    '''Invalid thread ID'''
    def __init__(self):
        self.message = ('Please enter a valid thread ID (positive integer). '
                        'Run `filum all` to see a list of thread IDs.')
        super().__init__(self.message)


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
