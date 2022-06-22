"""Contains filum functions that are accessed by the user via terminal commands or the interactive shell."""

import platform
import subprocess
import webbrowser

from rich.console import Console

from filum.config import FilumConfig
from filum.controller import Controller
from filum.exceptions import InvalidInputError, ItemAlreadyExistsError, WaybackMachineError
from filum.validation import id_exists, is_valid_id, is_valid_url

valid_id_message = 'Please enter a valid thread label (a positive integer). Run `filum show` to see a list of thread labels.'  # noqa: E501

config = FilumConfig()
config_parser = config.get_config()
console = Console()
c = Controller()


def add(url) -> None:
    try:
        is_valid_url(url)
        with console.status(f'[light_green]Downloading thread from[/light_green] {url}'):
            thread = c.download_thread(url)
            c.add_thread(thread)
        print('Thread downloaded.')
        show_all()
    except InvalidInputError as err:
        print(err)
    except ItemAlreadyExistsError:
        if confirm('Do you want to update this thread now?'):
            print('Updating thread ...')
            c.update_thread(thread)


def update(id: int) -> None:
    try:
        is_valid_id(id)
        if not id_exists(id):
            return
        if confirm('Do you want to update this thread now?'):
            with console.status('Updating thread'):
                url = c.get_permalink(id)
                is_valid_url(url)
                thread = c.download_thread(url)
                c.update_thread(thread)
            print(f'Thread no. {id} updated. ({url})')
            show_all()
    except InvalidInputError as err:
        print(err)


def show_thread(id: int, cond='', where_param='') -> None:
    try:
        is_valid_id(id)
        c.display_thread(
            id,
            cond=cond,
            pager=config_parser.getboolean('output', 'pager'),
            pager_colours=config_parser.getboolean('output', 'pager_colours'),
            where_param=where_param
            )
    except InvalidInputError as err:
        print(err)
    except IndexError:
        print(valid_id_message)


def show_all() -> None:
    c.show_all_ancestors()


def show_without_id(args):
    if args.tags:
        c.search('tags', args.tags)
    elif args.source:
        c.search('source', args.source)
    else:
        show_all()


def show(args):
    try:
        id = args.id
        if id is None:
            show_without_id(args)
            return
        if not id_exists(id):
            return
        else:
            cond = ''
            where_param = ''
            if args.tags:
                tags = args.tags
                cond = 'WHERE tags LIKE ?'
                where_param = f'%{tags}%'
            elif args.source:
                source = args.source
                cond = 'WHERE source LIKE ?'
                where_param = f'%{source}%'
            show_thread(id, cond=cond, where_param=where_param)
    except ValueError:
        print('Please enter a valid integer.')
    except InvalidInputError as err:
        print(err)


def delete(id: int) -> None:
    try:
        is_valid_id(id)
        if not id_exists(id):
            return
        if confirm(f'Are you sure you want to delete thread no. {id}? [y/n] '):
            c.delete(id)
            print(f'Thread no. {id} deleted.')
            show_all()
        else:
            print('Delete action cancelled.')
    except InvalidInputError as err:
        print(err)
    except IndexError:
        print(valid_id_message)


def confirm(prompt) -> bool:  # type: ignore
    yes_no = ''

    while yes_no not in ('y', 'n'):
        yes_no = input(f'{prompt} [y/n] ')
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


def tags(args):
    try:
        id = args.id
        tags = args.tags
        if id is None:
            get_all_tags()
        else:
            if not id_exists(id):
                return
            if tags is None:
                item_tags = c.get_tags_of_item(id)
                console.print(item_tags)
                return
            if args.delete:
                modify_tags(id, add=False, tags=tags)
            else:
                modify_tags(id, add=True, tags=tags)
    except SystemExit:
        return


def handle_config(args):
    try:
        if args.reset:
            reset_config_to_default()
        open_config()
    except SystemExit:
        return
    except Exception as err:
        print(err)


def open_config():
    print('Opening config file...')
    try:
        if platform.system() == 'Darwin':       # macOS
            subprocess.run(('open', config.config_filepath_default))
        elif platform.system() == 'Windows':    # Windows
            subprocess.run(['notepad', config.config_filepath_default])
        else:                                   # Linux variants
            subprocess.run(('nano', config.config_filepath_default))
    except Exception as err:
        print(err)


def reset_config_to_default():
    if confirm('Are you sure you want to reset the config file to its default?'):
        try:
            c.reset_config_to_default()
        except Exception as err:
            print(err)


def push_to_web_archive(id: int) -> None:
    is_valid_id(id)
    if confirm('Do you want to save a snapshot of this thread to the Wayback Machine?'):
        with console.status('Saving to the Wayback Machine (this may take a while ...)'):
            try:
                web_archive_url = c.push_to_web_archive(id)
                console.print(f'📁 {web_archive_url}')
            except WaybackMachineError:
                console.print('[bold red]Job failed.[/bold red] Try again later.')


def archive(args):
    try:
        id = args.id[0]
        is_valid_id(id)
        if not id_exists(id):
            return
        if not args.url and not args.open:
            push_to_web_archive(id)
        else:
            web_archive_url = c.get_web_archive_url(id)
            message = 'You have not made any snapshots of this thread on the Wayback Machine.'
            if web_archive_url is not None:
                message = f'💾 Saved on the Wayback Machine at:\n\n{web_archive_url}\n'
            if args.url:
                console.print(message)
            elif args.open:
                webbrowser.open_new_tab(web_archive_url)
    except InvalidInputError as err:
        print(err)
