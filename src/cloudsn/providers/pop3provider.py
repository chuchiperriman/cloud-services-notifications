# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from cloudsn.providers.providersbase import ProviderUtilsBuilder
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.keyring import Credentials
from cloudsn.core import utils
from cloudsn.core.config import SettingsController
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
        self.parser = EmailParser()

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
    
        mbox = self.__connect(account)
        
        messages, new_messages = self.__get_mails(mbox, account)
        
        num_messages = len(new_messages)
        max_not = float(SettingsController.get_instance().get_prefs()["max_notifications"])
        
        account.new_unread = []
        for mail_id, mail_num in new_messages:
            account.notifications[mail_id] = mail_num
            #We only get the e-mail content if all will be shown
            if num_messages <= max_not:
                msgNum, sub, fr = self.__get_mail_content(mbox, mail_num)
                #Store the mail_id, not the msgNum
                n = Notification(mail_id, sub, fr)
            else:
                n = Notification(mail_id, "New mail", "unknow")
            account.new_unread.append (n)
        
        #Remove old unread mails not in the current list of unread mails
        #TODO Do this better!!!!!
        only_current_ids = []
        for mail_id, mail_num in messages:
            only_current_ids.append(mail_id)
        for nid in account.notifications.keys():
            if nid not in only_current_ids:
                del account.notifications[nid]
        
        mbox.quit()

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
    
    #************** email methods **************
    def __connect(self, account):
        credentials = account.get_credentials()
        port = 110
        if "port" in account:
            port = int(float(account["port"]))
            
        if not utils.get_boolean(account["ssl"]):
            mbox = poplib.POP3(account["host"], port)
        else:
            mbox = poplib.POP3_SSL(account["host"], port)
        mbox.user(credentials.username)
        mbox.pass_(credentials.password)
        
        return mbox
        
    def __get_mails(self, mbox, account):
        """ Returns:
            [list of [msgId, msgNum] all mails, list of [msgId, msgNum] new mails"""
        
        new_messages = []
        messages = []
        ids = mbox.uidl()
        max_not = float(SettingsController.get_instance().get_prefs()["max_notifications"])
        for id_pop in ids[1]:
            msgNum = int(id_pop.split(" ")[0])
            msgId = id_pop.split(" ")[1]
            
            messages.append( [msgId, msgNum] )
            if msgId not in account.notifications:
                new_messages.append( [msgId, msgNum] )

        return [messages, new_messages]
        
    def __get_mail_content(self, mbox, msgNum):
        # retrieve only the header
        st = "\n".join(mbox.top(msgNum, 0)[1])
        #print st
        #print "----------------------------------------"
        msg = self.parser.parsestr(st, True) # header only
        sub = utils.mime_decode(msg.get("Subject"))
        fr = utils.mime_decode(msg.get("From"))
        return [msgNum, sub, fr]

