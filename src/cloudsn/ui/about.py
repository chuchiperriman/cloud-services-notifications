#encoding: utf-8
from gi.repository import Gtk
from cloudsn import const
from cloudsn.core import config

def show_about_dialog():
    dialog = Gtk.AboutDialog()
    dialog.set_name(const.APP_LONG_NAME)
    dialog.set_version(const.APP_VERSION)
    dialog.set_copyright (const.APP_COPYRIGHT)
    dialog.set_comments(const.APP_DESCRIPTION)
    dialog.set_website (const.APP_WEBSITE)
    dialog.set_logo(Gtk.gdk.pixbuf_new_from_file(config.add_data_prefix('cloudsn120.png')))
    dialog.set_authors (["Jesús Barbero Rodríguez"])
    dialog.run()
    dialog.hide()
