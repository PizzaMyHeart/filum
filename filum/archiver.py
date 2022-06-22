"""Save pages to archive.ph and archive.org (Wayback Machine)"""
# TODO: Optional integration with archivenow (https://github.com/oduwsdl/archivenow)

from filum.exceptions import WaybackMachineError
from filum.helpers import get_http_response


class ArchiveUploader:
    def __init__(self):
        self.archive_url = 'https://web.archive.org/save/'

    def save_snapshot(self, page_url) -> str:
        url = self.archive_url + page_url
        response = get_http_response(url)
        if response.status_code != 200:
            raise WaybackMachineError
        # link = self._get_archived_link(response)  # Maybe unnecessary
        link = response.url
        return link

    def _get_archived_link(self, response: object) -> str:
        """Helper function that takes the HTTP response object from the GET request to save
        a page to the Wayback Machine, and returns the corresponding Memento URL.
        """
        if not response.headers.get('link'):
            raise WaybackMachineError
        for i in [i for i in response.headers['link'].split(', <')]:
            if 'rel="memento"' in i:
                memento_string = i
        for i in memento_string.split('; '):
            if 'http' in i:
                link = i.strip('<>')
        return link
