from models import Model_db, ItemAlreadyExistsError
from download import Download
import traceback
from rich.pretty import pprint
from rich.console import Console
import argparse
from view import CommentView
import sys

console = Console()



class Controller(object):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        

    def download_thread(self, url):
        return Download(url).run()

    def add_thread(self, thread):
        try:
            self.model.insert_row(thread['parent_data'], 'ancestors')
            for comment in thread['comment_data']:
                self.model.insert_row(thread['comment_data'][comment], 'descendants')
        except ItemAlreadyExistsError:
            # TODO: Allow updating of existing thread
            print('This item already exists in your database.')
            sys.exit(0)
        except Exception as err:
            traceback.print_exc()


    def show_all_ancestors(self):
        results = self.model.select_all_ancestors()
        self.view.display_table(results)
    
    def show_one_ancestor(self, id):
        columns = ('row_id', 'num', 'permalink', 'author', 'posted_timestamp', 'score', 'body', 'title')
        results = self.model.select_one_ancestor(columns, id)
        self.view.display_top_level(results)

    def show_all_descendants(self, ancestor):
        results = self.model.select_all_descendants(ancestor)
        self.view.display_indented(results)
        
    def delete(self, ancestor):
        self.model.delete(ancestor)

