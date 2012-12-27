# $Id
# Author: Ziga Zupanec <ziga.zupanec@gmail.com>

import curses

import bindings
import command_
from db import data_json as data

# TODO: Replace current tags field with Textbox.

commands = []
"""Global list of commands that instanciate class Command."""

input_fields = []
"""Global list of input_fields."""

def parse_tags(tag_field):
    """Retrieves commands that matches entered tags."""

    global commands
    pad = 7
    commands = []
    items = data.get_commands(tag_field.split(' '))

    n_cols = 500
    """Virtual window character width."""

    y_offset = 5
    """_y_ offset from left terminal screen edge."""

    y_max, x_max = stdscr.getmaxyx()
    x_max -= 2 # Must at least be -1 (window inside window).
    """Character width of current terminal screen."""

    tab_offset = int(0.75 * x_max)
    """Number of characters tab characters to show."""

    for n, item in enumerate(items):
        if n >= len(input_fields):
            # Add new input field at the end if there are none left available.
            tmp_scr = curses.newpad(1, n_cols)
            input_fields.append(tmp_scr)

        command = command_.Command(
            item,
            (n + pad, y_offset, x_max),
            input_fields[n],
            tab_offset,
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
#curses.nocbreak()
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
"""Set Command's global, main terminal screen."""

max_i = 9
"""Maximum tag field length."""

key = ''
"""Current character."""

tag_field = ''
"""Input field for tags."""

asterisk = 6
"""Current asterisk position."""

pad = 7
"""Offset where commands are displayed."""

while key not in bindings.enter:
    key = stdscr.getch()
    stdscr.addstr(15, 15, str(hex(key)) + '   <')
    stdscr.refresh()

    if key in bindings.prev:
        stdscr.addstr(asterisk, 2, ' ')
        asterisk -= 1
        stdscr.addstr(asterisk, 2, '*')
        display_description(asterisk)
    elif key in bindings.next:
        stdscr.addstr(asterisk, 2, ' ')
        asterisk += 1
        stdscr.addstr(asterisk, 2, '*')
        display_description(asterisk)
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
        stdscr.addstr(15, 15, str(asterisk))
        edit_command(asterisk)
    elif key <= 0xff:
        max_i += 1
        tag_field += chr(key)
        stdscr.addstr(5, max_i, chr(key))

curses.endwin()
