from account import AccountData
from provider import Provider
import urllib2
import re
import urllib
import xml.dom.minidom
import config
import gtk
import utils

ICON = "/home/perriman/dev/cloud-services-notifications/data/greader.png"

_provider = None

class GReaderProvider(Provider):
    accounts = None
    def __init__(self):
        Provider.__init__(self, "Google Reader")
        self.icon = gtk.gdk.pixbuf_new_from_file(ICON)

    def get_accounts (self):
        if self.accounts is None:
            sc = config.GetSettingsController()
            self.accounts = []
            for account_name in sc.get_account_list_by_type("greader"):
                acc_config = sc.get_account_config(account_name)
                account = GReaderAccount (account_name)
                account.username = acc_config["username"]
                account.password = acc_config["password"]
                self.accounts.append (account)
                
        return self.accounts

    def update_account (self, account):
        g = GreaderAtom (account.username, account.password)
        g.refreshInfo()
        account.unread = g.getTotalUnread()

def GetGReaderProvider ():
    global _provider
    if _provider is None:
        _provider = GReaderProvider()
    return _provider

class GReaderAccount (AccountData):
    def __init__(self, name):
        AccountData.__init__(self, name, GetGReaderProvider())
    def activate (self):
        utils.show_url ("http://reader.google.com")


class GreaderAtom:
	
	login_url = "https://www.google.com/accounts/ServiceLogin"
	auth_url = "https://www.google.com/accounts/ServiceLoginAuth"
	reader_url = "https://www.google.com/reader/api/0/unread-count"
	
	def __init__(self, user, pswd):
		self.username = user
		self.password = pswd
		# initialize authorization handler
		_cproc = urllib2.HTTPCookieProcessor()
		self.opener = urllib2.build_opener(_cproc)
		urllib2.install_opener(self.opener)

	def sendRequest(self):
		f = urllib2.urlopen(self.login_url)
		data = f.read()
		galx_match_obj = re.search(r'name="GALX"\s*value="([^"]+)"', data, re.IGNORECASE)
		galx_value = galx_match_obj.group(1) if galx_match_obj.group(1) is not None else ''
		params = urllib.urlencode({'Email':self.username,
					'Passwd':self.password,
					'GALX':galx_value})
			   
		f = urllib2.urlopen(self.auth_url, params)

		return self.opener.open(self.reader_url)

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



