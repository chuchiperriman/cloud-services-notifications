"""
Based on pop3.py:

    Copyright 2009-2010 cGmail Core Team
    https://code.launchpad.net/cgmail
    
"""
from cloudsn.providers.providersbase import ProviderBase
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core import config
from cloudsn.core import utils
from cloudsn import logger

import poplib
from email.Parser import Parser as EmailParser
from email.header import decode_header
import gtk

class Pop3Provider(ProviderBase):

    __default = None

    def __init__(self):
        if Pop3Provider.__default:
           raise Pop3Provider.__default
        ProviderBase.__init__(self, "Pop3")

    @staticmethod
    def get_instance():
        if not Pop3Provider.__default:
            Pop3Provider.__default = Pop3Provider()
        return Pop3Provider.__default

    def load_account(self, props):
        return AccountCacheMails(props, self)
            
    def update_account (self, account):
        g = PopBox (account["username"], account["password"], account["host"])
        account.new_unread = []
        mails = g.get_mails()
        for mail_id, sub, fr in mails:
            if mail_id not in account.notifications:
                n = Notification(mail_id, sub, fr)
                account.notifications[mail_id] = sub
                account.new_unread.append (n)
    
    def populate_dialog(self, builder, acc):
        self._set_text_value ("host_entry",acc["host"])
        self._set_text_value ("username_entry",acc["username"])
        self._set_text_value ("password_entry", acc["password"])
    
    def save_from_dialog(self, builder, account_name, acc = None):
        if not acc:
            host = self._get_text_value ("host_entry")
            username = self._get_text_value ("username_entry")
            password = self._get_text_value ("password_entry")
            props = {'name' : account_name, 'provider_name' : self.get_name(),
                'host' : host, 'username' : username, 'password' : password}
            acc = self.load_account(props)
        else:
            acc["host"] = self._get_text_value ("host_entry")
            acc["username"] = self._get_text_value ("username_entry")
            acc["password"] = self._get_text_value ("password_entry")
        
        return acc
        
class PopBoxConnectionError(Exception): pass
class PopBoxAuthError(Exception): pass

class PopBox:
    #TODO Set the port and ssl correctly
    #def __init__(self, user, password, host, port = 110, ssl = False):
    def __init__(self, user, password, host, port = 995, ssl = True):
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
        except Exception, e:
            logger.error("Error connecting the POP3 account: " + str(e))
            raise PopBoxConnectionError()

        try:
            self.mbox.user(self.user)
            self.mbox.pass_(self.password)
        except poplib.error_proto, e:
            logger.error("Auth Error connecting the POP3 account: " + str(e))
            raise PopBoxAuthError()

    def get_mails(self):
        self.__connect()

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
                sub = utils.mime_decode(msg.get("Subject"))
                msgid = msg.get("Message-Id")
                if not msgid:
                    msgid = hash(msg.get("Received") + sub)
                fr = utils.mime_decode(msg.get("From"))
                messages.append( [msgid, sub, fr] )
            except Exception, e:
                logger.error("Error reading pop3 box: " + str(e))
		
        self.mbox.quit()
        return messages
