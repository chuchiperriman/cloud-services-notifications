"""
Based on pop3.py:

    Copyright 2009-2010 cGmail Core Team
    https://code.launchpad.net/cgmail
    
"""
from cloudsn.core.provider import Provider
from cloudsn.core.account import Account, AccountManager
from cloudsn.core import config
from cloudsn.core import utils

import poplib
from email.Parser import Parser as EmailParser
from email.header import decode_header
import gtk

class Pop3Provider(Provider):

    __default = None

    def __init__(self):
        if Pop3Provider.__default:
           raise Pop3Provider.__default
        Provider.__init__(self, "Pop3")
        self.icon = gtk.gdk.pixbuf_new_from_file(config.add_data_prefix('pop3.png'))

    @staticmethod
    def get_instance():
        if not Pop3Provider.__default:
            Pop3Provider.__default = Pop3Provider()
        return Pop3Provider.__default
        
    def register_accounts (self):
        sc = config.SettingsController.get_instance()
        am = AccountManager.get_instance()
        for account_name in sc.get_account_list_by_provider(self):
            acc_config = sc.get_account_config(account_name)
            acc = Pop3Account (account_name, acc_config["host"], acc_config["username"], acc_config["password"])
            am.add_account (acc)

    def update_account (self, account):
        g = PopBox (account["username"], account["password"], account["host"])
        news = []
        mails = g.get_mails()
        account.unread = len(mails)
        for mail_id, sub, fr in mails:
            if mail_id not in account.mails:
                account.mails[mail_id] = sub
                news.append (mail_id)

        account.new_unread = len (news);
        
    def _create_dialog(self):
        builder=gtk.Builder()
        builder.set_translation_domain("cloudsn")
        builder.add_from_file(config.add_data_prefix("pop3-account.ui"))
        dialog = builder.get_object("dialog")
        dialog.set_icon(self.get_icon())
        return (builder, dialog)
        
    def create_account_dialog(self, account_name):
        builder, dialog = self._create_dialog()
        account = None
        if dialog.run() == 0:
            host = builder.get_object("host_entry").get_text()
            username = builder.get_object("username_entry").get_text()
            password = builder.get_object("password_entry").get_text()
            account = Pop3Account(account_name, host, username, password)
        dialog.destroy()
        return account
        
    def edit_account_dialog(self, acc):
        res = False
        builder, dialog = self._create_dialog()
        builder.get_object("host_entry").set_text(acc["host"])
        builder.get_object("username_entry").set_text(acc["username"])
        builder.get_object("password_entry").set_text(acc["password"])
        account = None
        if dialog.run() == 0:
            acc["host"] = builder.get_object("host_entry").get_text()
            acc["username"] = builder.get_object("username_entry").get_text()
            acc["password"] = builder.get_object("password_entry").get_text()
            res = True
        dialog.destroy()
        return res


class Pop3Account (Account):

    def __init__(self, name, host, username, password):
        Account.__init__(self, name, Pop3Provider.get_instance())
        #TODO Add port, ssl etc
        self["host"] = host
        self["username"] = username
        self["password"] = password
        self.mails = {}
    def activate(self):
        utils.open_mail_reader()
    
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
        except Exception as e:
            logger.error("Error connecting the POP3 account: " + e)
            raise PopBoxConnectionError()

        try:
            self.mbox.user(self.user)
            self.mbox.pass_(self.password)
        except poplib.error_proto as e:
            logger.error("Auth Error connecting the POP3 account: " + e)
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
            except poplib.error_proto, e:
                logger.error("Error reading pop3 box: " + e)
		
        self.mbox.quit()
        return messages
