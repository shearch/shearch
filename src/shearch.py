# $Id: shearch.py 4564 2012-12-21 12:21:12Z wiemann $
# Author: Ziga Zupanec <ziga.zupanec@gmail.com>
# Copyright: This module has been placed in the public domain.

# TODO: Replace current tags field with Textbox.
# TODO: Replace string in history.

"""
A finite state machine specialized for regular-expression-based text filters,
this module defines the following classes:

- `StateMachine`, a state machine
- `State`, a state superclass
- `StateMachineWS`, a whitespace-sensitive version of `StateMachine`
- `StateWS`, a state superclass for use with `StateMachineWS`
- `ViewList`, extends standard Python lists.
- `StringList`, string-specific ViewList.

Exception classes:

- `StateMachineError`
- `UnexpectedIndentationError`
- `TransitionCorrection`: Raised to switch to another transition.
- `StateCorrection`: Raised to switch to another state & transition.

Functions:

- `string2lines()`: split a multi-line string into a list of one-line strings


How To Use This Module
======================
(See the individual classes, methods, and attributes for details.)

1. Import it: ``import statemachine`` or ``from statemachine import ...``.
   You will also need to ``import re``.

2. Derive a subclass of `State` (or `StateWS`) for each state in your state
   machine::

       class MyState(statemachine.State):

   Within the state's class definition:

   a) Include a pattern for each transition, in `State.patterns`::

          patterns = {'atransition': r'pattern', ...}

   b) Include a list of initial transitions to be set up automatically, in
      `State.initial_transitions`::

          initial_transitions = ['atransition', ...]

   c) Define a method for each transition, with the same name as the
      transition pattern::

          def atransition(self, match, context, next_state):
              # do something
              result = [...]  # a list
              return context, next_state, result
              # context, next_state may be altered

      Transition methods may raise an `EOFError` to cut processing short.

   d) You may wish to override the `State.bof()` and/or `State.eof()` implicit
      transition methods, which handle the beginning- and end-of-file.

   e) In order to handle nested processing, you may wish to override the
      attributes `State.nested_sm` and/or `State.nested_sm_kwargs`.

      If you are using `StateWS` as a base class, in order to handle nested
      indented blocks, you may wish to:

      - override the attributes `StateWS.indent_sm`,
        `StateWS.indent_sm_kwargs`, `StateWS.known_indent_sm`, and/or
        `StateWS.known_indent_sm_kwargs`;
      - override the `StateWS.blank()` method; and/or
      - override or extend the `StateWS.indent()`, `StateWS.known_indent()`,
        and/or `StateWS.firstknown_indent()` methods.

3. Create a state machine object::

       sm = StateMachine(state_classes=[MyState, ...],
                         initial_state='MyState')

4. Obtain the input text, which needs to be converted into a tab-free list of
   one-line strings. For example, to read text from a file called
   'inputfile'::

       input_string = open('inputfile').read()
       input_lines = statemachine.string2lines(input_string)

5. Run the state machine on the input text and collect the results, a list::

       results = sm.run(input_lines)

6. Remove any lingering circular references::

       sm.unlink()
"""

__docformat__ = 'restructuredtext'

import curses
import difflib
import re
import subprocess
from curses import textpad

import bindings
from db import data_json as data

