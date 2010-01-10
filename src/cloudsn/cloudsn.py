#!/usr/bin/python

from cloudsn.core.controller import Controller
from cloudsn import globals
import gettext

VERSION="0.1.1"
APP_NAME="cloudsn"
APP_LONG_NAME="Cloud Services Notifications"


def setup_locale_and_gettext():
    gettext.install(APP_NAME)
    print 'installed gettext'

def main ():
    setup_locale_and_gettext()
    cr = Controller.get_instance()
    cr.start()

if __name__ == "__main__":
    main()


