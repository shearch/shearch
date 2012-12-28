#!/usr/bin/python
# $Id
# Author: Ziga Zupanec <ziga.zupanec@gmail.com>

import curses
import os
import sys

import bindings
import command_
from db import data_json as data

# TODO: Replace current tags field with Textbox.

def display_description(idx):
    global commands, pad

    index = idx - pad

    if index < 0:
        return
    if index >= len(commands):
        return

    commands[index].print_description()

def edit_command(idx):
    """Calls `Command`'s `texbox.edit()`."""
    global commands, pad

    index = idx - pad

    if index < 0:
        return
    if index >= len(commands):
        return

    commands[index].get_input_field().move(0, 0)
    commands[index].edit()

def parse_tags(tag_field):
    """Retrieves commands that matches entered tags."""

    global commands, pad, y_offset

    for n, item in enumerate(commands):
        # Clear current commands.
        stdscr.move(n + pad, 1)
        stdscr.clrtoeol()
        stdscr.refresh()

    commands = []
    items = data.get_commands(tag_field.split(' '))

    n_cols = 500
    """Virtual window character width."""

    right_edge_offset = 0.75
    """Percent of characters that will be displayed until right edge."""

    y_max, x_max = stdscr.getmaxyx()
    x_max -= 2 # Must at least be -1 (window inside window).
    """Character width of current terminal screen."""

    tab_offset = int(right_edge_offset * x_max)
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

def print_command(idx):
    global commands, pad

    index = idx - pad

    if index < 0:
        return
    if index >= len(commands):
        return

    out = os.fdopen(3, 'w')
    out.write(commands[index].get_command())
    out.flush()

stdscr = curses.initscr()
stdscr.box()
#curses.cbreak()
#curses.nocbreak()
curses.noecho()
#curses.echo()
# Hide cursor.
#curses.curs_set(0)
stdscr.keypad(1)

# TODO: Remove this debug hack.
command_.stdscr = stdscr
"""Set Command's global, main terminal screen."""

asterisk = 6
"""Current asterisk position."""

commands = []
"""Global list of commands that instanciate class Command."""

input_fields = []
"""Global list of input_fields."""

key = ''
"""Current character."""

max_i = 9
"""Maximum tag field length."""

pad = 7
"""Offset where commands are displayed."""

tag_field = ''
"""Input field for tags."""

y_offset = 5
"""_y_ offset from left terminal screen edge."""

stdscr.addstr(0, y_offset, "Hit 'enter' to place command in command line.")
stdscr.addstr(y_offset, 1, " * tags: ")
stdscr.refresh()

while key not in bindings.enter:
    key = stdscr.getch()

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
        if max_i > pad:
            max_i -= 1
        stdscr.move(y_offset, max_i + 1)
    elif key in bindings.frwd:
        max_i += 1
        stdscr.move(y_offset, max_i + 1)
    elif key in bindings.space:
        max_i += 1
        stdscr.addstr(y_offset, max_i, ' ')
        parse_tags(tag_field)
        tag_field += ' '
    elif key == bindings.TAB:
        edit_command(asterisk)
    elif key <= 0xff:
        max_i += 1
        tag_field += chr(key)
        stdscr.addstr(y_offset, max_i, chr(key))

curses.endwin()
print_command(asterisk)