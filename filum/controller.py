import sys
import traceback

from rich.console import Console

from filum.download import Download
from filum.database import Database, ItemAlreadyExistsError
from filum.view import RichView

console = Console()


class Controller(object):
    def __init__(self):
        self.database = Database()
        self.view = RichView()

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

    def display_thread(self, id, pager, pager_colours, cond='', **kwargs):
        columns = ('row_id', 'num', 'permalink', 'author', 'posted_timestamp',
                   'score', 'body', 'title')
        print('cond:', cond)
        ancestor_query = self.database.select_one_ancestor(columns, id, cond=cond, **kwargs)
        top_level = self.view.create_thread_header(ancestor_query)

        descendants_query = self.database.select_all_descendants(id, cond=cond, **kwargs)
        indented = self.view.create_thread_body(descendants_query)

        self.view.display_thread(top_level, indented, pager=pager, pager_colours=pager_colours)

    def delete(self, ancestor):
        self.database.delete(ancestor)

    def get_ancestors_length(self):
        return self.database.get_ancestors_length()

    def modify_tags(self, id: int, add=True, **kwargs):
        '''Add or delete tags of a top-level item in the "ancestor" table
        :param int id: The ID of the item (in consecutive ascending order)
        :param list tags: User-supplied tags to be added
        '''
        current_tags = self.database.get_tags(id)
        if current_tags is not None:
            current_tags = current_tags.split(', ')
        else:
            current_tags = []
        entered_tags = kwargs['tags']
        print('Current tags: ', current_tags)
        print('User entered these tags: ', entered_tags)
        print(add)
        if add:
            # Ignore user-supplied tags that already exist
            new_tags = ', '.join(set(current_tags).union(entered_tags))
            self.database.update_tags(id, new_tags)

    def search(self, searchstr):
        print(searchstr)
        results = self.database.search_tag(searchstr)
        table = self.view.create_table(results)
        self.view.filum_print(table)



