from rich.tree import Tree
from rich.table import Table
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.pretty import pprint


class CommentView():
    def __init__(self):
        self.table = Table()
        self.console = Console()

    def stringify(self, _tuple):
        return tuple(str(i) for i in _tuple)

    def display_table(self, _tuple):
        table = self.table
        console = self.console
        table.add_column('Text')
        table.add_column('Ancestor ID')
        table.add_column('Depth')
        table.add_row(*self.stringify(_tuple))
        console.print(table)
    
    def display_indented(self, _tuple):
        (depth, id, parent_id, text, author) = _tuple
        console = self.console
        item = Padding(f'''⮡\n{author}\n{text}''', (0, 0, 0, depth))
        console.print()
        console.print(Panel(item))



