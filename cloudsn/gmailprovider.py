from account import AccountData
from provider import Provider
from xml.sax.handler import ContentHandler
from xml import sax
import config
import gtk
import utils
import urllib2

ICON = "/home/perriman/dev/cloud-services-notifications/data/gmail.png"

_provider = None

class GMailProvider(Provider):
    accounts = None
    def __init__(self):
        Provider.__init__(self, "GMail")
        self.icon = gtk.gdk.pixbuf_new_from_file(ICON)

    def get_accounts (self):
        if self.accounts is None:
            sc = config.GetSettingsController()
            self.accounts = []
            for account_name in sc.get_account_list_by_type("gmail"):
                acc_config = sc.get_account_config(account_name)
                account = GMailAccount (account_name)
                account.username = acc_config["username"]
                account.password = acc_config["password"]
                self.accounts.append (account)
                
        return self.accounts

    def update_account (self, account):
        g = GmailAtom (account.username, account.password)
        g.refreshInfo()
        """
        if g.getUnreadMsgCount () > 0:
            message = ""
            for i in range (g.getUnreadMsgCount ()):
                message += "- \n" + g.getMsgTitle (i) + "\n"
        """
        account.unread = g.getUnreadMsgCount ()
        news = []
        for mail in g.get_mails():
            if mail.mail_id not in account.mails:
                account.mails[mail.mail_id] = mail
                news.append (mail)

        account.new_unread = len (news);

def GetGMailProvider ():
    global _provider
    if _provider is None:
        _provider = GMailProvider()
    return _provider

class GMailAccount (AccountData):
    mails = {}
    def __init__(self, name):
        AccountData.__init__(self, name, GetGMailProvider())
    
    def activate (self):
        utils.show_url ("http://gmail.google.com")


# Auxiliar structure
class Mail:
    mail_id=""
    title=""
    summary=""
    author_name=""
    author_addr=""

# Sax XML Handler
class MailHandler(ContentHandler):
	
	# Tags
    TAG_FEED = "feed"
    TAG_FULLCOUNT = "fullcount"
    TAG_ENTRY = "entry"
    TAG_TITLE = "title"
    TAG_SUMMARY = "summary"
    TAG_AUTHOR = "author"
    TAG_NAME = "name"
    TAG_EMAIL = "email"
    TAG_ID = "id"

    # Path the information
    PATH_FULLCOUNT = [ TAG_FEED, TAG_FULLCOUNT ]
    PATH_TITLE = [ TAG_FEED, TAG_ENTRY, TAG_TITLE ]
    PATH_ID = [ TAG_FEED, TAG_ENTRY, TAG_ID ]
    PATH_SUMMARY = [ TAG_FEED, TAG_ENTRY, TAG_SUMMARY ]
    PATH_AUTHOR_NAME = [ TAG_FEED, TAG_ENTRY, TAG_AUTHOR, TAG_NAME ]
    PATH_AUTHOR_EMAIL = [ TAG_FEED, TAG_ENTRY, TAG_AUTHOR, TAG_EMAIL ]

    def __init__(self):
        self.startDocument()

    def startDocument(self):
        self.entries=list()
        self.actual=list()
        self.mail_count="0"

    def startElement( self, name, attrs):
        # update actual path
        self.actual.append(name)

        # add a new email to the list
        if name=="entry":
            m = Mail()
            self.entries.append(m)

    def endElement( self, name):
        # update actual path
        self.actual.pop()

    def characters( self, content):
        # New messages count
        if (self.actual==self.PATH_FULLCOUNT):
            self.mail_count = self.mail_count+content

        # Message title
        if (self.actual==self.PATH_TITLE):
            temp_mail=self.entries.pop()
            temp_mail.title=temp_mail.title+content
            self.entries.append(temp_mail)
		
        if (self.actual==self.PATH_ID):
            temp_mail=self.entries.pop()
            temp_mail.mail_id=temp_mail.mail_id+content
            self.entries.append(temp_mail)

        # Message summary
        if (self.actual==self.PATH_SUMMARY):
            temp_mail=self.entries.pop()
            temp_mail.summary=temp_mail.summary+content
            self.entries.append(temp_mail)

        # Message author name
        if (self.actual==self.PATH_AUTHOR_NAME):
            temp_mail=self.entries.pop()
            temp_mail.author_name=temp_mail.author_name+content
            self.entries.append(temp_mail)

        # Message author email
        if (self.actual==self.PATH_AUTHOR_EMAIL):
            temp_mail=self.entries.pop()
            temp_mail.author_addr=temp_mail.author_addr+content
            self.entries.append(temp_mail)

    def getUnreadMsgCount(self):
        return int(self.mail_count)

# The mail class
class GmailAtom:

    realm = "New mail feed" 
    host = "https://mail.google.com"
    url = host + "/mail/feed/atom"

    def __init__(self, user, pswd):
        self.m = MailHandler()
        # initialize authorization handler
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password( self.realm, self.host, user, pswd)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)

    def sendRequest(self):
        return urllib2.urlopen(self.url)

    def refreshInfo(self):
        # get the page and parse it
        p = sax.parseString( self.sendRequest().read(), self.m)

    def getUnreadMsgCount(self):
        return self.m.getUnreadMsgCount()

    def get_mails (self):
        return self.m.entries


