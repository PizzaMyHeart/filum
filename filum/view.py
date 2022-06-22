"""Contains RichView, a class used to print items to the terminal."""

from typing import Mapping, ValuesView, Any

from rich import box
from rich.console import Console, Group, group
from rich.markdown import Markdown
from rich.padding import Padding
from rich.table import Table
from rich.theme import Theme

from filum.config import FilumConfig
from filum.helpers import sanitise_text, timestamp_to_iso
from logger.logger import create_logger

logger = create_logger()

config = FilumConfig()
config_parser = config.get_config()

colours = {
    'link_colour': 'not bold not italic underline bright_cyan',
    'op_colour': 'bright_yellow',
    'poster_colour': 'bright_cyan',
    'reddit_colour': 'deep_pink2',
    'hn_colour': 'orange1',
    'se_colour': 'sea_green1'
}


console = Console(
    theme=Theme({
        'markdown.block_quote': 'yellow',
        'repr.url': colours['link_colour'], 'markdown.link_url': colours['link_colour']}),
    style='on black')


class FilumMarkdown(Markdown):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hyperlinks = config_parser.getboolean('output', 'hyperlinks')


class RichView:
    def __init__(self):
        self.console = console
        self.author = ''
        self.pager_colours = config_parser.getboolean('output', 'pager_colours')

    def stringify(self, row: ValuesView) -> tuple:
        """Turns each item in the SQL query result into a string
        that can be passed to rich.table.Table.add_row
        """
        return tuple(str(i) for i in row)

    def create_table(self, row_list: list) -> Table:
        """Create a table containing top-level items in response to a query. Returns a Rich Table object."""

        # Construct a new table each time to prevent concatenating
        # new tables together each time the "all" command is called in the
        # interactive shell.

        table = Table(box=box.SIMPLE, expand=True)
        table.add_column('ID', style='green')
        table.add_column('Title')
        table.add_column('Posted')
        table.add_column('Saved')
        table.add_column('Score')
        table.add_column('Source')
        table.add_column('Tags')

        # Convert each sqlite3.Row object to a dict
        rows = [dict(row) for row in row_list]

        for row in rows:
            row['posted_timestamp'] = timestamp_to_iso(row['posted_timestamp'])
            row['saved_timestamp'] = timestamp_to_iso(row['saved_timestamp'])
            colour = self.set_row_colour(row)
            table_row = (
                row['num'],
                f'[{colour}]{row["title"]}[/{colour}]',
                row['posted_timestamp'],
                row['saved_timestamp'],
                row['score'],
                f'[{colour}]{row["source"]}[/{colour}]',
                row['tags']
            )
            table.add_row(*self.stringify(table_row))
        return table

    def set_row_colour(self, row: dict) -> str:
        if row['source'] == 'reddit':
            colour = colours['reddit_colour']
        elif row['source'] == 'hn':
            colour = colours['hn_colour']
        elif row['source'] == 'se':
            colour = colours['se_colour']
        return colour

    def create_thread_header(self, item: Mapping) -> Group:
        """Create a header with post information such as author, time posted, score, etc.
        Returns a group of Rich renderable objects as a Group object.
        See https://rich.readthedocs.io/en/stable/group.html.
        """
        timestamp = timestamp_to_iso(item['posted_timestamp'])
        item_permalink = item["item_permalink"]
        if item_permalink == item['parent_permalink']:
            item_permalink = ''
        else:
            item_permalink = f'  » {item["item_permalink"]}\n'
        to_print = (
            f'\n¶ [bold underline violet]{item["title"]}[/bold underline violet]\n\n'
            f'{item_permalink}'
            f'\n[bold {colours["op_colour"]}]{item["author"]}[/bold {colours["op_colour"]}] '
            f'[green]{item["score"]} pts[/green] [blue]{timestamp}[/blue] {item["parent_permalink"]}\n'
            )
        body: Any = ''
        if item['body']:
            body = item['body']
            body = sanitise_text(body)
            logger.debug(body)
            body = FilumMarkdown(body)
        top_level_group = Group(
            Padding(to_print, (0, 0, 0, 2)),
            Padding(body, (0, 0, 0, 2))
        )
        self.author = item['author']
        return top_level_group

    def create_thread_body(self, results: list) -> Group:
        @group()
        def make_panels(results: list):
            for result in results:
                text = result['text']
                text = sanitise_text(text)
                logger.debug(text)
                text = FilumMarkdown(text)
                timestamp = ''
                # Padding can only accept integers not floats
                indent = (result["depth"] + 2)*2
                if result['timestamp']:
                    timestamp = timestamp_to_iso(result['timestamp'])
                if result['score'] is not None:
                    score = f'{result["score"]} pts'
                else:
                    score = ''
                if result['author'] == self.author:
                    author_colour = colours['op_colour']
                else:
                    author_colour = colours['poster_colour']
                header = (
                    f'\n¬ [bold {author_colour}]{result["author"]}[/bold {author_colour}] '
                    f'[green]{score}[/green] [blue]{timestamp}[/blue]'
                    )
                yield Padding(header, (0, 2, 0, indent))
                yield Padding(text, (0, 2, 0, indent + 2))

        return make_panels(results)

    def display_thread(self, top_level, indented, pager=True, pager_colours=True) -> None:
        if not pager:
            self.filum_print(top_level)
            self.filum_print(indented)
        elif pager:
            with self.console.pager(styles=pager_colours):
                # Only works if terminal pager supports colour
                self.filum_print(top_level)
                self.filum_print(indented)

    def filum_print(self, item):
        self.console.print(item)

    def filum_print_pager(self, item):
        with self.console.pager(styles=self.pager_colours):
            self.filum_print(item)
