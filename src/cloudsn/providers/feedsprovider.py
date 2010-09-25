# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from cloudsn.core.account import Account, AccountManager, Notification
from cloudsn.core.keyring import Credentials
from cloudsn.providers.providersbase import ProviderUtilsBuilder
from cloudsn.core.provider import Provider
from cloudsn.core import utils, indicator, config
from cloudsn import logger
from os.path import join
import os
import gtk
import urllib2
import csv

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

        doc = feedparser.parse(account["url"])

        account.new_unread = []
        for entry in doc.entries:
            entry_id = entry.get("id", entry.title)
            if not account.has_feed(entry_id):
                account.add_feed(entry_id, False)
                n = Notification(entry_id, entry.title, doc.feed.title)
                account.new_unread.append (n)

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

        doc = feedparser.parse(account["url"])
        account["activate_url"] = doc.feed.link
        return account

class FeedAccount (Account):
    def __init__ (self, properties, provider):
        Account.__init__(self, properties, provider)
        self.total_unread = 0
        self.cache = FeedCache(self)
        self.cache.load()
        for f in self.cache.feeds.values():
            if not f.feed_read:
                self.total_unread = self.total_unread + 1

        self.new_unread = []

    def get_new_unread_notifications(self):
        return self.new_unread

    def add_feed(self, feed_id, feed_read):
        self.cache.add_feed(feed_id, feed_read);
        if not feed_read:
            self.total_unread = self.total_unread + 1
        self.cache.save()

    def has_feed(self, feed_id):
        return feed_id in self.cache.feeds

    def has_credentials(self):
        return False

    def get_total_unread (self):
        return self.total_unread

    def can_mark_read(self):
        return True

    def mark_read(self):
        for f in self.cache.feeds.values():
            f.feed_read = True
        self.cache.save()
        self.total_unread = 0
        #Update the unread items
        indicator.IndicatorManager.get_instance().get_indicator().update_account(self)

    def activate (self):
        self.mark_read()
        Account.activate(self)

class Feed:
    def __init__(self, data):
        self.feed_num = int(data[0])
        self.feed_id = data[1]
        self.feed_read = utils.get_boolean(data[2])

class FeedCache:
    def __init__(self, account):
        self.account = account

    def get_filename(self):
        return "feed-" + utils.get_safe_filename(self.account.get_name()) + ".csv"

    def get_filepath(self):
        return join(config.get_ensure_cache_path(), self.get_filename())

    def load(self):
        file_path = self.get_filepath()
        if not os.path.exists (file_path):
            f = open(file_path, "w")
            f.close()
        reader = csv.reader(open(file_path, "r+"), delimiter='\t')

        self.feeds = dict()
        self.last_num = -1
        for data in reader:
            feed_num = int(data[0])
            self.feeds[data[1]] = Feed(data)
            if feed_num > self.last_num:
                self.last_num = feed_num

    def save(self):
        #TODO Only write the last 200 feeds
        rows = sorted(self.feeds.values(), key=lambda x: int(x.feed_num))
        num = len(rows)
        if num > 300:
            rows = rows[num - 300:]
        writer = csv.writer(open(self.get_filepath(), "w+"), delimiter='\t')
        num = 0
        for f in rows:
            writer.writerow((num, f.feed_id, f.feed_read))
            num = num + 1

    def add_feed(self, feed_id, feed_read):
        self.last_num = self.last_num + 1
        self.feeds[feed_id] = Feed((self.last_num, feed_id, feed_read))

