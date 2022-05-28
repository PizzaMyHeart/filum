import argparse
from controller import Controller
from models import Model_db
from view import CommentView



parser = argparse.ArgumentParser(description='Archive discussion threads', prog='filum')

subparsers = parser.add_subparsers(dest='subparser')

parser_add = subparsers.add_parser('add', help='add a URL')
parser_add.add_argument('url', nargs='?', type=str, help='add a URL')
parser_add.set_defaults(parser_add=True)

parser_all = subparsers.add_parser('all', help='show all saved top-level items')
parser_all.set_defaults(parser_all=False)

parser_thread = subparsers.add_parser('thread', help='display a saved thread')
parser_thread.add_argument('id', nargs='?')


parser.add_argument('-i', action='store_true', help='interactive mode')
args = parser.parse_args()


print(args)


c = Controller(Model_db(), CommentView())

def add(url):
    thread = c.download_thread(url)
    c.add_thread(thread)

def show_thread(id):
    c.show_one_ancestor(id)
    c.show_all_descendants(id)

#if args.url:
#    add(args.url)
        

if args.subparser == 'all':
    c.show_all_ancestors()


elif args.subparser == 'thread':
    show_thread(args.id)




            