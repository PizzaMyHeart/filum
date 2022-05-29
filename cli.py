import argparse
from cmd import Cmd
import sys
from xmlrpc.client import Boolean
from controller import Controller
from models import Model_db
from view import CommentView

class FilumShell(Cmd):
    intro = 'filum interactive mode'
    prompt = 'filum > '

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except Exception as err:
            print(err)
            return False
            
    def emptyline(self):
        # Do nothing if an empty line is entered at the prompt
        pass

    def do_add(self, arg):
        if arg == '':
            print('Please supply a URL')
            return False
        add(arg)

    def do_all(self, arg):
        show_all()

    def do_thread(self, arg):
        show_thread(int(arg))

    def do_delete(self, arg):
        delete(int(arg))

    def do_quit(self, arg):
        sys.exit(0)

    def do_EOF(self, arg):
        sys.exit(0)

parser = argparse.ArgumentParser(description='Archive discussion threads', prog='filum')

subparsers = parser.add_subparsers(dest='subparser')

parser_add = subparsers.add_parser('add', help='add a URL')
parser_add.add_argument('url', nargs='+', type=str, help='add a URL')
parser_add.set_defaults(parser_add=True)

parser_all = subparsers.add_parser('all', help='show all saved top-level items')
parser_all.set_defaults(parser_all=False)

parser_thread = subparsers.add_parser('thread', help='display a saved thread')
parser_thread.add_argument('id', nargs='+', type=int)

parser_delete = subparsers.add_parser('delete', help='delete a saved thread')
parser_delete.add_argument('id', nargs='+', type=int)


parser.add_argument('-i', action='store_true', help='interactive mode')
args = parser.parse_args()


print(args)


c = Controller(Model_db(), CommentView())

def add(url) -> None:
    thread = c.download_thread(url)
    c.add_thread(thread)

def show_thread(id: int) -> None:
    c.show_one_ancestor(id)
    c.show_all_descendants(id)

def show_all() -> None:
    c.show_all_ancestors()

def delete(id: int) -> None:
    if confirm_delete():
        c.delete(id)
        print(f'Thread no. {id} deleted.')
    else:
        print('Delete action cancelled.')

def confirm_delete() -> bool:
    yes_no = ''

    while yes_no not in ('y', 'n'):
        yes_no = input('Are you sure you want to delete this thread? [y/n]')
        if yes_no == 'y':
            return True
        elif yes_no == 'n':
            return False
        else:
            continue
    

if args.i:
    FilumShell().cmdloop()        


if args.subparser == 'add':
    add(args.url[0])

elif args.subparser == 'all':
    show_all()

elif args.subparser == 'thread':
    show_thread(args.id[0])

elif args.subparser == 'delete':
    delete(args.id[0])




            