# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.providers.providersbase import ProviderUtilsBuilder
from cloudsn.core.keyring import Credentials
from cloudsn.core import utils
import urllib2
import re
import urllib
import xml.dom.minidom
import gtk

class GReaderProvider(ProviderUtilsBuilder):

    __default = None

    def __init__(self):
        if GReaderProvider.__default:
           raise GReaderProvider.__default
        ProviderUtilsBuilder.__init__(self, "Google Reader", "greader")

    @staticmethod
    def get_instance():
        if not GReaderProvider.__default:
            GReaderProvider.__default = GReaderProvider()
        return GReaderProvider.__default

    def load_account(self, props):
        acc = AccountCacheMails(props, self)
        acc.properties["activate_url"] = "http://reader.google.com"
        return acc

    def update_account (self, account):
        credentials = account.get_credentials()
        g = GreaderAtom (credentials.username, credentials.password)
        g.refreshInfo()

        news = []
        new_count = g.getTotalUnread() - account.total_unread
        if new_count > 1:
            news.append(Notification('',
                _('%d new unread news of %i') % (new_count, g.getTotalUnread()),
                ''))
        elif new_count == 1:
            news.append(Notification('',
                _('%d new unread new of %i') % (new_count, g.getTotalUnread()),
                ''))

        account.new_unread = news;

        account.total_unread = g.getTotalUnread()

    def get_dialog_def (self):
        return [{"label": "User", "type" : "str"},
                {"label": "Password", "type" : "pwd"},
                {"label": "Show notifications", "type" : "check"}]

    def populate_dialog(self, widget, acc):
        credentials = acc.get_credentials_save()
        self._set_text_value ("User", credentials.username)
        self._set_text_value ("Password", credentials.password)
        if "show_notifications" in acc:
            show_notifications = acc["show_notifications"]
        else:
            show_notifications = True

        self._set_check_value("Show notifications", show_notifications)

    def set_account_data_from_widget(self, account_name, widget, account=None):
        username = self._get_text_value ("User")
        password = self._get_text_value ("Password")
        show_notifications = self._get_check_value("Show notifications")
        if username=='' or password=='':
            raise Exception(_("The user name and the password are mandatory"))

        if not account:
            props = {'name' : account_name, 'provider_name' : self.get_name(),
                'show_notifications' : show_notifications,
                'activate_url' : "http://reader.google.com"}
            account = self.load_account(props)
        else:
            account["show_notifications"] = show_notifications

        credentials = Credentials(username, password)
        account.set_credentials(credentials)

        return account

class GreaderAtom:

	auth_url = "https://www.google.com/accounts/ClientLogin"
	reader_url = "https://www.google.com/reader/api/0/unread-count?%s"

	def __init__(self, user, pswd):
		self.username = user
		self.password = pswd
		# initialize authorization handler
		_cproc = urllib2.HTTPCookieProcessor()
		self.opener = urllib2.build_opener(_cproc)
		urllib2.install_opener(self.opener)

	def sendRequest(self):
	    auth_req_data = urllib.urlencode({'Email': self.username,
                                  'Passwd': self.password,
                                  'service': 'reader'})
        auth_req = urllib2.Request(self.auth_url, data=auth_req_data)
        auth_resp_content = urllib2.urlopen(auth_req).read()
        auth_resp_dict = dict(x.split('=') for x in auth_resp_content.split('\n') if x)
        auth_token = auth_resp_dict["Auth"]
        
        # Create a cookie in the header using the SID 
        header = {}
        header['Authorization'] = 'GoogleLogin auth=%s' % auth_token

        reader_req_data = urllib.urlencode({'all': 'true',
                                            'output': 'xml'})
        
        reader_url = self.reader_url % (reader_req_data)
        reader_req = urllib2.Request(reader_url, None, header)
		return urllib2.urlopen(reader_req)

	def parseDocument (self, data):
		self.feeds=list()

		def processObject (ob):
			for c in ob.getElementsByTagName ("string"):
				if c.getAttribute("name") == "id":
					ftype, s, feed = c.childNodes[0].nodeValue.partition("/")
					self.feeds.append({"type" : ftype,
							   "feed" : feed})
					break

			for c in ob.getElementsByTagName ("number"):
				if c.getAttribute("name") == "count":
					self.feeds[-1]["count"] = c.childNodes[0].nodeValue
					break

		doc = xml.dom.minidom.parseString(data)
		elist = doc.childNodes[0].getElementsByTagName("list")[0]
		for e2 in elist.getElementsByTagName("object"):
			processObject (e2)

	def refreshInfo(self):
		self.parseDocument (self.sendRequest().read())

	def getTotalUnread(self):
		count = 0
		for feed in self.feeds:
			if feed["type"] == "user":
				name = feed["feed"]
				name = name[name.rfind ("/") + 1:]
				if name == "reading-list":
					count = int(feed["count"])

		return count

