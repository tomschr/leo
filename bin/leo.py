#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse

import logging
from logging.config import dictConfig

import os
import sys


if sys.version_info[0:2] <= (3, 7):
    from collections import OrderedDict
else:
    # Preserve insertion order of dict objects in v3.7
    OrderedDict = dict

__author__ = "Thomas Schraitle <toms@suse.de>"
__version__ = "1.1.0"

# Global URL
url = "http://pda.leo.org/{0}-deutsch/{1}"

LANGUAGES = OrderedDict(
    en="englisch",
    fr="französisch",
    es="spanisch",
    it="italienisch",
    # FIPS and NATO country code for China. ISO code for Switzerland:
    ch="chinesisch",
    ru="russisch",
    pt="portugiesisch",
    pl="polnisch"
    )

#: The dictionary, used by :class:`logging.config.dictConfig`
#: use it to setup your logging formatters, handlers, and loggers
#: For details, see
# https://docs.python.org/3.4/library/logging.config.html#configuration-dictionary-schema
DEFAULT_LOGGING_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': '[%(levelname)s] %(name)s: %(message)s'},
    },
    'handlers': {
        'default': {
            'level': 'NOTSET',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        __name__: {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

#: Map verbosity level (int) to log level
LOGLEVELS = {None: logging.WARNING,  # 0
             0: logging.WARNING,
             1: logging.INFO,
             2: logging.DEBUG,
             }

#: Instantiate our logger
log = logging.getLogger(__name__)

try:
    import requests
except ImportError:
    log.fatal("ERROR: No requests module found. Install it with:\n"
              "$ sudo zypper in python3-requests")
    sys.exit(200)

try:
    from lxml import html as htmlparser
except ImportError:
    log.fatal("ERROR: no lxml module found. Install it with:\n"
              "$ sudo zypper in python3-lxml")
    sys.exit(10)


def available_languages():
    """Bundles the available languages into one string.

    Allows easily printing the available languages in the usage instructions.

    :return: string of available languages
    :rtype: str
    """
    language_strings = ["{0} ({1})".format(l, s) for s, l in LANGUAGES.items()]
    return ", ".join(language_strings)


def lang_name(lang=None):
    """Translate language shortcut to the full language name.

    If an invalid shortcut or an unknown full name is given,
    the first full language name is returned as a fallback.

    :param str lang: language code
    :return: full language code
    :rtype: str
    """
    try:
        return LANGUAGES[lang]
    except KeyError:
        if lang in LANGUAGES.values():
            return lang
        else:
            return list(LANGUAGES.values())[0]


def lang_short(lang=None):
    """Translate language name to the shortcut.

    If an invalid name or an unknown shortcut is given,
    the first available language shortcut is returned as a fallback.

    :param str lang: language code
    :return: shortcut
    :rtype: str
    """
    if lang in LANGUAGES:
        return lang
    else:
        for short, name in LANGUAGES.items():
            if name == lang:
                return short

        return list(LANGUAGES.keys())[0]


def default_lang():
    """Returns the language part from the LANG environment variable
       or None

    :return: language code
    :rtype: str | None
    """
    try:
        lang = os.environ["LANG"].split("_")[0]
        # Fallback to English
        # see https://www.gnu.org/software/libc/manual/
        # html_node/Standard-Locales.html#Standard-Locales
        if lang.upper() in ("C", "POSIX", ""):
            lang = 'en'
        return lang
    except KeyError:
        return None


def parse(cliargs=None):
    """Parse the command line and return parsed results

    :param list cliargs: Arguments to parse or None (=use sys.argv)
    :return: parsed CLI result
    :rtype: :class:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(description='Query leo.org',
                                     usage='%(prog)s [OPTIONS] QUERYSTRING')
    parser.add_argument('-D', '--with-defs',
                        action="store_true",
                        default=False,
                        help="Include any definitions in the result "
                             "(default: %(default)s)",
                        )
    parser.add_argument('-E', '--with-examples',
                        action="store_true",
                        default=False,
                        help="Include examples in the result "
                             "(default: %(default)s)",
                        )
    parser.add_argument('-P', '--with-phrases',
                        action="store_true",
                        default=False,
                        help="Include phrases in the result "
                             "(default: %(default)s)",
                        )
    parser.add_argument('-v', '--verbose',
                        action="count",
                        help="Raise verbosity level",
                        )
    parser.add_argument('-l', '--language',
                        action="store",
                        default=default_lang(),
                        help="Translate from/to a specific language "
                             "by their full name or shortcut "
                             "(default: %(default)s). "
                             "Available languages: {}".format(
                                 available_languages()),
                        )

    # parser.add_argument( '-F', '--with-forums',
    #   action="store_true",
    #   default=False,
    #   help="Include forums in the result (default: %(default)s)",
    #   )
    parser.add_argument('query',
                        metavar="QUERYSTRING",
                        help="Query string",
                        )
    args = parser.parse_args(cliargs)

    # Setup logging and the log level according to the "-v" option
    dictConfig(DEFAULT_LOGGING_DICT)
    log.setLevel(LOGLEVELS.get(args.verbose, logging.DEBUG))
    log.debug("CLI args: %s", args)
    return args


def get_leo_page(url):
    """Return root node of Leo's result HTML page

    :param str url: the URL to be loaded
    :return: the HTML page as text
    :rtype: :class:`str`
    """
    log.debug("Trying to load %r...", url)
    response = requests.get(url)
    if not response.ok:
        raise requests.exceptions.HTTPError(response)
    return response.text


def parse_leo_page(text):
    """Return root node of Leo's result HTML page

    :param str text: the HTML page as text
    :return: the HTML tree
    :rtype: :class:`lxml.html.HtmlElement`
    """
    document = htmlparser.fromstring(text)
    html = document.getroottree()
    log.debug("Got HTML page")
    return html


def extract_text(element):
    """Extract text from element

    :param element: the element node
    :return: fixed text content
    :rtype: str
    """
    # Fix some encoding problems:
    txt = element.text_content().replace('\xa0', '')\
                                .replace('\xdf', 'ß')\
                                .replace('\n', '')
    return txt


def format_as_table(row):
    """Format the row as a table and print it out

    :param row: node of a row which contains <tr> elements
    """
    log.debug("Row: %s", row)
    widths = []
    translations = []

    for tr in row:
        entry = tr.getchildren()
        entry = entry[4], entry[7]
        c1, c2 = [extract_text(en) for en in entry if len(extract_text(en))]
        t1 = c1.strip()
        t1 = " ".join(t1.split())
        t1 = t1.replace("AE", " [AE]")  # TODO: fix this workaround
        t1 = t1.replace("BE", " [BE]")  # TODO: fix this workaround
        t2 = c2.strip()
        t2 = " ".join(t2.split())
        widths.append(len(t1))
        translations.append((t1, t2))

    max_width = max(widths)

    for t1, t2 in translations:
        print("{left:<{width}} | {right}".format(
            left=t1,
            width=max_width,
            right=t2)
            )


def get_results(args, root):
    """Print the results

    :param args: parsed command line arguments
    :param root: root element node
    """
    log.debug("Analysing results...")
    line = "-" * 10
    data = {"subst":      "Substantive",
            "verb":       "Verbs",
            "adjadv":     "Adjectives/Adverbs",
            }

    if args.with_defs:
        data.update({"definition": "Definitions"})

    if args.with_examples:
        data.update({"example": "Examples"})

    if args.with_phrases:
        data.update({"phrase": "Redewendung"})

    language_shortcut = lang_short(args.language)

    found = set()
    html = root.getroot()
    div = html.get_element_by_id('centerColumn')
    div = html.get_element_by_id('centerColumn')
    for section in div.find_class("section")[:5]:
        name = section.attrib.get('data-dz-name')
        if name in data:
            found.add(name)
            print("\n{0} {1} {0}".format(line, data[name]))
            trs = section.xpath("table/tbody/tr[td[@lang='{0}'] and "
                                "td[@lang='de']]".format(language_shortcut))
            format_as_table(trs)


if __name__ == "__main__":
    args = parse()
    language = lang_name(args.language)
    url = url.format(language, args.query)

    returncode = 0
    try:
        doc = parse_leo_page(get_leo_page(url))
        get_results(args, doc)
    except requests.exceptions.Timeout:
        log.error("Timeout")
        returncode = 10
    except requests.exceptions.BaseHTTPError as err:
        log.error("Basic HTTP error: %s", err)
        returncode = 15
    except IOError:
        # Term wasn't found
        log.error("No translation for %s was found", args.query)
        returncode = 20

    sys.exit(returncode)

# EOF
