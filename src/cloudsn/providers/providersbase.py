from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.provider import Provider
from cloudsn.core import utils
from cloudsn.core import config
from xml.sax.handler import ContentHandler
from xml import sax
import gtk
import urllib2

class ProviderBase(Provider):

    def __init__(self, name,id_provider = None):
        Provider.__init__(self, name)
        self.id_provider = id_provider
        if not id_provider:
            self.id_provider = name
        self.id_provider = self.id_provider.lower()
        self.icon = gtk.gdk.pixbuf_new_from_file(config.add_data_prefix(self.id_provider + '.png'))
        self._builder = None

    def _create_dialog(self, parent):
        self._builder=gtk.Builder()
        self._builder.set_translation_domain("cloudsn")
        self._builder.add_from_file(config.add_data_prefix(self.id_provider + ".ui"))
        dialog = self._builder.get_object("main")
        dialog.set_transient_for(parent)
        self._builder.connect_signals(self)
        dialog.set_icon(self.get_icon())
        return dialog
    
    def populate_dialog(self, builder, acc):
        raise NotImplementedError("The provider must implement this method")
    
    def save_from_dialog(self, builder, account_name, acc = None):
        """ 
        Must return the new Account if acc is None or the modified account
        """
        raise NotImplementedError("The provider must implement this method")
    
    def create_account_dialog(self, account_name, parent):
        dialog = self._create_dialog(parent)
        account = None
        if dialog.run() == 0:
            account = self.save_from_dialog(self._builder, account_name)
        dialog.destroy()
        return account
        
    def edit_account_dialog(self, acc, parent):
        res = False
        dialog = self._create_dialog(parent)
        self.populate_dialog (self._builder, acc)
        if dialog.run() == 0:
            acc = self.save_from_dialog(self._builder, acc.get_name(), acc)
            res = True
        dialog.destroy()
        return res

    def _get_text_value (self, widget_name):
        return self._builder.get_object(widget_name).get_text()

    def _set_text_value (self, widget_name, value):
        return self._builder.get_object(widget_name).set_text(value)
        
