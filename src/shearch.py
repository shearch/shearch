# TODO: Replace current tags field with Textbox.

import curses, re, subprocess
from curses import textpad

import bindings
from db import data_json as data

class Command():
    """ Methods for command handeling.
    """

    edible_mask = ''
    command = ''

    # Tab delimited command edible fields. Indexes where these arguments are in a line.
    command_tab = []
    # Values of tab delimited fields. Reverse highlight marked field.
    command_value = []

    def __init__(*args, **kwargs):
        pass

    def find_next_field(self, index, tab_field):
        for n, i in enumerate(tab_field):
            if i > index:
                return (n, i)
        return (0, tab_field[0])

    def format_command(self, index, command, args):
        #holders = re.findall("%s|%c", command)
        holders = re.split("(%s|%c)", command)

        tmp_len = 0
        j       = 0
        for i, holder in enumerate(holders):
            if holder == "%s":
                holder = args[j]
                holders[i] = holder
                self.command_tab.append(tmp_len + 1)
                self.command_value.append(holder)
                j += 1
            elif holder == "%c":
                holder = subprocess.Popen(args[j], stdout=subprocess.PIPE, shell=True).stdout.read().strip()
                holders[i] = holder
                self.command_tab.append(tmp_len + 1)
                self.command_value.append(holder)
                j += 1
            tmp_len += len(holder)

        return ''.join(holders)

    def reformat_command(self):
        # Reformats current state of a command to match edible state.
        # TODO: Try to recognize newly added arguments and reformat edible state accordingly.
        pass







class _Textbox(textpad.Textbox):
    """ curses.textpad.Textbox requires users to ^g on completion, which is sort
    of annoying for an interactive chat client such as this, which typically only
    requires an enter. This subclass fixes this problem by signaling completion
    on Enter as well as ^g. """

    marked = False
    field_value = ''

    def __init__(*args, **kwargs):
        textpad.Textbox.__init__(*args, **kwargs)

    def do_command(self, ch):
        global command_tab, command_value, command_field, asterix

        index = asterix - 7

        if ch in bindings.edit_term:
            self.marked = False # Agreed? or remember previous cursor position?
            return 0
        elif ch == bindings.TAB:
            cy, cx = command_field[index].getyx()
            # TODO: Detect cursor position and move tab to the next nearest field.
            field_value_index, next_field = find_next_field(cx, command_tab[index])
            self.field_value = command_value[index][field_value_index]
            #command_field[index].addnstr(0, next_field, self.field_value, len(self.field_value), curses.A_REVERSE)
            #command_field[index].insstr(0, next_field, self.field_value, curses.A_REVERSE)
            command_field[index].chgat(0, next_field, len(self.field_value), curses.A_REVERSE)
            command_field[index].move(0, next_field)
            self.marked = True
            return textpad.Textbox.do_command(self, ch)
        else:
            # TODO: Re-render new command.
            #self.field_value = reformat_command()
            pass

        if self.marked:
            # Delete the marked word.
            self.marked = False

            for i in range(len(self.field_value)):
                textpad.Textbox.do_command(self, bindings.CTRL_D)
            #textpad.Textbox.do_command(self, bindings.CTRL_D)

        return textpad.Textbox.do_command(self, ch)

def find_next_field(index, tab_field):
    for n, i in enumerate(tab_field):
        if i > index:
            return (n, i)
    return (0, tab_field[0])

# Tab delimited command edible fields. Indexes where these arguments are in a line.
command_tab = []
# Values of tab delimited fields. Reverse highlight marked field.
command_value = []

def format_command(index, command, args):
    # Constructs a formated command.
    global command_tab, command_value

    #holders = re.findall("%s|%c", command)
    holders = re.split("(%s|%c)", command)

    tmp_len = 0
    j       = 0
    for i, holder in enumerate(holders):
        if holder == "%s":
            holder = args[j]
            holders[i] = holder
            command_tab[index].append(tmp_len + 1)
            command_value[index].append(holder)
            j += 1
        elif holder == "%c":
            holder = subprocess.Popen(args[j], stdout=subprocess.PIPE, shell=True).stdout.read().strip()
            holders[i] = holder
            command_tab[index].append(tmp_len + 1)
            command_value[index].append(holder)
            j += 1
        tmp_len += len(holder)

    return ''.join(holders)

def reformat_command():
    # Reformats current state of a command to match edible state.
    # TODO: Try to recognize newly added arguments and reformat edible state accordingly.
    pass

# Commands and meta-data.
items = []
# Command edit fields.
command_field = []
# Edit fields for commands.
command_textbox = []

def parse_tags(tag_field):
    # Parses tags and send them to get_commands(tags) to get meta-data. Then creates command edit fields.
    global items, command_field, command_textbox, command_tab, command_value
    pad = 7

    items = data.get_commands(tag_field.split(' '))
    for n, item in enumerate(items):
        if n >= len(command_field):
            # TODO: This is not good. Only append?? This is only viable if n == len(command_field) but what if n is larger??!!
            ymax, xmax = stdscr.getmaxyx()
            tmp_scr    = stdscr.derwin(1, xmax - 18, n + pad, 4)
            tmp_tb     = _Textbox(tmp_scr, insert_mode=True)
            command_field.append(tmp_scr)
            command_textbox.append(tmp_tb)
            # Empty placeholders for tab edible commands.
            command_tab.append([])
            command_value.append([])

        command_field[n].move(0, 1)
        command_field[n].clrtoeol()

        if 'nix_edit' in item:
            command = format_command(n, item['nix_edit'], item['nix_args'])
        else:
            command = item['command']

        command_field[n].addstr(command)
        command_field[n].refresh()

def display_description(idx):
    pad = 7
    index = idx - pad

    if index < 0:
        return
    if index >= len(items):
        return

    stdscr.move(2, 1)
    stdscr.clrtoeol()
    stdscr.addstr(2, 2, items[index]['description'])

# TODO: Replace string in history.

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

while key not in bindings.enter:
    key = stdscr.getch()
    #stdscr.addstr(15, 15, str(key))
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
        #command_textbox[asterix - 7].do_command(key)
        command_field[asterix - 7].move(0, 1)
        command_textbox[asterix - 7].edit()
    elif key <= 0xff:
        max_i += 1
        tag_field += chr(key)
        stdscr.addstr(5, max_i, chr(key))

curses.endwin()
