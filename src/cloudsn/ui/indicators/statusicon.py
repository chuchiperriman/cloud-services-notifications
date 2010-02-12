#!/usr/bin/python
import pygtk
pygtk.require('2.0')
import gtk
from cloudsn.core.indicator import Indicator
from cloudsn.const import *

class StatusIconIndicator (Indicator):

    def __init__(self):
        self.statusIcon = gtk.StatusIcon()
        #TODO Use the correct Icon
        self.statusIcon.set_from_stock(gtk.STOCK_ABOUT)
        self.statusIcon.set_visible(True)
        self.statusIcon.set_tooltip(APP_LONG_NAME)

        self.menu = gtk.Menu()
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
        self.menuItem.connect('activate', self.execute_cb, self.statusIcon)
        self.menu.append(self.menuItem)
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.menuItem.connect('activate', self.quit_cb, self.statusIcon)
        self.menu.append(self.menuItem)

        self.statusIcon.connect('popup-menu', self.popup_menu_cb, self.menu)
        self.statusIcon.set_visible(1)

    def create_indicator(self, acc):
        print 'creating indicator for ',acc.get_name()
        
    def execute_cb(self, widget, event, data = None):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_border_width(10)

        button = gtk.Button("Hello World")
        button.connect_object("clicked", gtk.Widget.destroy, window)

        window.add(button)
        button.show()
        window.show()

    def quit_cb(self, widget, data = None):
       gtk.main_quit()

    def popup_menu_cb(self, widget, button, time, data = None):
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, gtk.status_icon_position_menu,
                           3, time, self.statusIcon)

if __name__ == "__main__":
    helloWord = HelloTray()
