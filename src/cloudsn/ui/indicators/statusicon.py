#!/usr/bin/python
import pygtk
pygtk.require('2.0')
import gtk
from cloudsn.core import config
from cloudsn.core.indicator import Indicator
from cloudsn.const import *

class StatusIconIndicator (Indicator):

    def __init__(self):
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_from_pixbuf(config.get_cloudsn_icon())
        self.statusIcon.set_visible(True)
        self.statusIcon.set_tooltip(APP_LONG_NAME)
        self.statusIcon.connect('activate', self.main_cb, self.statusIcon)
        
        self.indmenu = self.create_main_menu()
        
        self.menu = gtk.Menu()
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.menuItem.connect('activate', self.quit_cb, self.statusIcon)
        self.menuItem.set_always_show_image (True)
        self.menu.append(self.menuItem)

        self.statusIcon.connect('popup-menu', self.popup_menu_cb, self.menu)
        self.statusIcon.set_visible(1)

    def create_main_menu(self):
        indmenu = gtk.Menu()
        indmenuItem = gtk.MenuItem("")
        indmenuItem.get_child().set_markup("<b>%s</b>" % (APP_LONG_NAME))
        indmenuItem.connect('activate', self.quit_cb, self.statusIcon)
        indmenuItem.set_sensitive(False)
        indmenu.append(indmenuItem)
        return indmenu
        
    def create_indicator(self, acc):
        print 'creating indicator for ',acc.get_name()
        indmenuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        indmenuItem.get_child().set_label(acc.get_name())
        indmenuItem.connect('activate', self.quit_cb, self.statusIcon)
        indmenuItem.set_always_show_image (True)
        self.indmenu.append(indmenuItem)
        
    
    def main_cb(self, widget, data = None):
        print 'clicked'
        self.indmenu.show_all()
        self.indmenu.popup(None, None, gtk.status_icon_position_menu,
                           1, gtk.get_current_event_time(), self.statusIcon)
        
    def quit_cb(self, widget, data = None):
       gtk.main_quit()

    def popup_menu_cb(self, widget, button, time, data = None):
        print 'pu'
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, gtk.status_icon_position_menu,
                           3, time, self.statusIcon)

if __name__ == "__main__":
    helloWord = HelloTray()
