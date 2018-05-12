Translations through leo.org
****************************

The `leo` script expect a word, delegates it to leo.org and present the result.

Requirements
============

The script needs the following requirements:

* `lxml <http://pypi.org/project/lxml/>`_
* `request <https://pypi.org/project/requests/>`_


Quick Start
===========

To use the program without :command:`pip` and virtual environment, use the
following command after cloning this repository::

    $ python3 bin/leo.py

Or copy the script into your `bin` folder::

    $ cp bin/leo.py ~/bin


Workflow
========

The script does the following steps:

#. The script expects a word or phrase (in quotes) on the command line.
#. The word is delegated to the leo.org server
#. The result from leo.org is parsed
#. The parsed result is presented
