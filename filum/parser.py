"""Contains the Parser class that defines an argparse CLI parser with subcommands."""

import argparse
import textwrap


class Parser(object):
    parser = argparse.ArgumentParser(
                description='Archive discussion threads',
                prog='filum',
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=textwrap.dedent('''\
                    Example usage:

                    Add a URL
                    $ filum add <url>

                    View a table of all saved threads
                    $ filum show

                    Display a thread
                    $ filum show <id>
                    🖝 where <id> is the number in the left-most column of the table

                    Add tags to a saved thread
                    $ filum tags <tag 1> <tag 2> ... <tag n>
                    🖝 add the '--delete' flag to delete these tags instead
                    ''')
                )

    parser.add_argument('-i', action='store_true', help='Interactive mode')

    subparsers = parser.add_subparsers(dest='subparser')

    parser_add = subparsers.add_parser('add', help='Add a URL')
    parser_add.add_argument('url', nargs=1, type=str, help='add a URL')
    parser_add.set_defaults(parser_add=True)

    parser_archive = subparsers.add_parser('archive', help='Save a snapshot to the Wayback Machine')
    parser_archive.add_argument('--url', action='store_true', help='Display the Wayback Machine URL')
    parser_archive.add_argument('--open', action='store_true', help='Open the Wayback Machine snapshot in the web browser')  # noqa: E501
    parser_archive.add_argument('id', nargs=1, type=int)

    parser_update = subparsers.add_parser('update', help='Update a saved thread')
    parser_update.add_argument('id', nargs=1, type=int)

    parser_show = subparsers.add_parser('show', help='Display a saved thread')
    parser_show.add_argument('--tags', nargs='?', help='display a thread selected from the table filtered by tags')
    parser_show.add_argument('--source', nargs='?', help='display a thread selected from the table filtered by source')
    parser_show.add_argument('id', nargs='?', type=int, help='Item label. Omit this to show all items.')

    parser_delete = subparsers.add_parser('delete', help='Delete a saved thread')
    parser_delete.add_argument('id', nargs='+', type=int)

    parser_tags = subparsers.add_parser('tags', help='Add tags. Include --delete to remove tags instead')
    parser_tags.add_argument('id', nargs='?', type=int)
    parser_tags.add_argument('tags', nargs='?', help='include one or more tags separated by a comma without a space')
    parser_tags.add_argument('--delete', action='store_true')

    parser_config = subparsers.add_parser('config', help='Open the config file')
    parser_config.add_argument('--reset', action='store_true', help='Reset the config file to its defaults')
    parser_config.set_defaults(parser_config=False)

    args = parser.parse_args()
