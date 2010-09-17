# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.keyring import Credentials
from cloudsn.core.provider import Provider
from cloudsn.core import utils
from cloudsn.core import config
from cloudsn import logger
import gtk
import urllib2

import_error = None

try:
    import feedparser
except Exception, e:
    logger.error("Error loading the FeedsProvider: %s", e)
    import_error = Exception(_("You need install the python-feedparser module to use this provider"))

class FeedsProvider(Provider):

    __default = None

    def __init__(self):
        if FeedsProvider.__default:
           raise FeedsProvider.__default
        Provider.__init__(self, _("RSS news"))
        self.icon = gtk.gdk.pixbuf_new_from_file(config.add_data_prefix('rss.png'))

    @staticmethod
    def get_instance():
        if not FeedsProvider.__default:
            FeedsProvider.__default = FeedsProvider()
        return FeedsProvider.__default

    def get_import_error(self):
        return import_error

    def load_account(self, props):
        pass
        """
        acc = AccountCacheMails(props, self)

        #Hack for gmail domains like mail.quiter.com
        #TODO check this when the user change the configuration too
        domain = None
        try:
            user, tmp, domain = acc.get_credentials().username.partition('@')
        except Exception, e:
            logger.exception("Cannot load credentials for account "+acc.get_name()+", continue: %s", e)

        if domain and domain != "gmail.com":
            activate_url = "https://mail.google.com/a/" + domain
        else:
            activate_url = "https://mail.google.com/a/"

        acc.properties["activate_url"] = activate_url
        return acc
        """

    def update_account (self, account):
        pass

    def get_account_data_widget (self, account=None):
        self.builder=gtk.Builder()
        self.builder.set_translation_domain("cloudsn")
        self.builder.add_from_file(config.add_data_prefix("gmail-account.ui"))
        box = self.builder.get_object("container")
        self.labels_store = self.builder.get_object("labels_store")
        self.labels_treeview = self.builder.get_object("labels_treeview")
        self.builder.connect_signals(self)
        if account:
            credentials = account.get_credentials_save()
            self.builder.get_object("username_entry").set_text(credentials.username)
            self.builder.get_object("password_entry").set_text(credentials.password)
            if 'labels' in account.get_properties():
                labels = [l.strip() for l in account["labels"].split(",")]
                for label in labels:
                    if label != '':
                        siter = self.labels_store.append()
                        self.labels_store.set_value(siter, 0, label)
        return box

    def set_account_data_from_widget(self, account_name, widget, account=None):
        username = self.builder.get_object("username_entry").get_text()
        password = self.builder.get_object("password_entry").get_text()
        if not account:
            props = {"name" : account_name, "provider_name" : self.get_name(),
                "activate_url" : "http://gmail.google.com",
                "labels" : self.__get_labels()}
            account = AccountCacheMails(props, self)
            account.notifications = {}
        else:
            account["labels"] = self.__get_labels()

        credentials = Credentials(username, password)
        account.set_credentials(credentials)

        return account

