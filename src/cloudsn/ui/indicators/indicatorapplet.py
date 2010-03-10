#!/usr/bin/python
import pygtk
pygtk.require('2.0')
import gtk
from cloudsn.core import config, utils
from cloudsn.ui import preferences
from cloudsn.core.indicator import Indicator
import indicate
from cloudsn.const import *
from cloudsn import logger
from time import time

class IndicatorApplet (Indicator):

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
            #TODO Discable the indicators
            logger.debug("deactivate Not implemented")

    def create_indicator(self, acc):
        indicator = indicate.Indicator()
        indicator.set_property("name", acc.get_name())
        indicator.set_property_time("time", time())
        indicator.set_property_int("count", acc.get_total_unread())
        if acc.get_provider().get_icon() is not None:
            indicator.set_property_icon("icon", acc.get_provider().get_icon())
        indicator.show()
        indicator.connect("user-display", self.on_indicator_display_cb)
        acc.indicator = indicator
        indicator.account = acc

    def update_account(self, acc):
        #We had a previous error but now the update works.
        if acc.error_notified:
            acc.indicator.set_property_icon("icon", acc.get_provider().get_icon())
        acc.indicator.set_property_int("count", acc.get_total_unread())

    def update_error(self, acc):
        acc.indicator.set_property_icon("icon", utils.get_account_error_pixbuf(acc))
        acc.indicator.set_property_int("count", 0)
        
    def remove_indicator(self, acc):
        acc.indicator = None

    def on_server_display_cb(self, server):
        prefs = preferences.Preferences.get_instance()
        prefs.run()
    def on_indicator_display_cb(self, indicator):
        indicator.account.activate ()
        
