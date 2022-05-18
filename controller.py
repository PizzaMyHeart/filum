from models import Model_db
from download import Download
import pprint
import traceback

import argparse

parser = argparse.ArgumentParser(description='Archive discussion threads')

parser.add_argument('--add', dest='url', help='add a URL')
parser.add_argument('--list', action='store_true', help='show all saved posts')
parser.add_argument('--list-descendants', dest='ancestor')
args = parser.parse_args()

print(args)


class Controller(object):
    def __init__(self, model):
        self.model = model
        

    def download_thread(self, url):
        return Download(url).main()

    def add_thread(self, values, table_name):
        try:
            self.model.insert_row(values, table_name)
        except Exception as err:
            traceback.print_exc()

    def show_all_ancestors(self):
        results = self.model.select_all_ancestors()
        print(results)

    def show_all_descendants(self, ancestor):
        results = self.model.select_all_descendants(ancestor)
        print(results)


def main():
    c = Controller(Model_db())
    if args.url:
        thread = c.download_thread(args.url)
        values = (
            thread['parent_metadata']['id'], 
            thread['parent_metadata']['title'],
            thread['parent_metadata']['timestamp'],
            thread['parent_metadata']['permalink'],
            thread['parent_metadata']['num_comments'],
            thread['parent_metadata']['author'],
            thread['parent_metadata']['source']
            )
        c.add_thread([values], 'ancestors')
        comments = []
        for id, comment in thread['comments'].items():
            comments.append((
                comment['ancestor_id'],
                id,
                comment['author'],
                comment['author_id'],
                comment['depth'],
                comment['downvotes'],
                comment['is_submitter'],
                comment['parent_id'],
                comment['path'],
                comment['permalink'],
                comment['score'],
                comment['text'],
                comment['timestamp'],
                comment['upvotes']
            ))
        #pprint.pprint(comments)
        c.add_thread(comments, 'descendants')      

    elif args.list:
        c.show_all_ancestors()


    elif args.ancestor:
        c.show_all_descendants(args.ancestor)
        

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        traceback.print_exc()
