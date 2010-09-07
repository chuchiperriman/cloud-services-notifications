# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
"""
Based on pop3.py:

    Copyright 2009-2010 cGmail Core Team
    https://code.launchpad.net/cgmail
    
"""
from cloudsn.providers.providersbase import ProviderUtilsBuilder
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.keyring import Credentials
from cloudsn.core import config
from cloudsn.core import utils
from cloudsn import logger

import poplib
from email.Parser import Parser as EmailParser
from email.header import decode_header
import gtk

class Pop3Provider(ProviderUtilsBuilder):

    __default = None

    def __init__(self):
        if Pop3Provider.__default:
           raise Pop3Provider.__default
        ProviderUtilsBuilder.__init__(self, "Pop3")

    @staticmethod
    def get_instance():
        if not Pop3Provider.__default:
            Pop3Provider.__default = Pop3Provider()
        return Pop3Provider.__default

    def load_account(self, props):
        acc = AccountCacheMails(props, self)
        if not "port" in acc:
            acc["port"] = 110
        if not "ssl" in acc:
            acc["ssl"] = False
        return acc
            
    def update_account (self, account):
        credentials = account.get_credentials()
        g = PopBox (credentials.username, credentials.password, 
            account["host"], account["port"], 
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
        logger.debug("Starting reading POP messages")
        msgs = self.mbox.list()[1]
        logger.debug("POP messages readed: %i" % (len(msgs)))
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
