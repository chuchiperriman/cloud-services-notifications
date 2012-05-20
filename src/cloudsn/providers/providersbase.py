# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.provider import Provider
from cloudsn.core import utils
from cloudsn.core import config
from cloudsn.ui.utils import create_provider_widget, get_widget_by_label
from xml.sax.handler import ContentHandler
from xml import sax
from gi.repository import Gtk, GdkPixbuf
import urllib2

class ProviderBase(Provider):

    def __init__(self, name, id_provider = None):
        Provider.__init__(self, name)
        self.id_provider = id_provider
        if not id_provider:
            self.id_provider = name
        self.id_provider = self.id_provider.lower()
        self.icon = GdkPixbuf.Pixbuf.new_from_file(config.add_data_prefix(self.id_provider + '.png'))


class ProviderGtkBuilder(ProviderBase):

    def __init__(self, name,id_provider = None):
        ProviderBase.__init__(self, name, id_provider)
        self._builder = None

    def _create_dialog(self, parent):
        self._builder=Gtk.Builder()
        self._builder.set_translation_domain("cloudsn")
        self._builder.add_from_file(config.add_data_prefix(self.id_provider + ".ui"))
        dialog = self._builder.get_object("main")
        self._builder.connect_signals(self)
        return dialog

    def populate_dialog(self, builder, acc):
        raise NotImplementedError("The provider must implement this method")

    def get_account_data_widget (self, account=None):
        box = self._create_dialog(parent).get_child()
        if account:
            self.populate_dialog(self.builder, account)

    def _get_text_value (self, widget_name):
        return self._builder.get_object(widget_name).get_text()

    def _set_text_value (self, widget_name, value):
        return self._builder.get_object(widget_name).set_text(value)


class ProviderUtilsBuilder(ProviderBase):

    def __init__(self, name,id_provider = None):
        ProviderBase.__init__(self, name, id_provider)
        self.box=None

    def get_dialog_def(self):
        raise NotImplementedError("The provider must implement this method")

    def populate_dialog(widget, account):
        raise NotImplementedError("The provider must implement this method")

    def get_account_data_widget (self, account=None):
        self.box = create_provider_widget (self.get_dialog_def())
        if account:
            self.populate_dialog(self.box, account)
        return self.box

    def _get_text_value (self, label):
        return get_widget_by_label(self.box, label).get_text()

    def _set_text_value (self, label, value):
        return get_widget_by_label(self.box, label).set_text(value)

    def _get_check_value (self, label):
        return get_widget_by_label(self.box, label).get_active()

    def _set_check_value (self, label, value):
        return get_widget_by_label(self.box, label).set_active(utils.get_boolean(value))

