import sys
import warnings
from cmd import Cmd

from filum.operations import add, get_all_tags, update, show_all, show_thread, delete, modify_tags, search, open_config
from filum.parser import Parser


parser = Parser()


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
        '''Add a URL to the filum database: $ add <url>'''
        if arg == '':
            print('Please supply a URL.')
            return False
        add(arg)

    def do_update(self, arg):
        try:
            update(int(arg))
        except ValueError:
            print('Please enter a valid integer.')

    def do_all(self, arg):
        '''Show all top-level items currently saved in the filum database: $ all'''
        show_all()

    def do_show(self, line):
        '''Display a thread given its top-level selector: $ thread 1.\n
        Top-level selectors are contained in the left-most column in the table shown by the "all" command.'''
        args = parser.parser_show.parse_args(line.split())
        try:
            if args.tags:
                show_thread(args.id[0], cond='WHERE tags LIKE ?', where_param=f'%{args.tags[0]}%')
            elif args.source:
                show_thread(args.id[0], cond='WHERE source LIKE ?', where_param=f'%{args.source[0]}%')
            else:
                show_thread(args.id[0])
        except ValueError:
            print('Please enter a valid integer.')

    def do_delete(self, arg):
        '''Delete a thread given its top-level selector: $ thread 1.\n
        Top-level selectors are contained in the left-most column in the table shown by the "all" command.'''
        try:
            delete(int(arg))
        except ValueError:
            print('Please enter a valid integer.')

    def do_tags(self, line):
        try:
            args = parser.parser_tags.parse_args(line.split())
            if args.id:
                if args.delete:
                    modify_tags(args.id, add=False, tags=args.tags)
                else:
                    modify_tags(args.id, add=True, tags=args.tags)
            else:
                get_all_tags()
        except SystemExit:
            return

    def do_search(self, line):
        try:
            args = parser.parser_search.parse_args(line.split())
            if args.tags:
                search('tags', args.tags[0])
            elif args.source:
                search('source', args.source[0])
        except SystemExit:
            return

    def do_config(self, arg):
        '''Open the config file in an editor. Change settings by modifying the parameter values: $ config'''
        try:
            open_config()
        except Exception as err:
            print(err)

    def do_quit(self, arg):
        '''Quit the interactive session using 'quit' or CTRL-D'''
        sys.exit(0)

    def do_EOF(self, arg):
        '''Quit the interactive session using 'quit' or CTRL-D'''
        sys.exit(0)


def main():
    warnings.filterwarnings(
            'ignore',
            category=UserWarning,
            module='bs4',
            message='.*looks more like a filename than markup.*'
            )

    description = (
        'filum - archive discussion threads from the command line.\n\n'
        'Usage:\n'
        'filum all\nfilum add <url>\nfilum thread <id>\nfilum delete <id>\n\n'
        'filum is a tool to save discussion threads from Reddit, Hacker News, and Stack Exchange on your PC. '
        'Like a bookmarking tool, but the text itself is saved locally. Worry no more about deleted threads.\n\n'
        'Run "filum -h" for a full list of options.'
    )

    args = parser.args
    if args.i:
        FilumShell().cmdloop()

    if args.subparser == 'config':
        print('Opening config file...')
        open_config()

    if args.subparser == 'add':
        add(args.url[0])

    elif args.subparser == 'update':
        update(args.id[0])

    elif args.subparser == 'all':
        show_all()

    elif args.subparser == 'show':
        if args.tags:
            show_thread(args.id[0], cond='WHERE tags LIKE ?', where_param=f'%{args.tags[0]}%')
        elif args.source:
            show_thread(args.id[0], cond='WHERE source LIKE ?', where_param=f'%{args.source[0]}%')
        else:
            show_thread(args.id[0])

    elif args.subparser == 'delete':
        delete(args.id[0])

    elif args.subparser == 'tags':
        if args.id:
            if args.delete:
                modify_tags(args.id, add=False, tags=args.tags)
            else:
                modify_tags(args.id, add=True, tags=args.tags)
        else:
            get_all_tags()

    elif args.subparser == 'search':
        if args.tags:
            search('tags', args.tags[0])
        elif args.source:
            search('source', args.source[0])

    else:
        print(description)


if __name__ == '__main__':
    main()
