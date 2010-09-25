# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-

from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.keyring import Credentials
from cloudsn.core.provider import Provider
from cloudsn.core import utils
from cloudsn.core import config
from cloudsn import logger
from xml.sax.handler import ContentHandler
from xml import sax
import gtk
import urllib2

class GMailProvider(Provider):

    __default = None

    def __init__(self):
        if GMailProvider.__default:
           raise GMailProvider.__default
        Provider.__init__(self, "GMail")
        self.icon = gtk.gdk.pixbuf_new_from_file(config.add_data_prefix('gmail.png'))

    @staticmethod
    def get_instance():
        if not GMailProvider.__default:
            GMailProvider.__default = GMailProvider()
        return GMailProvider.__default

    def load_account(self, props):
        return GMailAccount(props, self)

    def update_account (self, account):
        news = []
        notifications = {}
        labels = []
        if 'labels' in account.get_properties():
            labels += [l.strip() for l in account["labels"].split(",")]

        if 'inbox' not in labels and '' not in labels:
            labels.append('inbox')

        credentials = account.get_credentials()
        for label in labels:
            g = GmailAtom (credentials.username, credentials.password, label)
            g.refreshInfo()

            for mail in g.get_mails():
                notifications[mail.mail_id] = mail
                if mail.mail_id not in account.notifications:
                    news.append (Notification(mail.mail_id, mail.title, mail.author_name))

        account.new_unread = news;
        account.notifications = notifications

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
                "labels" : self.__get_labels()}
            account = AccountCacheMails(props, self)
            account.notifications = {}
        else:
            account["labels"] = self.__get_labels()

        credentials = Credentials(username, password)
        account.set_credentials(credentials)

        return account

class GMailAccount(AccountCacheMails):
    def __init__(self, properties, provider):
        AccountCacheMails.__init__(self, properties, provider)

    def activate (self):
        #Hack for gmail domains like mail.quiter.com
        #TODO check this when the user change the configuration too
        domain = None
        try:
            user, tmp, domain = self.get_credentials().username.partition('@')
        except Exception, e:
            logger.exception("Cannot load credentials for account "+acc.get_name()+", continue: %s", e)

        if domain and domain != "gmail.com":
            activate_url = "https://mail.google.com/a/" + domain
        else:
            activate_url = "https://mail.google.com/a/"

        self.properties["activate_url"] = activate_url

        AccountCacheMails.activate(self)

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

    def __init__(self, user, pswd, label = None):
        self.m = MailHandler()
        self.label = label
        # initialize authorization handler
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password( self.realm, self.host, user, pswd)
        self.opener = urllib2.build_opener(auth_handler)

    def sendRequest(self):
        url = self.url
        if self.label:
            url = url + "/" + self.label
        return self.opener.open(url)

    def refreshInfo(self):
        p = sax.parseString( self.sendRequest().read(), self.m)

    def getUnreadMsgCount(self):
        return self.m.getUnreadMsgCount()

    def get_mails (self):
        return self.m.entries

