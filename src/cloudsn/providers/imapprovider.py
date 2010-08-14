# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
"""
Based on imap.py:

    Copyright 2009-2010 cGmail Core Team
    https://code.launchpad.net/cgmail
    
"""
from cloudsn.providers.providersbase import ProviderUtilsBuilder
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.keyring import Credentials
from cloudsn.core import config
from cloudsn.core import utils
import imaplib
from email.Parser import HeaderParser
import gtk

class ImapProvider(ProviderUtilsBuilder):
    __default = None

    def __init__(self):
        if ImapProvider.__default:
           raise ImapProvider.__default
        ProviderUtilsBuilder.__init__(self, "Imap")
        self.icon = gtk.gdk.pixbuf_new_from_file(config.add_data_prefix('imap.png'))

    @staticmethod
    def get_instance():
        if not ImapProvider.__default:
            ImapProvider.__default = ImapProvider()
        return ImapProvider.__default

    def load_account(self, props):
        return AccountCacheMails(props, self)
    
    def update_account (self, account):
        credentials = account.get_credentials()
        g = ImapBox (account["host"], credentials.username, 
            credentials.password, account["port"],
            utils.get_boolean(account["ssl"]))
        account.new_unread = []
        notifications = {}
        mails = g.get_mails()
        for mail_id, sub, fr in mails:
            notifications[mail_id] = sub
            if mail_id not in account.notifications:
                n = Notification(mail_id, sub, fr)
                account.new_unread.append (n)
        account.notifications = notifications

    def get_dialog_def (self):
        return [{"label": "Host", "type" : "str"},
                {"label": "User", "type" : "str"},
                {"label": "Password", "type" : "pwd"},
                {"label": "Port", "type" : "str"},
                {"label": "Use SSL", "type" : "check"}]
    
    def populate_dialog(self, widget, acc):
        credentials = acc.get_credentials_save()
        self._set_text_value ("Host",acc["host"])
        self._set_text_value ("User", credentials.username)
        self._set_text_value ("Password", credentials.password)
        self._set_text_value ("Port",str(acc["port"]))
        self._set_check_value ("Use SSL",utils.get_boolean(acc["ssl"]))
    
    def set_account_data_from_widget(self, account_name, widget, account=None):
        host = self._get_text_value ("Host")
        username = self._get_text_value ("User")
        password = self._get_text_value ("Password")
        port = self._get_text_value ("Port")
        ssl = self._get_check_value("Use SSL")
        if host=='' or username=='' or password=='':
            raise Exception(_("The host, user name and the password are mandatory"))
        
        #TODO check valid values
        if not account:
            props = {'name' : account_name, 'provider_name' : self.get_name(),
                'host' : host, 'port' : port, 'ssl' : ssl}
            account = self.load_account(props)
        else:
            account["host"] = host
            account["port"] = int(port)
            account["ssl"] = ssl
        account.set_credentials(Credentials(username, password))
        return account
        
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

