from cloudsn.core.account import AccountCacheMails, AccountManager
from cloudsn.providers.providersbase import ProviderBase
from cloudsn.core import utils
from cloudsn.core import config
import urllib2
import re
import urllib
import xml.dom.minidom
import gtk

class GReaderProvider(ProviderBase):

    __default = None

    def __init__(self):
        if GReaderProvider.__default:
           raise GReaderProvider.__default
        ProviderBase.__init__(self, "Google Reader", "greader")

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
        g = GreaderAtom (account["username"], account["password"])
        g.refreshInfo()
        account.total_unread = g.getTotalUnread()

    def populate_dialog(self, builder, acc):
        self._set_text_value ("username_entry",acc["username"])
        self._set_text_value ("password_entry", acc["password"])
    
    def save_from_dialog(self, builder, account_name, acc = None):
        if not acc:
            username = self._get_text_value ("username_entry")
            password = self._get_text_value ("password_entry")
            props = {'name' : account_name, 'provider_name' : self.get_name(),
                'username' : username, 'password' : password,
                'activate_url' : "http://reader.google.com"}
            acc = self.load_account(props)
        else:
            acc["username"] = self._get_text_value ("username_entry")
            acc["password"] = self._get_text_value ("password_entry")
        
        return acc
        
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



