# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from cloudsn.core.account import Account, AccountManager, Notification
from cloudsn.core.keyring import Credentials
from cloudsn.providers.providersbase import ProviderUtilsBuilder
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

class FeedsProvider(ProviderUtilsBuilder):

    __default = None

    def __init__(self):
        if FeedsProvider.__default:
           raise FeedsProvider.__default
        ProviderUtilsBuilder.__init__(self, _("RSS news"), 'rss')
        self.icon = gtk.gdk.pixbuf_new_from_file(config.add_data_prefix('rss.png'))

    @staticmethod
    def get_instance():
        if not FeedsProvider.__default:
            FeedsProvider.__default = FeedsProvider()
        return FeedsProvider.__default

    def load_account(self, props):
        return FeedAccount(props, self)

    def get_import_error(self):
        return import_error

    def update_account (self, account):
        print account["url"]
        d = feedparser.parse(account["url"])
        print d.feed.title

    def get_dialog_def (self):
        return [{"label": "Url", "type" : "str"}]

    def populate_dialog(self, widget, acc):
        self._set_text_value ("Url",acc["url"])

    def set_account_data_from_widget(self, account_name, widget, account=None):
        url = self._get_text_value ("Url")
        if url=='':
            raise Exception(_("The url is mandatory"))

        #TODO check valid values
        if not account:
            props = {'name' : account_name, 'provider_name' : self.get_name(),
                'url' : url}
            account = self.load_account(props)
        else:
            account["url"] = url
        return account

class FeedAccount (Account):
    def __init__ (self, properties, provider):
        Account.__init__(self, properties, provider)
    def has_credentials(self):
        return False