class Command(textpad.Textbox):
    """
    `Textbox` subclass with methods for smooth text editing.

    Added methods:
    edible_mask  : Mask that explains how command is formatted.
    input_field  : Each command has its own edible window - field named "input_field" (one line).
    line_number  : On which line number is command rendered in global window.
    place_holder : Current command text.
    pplace_holder: Previous place holder. Needed to analyze changes and reformat accordingly.
    tab_marked   : If True, current word is selected and pressing non terminating character will replace this word.

    """

    tab_marked = False
    field_value = ''

    edible_mask = ''
    input_field = ''
    item = ''
    line_number = ''
    place_holder = ''
    pplace_holder = ''
    #text_box = ''

    # Match text inside single and/or double quotes.
    #re.split(r'''("(?:[^\\"]+|\\.)*")|('(?:[^\\']+|\\.)*')''', nstr)

    # Tab delimited command edible fields. Indexes where these arguments are in a line.
    index_tab = []

    org_command = ''

    # Dictionary of words (arguments), that are tabbable. Key is the word, value is a list of starting indexes of that word.
    tab_args = {}
    # Dictionary of indexes of words (arguments) that are tabbable. Key is index of position in input field, value is word.
    tab_value = {}
    def __init__(self, item, line_number, input_field, *args, **kwargs):
        """
        Initialize a `Command` object.

        Parameters:

        - `item`: a dictionary containing command, description, tags.
        - `line_number`: line number where this command is displayed in terminal.
        - `input_field`: edible window (one line).
        """

        self.item = item
        self.input_field = input_field
        self.line_number = line_number

        # These have to be initialized, otherwise they are shared between instances of the same class.
        self.tab_value = {}
        self.tab_args = {}
        self.index_tab = []
        self.org_command = ''
        self.tab_marked = False
        self.field_value = ''
        self.edible_mask = ''
        #self.place_holder = item['nix_edit']

        #self.text_box = _Textbox(self.input_field, insert_mode=True)

        if 'nix_edit' in self.item:
            self.place_holder = self.format_command(
                self.line_number,
                self.item['nix_edit'],
                self.item['nix_args']
            )
        else:
            self.place_holder = self.item['command']

        self.pplace_holder = self.place_holder
        self.org_command = self.place_holder
        #command = self.format_command(line_number, self.item['nix_edit'], self.item['nix_args'])
        self.print_command(self.place_holder)

        textpad.Textbox.__init__(self, *args, **kwargs)

    def do_command(self, ch):
        """Extends `Textbox` `do_command` method."""

        if ch in bindings.edit_term:
            self.tab_marked = False # Agreed? or remember previous cursor position?
            return 0
        elif ch == bindings.TAB:
            # Cursor position y, x.
            cy, cx = self.input_field.getyx()
            # Detect cursor position and move tab to the next nearest field.
            field_value_index, next_field = self.find_next_field(cx, self.index_tab)
            self.field_value = self.tab_value[next_field]

            #http://stackoverflow.com/questions/6807808/highlighting-and-selecting-text-with-python-curses

            ##command_field[index].addnstr(0, next_field, self.field_value, len(self.field_value), curses.A_REVERSE)
            ##command_field[index].insstr(0, next_field, self.field_value, curses.A_REVERSE)

            #command_field[index].chgat(0, next_field, len(self.field_value), curses.A_REVERSE)
            self.input_field.move(0, next_field)

            self.tab_marked = True
            return textpad.Textbox.do_command(self, ch)
        else:
            # Remove marking from word, if non accumulative character. Otherwise recalculate index_tab.
            if ch in bindings.NON_CHANGING:
                self.tab_marked = False
            else:
                self.adjust_index_tab(ch)

            # TODO: Re-render new command.
            #self.place_holder = self.input_field.instr()
            #if self.place_holder != self.pplace_holder:
            #    self.calculate_new_index_tab(self.pplace_holder, self.place_holder)

            #self.calculate_new_index_tab(self.pplace_holder, self.place_holder)

        if self.tab_marked:
            # Delete the marked word.
            self.tab_marked = False
            arg_len = len(self.field_value)
            #cy, cx = self.input_field.getyx()
            #self.pplace_holder = self.input_field.instr(0, 0)

            #stdscr.move(2, 1)
            #stdscr.clrtoeol()
            #stdscr.addstr(2, 2, self.pplace_holder)
            #stdscr.refresh()

            #self.input_field.move(0, cx)

            # Save just from unmodified part till end. Get before change, so we know the state before changed.
            #self.pplace_holder = self.input_field.instr()

            for i in range(arg_len):
                textpad.Textbox.do_command(self, bindings.CTRL_D)

            # # Save just from unmodified part till end. ?? This is wrong!
            # self.pplace_holder = self.input_field.instr()

            #stdscr.move(2, 1)
            #stdscr.clrtoeol()
            #stdscr.addstr(2, 2, self.pplace_holder)
            #stdscr.refresh()

        #self.pplace_holder = self.place_holder
        return textpad.Textbox.do_command(self, ch)

    def adjust_index_tab(self, ch):
        # TODO: Create new tab value for new arguments.
        cy, cx = self.input_field.getyx()

        # Check, if any of the tabbable arguments is being changed.
            # Find nearest index_tab
        c_lo = -1
        c_hi = -1
        p_lo = -1
        p_hi = -1
        n_lo = -1
        n_hi = -1

        arg_word = ''
        change_arg = False

        idx, c_lo = self.find_next_field(cx, self.index_tab)
        if c_lo > -1:
            # Look at tabbable index ahead, current and after position and deduct.
            # TODO: Go arround array to find values.
            c_hi = c_lo + len(self.tab_value[c_lo])

            if idx >= 0 and len(self.index_tab) > 0:
                # mylist[-1] is ok with python as long as there is at least one item in the list.
                p_lo = self.index_tab[idx - 1]
                p_hi = p_lo + len(self.tab_value[p_lo])

            if (idx + 1) == len(self.index_tab):
                # This case covers cyclicism.
                n_lo = self.index_tab[0]
                n_hi = n_lo + len(self.tab_value[n_lo])
            elif (idx + 1) < len(self.index_tab):
                n_lo = self.index_tab[idx + 1]
                n_hi = n_lo + len(self.tab_value[n_lo])

            # Find if changed occured on tabbable word.
            if p_lo <= cx <= p_hi:
                change_arg = True
                arg_word = self.tab_value[p_lo]
            if c_lo <= cx <= c_hi:
                change_arg = True
                arg_word = self.tab_value[c_lo]
            if n_lo <= cx <= n_hi:
                change_arg = True
                arg_word = self.tab_value[n_lo]

            stdscr.addstr(19 + self.line_number, 0, 'override: ' + str(cx) + ' ' + arg_word)
            stdscr.refresh()

            # Figure if word is in tab_args
            # Figure out changes of that word.
            # Create new tabbable argument.

        #stdscr.addstr(19 + self.line_number, 0, str(self.tab_args))
        #stdscr.refresh()

        #http://stackoverflow.com/questions/3065116/get-the-text-in-the-display-with-ncurses

        #http://stackoverflow.com/questions/5984633/python-re-sub-group-number-after-number
        #http://stackoverflow.com/questions/2657693/insert-a-newline-character-every-64-characters-using-python
        # re.sub(r'(^.{64})', r'\g<1> === ', s3)
        if ch > -1 and ch <= 0xff:
            # TODO: Delete characters, handle ch > 0xff.
            self.org_command = re.sub(r'(^.{' + str(cx) + '})', r'\g<1>' + chr(ch), self.org_command)

        self.index_tab = []
        for key, value in self.tab_args.iteritems():
            kw = r'\b' + key + r'\b'
            self.tab_args[key] = [m.start() for m in re.finditer(kw, self.org_command)]

            for pos in self.tab_args[key]:
                self.tab_value[pos] = key

            # Compare previous and current tab indexes for a given word (argument).
            # This seems buggy and probably is.
            #self.prev_tab_args[key]

            self.index_tab = sorted(list(set(self.index_tab + self.tab_args[key])))

        #stdscr.addstr(12, 2, prev)
        #stdscr.addstr(13 + self.line_number, 2, str(self.index_tab) + ' ' + arg_word + str((c_lo, c_hi, p_lo, p_hi, n_lo, n_hi)))
        #stdscr.refresh()

    def calculate_new_index_tab(self, prev, curr):
        stdscr.addstr(12, 2, prev)
        stdscr.addstr(13, 2, curr)

        #http://stackoverflow.com/questions/1209800/difference-between-two-strings-in-python-php
        diff = difflib.SequenceMatcher(
            a=prev,
            b=curr
        )
        for i, block in enumerate(diff.get_matching_blocks()):
            nstr = "match at a[%d] and b[%d] of length %d" % block
            stdscr.addstr(14 + i, 2, nstr)

        stdscr.refresh()

    def clear_input_field(self):
        self.input_field.move(0, 0)
        self.input_field.clrtoeol()

    def find_next_field(self, index, tab_field):
        if len(tab_field) < 1:
            return (0, -1)
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

                if holder not in self.tab_args:
                    self.tab_args[holder] = []
                j += 1
            elif holder == "%c":
                holder = subprocess.Popen(args[j], stdout=subprocess.PIPE, shell=True).stdout.read().strip()
                holders[i] = holder

                if holder not in self.tab_args:
                    self.tab_args[holder] = []
                j += 1
            tmp_len += len(holder)

        self.org_command = ''.join(holders)
        # Create index_tab
        self.adjust_index_tab(-1)

        #stdscr.addstr(19 + self.line_number, 0, str(self.tab_value))
        #stdscr.refresh()

        return ''.join(holders)

    def get_input_field(self):
        return self.input_field

    def reformat_command(self):
        # Reformats current state of a command to match edible state.
        # TODO: Try to recognize newly added arguments and reformat edible state accordingly.
        pass

    def print_command(self, command):
        self.input_field.addstr(command)
        self.input_field.refresh()

    def print_description(self):
        stdscr.move(2, 1)
        stdscr.clrtoeol()
        stdscr.addstr(2, 2, self.item['description'])
        stdscr.refresh()





# Global list of commands that instanciate class Command.
commands = []
# Global list of input_fields.
input_fields = []

def parse_tags(tag_field):
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

        command = Command(
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
        edit_command(asterix)
    elif key <= 0xff:
        max_i += 1
        tag_field += chr(key)
        stdscr.addstr(5, max_i, chr(key))

curses.endwin()
