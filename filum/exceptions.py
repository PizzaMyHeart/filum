"""Custom exceptions."""


# Custom exceptions for input validation


class InvalidInputError(Exception):
    """Exception for errors due to invalid user input"""


class InvalidUrl(InvalidInputError):
    """Invalid URL"""
    def __init__(self):
        self.message = ('Please enter a URL prefixed with "https://".\n'
                        'Supported sites: Reddit, Hacker News, Stack Exchange')
        super().__init__(self.message)


class InvalidThreadId(InvalidInputError):
    """Invalid thread ID"""
    def __init__(self):
        self.message = ('Please enter a valid thread ID (positive integer). '
                        'Run `filum show` to see a list of thread IDs.')
        super().__init__(self.message)

# Custom exceptions for database operations


class ItemAlreadyExistsError(Exception):
    """Custom exception that is raised when attempting
    to add an item with a permalink that already exists in the database."""
    def __init__(self, title):
        self.title = title

# Custom exceptions to handle unsuccessful HTTP requests


class FailedRequest(Exception):
    pass


class WaybackMachineError(Exception):
    """Catch-all exception for Wayback Machine requests.

    Raised when the HTTP status code is anything other than 200.
    """
    pass
