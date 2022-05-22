from rich.tree import Tree
from rich.table import Table
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.pretty import pprint
from helpers import html_to_md


class CommentView():
    def __init__(self):
        self.table = Table()
        self.console = Console()

    def stringify(self, _tuple):
        return tuple(str(i) for i in _tuple)

    def display_table(self, _tuple):
        table = self.table
        console = self.console
        table.add_column('')
        table.add_column('Title')
        table.add_column('Posted')
        table.add_column('Saved')
        table.add_column('Score')
        table.add_column('Source')
        table.add_column('Tags')
        for row in _tuple:
            table.add_row(*self.stringify(row))
        console.print(table)
    
    def display_indented(self, _tuple):
        (depth, id, parent_id, text, author, key) = _tuple
        #text = html_to_md(text)
        console = self.console
        item = Padding(f'''⮡\n{author}\n{text}''', (0, 0, 0, depth))
        console.print()
        console.print(Panel(item))



