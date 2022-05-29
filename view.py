from rich.tree import Tree
from rich.table import Table
from rich.console import Console, group
from rich.padding import Padding
from rich.panel import Panel
from rich import box
from rich.pretty import pprint
from helpers import html_to_md
from rich.prompt import Prompt
from rich.markdown import Markdown


console = Console()


class CommentView():
    def __init__(self):
        self.console = console

    def stringify(self, _tuple):
        return tuple(str(i) for i in _tuple)

    def display_table(self, _tuple):
        '''Construct a new table each time to prevent concatenating
        new tables together each time the "all" command is called in the
        interactive shell.
        '''
        table = Table(box=box.SIMPLE)
        console = self.console
        table.add_column('', style='green')
        table.add_column('Title')
        table.add_column('Posted')
        table.add_column('Saved')
        table.add_column('Score')
        table.add_column('Source')
        table.add_column('Tags')
        for row in _tuple:
            table.add_row(*self.stringify(row))
        console.print(table)
    
    def display_top_level(self, item):
        print(item)
        item = item[0]
        to_print = f'''\n[bold bright_yellow]{item["author"]}[/bold bright_yellow] {item["score"]} {item["permalink"]}\n{item["title"]}\n'''
        if item['body']:
            to_print += f'{item["body"]}\n'
        console.print(to_print)
    

    def display_indented(self, results: list):

        @group()
        def make_panels(results: list):
            for result in results:
                text = Markdown(result['text'])
                
                item = f'\n[bold bright_cyan]{result["author"]}[/bold bright_cyan] [[green]{result["id"]}[/green]]\n'
                
                yield Padding(item, (0, 0, 0, result["depth"]))
                yield Padding(text, (0, 0, 0, result["depth"]))

        self.console.print(make_panels(results))
        '''
        with self.console.pager(styles=True):
            self.console.print(make_panels(results))
        '''


