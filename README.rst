shearch
========
.. image:: https://travis-ci.org/shearch/shearch.png?branch=master
   :target: https://travis-ci.org/shearch/shearch
   :alt: Build status

**Table of Contents**

.. contents::
    :local:
    :depth: 1
    :backlinks: none

About
-----
shearch wants to be easier to use shell's history. It is highly cusomizable
meaning you can `add your own commands`_, quickly navigate through them and
recall them simply by entering a few key tags. It offers you in-place editing
of command's arguments by pressing ``TAB`` key to cycle through them. When
satisfied hitting ``RETURN`` will push chosen command to the command line
without executing it! The most convenient way to use shearch is by binding it
to a shortcut key. By default ``F12`` is used.


Contribute
----------
Share your commands with the rest of us. How? Look at `add your own commands`_
section. When you are ready to share follow this steps:

- Fork_ code from main repository https://github.com/shearch/shearch/fork.
- Clone your forked repository to local machine.

.. code-block:: bash

    $ cd ~
    $ git clone git@github.com:myusername/shearch.git # Replace myusername with your username on github

- Add upstream so you are always up to date!

.. code-block:: bash

    $ cd .shearch
    $ git remote add upstream git://github.com/shearch/shearch.git

- Create your branch

.. code-block:: bash

    $ git branch mycommands # name of your branch

- Checkout (migrate) to your branch.

.. code-block:: bash

    $ git checkout mycommands # move to your branch

- `add your own commands`_
- Add your commands to repository.

.. code-block:: bash

    $ git add ~/.shearch/src/db/mycommands.json

- Commit your newly added commands.

.. code-block:: bash

    $ git commit ~/.shearch/src/db/mycommands.json -m "Added commands to list directories."

- When all work is done on that issue, make sure you commit all the changes.

.. code-block:: bash

    $ git commit -a -m "Final commit before push."

- Always update from main repository before submiting pull request.

.. code-block:: bash

    $ git checkout master # Move to your master branch.
    $ git fetch upstream # Get latest code.
    $ git merge upstream/master # Merge upstream master with your local master.
    $ git push origin master # Merge upstream master with your remote fork.
    $ git checkout mycommands # Move back to your mycommands branch.
    $ git merge master # Update your mycommands branch with latest code.
    $ git push origin mycommands # Push mycommands to your remote fork.

- Create pull request from github.


.. _Fork: https://github.com/shearch/shearch/fork


Installation
------------
- from curl
.. code-block:: bash

    $ curl -L https://github.com/shearch/shearch/raw/master/tools/install.sh | .

- from wget

.. code-block:: bash

    $ wget --no-check-certificate https://github.com/shearch/shearch/raw/master/tools/install.sh -O - | .

- manually (rather use one of the above)

.. code-block:: bash

    $ cd ~
    $ git clone git://github.com/shearch/shearch.git ~/.shearch
    $ . ~/.shearch/tools/install.sh


Requirements
------------
Python. Currently bash and zsh shells are supported.


Usage
-----
Press ``F12``, choose a command and press ``RETURN``.


Features
--------
shearch uses standard EMACS(?) style navigation::

    ALT_B: Back, left one word.
    ALT_F: Forward, right one word.
    CTRL_A: Beginning of the line (Home).
    CTRL_B: Back one character.
    CTRL_D: Delete.
    CTRL_E: End of the line (End).
    CTRL_F: Forward one character.
    CTRL_H: Backspace.
    CTRL_K: Cut line after cursor to clipboard.
    CTRL_U: Cut line before cursor to clipboard.
    CTRL_W: Cut word before cursor to clipboard.
    CTRL_Y: Yank (paste). DSUSP, delayed suspend on BSD-based systems.


Cycle through arguments.

    TAB: Cycle through command arguments.
    SHIFT_TAB: Reverse cycle through command arguments.


Add your own commands
---------------------
- Create a file in `~/.shearch/src/db/` ending with `.json` suffix.

.. code-block:: http

    {
        "age": 29,
        "hobbies": [
            "http",
            "pies"
        ],
        "married": false,
        "name": "John"
    }

JSON database structure. Single item contains::

    command - plain command typed in a command line,
    description - Describe what command does.
    nix_edit - Mask marks edible arguments. Args is an array providing default values for those arguments.
    tag -  comma separated tags

Please see provided sample files curl_ and example_ to make it clearer.

.. _curl: https://github.com/shearch/shearch/blob/master/src/db/curl.json
.. _example: https://github.com/shearch/shearch/blob/master/src/db/example.json
