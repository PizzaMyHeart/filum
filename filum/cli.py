"""The entry point of the filum application."""

import sys
import warnings
from cmd import Cmd

from filum.operations import (add, archive, show, tags, update,
                              delete, show_without_id, handle_config)
from filum.parser import Parser

from logger.logger import create_logger

logger = create_logger()

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
        """Add a URL to the filum database: $ add <url>"""
        add(arg)

    def do_update(self, arg):
        """Update an existing thread in the database: $ update <id>"""
        try:
            update(int(arg))
        except ValueError:
            print('Please enter a valid integer.')

    def do_archive(self, line):
        """Save a snapshot to the Wayback Machine: $ archive <id>"""
        try:
            args = parser.parser_archive.parse_args(line.split())
            archive(args)
        except SystemExit:
            return

    def do_show(self, line):
        """Display a thread given its label: $ show <id>.\n
        IDs are contained in the left-most column in the table that is displayed when using the '$ show'
        command without any arguments."""
        try:
            args = parser.parser_show.parse_args(line.split())
            show(args)
        except SystemExit:
            return

    def do_delete(self, arg):
        """Delete a thread given its top-level selector: $ delete <id>.\n
        IDs are contained in the left-most column in the table that is displayed when using the '$ show'
        command without any arguments."""
        try:
            delete(int(arg))
        except ValueError:
            print('Please enter a valid integer.')

    def do_tags(self, line):
        """Add tags, delete tags, or return a list of tags."""
        try:
            args = parser.parser_tags.parse_args(line.split())
            tags(args)
        except SystemExit:
            return

    def do_config(self, line):
        """Open the config file in an editor. Change settings by modifying the parameter values: $ config"""
        try:
            args = parser.parser_config.parse_args(line.split())
            handle_config(args)
        except SystemExit:
            return

    def do_quit(self, arg):
        """Quit the interactive session using 'quit' or CTRL-D"""
        sys.exit(0)

    def do_EOF(self, arg):
        """Quit the interactive session using 'quit' or CTRL-D"""
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
        'filum show\nfilum add <url>\nfilum show <id>\nfilum delete <id>\n\n'
        'filum is a tool to save discussion threads from Reddit, Hacker News, and Stack Exchange on your PC. '
        'Run "filum -h" for a full list of options.\n\n'
        'To enable colour output, run `filum config` and set '
        'pager_colours to "true"\n\n'
        'Visit https://github.com/PizzaMyHeart/filum for more info and updates.'
    )

    args = parser.args

    logger.debug(args)

    if args.i:
        FilumShell().cmdloop()

    if args.subparser == 'config':
        handle_config(args)

    if args.subparser == 'add':
        add(args.url[0])

    elif args.subparser == 'update':
        update(args.id[0])

    elif args.subparser == 'archive':
        archive(args)

    elif args.subparser == 'show':
        show(args)

    elif args.subparser == 'delete':
        delete(args.id[0])

    elif args.subparser == 'tags':
        tags(args)

    elif args.subparser == 'search':
        show_without_id(args)

    else:
        print(description)


if __name__ == '__main__':
    main()
