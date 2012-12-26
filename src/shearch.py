import curses

import bindings
import command_
from db import data_json as data

# TODO: Replace current tags field with Textbox.

# Global list of commands that instanciate class Command.
commands = []
# Global list of input_fields.
input_fields = []

def parse_tags(tag_field):
    """Retrieves commands that matches entered tags."""

    global commands
    pad = 7
    commands = []
    items = data.get_commands(tag_field.split(' '))

    for n, item in enumerate(items):
        if n >= len(input_fields):
            # Add new input field at the end if there are none left available.
            ymax, xmax = stdscr.getmaxyx()
            tmp_scr    = stdscr.derwin(1, xmax - 18, n + pad, 4)
            input_fields.append(tmp_scr)

        command = command_.Command(
            item,
            n,
            input_fields[n],
            input_fields[n],
            insert_mode=True
        )

        commands.append(command)

def display_description(idx):
    global commands

    pad = 7
    index = idx - pad

    if index < 0:
        return
    if index >= len(commands):
        return

    commands[index].print_description()

def edit_command(idx):
    """Calls `Command`'s `texbox.edit()`."""
    global commands

    pad = 7
    index = idx - pad

    if index < 0:
        return
    if index >= len(commands):
        return

    commands[index].get_input_field().move(0, 0)
    commands[index].edit()

stdscr = curses.initscr()
stdscr.box()
#curses.cbreak()
curses.noecho()
#curses.echo()
# Hide cursor.
#curses.curs_set(0)

stdscr.keypad(1)
stdscr.addstr(0, 5, "Hit 'enter' to quit")
stdscr.addstr(5, 1, " * tags: ")
stdscr.refresh()

# TODO: Remove this debug hack.
command_.stdscr = stdscr

# Cursor index.
i = 9
# Maximum tag field length.
max_i = i
# Current character.
key = ''
# Tag field.
tag_field = ''
# Command line asterix number.
asterix = 6
# Offset where commands are displayed
pad = 7

while key not in bindings.enter:
    key = stdscr.getch()
    stdscr.addstr(15, 15, str(hex(key)) + '   <')
    stdscr.refresh()

    if key in bindings.prev:
        stdscr.addstr(asterix, 2, ' ')
        asterix -= 1
        stdscr.addstr(asterix, 2, '*')
        display_description(asterix)
    elif key in bindings.next:
        stdscr.addstr(asterix, 2, ' ')
        asterix += 1
        stdscr.addstr(asterix, 2, '*')
        display_description(asterix)
    elif key in bindings.back:
        if max_i > 7:
            max_i -= 1
        stdscr.move(5, max_i + 1)
    elif key in bindings.frwd:
        max_i += 1
        stdscr.move(5, max_i + 1)
    elif key in bindings.space:
        max_i += 1
        stdscr.addstr(5, max_i, ' ')
        parse_tags(tag_field)
        tag_field += ' '
    elif key == bindings.TAB:
        stdscr.addstr(15, 15, str(asterix))
        edit_command(asterix)
    elif key <= 0xff:
        max_i += 1
        tag_field += chr(key)
        stdscr.addstr(5, max_i, chr(key))

curses.endwin()
