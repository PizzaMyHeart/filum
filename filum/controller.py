import sys
import traceback

from rich.console import Console

from filum.download import Download
from filum.database import ItemAlreadyExistsError

console = Console()


class Controller(object):
    def __init__(self, database, view):
        self.database = database
        self.view = view

    def download_thread(self, url):
        return Download(url).run()

    def add_thread(self, thread):
        try:
            self.database.insert_row(thread['parent_data'], 'ancestors')
            for comment in thread['comment_data']:
                self.database.insert_row(thread['comment_data'][comment], 'descendants')
        except ItemAlreadyExistsError:
            # TODO: Allow updating of existing thread
            print('This item already exists in your database.')
            sys.exit(0)
        except Exception:
            traceback.print_exc()

    def show_all_ancestors(self):
        results = self.database.select_all_ancestors()
        table = self.view.create_table(results)
        self.view.filum_print(table)

    def display_thread(self, id, pager, pager_colours):
        columns = ('row_id', 'num', 'permalink', 'author', 'posted_timestamp',
                   'score', 'body', 'title')

        ancestor_query = self.database.select_one_ancestor(columns, id)
        top_level = self.view.create_thread_header(ancestor_query)

        descendants_query = self.database.select_all_descendants(id)
        indented = self.view.create_thread_body(descendants_query)

        self.view.display_thread(top_level, indented, pager=pager, pager_colours=pager_colours)

    def delete(self, ancestor):
        self.database.delete(ancestor)

    def get_ancestors_length(self):
        return self.database.get_ancestors_length()
