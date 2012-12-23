"""
This is where key bindings are defined.
"""

# Hex values from (http://www.bbdsoft.com/ascii.html)
BACKSPACE = 0x7F
COMMA     = 0x2c
CTRL_A    = 0x1
CTRL_B    = 0x2
CTRL_D    = 0x4
CTRL_E    = 0x5
CTRL_F    = 0x6
CTRL_H    = 0x107
CTRL_N    = 0x0E
CTRL_P    = 0x10
DELETE    = 0x14a
ENTER     = 0x157
ESC       = 0x1b
KEY_DOWN  = 0x102
KEY_HOME  = 0x106
KEY_END   = 0x168
KEY_LEFT  = 0x104
KEY_RIGHT = 0x105
KEY_UP    = 0x103
RETURN    = 0xa
SPACE     = 0x20
STAB      = 0x161
TAB       = 0x9

next = (KEY_DOWN, CTRL_N)
prev = (KEY_UP, CTRL_P)

back = (KEY_LEFT, CTRL_B)
frwd = (KEY_RIGHT, CTRL_F)

begin = (KEY_HOME, CTRL_A)
end   = (KEY_END, CTRL_E)

enter = (ENTER, RETURN)
space = (SPACE, COMMA)

backspace = (BACKSPACE, CTRL_H)
delete    = (DELETE, CTRL_D)

edit_term = (KEY_DOWN, CTRL_N, KEY_UP, CTRL_P, RETURN, ENTER)

tabs = (TAB, STAB)

NON_CHANGING = (CTRL_A, CTRL_B, CTRL_E, CTRL_F, CTRL_N, CTRL_P, KEY_DOWN, KEY_HOME, KEY_END, KEY_LEFT, KEY_RIGHT, KEY_UP)
