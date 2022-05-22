from models import Model_db, ItemAlreadyExistsError
from download import Download
import pprint
import traceback
from rich.pretty import pprint
import argparse
from view import CommentView
import sys

parser = argparse.ArgumentParser(description='Archive discussion threads')

parser.add_argument('--add', dest='url', help='add a URL')
parser.add_argument('--list', action='store_true', help='show all saved posts')
parser.add_argument('--list-descendants', dest='ancestor')
args = parser.parse_args()

print(args)


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
        columns = ('row_id','permalink', 'author', 'posted_timestamp', 'score', 'body')
        results = self.model.select_row(columns, 'ancestor', id)
        self.view.display_top_level(results)

    def show_all_descendants(self, ancestor):
        results = self.model.select_all_descendants(ancestor)
        self.view.display_indented(results)
        '''
        for result in results:
            self.view.display_indented(result)
        '''
def main():
    c = Controller(Model_db(), CommentView())
    if args.url:
        thread = c.download_thread(args.url)
        c.add_thread(thread)
            

    elif args.list:
        c.show_all_ancestors()


    elif args.ancestor:
        #c.show_one_ancestor(args.ancestor)
        c.show_all_descendants(args.ancestor)

        

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        traceback.print_exc()
