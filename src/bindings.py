"""This is where key bindings are defined."""

# Breaking coding style here (excessive whitespace).
# Hex values from (http://www.bbdsoft.com/ascii.html)
BACKSLASH = 0x5c
BACKSPACE = 0x7F
COMMA     = 0x2c
CTRL_A    = 0x1   # Beginning of the line (Home).
CTRL_B    = 0x2   # Back one character.
CTRL_D    = 0x4   # Delete.
CTRL_E    = 0x5   # End of the line (End).
CTRL_F    = 0x6   # Forward one character.
CTRL_H    = 0x107 # Backspace. Default value 0x8? Python remmaping this key?
CTRL_K    = 0xb   # Cut line after cursor to clipboard.
CTRL_L    = 0xc   # Clear screen.
CTRL_N    = 0x0E  # Next command (down arrow).
CTRL_P    = 0x10  # Previous command (up arrow).
CTRL_U    = 0x15  # Cut line before cursor to clipboard.
CTRL_W    = 0x17  # Cut word before cursor to clipboard.
CTRL_Y    = 0x19  # DSUSP, delayed suspend on BSD-based systems.
CTRL__    = 0x1f  # Undo.
DELETE    = 0x14a
ENTER     = 0x157
ESC       = 0x1b
KEY_B     = 0x62
KEY_C     = 0x63
KEY_D     = 0x64
KEY_DOWN  = 0x102
KEY_HOME  = 0x106
KEY_END   = 0x168
KEY_F     = 0x66
KEY_L     = 0x6c
KEY_LEFT  = 0x104
KEY_R     = 0x72
KEY_RIGHT = 0x105
KEY_T     = 0x74
KEY_U     = 0x75
KEY_UP    = 0x103
RETURN    = 0xa
SPACE     = 0x20
STAB      = 0x161 # Shift Tab.
TAB       = 0x9

# TODO: OS X CTRL_Y bug. *Not* a bug but behavior. $ stty dsusp undef
ALT_SHIFT_Y = 0x81

# OS X hacks.
ALT_KEYS = (BACKSPACE, KEY_B, KEY_C, KEY_D, KEY_F, KEY_L, KEY_R, KEY_T, KEY_U)

editing = (CTRL_K, CTRL_U, CTRL_W)

moving = (CTRL_A, CTRL_B, CTRL_E, CTRL_F, KEY_HOME,
    KEY_END, KEY_LEFT, KEY_RIGHT)

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

yank = (CTRL_Y, ALT_SHIFT_Y)
