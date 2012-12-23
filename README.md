Elevator pitch: History on low potent caffeine, wannabe history on steroids.
I created this in my spare time between my spare time.

Is an extended shell's history. It co-exists with your current shell history and makes searching easier and lazier. Shearch uses git as a database to store and expand your command arsenal.

Installation:
git clone …
add your favorite binding key to .shell_rc

Usage:

Search: [ctlr+r]
Next: ctrl+n
Previous: ctrl+p

Adding a command:
[administrator:~]$ ls -la ## dir, folder, hidden ## List hidden folders.


Check if the INTERACTIVE_COMMENTS option is set.

According to this page, "[...] in interactive shells with the INTERACTIVE_COMMENTS option set, [...] # causes that word and all the following characters up to a newline to be ignored."

According to the comments were added later, set -k does exactly the same thing.
http://unix.stackexchange.com/questions/33994/zsh-interpret-ignore-commands-beginning-with-as-comments

Pull Requests are welcome! Please note coding style*.

JSON database structure. Single item contains.
"tag"        : "comma separated tags",
"description": "Describe what command does.",
"command"    : "find . -name \"*.txt\"",
"edibles"    : "find . -name \"%s\"",
"win"        : "dir *.*",
"ps"         : "ls"

"edibles" field is optional. "win" field is optional (command for windows). "ps" field is optional (powershell command).If defined, "ps" field will be used in powershell enviornment. Two commands all have their respective edibles.

Install:
curl -L https://github.com/agiz/shearch/raw/master/tools/install.sh | sh
wget --no-check-certificate https://github.com/agiz/shearch/raw/master/tools/install.sh -O - | sh

![Go](http://racingpool.si/wp-content/themes/ImpreZZ/images/search_btn.gif "Go")