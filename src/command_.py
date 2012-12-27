# $Id
# Author: Ziga Zupanec <ziga.zupanec@gmail.com>
# Copyright: This module has been placed in the public domain.

"""
Textbox subclass for easier text manipulation, this module defines
the following class:

- `Command`, meta-data about shell command.


How To Use This Module
======================
(See the individual classes, methods, and attributes for details.)

1. Import it: ``import command_``.

2. Initialize command: ``mycommand = command_.Command(...)``.

3. Interact with command::

    a) Print command description: ``mycommand.print_description()``.

    b) Manipulate cursor position: ``mycommand.get_input_field().move(0, 0)``.

    c) Edit command in-place: ``mycommand.edit()``.
"""

__docformat__ = 'reStructuredText'

import curses
from curses import textpad
import difflib
import re
import sre_constants
import subprocess

import bindings

class Command(textpad.Textbox):

    """
    `Textbox` subclass with methods for smooth text editing.

    Command contains methods for simpler text formatting and string
    manipulation.
    """

    # TODO: Remove this debug hack.
    stdscr = None

    def __init__(self, item, box, input_field, tab_offset, *args, **kwargs):
        """
        Extend `Textbox` `__init__` method. Initialize a `Command` object.

        Parameters:

        - `item`: a dictionary containing command, description, tags.
        - `box`:
            - `_line_number`: Number of row command is rendered in terminal.
            - `_y_offset`: _y_ offset from left terminal screen edge.
            - `_xmax`: Maximum screen size, _x_ axis.
        - `input_field`: edible window (one line).
        - `tab_offset`: Number of characters tab characters to show.
        """

        self._item = item
        self._line_number, self._y_offset, self._xmax = box
        self._input_field = input_field
        self._tab_offset = tab_offset

        self._tab_value = {}
        """Dictionary of indexes of words (arguments) that are tabbable.
        Key is index of position in input field, value is word."""

        self._tab_args = {}
        """Dictionary of words (arguments), that are tabbable.
        Key is the word, value is a list of starting indexes of that word."""

        self._index_tab = []
        """Indexes of edible arguments (_x_ axis)."""

        self._shadow_command = ''

        self._prev_ch = ''
        """Previous character. Used for navigation hacks."""

        self._selected_word = ''
        """Currently marked argument."""

        self._edible_mask = ''
        """Mask that explains how command is formatted. Similar to printf."""

        self._yank = ''
        """Holds content of cut string to paste."""

        self._center = False
        """Center for tab arguments."""

        self._myoff = self._xmax - self._y_offset
        self._curr_offset = 0
        """Relative _x_ offset."""

        if 'nix_edit' in self._item:
            self._shadow_command = self._format_command(
                self._item['nix_edit']['mask'],
                self._item['nix_edit']['args']
            )
        else:
            self._shadow_command = self._item['command']

        self._print_command(self._shadow_command)

        textpad.Textbox.__init__(self, *args, **kwargs)

    def do_command(self, ch):
        """Extend `Textbox` `do_command` method."""

        cy, cx = self._input_field.getyx()
        """Cursor position within this line."""

        if ch in bindings.edit_term:
            # Termination keys. Leave input_field. Mark prev cursor position?
            return 0

        if self._prev_ch == bindings.ESC:
            if ch == bindings.ESC:
                # Leaving input on double ESC.
                return 0
            elif ch in (bindings.ALT_KEYS):
                if ch == bindings.KEY_B:
                    _s = self._prev_word(cx)
                    self._input_field.move(0, _s)
                elif ch == bindings.KEY_F:
                    _s = self._next_word(cx)
                    self._input_field.move(0, _s)
                self._adjust_index_tab()
                return self._super_return(1, 0)
            #else: Treat the rest as _prev_ch was not ESC key. Ignore or cont?

        if ch == bindings.ESC:
            return self._super_return(1, ch)

        if ch in bindings.tabs:
            # Move cursor to the next nearest tab field.
            selected_word_index, next_field = self._find_next_field(
                cx,
                self._index_tab
            )
            try:
                self._selected_word = self._tab_value[next_field]
            except KeyError:
                self._selected_word = ''
                next_field = cx

            self._input_field.move(0, next_field)
            self._center = True
            # TODO: Mark current word.
            #self._mark_word(cx, self._selected_word)
            return self._super_return(
                textpad.Textbox.do_command(self, ch), ch)

        if ch in bindings.moving:
            return self._super_return(
                textpad.Textbox.do_command(self, ch), 0)

        if ch in bindings.editing:
            return self._super_return(self._edit(cx, ch), 0)

        # Characters from now on assumed invasive.
        _e = cx # End position. Replacing marked word changes that.
        chr_fail = False
        clear_word = False
        insert_char = True

        if self._prev_ch in bindings.tabs:
            clear_word = True
            arg_len = len(self._selected_word)
            _e = cx + arg_len
            self._delete_chars(arg_len)

        if ch == bindings.BACKSLASH:
            character = '\\\\'
            _e += 1 # Increase _e too?
        elif ch in bindings.backspace:
            insert_char = False
            if clear_word:
                self._shadow_command = (self._shadow_command[:cx - 1] +
                    self._shadow_command[_e - 1:])
                self._adjust_index_tab()
                return self._super_return(1, 0)
            self._shadow_command = (self._shadow_command[:cx - 1] +
                self._shadow_command[_e:])
            ch = bindings.CTRL_H
        elif ch in bindings.delete:
            insert_char = False
            if clear_word:
                self._shadow_command = (self._shadow_command[:cx - 1] +
                    self._shadow_command[_e - 1:])
                self._adjust_index_tab()
                return self._super_return(1, 0)
            self._shadow_command = (self._shadow_command[:cx] +
                self._shadow_command[_e + 1:])
            ch = bindings.CTRL_D
        elif ch in bindings.yank:
            self._shadow_command = (self._shadow_command[:cx] +
                str(self._yank) + self._shadow_command[_e:])
            self._put_chars(str(self._yank))
            self._adjust_index_tab()
            return self._super_return(1, 0)
        else:
            try:
                character = chr(ch)
            except ValueError:
                chr_fail = True

        if chr_fail:
            # We are lost. Read the command from _input_field.
            ret_val = textpad.Textbox.do_command(self, ch)
            cy, cx = self._input_field.getyx()
            self._shadow_command = self._input_field.instr(0, 0)
            self._input_field.move(0, cx)
            return self._super_return(ret_val, 0)

        if insert_char:
            try:
                self._shadow_command = (self._shadow_command[:cx] +
                    character +
                    self._shadow_command[_e:])
            except UnicodeDecodeError:
                return self._super_return(1, 0)

        ret_val = textpad.Textbox.do_command(self, ch)
        self._adjust_index_tab()

        return self._super_return(ret_val, 0)

    def edit(self, validate=None):
        "Edit in the widget window and collect the results."
        while 1:
            ch = self.win.getch()
            if validate:
                ch = validate(ch)
            if not ch:
                continue
            if not self.do_command(ch):
                break

            cy, cx = self._input_field.getyx()
            if cx - self._myoff > self._curr_offset:
                self._curr_offset = cx - self._myoff
            elif cx < self._curr_offset:
                self._curr_offset = cx
            if self._center:
                self._center = False
                tab_offset = self._tab_offset
                if cx - self._curr_offset < self._myoff:
                    tab_offset = (cx - self._curr_offset -
                        (self._myoff - tab_offset))
                self._curr_offset += tab_offset
            self.win.refresh(0, self._curr_offset, self._line_number,
                self._y_offset, self._line_number, self._xmax)

        return self.gather()

    def _adjust_index_tab(self):
        """
        Recalculate new <TAB> indexes for edible arguments.

        Updates followin structures:

        - `_tab_args`
        - `_tab_value`
        - `_index_tab`
        """
        # TODO: Create new tab value for new arguments.
        #is_changed, prev_arg, start_idx, end_idx = _detect_broken_args()
        self._index_tab = []
        for key, value in self._tab_args.iteritems():
            kw = r'\b' + re.escape(key)
            self._tab_args[key] = [m.start() for m in re.finditer(
                kw, self._shadow_command)]

            for pos in self._tab_args[key]:
                self._tab_value[pos] = key

            # Compare previous and current tab indexes for a current argument.
            # This seems buggy and probably is.
            #self.prev_tab_args[key]

            self._index_tab = sorted(list(set(
                self._index_tab + self._tab_args[key])))

    def _calculate_new_index_tab(self, prev, curr):
        """Difference between previous and current command."""
        stdscr.addstr(12, 2, prev)
        stdscr.addstr(13, 2, curr)
        # Difference between two strings in python [6]
        # [6]: http://stackoverflow.com/questions/1209800/difference-between-two-strings-in-python-php
        diff = difflib.SequenceMatcher(
            a=prev,
            b=curr
        )
        for i, block in enumerate(diff.get_matching_blocks()):
            nstr = "match at a[%d] and b[%d] of length %d" % block
            stdscr.addstr(14 + i, 2, nstr)
        stdscr.refresh()

    def _clear_input_field(self):
        """Clear input field."""
        self._input_field.move(0, 0)
        self._input_field.clrtoeol()

    def _delete_chars(self, count, move_cursor=-1):
        """Removes n characters from a string."""
        ret_val = 1
        if move_cursor > -1:
            self._input_field.move(0, move_cursor)
        for i in range(count):
            ret_val = textpad.Textbox.do_command(self, bindings.CTRL_D)
        return ret_val

    def _detect_broken_args(self):
        """
        Return tuple: (is_changed, prev_arg, start_idx, end_idx).

        Return values:

        - is_changed: True, if edible argument has changed.
        - prev_arg: Argument that is about to change.
        - start_idx: Start index of argument.
        - end_idx: End index of argument.

        When there is no match, (False, '', -1, -1) is return value.
        """
        # Check, if any of the tabbable arguments is being changed.
        # Find nearest index_tab
        c_lo = -1
        c_hi = -1
        p_lo = -1
        p_hi = -1
        n_lo = -1
        n_hi = -1

        is_changed = False
        prev_arg = ''
        start_idx = -1
        end_idx = -1

        cy, cx = self._input_field.getyx()

        idx, c_lo = self._find_next_field(cx, self._index_tab)
        if c_lo > -1:
            # Get tabbable index previous, current and next position.
            c_hi = c_lo + len(self._tab_value[c_lo])

            if idx >= 0 and len(self._index_tab) > 0:
                # mylist[-1] is ok with python.
                p_lo = self._index_tab[idx - 1]
                p_hi = p_lo + len(self._tab_value[p_lo])

            if (idx + 1) == len(self._index_tab):
                # This case covers cyclicism.
                n_lo = self._index_tab[0]
                n_hi = n_lo + len(self._tab_value[n_lo])
            elif (idx + 1) < len(self._index_tab):
                n_lo = self._index_tab[idx + 1]
                n_hi = n_lo + len(self._tab_value[n_lo])

            # Find if changed occured on tabbable word.
            if p_lo <= cx <= p_hi:
                is_changed = True
                prev_arg = self._tab_value[p_lo]
                start_idx = p_lo
                end_idx = p_hi
            if c_lo <= cx <= c_hi:
                is_changed = True
                prev_arg = self._tab_value[c_lo]
                start_idx = c_lo
                end_idx = c_hi
            if n_lo <= cx <= n_hi:
                is_changed = True
                prev_arg = self._tab_value[n_lo]
                start_idx = n_lo
                end_idx = n_hi

            stdscr.addstr(
                self._line_number + 12,
                0,
                'override: ' + str(cx) + ' ' + prev_arg
            )
            stdscr.refresh()

            # Figure if word is in tab_args
            # Figure out changes of that word.
            # Create new tabbable argument.

    def _edit(self, cx, ch):
        """Puts removed characters before/after cursor in yank."""
        _s = -1
        self._yank = ''

        if ch == bindings.CTRL_K:
            self._yank = self._shadow_command[cx:]
            self._shadow_command = self._shadow_command[:cx]
        elif ch == bindings.CTRL_U:
            _s = 0
            self._yank = self._shadow_command[:cx]
            self._shadow_command = self._shadow_command[cx:]
        elif ch == bindings.CTRL_W:
            _s = self._prev_word(cx)
            self._yank = self._shadow_command[_s:cx]
            self._shadow_command = (self._shadow_command[:_s] +
                self._shadow_command[cx:])

        self._adjust_index_tab()
        return self._delete_chars(len(self._yank), _s)

    def _next_word(self, cx):
        """Return starting index of next word."""
        p = re.compile(r'\w+\b')
        _s = [m.start() for m in p.finditer(self._shadow_command, cx)]
        try:
            _s = _s[1]
        except IndexError:
            _s = len(self._shadow_command)
        return _s

    def _prev_word(self, cx):
        """Return starting index of previous word."""
        p = re.compile(r'\w+\b')
        _s = [m.start() for m in p.finditer(self._shadow_command, 0, cx)]
        try:
            _s = _s[-1]
        except IndexError:
            _s = 0
        return _s

    def _find_next_field(self, index, tab_field):
        """Return tuple, index & position of next edible argument on <TAB>."""
        if len(tab_field) < 1:
            return (0, -1)
        for n, i in enumerate(tab_field):
            if i > index:
                return (n, i)
        return (0, tab_field[0])

    def _format_command(self, command, args):
        """
        Make and return formatted command as string.

        This is run on initialization.

        Parameters:

        - `command`: printf like formatted string.
        - `args`: tuple of arguments that should be put into formatted string.
        """
        holders = re.split("(%s|%c)", command)

        tmp_len = 0
        j = 0
        for i, holder in enumerate(holders):
            if holder == "%s":
                holder = args[j]
                holders[i] = holder

                if holder not in self._tab_args:
                    self._tab_args[holder] = []
                j += 1
            elif holder == "%c":
                holder = subprocess.Popen(
                    args[j],
                    stdout=subprocess.PIPE,
                    shell=True
                ).stdout.read().strip()
                holders[i] = holder

                if holder not in self._tab_args:
                    self._tab_args[holder] = []
                j += 1
            tmp_len += len(holder)

        self._shadow_command = ''.join(holders)
        # Create index_tab
        self._adjust_index_tab()

        return ''.join(holders)

    def get_input_field(self):
        """Public method return input field. Used to control cursor."""
        return self._input_field

    def _mark_word(self, cx, selected_word):
        # Highlighting and selecting text with python curses [1]
        # [1]: http://stackoverflow.com/questions/6807808/highlighting-and-selecting-text-with-python-curses
        """
        command_field[index].addnstr(
            0,
            next_field,
            selected_word,
            len(selected_word),
            curses.A_REVERSE
        )
        command_field[index].insstr(
            0,
            next_field,
            selected_word,
            curses.A_REVERSE
        )
        """

        """
        command_field[index].chgat(
            0,
            next_field,
            len(selected_word),
            curses.A_REVERSE
        )
        """
        pass

    def _reformat_command(self):
        """Reformats current state of a command to match edible state."""
        # Match text inside single and/or double quotes.
        #re.split(r'''("(?:[^\\"]+|\\.)*")|('(?:[^\\']+|\\.)*')''', nstr)
        pass

    def _print_command(self, command):
        """Print command in the commands list in main terminal window."""
        self._input_field.addstr(0, 0, command)
        self._input_field.refresh(0, 0, self._line_number,
            self._y_offset, self._line_number, self._xmax)

    def print_description(self):
        """Print command description in main terminal window."""
        stdscr.move(2, 1)
        stdscr.clrtoeol()
        stdscr.addstr(2, 2, self._item['description'])
        stdscr.refresh()

    def _put_chars(self, yank):
        """Inserts n characters in a string."""
        for chy in yank:
            textpad.Textbox.do_command(self, chy)

    def _super_return(self, ret_val, ch):
        """Only exit point from the graph."""
        self._prev_ch = ch
        return ret_val
