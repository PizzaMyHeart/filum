from typing import Text
from textual.app import App
from textual.widget import Widget
from textual.widgets import Placeholder, Button
from textual.reactive import Reactive
from textual import events
from rich.panel import Panel
from rich.text import Text
from rich.console import RenderableType
from rich.align import Align

class InputText(Widget):
    title: Reactive[RenderableType] = Reactive('')
    content: Reactive[RenderableType] = Reactive('')

    def __init__(self, title: str):
        super().__init__(title)
        self.title = title

    def on_key(self, event: events.Key) -> None:
        if event.key == 'ctrl+h':
            self.content = self.content[:-1]
        else:
            self.content += event.key

    def render(self) -> RenderableType:
        renderable = Align.left(Text(self.content, style='bold'))
        return Panel(
            renderable,
            height=5,
            title=self.title,
            title_align='center',
            style='bold white on rgb(50,57,50)'
            )

class Filum(App):
    async def on_mount(self) -> None:
        await self.view.dock(Button(label='url', name='url'), edge='left', size=3)
        await self.view.dock(InputText('url'), edge='left')
        
        

if __name__ == '__main__':
    Filum.run()