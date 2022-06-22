# filum 

`filum` is a command-line tool that saves discussion threads to your local machine. 

It's like a bookmark manager that saves actual content rather than just the link pointing to it.

Like Pocket and Instapaper, it extracts text content for an uncluttered experience&mdash;specifically for discussion threads on Reddit, Hacker News, and Stack Exchange.

Fully supported on Linux and mostly works on Windows (use WSL for the ideal experience). Not tested on MacOS.

[![asciicast](https://asciinema.org/a/503560.svg)](https://asciinema.org/a/503560)

![A table rendered in the terminal](https://raw.githubusercontent.com/PizzaMyHeart/filum/main/img/table.png)

![A Hacker News thread rendered in the terminal](https://raw.githubusercontent.com/PizzaMyHeart/filum/main/img/thread.png)

## Installation

1. Create a virtual environment for `filum` (optional but recommended).

    Linux: 

    `$ python3 -m venv /path/to/new/venv`

    Windows: 

    `$ c:\Python35\python -m venv c:\path\to\new\venv`

    For more details [click here](https://docs.python.org/3/library/venv.html).


2. Install from PyPI.

    `python3 -m pip install filum`


3. Activate the virtual environment.

    Linux:

    `$ source /path/to/venv/bin/activate`

    Windows:

    `$ \path\to\venv\Scripts\Activate`

    Now you can run the commands in the following section.


## Usage

### Save a new thread

`$ filum add <url>`

Example: 

`$ filum add https://www.reddit.com/r/Python/comments/v1rde4/whats_a_python_feature_that_is_very_powerful_but/ianzrfp/`

You may supply a permalink to a child node of the thread to save only a specific section of the thread.

The following platforms are supported: Reddit, Hacker News, Stack Exchange.

### View information about currently saved threads

`$ filum show`

The left-most column of the table contains values to be used as selectors (in place of `<id>`) for the subsequent commands.

*Note that the values in the `ID` column are dynamic. Run `$ filum show` each time after you modify the database to see all updated changes.* 

### View a specific thread

`$ filum show <id>`

Example: 

`$ filum show 2` for the thread in the table with '2' in the `ID` column.

The thread is piped through a terminal pager by default. To disable this, run `$ filum config` and edit `pager = true` to `pager = false`.

If you use a pager, you can navigate between nodes in the thread by searching for the `¬` symbol (yes very hacky).

### Delete a thread

`$ filum delete <id>`

Example: 

`$ filum delete 2` for the thread in the table with '2' in the `ID` column.

### Update a thread

`$ filum update <id>`

Example: 

`$ filum update 2` for the thread in the table with '2' in the `ID` column.

`filum` will offer to update a thread if you try to add a thread that's already saved in the database.

### Add tags to a saved thread

`$ filum tags <id> <tag 1>,<tag 2>,...`

Example: 

`$ filum tags 2 python webdev` to add the tags "python" and "webdev" to the thread in the table with '2' in the `ID` column.

### Delete tags from a saved thread

`$ filum tags <id> <tag 1>,<tag 2>, ... --delete`

Example: 

`$ filum tags 2 webdev --delete` to remove the tag "webdev" from the thread in the table with '2' in the `ID` column.

### Show all current tags

`$ filum tags`

### Search for a thread

Full-text search of saved threads is currently unavailable. However, you can filter the threads by tags or by source.

`$ filum show --tags <tag>`

`$ filum show --source <source>`

You can now select a thread based on the filtered table.

`$ filum show --tags <tag> <id>`

`$ filum show --source <source> <id>`

### Save a thread to the Wayback Machine

`$ filum archive <id>`

Re-running this command on a thread you have already saved to the Wayback Machine will prompt you to confirm whether you want to save a new snapshot. Currently only the latest snapshot is saved.

*This feature depends on the availability of the Wayback Machine's Save Page Now service, which is under incredibly high demand. Please be mindful when using this command.*

Show the URL of a Wayback Machine snapshot: `$ filum archive --url`

Visit a Wayback Machine snapshot: `$ filum archive --open`


## Interactive mode

Run `$ filum -i` to start an interpreter where you can use `filum` subcommands without specifying the `filum` keyword.


## Configuration options

- `pager`: Pipes thread output to your default pager. Defaults to true.

- `pager_colours`: Enables coloured pager output. Note that you may need to tweak your environment variables for this to work. Defaults to true.
    - [Linux](https://serverfault.com/a/35888)

- `hyperlinks`: Enables hyperlink rendering in Markdown. Not all terminals support this. Defaults to false.

- `max_rows_without_pager`: Sets the maximum number of rows of the table returned by `filum show` above which the table should be displayed via the pager.


## Known limitations

These are on my to-do list to improve. 

- Reddit comment sub-threads that are hidden under a comment fold (with a "load more comments" link) are ignored
- The search command only takes in one search string at a time
- Filters for searching cannot be combined, e.g. you can search either by a tag or by source
- Look into alternatives to the Wayback Machine for archival (although archive.today makes it really painful to work with using scripts)
- I may add support for discussion threads on other websites and forums in the future

If you find any bugs (of which there will be many), please file it in a GitHub issue.


## Contributing

Not currently open to pull requests, but questions and suggestions are more than welcome. Feel free to open a GitHub issue.


## Disclaimer

`filum` is alpha software and far from stable. Please do not rely solely on `filum` for archival&mdash;at the very least bookmark the page or use the save feature on the respective platforms.