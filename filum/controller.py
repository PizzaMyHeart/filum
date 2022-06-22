"""Contains the Controller class which integrates database operations with application logic."""

import traceback

from rich.console import Console

from filum.archiver import ArchiveUploader
from filum.config import FilumConfig
from filum.database import Database
from filum.download import Download
from filum.exceptions import ItemAlreadyExistsError
from filum.view import RichView

from logger.logger import create_logger

logger = create_logger()

config = FilumConfig()
config_parser = config.get_config()

console = Console()


class Controller(object):
    def __init__(self):
        self.database = Database()
        self.view = RichView()
        self.archive_uploader = ArchiveUploader()
        self.max_rows_without_pager = config_parser.getint('output', 'max_rows_without_pager')

    def download_thread(self, url):
        return Download(url).run()

    def add_thread(self, thread: dict):
        """Add a discussion thread to the database.

        Inserts the top-level node of a saved thread into the 'ancestors' table,
        and the descendant nodes into the 'desendants' table.

        Args:
            thread: The dictionary returned by the download_thread method.

        Returns:
            None

        Raises:
            ItemAlreadyExistsError: A custom exception to indicate that the thread has already been saved previously.
        """
        try:
            self.database.insert_row(thread['parent_data'], 'ancestors')
            for comment in thread['comment_data']:
                self.database.insert_row(thread['comment_data'][comment], 'descendants')
        except ItemAlreadyExistsError as err:
            console.print(
                f'\n[bold red]This item already exists in your database.[/bold red]\n'
                f'→ [bold cyan]{err.title}[/bold cyan]')
            raise ItemAlreadyExistsError(err.title)  # This should probably raise a new exception instead.
        except Exception:
            traceback.print_exc()

    def update_thread(self, thread: dict):
        ancestor_id = self.database.update_ancestor(thread['parent_data'])
        self.database.delete_descendants(ancestor_id)
        for comment in thread['comment_data']:
            self.database.insert_row(thread['comment_data'][comment], 'descendants')

    def _get_ancestor_id(self, id):
        ancestor_id = dict(self.database.select_one_ancestor(id))
        # print(ancestor_id['id'])

    def push_to_web_archive(self, id: int) -> str:
        """Saves a snapshot of a thread to the Wayback Machine.

        Args:
            id: The thread ID

        Returns:
            web_archive_url: The URL of the saved item.
        """
        permalink = self.get_permalink(id)
        web_archive_url = self.archive_uploader.save_snapshot(permalink)
        self.database.update_web_archive_link(
            item_permalink=permalink,
            web_archive_url=web_archive_url,
            column='web_archive_url',
            table='ancestors')
        return web_archive_url

    def get_permalink(self, id: int) -> str:
        return self.database.select_one_value_from_ancestors(id, 'item_permalink')

    def get_web_archive_url(self, id: int) -> str:
        return self.database.select_one_value_from_ancestors(id, 'web_archive_url')

    def get_tags_of_item(self, id: int) -> str:
        return self.database.select_one_value_from_ancestors(id, 'tags')

    def check_thread_exists(self, id):
        self.database.select_one_ancestor(id)

    def show_all_ancestors(self):
        results = self.database.select_all_ancestors()
        table = self.view.create_table(results)
        if self.database.get_ancestors_length() > self.max_rows_without_pager:
            self.view.filum_print_pager(table)
            return
        self.view.filum_print(table)

    def display_thread(self, id, pager, pager_colours, cond='', where_param=''):
        ancestor_query = self.database.select_one_ancestor(id, cond=cond, where_param=where_param)
        top_level = self.view.create_thread_header(ancestor_query)
        descendants_query = self.database.select_all_descendants(id, cond=cond, where_param=where_param)
        indented = self.view.create_thread_body(descendants_query)

        self.view.display_thread(top_level, indented, pager=pager, pager_colours=pager_colours)

    def delete(self, ancestor):
        self.database.delete_descendants(ancestor)
        self.database.delete_ancestor(ancestor)

    def get_ancestors_length(self):
        return self.database.get_ancestors_length()

    def remove_null(self, list_with_null: list) -> list:
        """Remove null values from a list"""
        return [i for i in list_with_null if i is not None]

    def show_all_tags(self):
        """Display a list of existing tags"""

        rows = self.database.get_all_tags()
        tags = [row[0] for row in rows]
        tags = self.remove_null(tags)
        tags = [tag.split(', ') for tag in tags]
        tags_flattened = set([item for items in tags for item in items])
        self.view.filum_print(f'[bold green]Current tags:[/bold green] {", ".join(tags_flattened)}\n')

    def modify_tags(self, id: int, add=True, **kwargs):
        """Add or delete tags of a top-level item in the "ancestor" table

        Args:
            id: the ID of the item (in consecutive ascending order)
            add: default is to add tags, otherwise delete tags
            **kwargs: user-supplied tags to be added
        """

        current_tags = self.database.get_tags(id)
        if current_tags is not None:
            current_tags = current_tags.split(', ')
        else:
            current_tags = []
        entered_tags = [tag.lower() for tag in kwargs['tags'].split(',')]
        if add:
            # Ignore user-supplied tags that already exist
            new_tags = ', '.join(set(current_tags).union(entered_tags))
        else:
            new_tags = ', '.join([tag for tag in current_tags if tag not in entered_tags])
            if new_tags == '':
                new_tags = None
        self.database.update_tags(id, new_tags)

    def search(self, column, searchstr):
        results = self.database.search(column, searchstr)
        table = self.view.create_table(results)
        self.view.filum_print(table)

    def reset_config_to_default(self):
        config.get_config(reset=True)


if __name__ == '__main__':
    c = Controller()
    c._get_ancestor_id(1)
