import argparse
from cmd import Cmd
import sys
from controller import Controller
from models import Model_db
from view import CommentView
from validation import is_valid_url, is_valid_id, InvalidInputError

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
            print('Please supply a URL.')
            return False
        add(arg)

    def do_all(self, arg):
        show_all()

    def do_thread(self, arg):
        try:
            show_thread(int(arg))
        except ValueError:
            print('Please enter a valid integer.')

    def do_delete(self, arg):
        try:
            delete(int(arg))
        except ValueError:
            print('Please enter a valid integer.')

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

valid_id_message = 'Please enter a valid thread ID (positive integer). Run `filum all` to see a list of thread IDs.'

c = Controller(Model_db(), CommentView())

def add(url) -> None:
    try:
        is_valid_url(url)
        thread = c.download_thread(url)
        c.add_thread(thread)
    except InvalidInputError as err:
        print(err)


def show_thread(id: int) -> None:
    try:
        is_valid_id(id)
        c.show_one_ancestor(id)
        c.show_all_descendants(id)
    except InvalidInputError as err:
        print(err)
    except IndexError as err:
        print(valid_id_message)


def show_all() -> None:
    c.show_all_ancestors()

def delete(id: int) -> None:
    try:
        if confirm_delete():
            is_valid_id(id)
            ancestors_length = c.get_ancestors_length()
            print(ancestors_length)
            success = True if id <= ancestors_length else False
            if success:
                c.delete(id)
                print(f'Thread no. {id} deleted.')
            else:
                print(f'Thread no. {id} does not exist.\n{valid_id_message}')
        else:
            print('Delete action cancelled.')
    except InvalidInputError as err:
        print(err)
    except IndexError as err:
        print(valid_id_message)

def confirm_delete() -> bool:
    yes_no = ''

    while yes_no not in ('y', 'n'):
        yes_no = input('Are you sure you want to delete this thread? [y/n] ')
        if yes_no == 'y':
            return True
        elif yes_no == 'n':
            return False
        else:
            print('Enter "y" for yes or "n" for no.')
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




            