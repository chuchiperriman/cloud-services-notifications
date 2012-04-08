# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
"""
Based on imap.py:

    Copyright 2009-2010 cGmail Core Team
    https://code.launchpad.net/cgmail

"""
from cloudsn.providers.providersbase import ProviderBase
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.keyring import Credentials
from cloudsn.core import config
from cloudsn.core import utils
from cloudsn import logger
import imaplib
from email.Parser import HeaderParser
from gi.repository import Gtk

class ImapProvider(ProviderBase):
    __default = None

    def __init__(self):
        if ImapProvider.__default:
           raise ImapProvider.__default
        ProviderBase.__init__(self, "Imap")
        self.icon = Gtk.gdk.pixbuf_new_from_file(config.add_data_prefix('imap.png'))

    @staticmethod
    def get_instance():
        if not ImapProvider.__default:
            ImapProvider.__default = ImapProvider()
        return ImapProvider.__default

    def load_account(self, props):
        return AccountCacheMails(props, self)

    def update_account (self, account):
        account.new_unread = []
        notifications = {}
        all_inbox = []
        credentials = account.get_credentials()

        #Main inbox
        all_inbox.append(ImapBox (account["host"], credentials.username,
            credentials.password, account["port"],
            utils.get_boolean(account["ssl"])))

        if 'labels' in account.get_properties():
            labels = []
            labels += [l.strip() for l in account["labels"].split(",")]
            for l in labels:
                if l != '':
                    all_inbox.append(ImapBox (account["host"], credentials.username,
                        credentials.password, account["port"],
                        utils.get_boolean(account["ssl"]),
                        False, l))

        for g in all_inbox:
            mails = g.get_mails()
            logger.debug("Checking label %s: %i" %(g.mbox_dir, len(mails)))
            for mail_id, sub, fr in mails:
                notifications[mail_id] = sub
                if mail_id not in account.notifications:
                    n = Notification(mail_id, sub, fr)
                    account.new_unread.append (n)

        account.notifications = notifications

    def get_account_data_widget (self, account=None):
        self.conf_widget = ImapPrefs(account, self)
        return self.conf_widget.load()

    def set_account_data_from_widget(self, account_name, widget, account=None):
        return self.conf_widget.set_account_data(account_name)

class ImapPrefs:

    def __init__(self, account, provider):
        self.account = account
        self.provider = provider

    def load(self):
        self.builder=Gtk.Builder()
        self.builder.set_translation_domain("cloudsn")
        self.builder.add_from_file(config.add_data_prefix("imap-account.ui"))
        self.box = self.builder.get_object("container")
        self.labels_store = self.builder.get_object("labels_store")
        self.labels_treeview = self.builder.get_object("labels_treeview")
        self.builder.connect_signals(self)
        if self.account:
            credentials = self.account.get_credentials_save()
            self.builder.get_object("host_entry").set_text(self.account["host"])
            self.builder.get_object("username_entry").set_text(credentials.username)
            self.builder.get_object("password_entry").set_text(credentials.password)
            self.builder.get_object("port_entry").set_text(str(self.account["port"]))
            self.builder.get_object("ssl_check").set_active(utils.get_boolean(self.account["ssl"]))
            if 'labels' in self.account.get_properties():
                labels = [l.strip() for l in self.account["labels"].split(",")]
                for label in labels:
                    if label != '':
                        siter = self.labels_store.append()
                        self.labels_store.set_value(siter, 0, label)
        return self.box

    def set_account_data (self, account_name):
        host = self.builder.get_object("host_entry").get_text()
        port = self.builder.get_object("port_entry").get_text()
        username = self.builder.get_object("username_entry").get_text()
        password = self.builder.get_object("password_entry").get_text()
        ssl = self.builder.get_object("ssl_check").get_active()
        if host=='' or username=='' or password=='':
            raise Exception(_("The host, user name and the password are mandatory"))

        if not self.account:
            props = {"name" : account_name, "provider_name" : self.provider.get_name(),
                "host": host, "port": port, "ssl": ssl,
                "labels" : self.__get_labels()}
            self.account = AccountCacheMails(props, self.provider)
            self.account.notifications = {}
        else:
            self.account["host"] = host
            self.account["port"] = port
            self.account["ssl"] = ssl
            self.account["labels"] = self.__get_labels()

        credentials = Credentials(username, password)
        self.account.set_credentials(credentials)

        return self.account

    def __get_labels(self):
        labels = []
        def add(model, path, siter, labels):
            label = model.get_value(siter, 0)
            labels.append(label)
        self.labels_store.foreach(add, labels)
        labels_string = ""
        for label in labels:
            labels_string += label + ","
        return labels_string[:len(labels_string)-1]

    def add_label_button_clicked_cb (self, widget, data=None):
        siter = self.labels_store.append()
        self.labels_store.set_value(siter, 0, _("Type the label name here"))
        selection = self.labels_treeview.get_selection()
        selection.select_iter(siter)
        model, path_list = selection.get_selected_rows()
        path = path_list[0]
        self.labels_treeview.grab_focus()
        self.labels_treeview.set_cursor(path,self.labels_treeview.get_column(0), True)


    def del_label_button_clicked_cb (self, widget, data=None):
        selection = self.labels_treeview.get_selection()
        model, path_list = selection.get_selected_rows()
        if path_list:
            path = path_list[0]
            siter = model.get_iter(path)
            self.labels_store.remove(siter)

    def label_cell_edited_cb(self, cell, path, new_text):
        siter = self.labels_store.get_iter((int(path), ))
        self.labels_store.set_value(siter, 0, new_text)


class ImapBoxConnectionError(Exception): pass
class ImapBoxAuthError(Exception): pass

class ImapBox:
	def __init__(self, host, user, password,
			port = 143, ssl = False,
			use_default_mbox = True,
			mbox_dir = None):
		self.user = user
		self.password = password
		self.port = int(port)
		self.host = host
		self.ssl = ssl
		self.use_default_mbox = use_default_mbox
		self.mbox_dir = mbox_dir

		self.mbox = None

	def __connect(self):
		if not self.ssl:
			self.mbox = imaplib.IMAP4(self.host, self.port)
		else:
			self.mbox = imaplib.IMAP4_SSL(self.host, self.port)

		self.mbox.login(self.user, self.password)

	def get_mails(self):

		try:
			self.__connect()
		except ImapBoxConnectionError:
			raise ImapBoxConnectionError()
		except ImapBoxAuthError:
			raise ImapBoxAuthError()

		mails = []
		try:
			if self.use_default_mbox:
				result, message = self.mbox.select(readonly=1)
			else:
				result, message = self.mbox.select(self.mbox_dir, readonly=1)
			if result != 'OK':
				raise Exception, message

			# retrieve only unseen messages
			typ, data = self.mbox.search(None, 'UNSEEN')
			for num in data[0].split():
				# fetch only needed fields
				f = self.mbox.fetch(num, '(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM MESSAGE-ID)])')
				hp = HeaderParser()
				m = hp.parsestr(f[1][0][1])
				sub = utils.mime_decode(m['subject'])
				fr = utils.mime_decode(m['from'])
				mails.append([m['Message-ID'], sub, fr])
		except Exception, e:
			print str(e)

		self.mbox.logout()
		return mails

