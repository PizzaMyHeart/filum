"""Contains RichView, a class used to print items to the terminal."""

from typing import Mapping, ValuesView, Any

from rich import box
from rich.console import Console, Group, group
from rich.markdown import Markdown
from rich.padding import Padding
from rich.table import Table
from rich.theme import Theme

from filum.config import FilumConfig
from filum.helpers import timestamp_to_iso
from logger.logger import create_logger

logger = create_logger()

config = FilumConfig()
config_parser = config.get_parser()

colors = {
    'link_color': 'not bold not italic underline bright_cyan',
    'op_color': 'bright_yellow',
    'poster_color': 'bright_cyan'
}


console = Console(
    theme=Theme({
        'markdown.block_quote': 'yellow',
        'repr.url': colors['link_color'], 'markdown.link_url': colors['link_color']}),
    style='on black')


class FilumMarkdown(Markdown):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hyperlinks = config_parser.getboolean('output', 'hyperlinks')


class RichView:
    def __init__(self):
        self.console = console
        self.author = ''

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
        table.add_column('#', style='green')
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
            table_row = (
                row['num'],
                row['title'],
                row['posted_timestamp'],
                row['saved_timestamp'],
                row['score'],
                row['source'],
                row['tags']
            )
            table.add_row(*self.stringify(table_row))
        return table

    def create_thread_header(self, item: Mapping) -> Group:
        """Create a header with post information such as author, time posted, score, etc.
        Returns a group of Rich renderable objects as a Group object.
        See https://rich.readthedocs.io/en/stable/group.html.
        """
        timestamp = timestamp_to_iso(item['posted_timestamp'])
        to_print = (
            f'\n[bold {colors["op_color"]}]{item["author"]}[/bold {colors["op_color"]}] '
            f'[green]{item["score"]} pts[/green] [blue]{timestamp}[/blue] {item["permalink"]}\n\n'
            f'✎ {item["title"]}\n'
            )
        body: Any = ''
        if item['body']:
            body = FilumMarkdown(item["body"])
            logger.debug(item['body'])
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
                logger.debug(result['text'])
                text = FilumMarkdown(result['text'])
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
                    author_color = colors['op_color']
                else:
                    author_color = colors['poster_color']
                header = (
                    f'\n¬ [bold {author_color}]{result["author"]}[/bold {author_color}] '
                    f'[green]{score}[/green] [blue]{timestamp}[/blue]\n'
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
