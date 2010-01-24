#!/usr/bin/python

from .core.controller import Controller
from .core import config
from os.path import join, abspath
import gettext
import locale
from const import *

def setup_locale_and_gettext():
    """Set up localization with gettext"""
    localedir = join (config.get_base_data_prefix(),"locale")
    # Install _() builtin for gettext; always returning unicode objects
    # also install ngettext()
    gettext.install(APP_NAME, localedir=localedir, unicode=True,
            names=("ngettext",))
    # For gtk.Builder, we need to call the C library gettext functions
    # As well as set the codeset to avoid locale-dependent translation
    # of the message catalog
    locale.bindtextdomain(APP_NAME, localedir)
    locale.bind_textdomain_codeset(APP_NAME, "UTF-8")
    # to load in current locale properly for sorting etc
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error, e:
        pass

def start ():
    setup_locale_and_gettext()
    cr = Controller.get_instance()
    cr.start()

if __name__ == "__main__":
    start()


