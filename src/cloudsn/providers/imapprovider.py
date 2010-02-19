"""
Based on imap.py:

    Copyright 2009-2010 cGmail Core Team
    https://code.launchpad.net/cgmail
    
"""
from cloudsn.core.provider import Provider
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core import config
from cloudsn.core import utils
import imaplib
from email.Parser import HeaderParser
import gtk

class ImapProvider(Provider):
    __default = None

    def __init__(self):
        if ImapProvider.__default:
           raise ImapProvider.__default
        Provider.__init__(self, "Imap")
        self.icon = gtk.gdk.pixbuf_new_from_file(config.add_data_prefix('imap.png'))

    @staticmethod
    def get_instance():
        if not ImapProvider.__default:
            ImapProvider.__default = ImapProvider()
        return ImapProvider.__default

    def load_account(self, props):
        return AccountCacheMails(props, self)
    
    def update_account (self, account):
        #TODO Check port, ssl etc correctly
        g = ImapBox (account["host"], account["username"], account["password"], account["port"], account["ssl"])
        account.new_unread = []
        mails = g.get_mails()
        for mail_id, sub, fr in mails:
            if mail_id not in account.notifications:
                n = Notification(mail_id, sub, fr)
                account.notifications[mail_id] = sub
                account.new_unread.append (n)

    def _create_dialog(self, parent):
        builder=gtk.Builder()
        builder.set_translation_domain("cloudsn")
        builder.add_from_file(config.add_data_prefix("imap-account.ui"))
        dialog = builder.get_object("dialog")
        dialog.set_icon(self.get_icon())
        dialog.set_transient_for(parent)
        return (builder, dialog)

    def create_account_dialog(self, account_name, parent):
        builder, dialog = self._create_dialog(parent)
        account = None
        if dialog.run() == 0:
            host = builder.get_object("host_entry").get_text()
            username = builder.get_object("username_entry").get_text()
            password = builder.get_object("password_entry").get_text()
            #TODO check valid values
            port = int(builder.get_object("port_entry").get_text())
            ssl = builder.get_object("ssl_check").get_active()
            props = {'name' : account_name, 'provider_name' : self.get_name(),
                'host' : host, 'username' : username, 'password' : password,
                'port' : port, 'ssl' : ssl}
            account = self.load_account(props)
        dialog.destroy()
        return account

    def edit_account_dialog(self, acc, parent):
        res = False
        builder, dialog = self._create_dialog(parent)
        builder.get_object("host_entry").set_text(acc["host"])
        builder.get_object("username_entry").set_text(acc["username"])
        builder.get_object("password_entry").set_text(acc["password"])
        builder.get_object("port_entry").set_text(str(acc["port"]))
        builder.get_object("ssl_check").set_active(utils.get_boolean(acc["ssl"]))
        account = None
        if dialog.run() == 0:
            acc["host"] = builder.get_object("host_entry").get_text()
            acc["username"] = builder.get_object("username_entry").get_text()
            acc["password"] = builder.get_object("password_entry").get_text()
            acc["port"] = int(builder.get_object("port_entry").get_text())
            acc["ssl"] = builder.get_object("ssl_check").get_active()
            res = True
        dialog.destroy()
        return res

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


if __name__ == "__main__":
	i = ImapBox("", "", "", 993, True)
	print 'aaa'
	print i.get_mails()
