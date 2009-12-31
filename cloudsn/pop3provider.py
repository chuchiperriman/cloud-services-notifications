"""
Based on pop3.py:

    Copyright 2009-2010 cGmail Core Team
    https://code.launchpad.net/cgmail
    
"""
import poplib
from email.Parser import Parser as EmailParser
from email.header import decode_header

import provider
import account
import config
import gtk

class Pop3Provider(provider.Provider):

    __default = None

    def __init__(self):
        if Pop3Provider.__default:
           raise Pop3Provider.__default
        provider.Provider.__init__(self, "Pop3")
        self.icon = gtk.gdk.pixbuf_new_from_file(config.get_data_dir() + '/pop3.png')

    @staticmethod
    def get_instance():
        if not Pop3Provider.__default:
            Pop3Provider.__default = Pop3Provider()
        return Pop3Provider.__default
        
    def register_accounts (self):
        sc = config.SettingsController.get_instance()
        am = account.AccountManager.get_instance()
        for account_name in sc.get_account_list_by_provider(self):
            acc_config = sc.get_account_config(account_name)
            acc = Pop3Account (account_name, acc_config["host"], acc_config["username"], acc_config["password"])
            am.add_account (acc)

    def update_account (self, account):
        print 'updating'
        g = PopBox (account["username"], account["password"], account["host"])
        news = []
        mails = g.get_mails()
        account.unread = len(mails)
        for mail_id, sub, fr in mails:
            if mail_id not in account.mails:
                account.mails[mail_id] = sub
                news.append (mail_id)

        account.new_unread = len (news);

class Pop3Account (account.AccountData):

    def __init__(self, name, host, username, password):
        account.AccountData.__init__(self, name, Pop3Provider.get_instance())
        #TODO Add port, ssl etc
        self["host"] = host
        self["username"] = username
        self["password"] = password
        self.mails = {}
    
def mime_decode(str):
    strn, encoding = decode_header(str)[0]
    if encoding is None:
            return strn
    else:
            return strn.decode(encoding, "replace")

class PopBoxConnectionError(Exception): pass
class PopBoxAuthError(Exception): pass

class PopBox:
    def __init__(self, user, password, host, port = 110, ssl = False):
        self.user = user
        self.password = password
        self.host = host
        self.port = int(port)
        self.ssl = ssl

        self.mbox = None
        self.parser = EmailParser()

    def __connect(self):
        try:
            if not self.ssl:
                self.mbox = poplib.POP3(self.host, self.port)
            else:
                self.mbox = poplib.POP3_SSL(self.host, self.port)
        except Exception:
            raise PopBoxConnectionError()

        try:
            self.mbox.user(self.user)
            self.mbox.pass_(self.password)
        except poplib.error_proto:
            raise PopBoxAuthError()

    def get_mails(self):
        try:
            self.__connect()
        except PopBoxConnectionError:
            raise PopBoxConnectionError()
        except PopBoxAuthError:
            raise PopBoxAuthError()

        messages = []
        msgs = self.mbox.list()[1]
        for msg in msgs:
	        
            try:
                msgNum = int(msg.split(" ")[0])
                msgSize = int(msg.split(" ")[1])

                # retrieve only the header
                st = "\n".join(self.mbox.top(msgNum, 0)[1])
                #print st
                #print "----------------------------------------"
                msg = self.parser.parsestr(st, True) # header only
                sub = mime_decode(msg.get("Subject"))
                msgid = msg.get("Message-Id")
                if not msgid:
                    msgid = hash(msg.get("Received") + sub)
                fr = mime_decode(msg.get("From"))
                messages.append( [msgid, sub, fr] )
            except poplib.error_proto, e:
                print "Warning: pop3 error %s" % e
		
        self.mbox.quit()
        return messages
