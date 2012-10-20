#!/usr/bin/python

from . import logger
from core import config, utils, notification
from core.controller import Controller
from os.path import join, abspath
import gettext
import locale
from const import *

def setup_locale_and_gettext():
    #Set up localization with gettext
    localedir = join (config.get_base_data_prefix(),"locale")
    # Install _() builtin for gettext; always returning unicode objects
    # also install ngettext()
    gettext.install(APP_NAME, localedir=localedir, unicode=True,
            names=("ngettext",))
    # For Gtk.Builder, we need to call the C library gettext functions
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
    logger.info("1")
    try:
        setup_locale_and_gettext()
    except Exception, e:
        logger.exception("Error loading the internationalitation: %s", e)
    
    try:
        cr = Controller.get_instance()
        cr.start()
    except Exception, e:
        logger.exception("Error starting cloudsn: %s", e)
        #We not traduce this notification because the problem can be gettext
        notification.notify ("Error starting cloudsn",
                            str(e),
                            utils.get_error_pixbuf())

if __name__ == "__main__":
    logger.debug("0")
    start()


