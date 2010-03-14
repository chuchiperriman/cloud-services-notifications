import pygtk
pygtk.require('2.0')
import gtk
from cloudsn import const
from cloudsn.core import config, controller, utils
from cloudsn.ui import preferences, about
from cloudsn.core.indicator import Indicator
from cloudsn.const import *
import gettext

class StatusIconIndicator (Indicator):

    def set_active(self, active):
        if active:
            self.statusIcon = gtk.StatusIcon()
            self.statusIcon.set_from_pixbuf(config.get_cloudsn_icon())
            self.statusIcon.set_visible(True)
            self.statusIcon.set_tooltip(APP_LONG_NAME)
            self.statusIcon.connect('activate', self.main_cb, self.statusIcon)

            self.menu = self.create_pref_menu()        
            self.indmenu = self.create_main_menu()

            self.statusIcon.connect('popup-menu', self.popup_menu_cb, self.menu)
            self.statusIcon.set_visible(1)
        else:
            #TODO Discable the indicators
            logger.debug("deactivate Not implemented")

    def get_name(self):
        return _("Status Icon")

    def create_main_menu(self):
        indmenu = gtk.Menu()
        indmenuItem = gtk.MenuItem("")
        indmenuItem.get_child().set_markup("<b>%s</b>" % (APP_LONG_NAME))
        indmenuItem.connect('activate', self.quit_cb, self.statusIcon)
        indmenuItem.set_sensitive(False)
        indmenu.append(indmenuItem)

        return indmenu

    def create_pref_menu(self):
        menu = gtk.Menu()
        menuItem = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        menuItem.get_child().set_text(_("Update accounts"))
        menuItem.connect('activate', self.update_accounts_cb, self.statusIcon)
        menu.append(menuItem)
        menuItem = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        menuItem.connect('activate', self.preferences_cb, self.statusIcon)
        menu.append(menuItem)
        menuItem =  gtk.SeparatorMenuItem()
        menu.append(menuItem)
        menuItem = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        menuItem.connect('activate', self.about_cb, self.statusIcon)
        menu.append(menuItem)
        menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        menuItem.connect('activate', self.quit_cb, self.statusIcon)
        menu.append(menuItem)
        return menu
        
    def create_indicator(self, acc):
        indmenuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        pix = self.scale_pixbuf(acc.get_icon())
        
        """
        indmenuItem.set_image(gtk.image_new_from_pixbuf(pix))
        indmenuItem.get_child().set_label(("%s (%i)") % (acc.get_name(),acc.get_total_unread()))
        indmenuItem.connect('activate', self.acc_activate_cb, acc)
        indmenuItem.set_always_show_image (True)
        """
        indmenuItem = gtk.MenuItem()
        box = gtk.HBox()
        menu_icon = gtk.image_new_from_pixbuf(pix)
        box.pack_start(menu_icon, False, False)
        box.pack_start(gtk.Label(acc.get_name()), False, True, 10)
        total_label = gtk.Label(("(%i)") % (acc.get_total_unread()))
        box.pack_end(total_label, False, False)
        indmenuItem.add(box)
        indmenuItem.connect('activate', self.acc_activate_cb, acc)
        self.indmenu.append(indmenuItem)
        acc.indicator = indmenuItem
        acc.total_label = total_label
        acc.menu_icon = menu_icon
        acc.is_error_icon = False
    
    def update_account(self, acc):
        #We had a previous error but now the update works.
        if acc.is_error_icon:
            acc.menu_icon.set_from_pixbuf(self.scale_pixbuf(acc.get_icon()))
            acc.is_error_icon = False
        
        acc.total_label.set_label(("(%i)") % (acc.get_total_unread()))

    def update_error(self, acc):
        if not acc.is_error_icon:
            acc.menu_icon.set_from_pixbuf(self.scale_pixbuf(acc.get_icon()))
            acc.is_error_icon = True
        acc.total_label.set_label("")

    def remove_indicator(self, acc):
        self.indmenu.remove(acc.indicator)
        acc.indicator = None
        acc.total_label = None
        
    def preferences_cb(self, widget, acc = None):
        prefs = preferences.Preferences.get_instance()
        prefs.run()
    
    def update_accounts_cb(self, widget, acc = None):
        c = controller.Controller.get_instance()
        c.update_accounts()
        
    def acc_activate_cb(self, widget, acc = None):
        acc.activate()
        
    def main_cb(self, widget, data = None):
        self.indmenu.show_all()
        self.indmenu.popup(None, None, gtk.status_icon_position_menu,
                           1, gtk.get_current_event_time(), self.statusIcon)
        
    def quit_cb(self, widget, data = None):
       gtk.main_quit()
    
    def about_cb (self, widget, data = None):
        about.show_about_dialog()

    def popup_menu_cb(self, widget, button, time, data = None):
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, gtk.status_icon_position_menu,
                           3, time, self.statusIcon)
    def scale_pixbuf (self, pix):
        return pix.scale_simple(16,16,gtk.gdk.INTERP_BILINEAR)
