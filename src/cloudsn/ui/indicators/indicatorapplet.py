# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
#!/usr/bin/python
from gi.repository import Gtk
from cloudsn.core import config, utils, account
from cloudsn.ui import window
from cloudsn.core.indicator import Indicator
import indicate
from cloudsn.const import *
from cloudsn import logger

class IndicatorApplet (Indicator):

    def __init__(self):
        self.am = account.AccountManager.get_instance()
        
    def get_name(self):
        return _("Indicator Applet")

    def set_active(self, active):
        if active:
            self.server = indicate.indicate_server_ref_default()
            self.server.set_type("message.im")
            self.server.connect("server-display", self.on_server_display_cb)
            self.server.set_desktop_file(config.add_apps_prefix("cloudsn.desktop"))
            self.server.show()
            logger.debug("Indicator server created")
        else:
            #TODO Disable the indicators
            logger.debug("deactivate Not implemented")

    def create_indicator(self, acc):
        indicator = indicate.Indicator()
        indicator.set_property("name", acc.get_name())
        indicator.set_property("count", str(acc.get_total_unread()))
        indicator.set_property_icon("icon", acc.get_icon())
        indicator.show()
        indicator.connect("user-display", self.on_indicator_display_cb)
        acc.indicator = indicator
        indicator.account = acc
        acc.is_error_icon = False

    def update_account(self, acc):
        #We had a previous error but now the update works.
        if acc.is_error_icon:
            acc.indicator.set_property_icon("icon", acc.get_icon())
            acc.is_error_icon = False
        else:
            if len(acc.get_new_unread_notifications()) > 0:
                acc.indicator.set_property('draw-attention', 'true')

        if acc.get_total_unread() < 1:
            acc.indicator.set_property('draw-attention', 'false')
            
        acc.indicator.set_property("count", str(acc.get_total_unread()))

    def update_error(self, acc):
        if not acc.is_error_icon:
            acc.indicator.set_property_icon("icon", acc.get_icon())
            acc.is_error_icon = True
        acc.indicator.set_property("count", "0")
        
    def remove_indicator(self, acc):
        acc.indicator = None

    def on_server_display_cb(self, server, timestamp=None):
        for acc in self.am.get_accounts():
            if acc.get_active() and acc.indicator:
                acc.indicator.set_property('draw-attention', 'false')
	    win = window.MainWindow.get_instance()
        win.run()
    
    def on_indicator_display_cb(self, indicator, timestamp=None):
        indicator.set_property('draw-attention', 'false')
        indicator.account.activate ()
        
