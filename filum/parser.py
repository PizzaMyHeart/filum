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
                    $ filum all

                    Display a thread
                    $ filum show <thread label>
                    🖝 where <thread label> is the number in the left-most column of the table

                    Add tags to a saved thread
                    $ filum tags <tag 1> <tag 2> ... <tag n>
                    🖝 add the '--delete' flag to delete these tags instead
                    ''')
                )

    parser.add_argument('-i', action='store_true', help='interactive mode')

    subparsers = parser.add_subparsers(dest='subparser')

    parser_add = subparsers.add_parser('add', help='add a URL')
    parser_add.add_argument('url', nargs='+', type=str, help='add a URL')
    parser_add.set_defaults(parser_add=True)

    parser_update = subparsers.add_parser('update', help='update a saved thread')
    parser_update.add_argument('id', nargs=1, type=int)

    parser_all = subparsers.add_parser('all', help='show all saved top-level items')
    parser_all.set_defaults(parser_all=False)

    parser_show = subparsers.add_parser('show', help='display a saved thread')
    # TODO: Make the 'id' argument optional. If calling 'show'
    # without any arguments then show all threads (replacing the cmd 'all')
    parser_show.add_argument('id', nargs=1, type=int)
    parser_show.add_argument('--tags', nargs='+', help='display a thread selected from the table filtered by tags')
    parser_show.add_argument('--source', nargs='+', help='display a thread selected from the table filtered by source')

    parser_delete = subparsers.add_parser('delete', help='delete a saved thread')
    parser_delete.add_argument('id', nargs='+', type=int)

    parser_tags = subparsers.add_parser('tags', help='add tags. Include --delete to remove tags instead')
    parser_tags.add_argument('id', nargs='?', type=int)
    parser_tags.add_argument('tags', nargs='?', help='include one or more tags separated by a comma without a space')
    parser_tags.add_argument('--delete', action='store_true')

    parser_search = subparsers.add_parser('search', help='search for a thread')
    parser_search.add_argument('--tags', nargs=1, help='filter table based on a tag')
    parser_search.add_argument('--source', nargs=1, help='filter table by source')

    parser_config = subparsers.add_parser('config', help='open config file')
    parser_config.set_defaults(parser_config=False)

    args = parser.parse_args()
