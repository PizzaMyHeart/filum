from rich.tree import Tree
from rich.table import Table
from rich.console import Console, group
from rich.padding import Padding
from rich.panel import Panel
from rich import box
from rich.pretty import pprint
from helpers import html_to_md
from rich.prompt import Prompt

console = Console(color_system='standard')


class CommentView():
    def __init__(self):
        self.table = Table(box=box.SIMPLE)
        self.console = console

    def stringify(self, _tuple):
        return tuple(str(i) for i in _tuple)

    def display_table(self, _tuple):
        table = self.table
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
        item = item[0]
        to_print = f'{item["author"]} {item["score"]} {item["permalink"]}\n{item["body"]}'
        
        console.print(to_print)
    

    def display_indented(self, results: list):

        @group()
        def make_panels(results: list):
            for result in results:
                item = f'[red]{result["author"]}[/red] [[green]{result["id"]}[/green]]\n{result["text"]}\n\n'
                yield Padding(item, (0, 0, 0, result["depth"]))

        self.console.print(make_panels(results))
        '''
        with self.console.pager(styles=True):
            self.console.print(make_panels(results))
        '''


