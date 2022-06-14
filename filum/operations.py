'''filum functions that are accessed by the user via terminal commands or the interactive shell.'''

import platform
import subprocess

from rich.console import Console

from filum.config import FilumConfig
from filum.controller import Controller
from filum.database import ItemAlreadyExistsError
from filum.validation import InvalidInputError, is_valid_id, is_valid_url

valid_id_message = 'Please enter a valid thread label (+ve int). Run `filum all` to see a list of thread labels.'

config = FilumConfig()
config_parser = config.get_parser()
console = Console()
c = Controller()


def add(url) -> None:
    print(url)
    try:
        is_valid_url(url)
        with console.status(f'Downloading thread from {url}'):
            thread = c.download_thread(url)
            c.add_thread(thread)
        print('Thread downloaded.')
    except InvalidInputError as err:
        print(err)
    except ItemAlreadyExistsError:
        if confirm('Do you want to update this thread now? [y/n] '):
            print('Updating thread ...')
            c.update_thread(thread)


def update(id: int) -> None:
    if confirm('Do you want to update this thread now? [y/n] '):
        with console.status('Updating thread...'):
            url = c.get_permalink(id)
            is_valid_url(url)
            thread = c.download_thread(url)
            c.update_thread(thread)
        print(f'Thread updated. ({url})')
        show_all()


def show_thread(id: int, cond='', **kwargs) -> None:
    try:
        is_valid_id(id)
        c.display_thread(
            id,
            cond=cond,
            pager=config_parser.getboolean('output', 'pager'),
            pager_colours=config_parser.getboolean('output', 'pager_colours'),
            **kwargs
            )
    except InvalidInputError as err:
        print(err)
    except IndexError:
        print(valid_id_message)


def show_all() -> None:
    c.show_all_ancestors()


def delete(id: int) -> None:
    try:
        if confirm('Are you sure you want to delete this thread? [y/n] '):
            is_valid_id(id)
            ancestors_length = c.get_ancestors_length()
            success = True if id <= ancestors_length else False
            if success:
                c.delete(id)
                print(f'Thread no. {id} deleted.')
                show_all()
            else:
                print(f'Thread no. {id} does not exist.\n{valid_id_message}')
        else:
            print('Delete action cancelled.')
    except InvalidInputError as err:
        print(err)
    except IndexError:
        print(valid_id_message)


def confirm(prompt) -> bool:  # type: ignore
    yes_no = ''

    while yes_no not in ('y', 'n'):
        yes_no = input(prompt)
        if yes_no == 'y':
            return True
        elif yes_no == 'n':
            return False
        else:
            print('Enter "y" for yes or "n" for no.')
            continue


def get_all_tags():
    c.show_all_tags()


def modify_tags(id, add: bool, **kwargs):
    c.modify_tags(id, add, **kwargs)
    show_all()


def search(column, searchstr):
    c.search(column, searchstr)


def open_config():
    # filepath = pathlib.Path(__file__).parent.resolve() / 'config.ini'
    if platform.system() == 'Darwin':       # macOS
        subprocess.run(('open', config.config_filepath))
    elif platform.system() == 'Windows':    # Windows
        subprocess.run('notepad', config.config_filepath)
    else:                                   # Linux variants
        subprocess.run(('nano', config.config_filepath))
